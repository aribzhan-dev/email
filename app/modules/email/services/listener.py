import asyncio


async def start_email_listener():
    while True:
        print("checking email...")
        await asyncio.sleep(10)