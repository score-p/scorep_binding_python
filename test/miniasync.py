#!/usr/bin/env python3

import asyncio

work_size = 10000000


def actual_work(i):
    return sum(range(i))


async def work1():
    for i in range(5):
        print("work1 ", actual_work(i * work_size))
        await asyncio.sleep(1)


async def work2():
    for i in range(5):
        print("work2 ", actual_work(i * work_size))
        await asyncio.sleep(1)


async def amain():
    await asyncio.gather(
        work1(),
        work2(),
        asyncio.get_event_loop().getaddrinfo("tu-dresden.de", 80),
        asyncio.get_event_loop().getaddrinfo("www.tu-dresden.de", 80),
    )


def main():
    asyncio.run(amain())


if __name__ == "__main__":
    main()
