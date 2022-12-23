import os

from .bot import GiftBot


bot = GiftBot()
bot.run(os.getenv("BLURPLE"))
