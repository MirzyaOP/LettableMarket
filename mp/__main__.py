import asyncio
import importlib

from pyrogram import idle

from mp import app, LOGGER
from mp.modules import ALL_MODULES


async def market():
    for all_module in ALL_MODULES:
        importlib.import_module(f"mp.modules.{all_module}")
    LOGGER.info(f"Successfully loaded {len(ALL_MODULES)}.")
    LOGGER.info("Bot Started")
    await idle()

    try:
        await app.stop()
    except:
        pass
    LOGGER.info("Stopping! GoodBye")


if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(market())