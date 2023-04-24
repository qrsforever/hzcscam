import asyncio
import asyncio_mqtt as aiomqtt


async def listen():
    reconnect_interval = 5  # In seconds
    while True:
        try:
            async with aiomqtt.Client("127.0.0.1", port=1883) as client:
                async with client.messages() as messages:
                    await client.subscribe("humidity/#")
                    async for message in messages:
                        print(message.payload.decode())
        except aiomqtt.MqttError as error:
            print(f'Error "{error}". Reconnecting in {reconnect_interval} seconds.')
            await asyncio.sleep(reconnect_interval)


async def main():
    # Wait for messages in (unawaited) asyncio task
    loop = asyncio.get_event_loop()
    task = loop.create_task(listen())
    # This will still run!
    print("Magic!")
    # If you don't await the task here the program will simply finish.
    # However, if you're using an async web framework you usually don't have to await
    # the task, as the framework runs in an endless loop.
    await task


asyncio.run(main())
