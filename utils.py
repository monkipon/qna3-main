import aiofiles
import art

async def read_private_keys(file_path):
    async with aiofiles.open(file_path, 'r') as file:
        return [line.strip() for line in await file.readlines()]


async def read_proxies(file_path):
    proxies = []
    async with aiofiles.open(file_path, 'r') as file:
        async for line in file:
            parts = line.strip().split(':')
            try:
                proxy = f'http://{parts[2]}:{parts[3]}@{parts[0]}:{parts[1]}'
                proxies.append(proxy)
            except IndexError:
                print(f"Ignore invalid line: {line}")
    return proxies

def make_art():
    art_text = art.text2art('Qna3')
    lines = "-" * len(art_text.split('\n')[0])
    print(f"{lines}\n{art_text}{lines}")
    print('Создатель: https://t.me/Genjurx')
