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
    def embed(self):
        
        match self.status:
            case 0:
                description = f"\"*{self.gift_description}*\"\n\nThis gift is LOCKED🔒! "
            case 1:
                description = f"\"*{self.gift_description}*\"\n\nThis gift has ONE steal left! "
            case 2:
                description = f"\"*{self.gift_description}*\"\n\nThis gift has TWO steals left! "
            case 3:
                description = f"\"*{self.gift_description}*\""

        if self.status < 3:
            description += f"It is Currently held by {self.holder.mention}, and it was brought by {self.buyer.mention}."

        embed = discord.Embed(
            color=discord.Color.blurple(), 
            description=description)

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
            
            match gift.status:
                case 0:
                    emoji = "🔒"
                    description = gift.gift_description
                case 1:
                    emoji = "1️⃣"
                    description = gift.gift_description
                case 2:
                    emoji = "2️⃣"
                    description = gift.gift_description
                case _:
                    emoji = "🎁"
                    description = gift.box_description

            embed.description += f"**{i + 1})** {emoji} \"*{description}*\""
            if gift.status < 3:
                embed.description += f" - {gift.holder.mention}"
            embed.description += "\n"

        return embed
