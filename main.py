import pprint
import asyncio
import yaml
import glob

from LyricsImageGenerator import LyricsImageGenerator

def load_yaml(file_path):
    try:
        with open(file_path, mode='r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        return None


class Settings():
    def __init__(self):
        self.settings = load_yaml(fr"input/settings.yml")
        self.back_ground_color_1 = self.settings["배경색1"]
        self.back_ground_color_2 = self.settings["배경색2"]
        self.font_file_path = self.settings["글자체 주소"]
        self.video_url = self.settings["동영상 url"]


settings = Settings()


class CreateDatas:
    def __init__(self):
        self.title_settings = load_yaml(fr"input/title.yml")

        self.korean_title = self.title_settings["조선말 제목"]
        self.korean_title_font_size = self.title_settings["조선말 제목 글자 크기"]

        self.japanese_title = self.title_settings["일본말 제목"]
        self.japanese_title_font_size = self.title_settings["일본말 제목 글자 크기"]

        self.lyricist = self.title_settings["작사"]
        self.composer = self.title_settings["작곡"]
        self.performer = self.title_settings["연주"]

        self.title_display_time = self.title_settings["표시시간"]

    async def create_title_image(self):
        img = await LyricsImageGenerator.create_title_image(self.korean_title, self.japanese_title, settings.back_ground_color_1, settings.back_ground_color_2, settings.font_file_path, self.korean_title_font_size, self.japanese_title_font_size, self.lyricist, self.composer, self.performer)
        return img
    

    async def create_lyrics_image(self):
        imgs = []
        files = glob.glob("./input/*")

        for file in files:
            file_path = file
            file_name = file_path.removeprefix("./input\\").removesuffix(".yml")
            words = ["settings", "title", "input_templates"]
            if not any(word in file_name for word in words):
                lyrics_datas = load_yaml(f"input/{file_name}.yml")
                lyrics = (lyrics_datas["가사"]).split("\n")

                img = await LyricsImageGenerator.create_lyrics_image(lyrics, settings.back_ground_color_1, settings.font_file_path, file_name)
                imgs.append(img)

        return imgs


        

cd = CreateDatas()


async def main():
    img = await cd.create_title_image()
    imgs = await cd.create_lyrics_image()



if __name__ == "__main__":
    asyncio.run(main())