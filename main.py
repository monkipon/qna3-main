from qna3 import Qna3
import random
import time
import art
from utils import *
import asyncio
from config import THREADS


async def process_private_key(private_key, proxy, semaphore):
    async with semaphore:
        qna3_bot = Qna3(private_key, proxy)
        await qna3_bot.get_graphl()

        if qna3_bot.todayCount == 0:
            result = await qna3_bot.verify_transaction()
            print(f"{qna3_bot.account.address} | {result} | {qna3_bot.proxy_ip}")
        else:
            print(f"{qna3_bot.account.address} | {qna3_bot.checkInDays} | {qna3_bot.todayCount} | {qna3_bot.proxy_ip}")

        await qna3_bot.close_session()




def make_art():
    art_text = art.text2art('Qna3')
    lines = "-" * len(art_text.split('\n')[0])
    print(f"{lines}\n{art_text}{lines}")
    print('Создатель: https://t.me/Genjurx')


async def main():
    make_art()
    time1 = time.time()
    private_keys = await read_private_keys('./inputs/keys.txt')
    proxies = await read_proxies('./inputs/proxies.txt')

    semaphore = asyncio.Semaphore(THREADS)

    tasks = [process_private_key(private_key, proxies[i % len(proxies)], semaphore) for i, private_key in enumerate(private_keys)]

    await asyncio.gather(*tasks)

    time2 = time.time()
    final_time = time2 - time1
    print(final_time)

if __name__ == "__main__":
    asyncio.run(main())
