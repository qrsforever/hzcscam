# SuperFastPython.com
# forcing the exit of the event loop
import asyncio
 
# task coroutine
async def work():
    # report a message
    print('Task starting')
    # simulate work
    await asyncio.sleep(2)
    # exit the event loop
    raise Exception('Stop this thing')
    # report a message
    print('Task done')
 

# main coroutine
async def main1():
    # schedule the task
    task = asyncio.create_task(work())
    # suspend a moment
    await task
    # report a message
    print('Main done')

# if __name__ == "__main__":
    # # run the asyncio program
    # asyncio.run(main1())

async def my_callback(arg1, arg2):
    print(f'Callback called with arguments {arg1}, {arg2}')

loop = asyncio.get_event_loop()
loop.call_later(5, my_callback, 'hello', 'world')
loop.run_forever()
