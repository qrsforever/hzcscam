#!/usr/bin/python3
# -*- coding: utf-8 -*-

import asyncio

async def main1():
    print("hello1")
    await asyncio.sleep(2)
    print('hello2')


async def cancel_me():
    print('cancel_me(): sleep')
    try:
        # Wait for 1 hour
        await asyncio.sleep(3600)
    except asyncio.CancelledError:
        print('cancel_me(): cancel sleep')
        raise
    finally:
        print('cancel_me(): after sleep')

async def main2():
    print('main(): running')
    # Create a "cancel_me" Task
    task = asyncio.create_task(cancel_me())

    print("main(): sync sleep 2s")
    import time
    time.sleep(2)
    print("main(): sync sleep 2s after (not call cancel_me)")

    # Wait for 5 second
    print('main(): sleep')
    await asyncio.sleep(5)  # this --to--> cancel_me routine
    print('main(): sleep 5s after (already call cancel_me)')

    print('main(): call cancel')
    task.cancel()
    print("main(): after call cancel")
    try:
        await task # already run before await
    except asyncio.CancelledError:
        print('main(): cancel_me is cancelled now')


async def cancel_me3():
    print('cancel_me(): sleep')
    for i in range(1, 21):
        print('cancel_me(): print', i)
        if i % 10 == 0:
            await asyncio.sleep(2)


async def main3():
    print('main(): running')
    # Create a 'cancel_me' Task
    task = asyncio.create_task(cancel_me3())

    # Wait for 60 second
    print('main(): sleep')
    # await asyncio.sleep(60) # after task finish, still wait remain time.

    await task # after task finish, quit


async def do_async_job(fut):
    await asyncio.sleep(2)
    fut.set_result('Hello future')


async def main4():
    loop = asyncio.get_running_loop()

    future = loop.create_future()
    loop.create_task(do_async_job(future))

    # Wait until future has a result
    await future

    print(future.result())


import threading
from datetime import datetime

async def do_async_job5():
    await asyncio.sleep(2)
    print(datetime.now().isoformat(), 'thread id', threading.current_thread().ident)


async def main5():
    job1 = do_async_job5()
    job2 = do_async_job5()
    job3 = do_async_job5()
    await asyncio.gather(job1, job2, job3)


class TestA():
    def __init__(self, loop):
        self.init()
        loop.create_task(self.do_sync_job_a()) # append to task queue
        print("__init__")

    async def do_sync_job_a(self):
        print("do_sync_job_a 1")
        await asyncio.sleep(2)
        print("do_sync_job_a 2")
        print(datetime.now().isoformat(), 'thread id', threading.current_thread().ident)

    def init(self):
        print("init")

async def main6(loop):
    print(asyncio.get_running_loop() == loop)
    testa = TestA(loop)
    await asyncio.sleep(8)

# class TestB():
#     def __init__(self, duration):
#         self.duration = duration
# 
#     def __await__(self):
#         task = asyncio.create_task(asyncio.sleep(self.duration))
#         yield from task
# 
# await TestB()

# class TestB():
#     def __init__(self, **kwargs):
#         self.local = kwargs
# 
#     def __await__(self):
#         task = asyncio.create_task(aiohttp.ClientSession.request(url))
#         self.data = yield from task
#         return self
# 
# dataInstance = await TestB()

class TestD():
    async def run(self):
        raise NotImplementedError

    def create_task(self):
        return asyncio.create_task(self.run())

    def __await__(self):
        return self.run().__await__()

class TestDD(TestD):
    async def run(self):
        print("TestDD--1")
        await asyncio.sleep(3)
        print("TestDD--2")

async def main6():
    await TestDD()

if __name__ == "__main__":
    asyncio.run(main6())
    # loop = asyncio.new_event_loop()
    # asyncio.set_event_loop(loop)
    # try:
    #     loop.run_until_complete(main6(loop=loop))
    # except KeyboardInterrupt:
    #     pass
# https://myapollo.com.tw/blog/begin-to-asyncio/
