import asyncio
import os
import tempfile
from typing import List, Tuple, Union
from PIL import Image
import numpy as np
import io

import asyncio
import os
import uuid

FPS = 60

# 型: (画像データ, 開始時間, 終了時間)
ImageData = Union[bytes, Image.Image, np.ndarray]
ImageSpec = Tuple[ImageData, str, str]


async def time_to_seconds(t: str) -> float:
    parts = t.split(":")

    if len(parts) == 3:
        # H:MM:SS
        h = int(parts[0])
        m = int(parts[1])
        s = float(parts[2])
        return h * 3600 + m * 60 + s

    elif len(parts) == 2:
        # M:SS
        m = int(parts[0])
        s = float(parts[1])
        return m * 60 + s

    else:
        # 秒のみ入力
        return float(t)


async def seconds_to_frames(seconds: float) -> int:
    return round(seconds * FPS)


async def run_ffmpeg(cmd):
    proc = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    _, stderr = await proc.communicate()

    if proc.returncode != 0:
        raise RuntimeError(stderr.decode())



async def overlay_video(base_path, overlay_path, output_path, x=0, y=0):
    # 一時ファイルを作る
    temp_output = f"{output_path}.{uuid.uuid4().hex}.tmp.mp4"

    cmd = [
        "ffmpeg",
        "-y",
        "-i", base_path,
        "-i", overlay_path,
        "-filter_complex", f"overlay={x}:{y}",
        "-crf", "23",
        "-c:a", "copy",
        "-c:v", "h264_nvenc",
        "-preset", "p1",
        "-rc", "constqp",
        "-qp", "0",
        temp_output
    ]

    proc = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )

    _, stderr = await proc.communicate()

    if proc.returncode != 0:
        raise RuntimeError(stderr.decode())


    os.replace(temp_output, output_path)

    return output_path


async def add_audio(video_path, audio_path, output_path):

    cmd = [
        "ffmpeg",
        "-y",
        "-i", video_path,
        "-i", audio_path,
        "-c:v", "copy",
        "-c:a", "aac",
        "-shortest",
        output_path
    ]
    await run_ffmpeg(cmd)
    return output_path


async def save_image_to_temp(image) -> str:
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
    path = tmp.name
    tmp.close()

    # dict対応
    if isinstance(image, dict) and "image" in image:
        image = image["image"]

    # BytesIO対応
    if isinstance(image, io.BytesIO):
        image.seek(0)  # ← これ超重要
        data = image.read()
        if not data:
            raise ValueError("BytesIO is empty")
        with open(path, "wb") as f:
            f.write(data)

    elif isinstance(image, bytes):
        with open(path, "wb") as f:
            f.write(image)

    elif isinstance(image, Image.Image):
        image.save(path, format="PNG")

    elif isinstance(image, np.ndarray):
        img = Image.fromarray(image)
        img.save(path, format="PNG")

    else:
        raise TypeError(f"Unsupported image type: {type(image)}")
    
    return path


async def create_clip(index: int, image, start: str, end: str) -> str:
    start_sec = await time_to_seconds(start)
    end_sec = await time_to_seconds(end)
    duration = end_sec - start_sec

    image_path = await save_image_to_temp(image)
    temp_video = f"temp_{index}.mp4"

    cmd = [
    "ffmpeg",
    "-y",
    "-loop", "1",
    "-framerate", "60",
    "-i", image_path,
    "-t", str(duration),

    "-c:v", "libx264",
    "-preset", "medium",
    "-crf", "18",                 
    "-pix_fmt", "yuv420p",       
    "-profile:v", "high",         
    "-level", "4.2",              
    "-movflags", "+faststart",    
    

    temp_video
    ]

    await run_ffmpeg(cmd)
    os.remove(image_path)
    return temp_video


async def images_data_to_mp4(
    images: List[ImageSpec],
    output_path: str = "動画/output.mp4",
    cleanup: bool = True,
    synthesize: bool = False,
    video_path = None
):
    for i, (img, s, e) in enumerate(images):
        print(i, type(img), img)
    tasks = [
        create_clip(i, img, start, end)
        for i, (img, start, end) in enumerate(images)
    ]

    temp_files = await asyncio.gather(*tasks)

    concat_file = "concat.txt"
    with open(concat_file, "w", encoding="utf-8") as f:
        for file in temp_files:
            f.write(f"file '{os.path.abspath(file)}'\n")

    await run_ffmpeg([
        "ffmpeg",
        "-y",
        "-f", "concat",
        "-safe", "0",
        "-i", concat_file,
        "-c", "copy",
        output_path
    ])

    if synthesize:
        if not video_path is None:
            temp_with_audio = output_path.replace(".mp4", "_with_audio.mp4")
            await add_audio(output_path, video_path, temp_with_audio)
            os.replace(temp_with_audio, output_path)

    if cleanup:
        for file in temp_files:
            os.remove(file)
        os.remove(concat_file)

    return output_path