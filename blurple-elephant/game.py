"""Base gift and game classes."""

from dataclasses import dataclass
from enum import Enum
from typing import Iterator

import discord


class GameStage(Enum):
    
    prep = 0
    play = 1
    last = 2
    end = 3


@dataclass
class Gift:
    
    buyer: discord.User
    holder: discord.User
    box_description: str
    gift_description: str
    image_link: str
    status: int
   
    @property
    def description(self):
        match self.status:
            case 0:
                return f'🔒 "*{self.gift_description}*"'
            case 1:
                return f'1️⃣ "*{self.gift_description}*"'
            case 2:
                return f'2️⃣ "*{self.gift_description}*"'
            case _:
                return f'🎁 "*{self.box_description}*"'

    @property
    def embed(self):
        
        embed=discord.Embed(
            color=discord.Color.blurple(),
            description=f"\"*{self.gift_description}*\"")

        match self.status:
            case 0:
                footer = f"🔒 LOCKED • Won by {self.holder}"
            case 1:
                footer = f"1️⃣ Steal Left • Held by {self.holder}"
            case 2:
                footer = f"2️⃣ Steals Left • Held by {self.holder}"
            case _:
                footer = f"🎁 Box Description: \"{self.box_description}\""

        embed.set_footer(text=footer)

        if self.image_link:
            embed.set_image(url=self.image_link)

        return embed


class Game:

    def __init__(self):
        self.gifts = list[Gift]()
        self.turns: Iterator[discord.User] = None
        self.first_player: discord.User = None
        self.active_user: discord.User = None
        self.stage = GameStage.prep
        self.last_message: discord.Message = None

    @property
    def embed(self):
        embed = discord.Embed(
            color=discord.Color.blurple(),
            title="This game's gifts:",
            description="")

        for i, gift in enumerate(self.gifts):
            embed.description += f"**{i + 1})** {gift.description}"
            if gift.status < 3:
                embed.description += f" - {gift.holder.mention}"
            embed.description += "\n"

        return embed
