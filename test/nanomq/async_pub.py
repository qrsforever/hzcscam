import asyncio
import asyncio_mqtt as aiomqtt


async def publish_humidity(client):
    await client.publish("humidity/outside", payload=0.38)


async def publish_temperature(client):
    await client.publish("temperature/outside", payload=28.3)


async def main():
    async with aiomqtt.Client("127.0.0.1", port=1883) as client:
        await publish_humidity(client)
        await publish_temperature(client)
        print('finish quit')


asyncio.run(main())
