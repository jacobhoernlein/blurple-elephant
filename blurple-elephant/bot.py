"""White Elephant bot."""

import discord
from discord.ext.commands import Bot

from .game import Game


class GiftBot(Bot):

    def __init__(self):
        super().__init__(
            "NOPREFIX",
            help_command=None,
            intents=discord.Intents.default())
        
        self.games = dict[int, Game]()

    async def on_ready(self):
        await self.load_extension(".commands", package="blurple-elephant")
        await self.tree.sync()
        print("Online")
