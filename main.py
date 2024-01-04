from qna3 import Qna3
import random
import time
from utils import *
import asyncio
from config import THREADS


async def process_private_key(private_key, proxies, semaphore):
    async with semaphore:
        proxy = random.choice(proxies) if proxies else None
        qna3_bot = Qna3(private_key, proxy)
        result = await qna3_bot.verify_transaction()
        print(f"{qna3_bot.account.address} | {result} | {qna3_bot.proxy_ip}")
        await qna3_bot.close_session()

async def main():
    make_art()
    time1 = time.time()
    private_keys = await read_private_keys('./inputs/keys.txt')
    proxies = await read_proxies('./inputs/proxies.txt')

    semaphore = asyncio.Semaphore(THREADS)

    tasks = [process_private_key(private_key, proxies, semaphore) for private_key in private_keys]

    await asyncio.gather(*tasks)

    time2 = time.time()
    final_time = time2 - time1
    print(final_time)

if __name__ == "__main__":
    asyncio.run(main())
