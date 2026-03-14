import pprint
import asyncio
import aiofiles
import yaml

async def load_yaml(file_path):
    async with aiofiles.open(file_path, mode='r', encoding='utf-8') as f:
        data = yaml.safe_load(await f.read())
    return data


async def main():
    datas = await load_yaml(fr"input/input_templates/title_template.yml")
    pprint.pprint(datas)

if __name__ == "__main__":
    asyncio.run(main())