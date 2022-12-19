"""Commands for the bot."""

import asyncio
from random import shuffle

import discord

from .game import Gift, Game, GameStage
from .bot import GiftBot


class GameCommandGroup(discord.app_commands.Group):

    def __init__(self, bot: "GiftBot"):
        super().__init__(
            name="game",
            description="Create, start, or delete a game.",
            guild_only=True)
        self.bot = bot

    @discord.app_commands.command(
        name="create",
        description="Create a new game in the current channel.")
    async def game_create(self, interaction: discord.Interaction):
        
        if interaction.channel_id in self.bot.games.keys():
            await interaction.response.send_message(
                "There is already a game in this channel!",
                ephemeral=True)
            return

        self.bot.games[interaction.channel_id] = Game()

        await interaction.response.send_message(
            "Game created. 👍",
            ephemeral=True)

    @discord.app_commands.command(
        name="start",
        description="Start the game in the current channel.")
    async def game_start(self, interaction: discord.Interaction):
        
        try:
            game = self.bot.games[interaction.channel_id]
        except KeyError:
            await interaction.response.send_message(
                "There is no game in this channel!",
                ephemeral=True)
            return

        if game.stage != GameStage.prep:
            await interaction.response.send_message(
                "The game has already started!",
                ephemeral=True)
            return

        shuffle(game.gifts)

        users = [gift.buyer for gift in game.gifts]
        shuffle(users)
        game.turns = iter(users)

        game.first_player = next(game.turns)
        game.active_user = game.first_player

        game.stage = GameStage.play

        await interaction.response.send_message(
            "Game started. 👍",
            ephemeral=True)

        await interaction.channel.send(
            f"The game has begun! {game.active_user.mention}, you can either steal or open a gift!",
            embed=game.embed)

    @discord.app_commands.command(
        name="delete",
        description="Delete the game in the current channel.")
    async def game_delete(self, interaction: discord.Interaction):
        
        try:
            del self.bot.games[interaction.channel_id]
        except KeyError:
            await interaction.response.send_message(
                "There is no game in this channel!",
                ephemeral=True)
            return

        await interaction.response.send_message(
                "Deleted this channel's game!",
                ephemeral=True)
            

class GiftCommandGroup(discord.app_commands.Group):

    def __init__(self, bot: "GiftBot"):
        super().__init__(
            name="gift",
            description="Add, open, steal, or inspect a gift.",
            guild_only=True)
        self.bot = bot

    @discord.app_commands.command(
        name="add",
        description="Add a gift to the game.")
    async def gift_add(
            self, interaction: discord.Interaction,
            box_description: str, description: str,
            image_link: str = ""):

        try:
            game = self.bot.games[interaction.channel_id]
        except KeyError:
            await interaction.response.send_message(
                "There is no game in this channel!",
                ephemeral=True)
            return

        if game.stage != GameStage.prep:
            await interaction.response.send_message(
                "The game has already started!",
                ephemeral=True)
            return

        if interaction.user in [gift.buyer for gift in game.gifts]:
            await interaction.response.send_message(
                "You already have a gift in the game!",
                ephemeral=True)
            return

        gift = Gift(
            interaction.user, interaction.user,
            box_description, description,
            image_link, 3)

        game.gifts.append(gift)

        await interaction.response.send_message(
            "Gift added!",
            embed=gift.embed,
            ephemeral=True)  

    @discord.app_commands.command(
        name="open",
        description="Open an unopened gift.")
    async def gift_open(
            self, interaction: discord.Interaction,
            number: int):

        try:
            game = self.bot.games[interaction.channel_id]
        except KeyError:
            await interaction.response.send_message(
                "There is no game in this channel!",
                ephemeral=True)
            return

        try:
            gift = game.gifts[number - 1]
        except IndexError:
            await interaction.response.send_message(
                "That's not a gift in the game!",
                ephemeral=True)
            return
        
        if interaction.user != game.active_user:
            await interaction.response.send_message(
                "It's not your turn!",
                ephemeral=True)
            return

        if gift.status != 3:
            await interaction.response.send_message(
                "That gift is already opened!",
                ephemeral=True)
            return

        if interaction.user == gift.buyer:
            await interaction.response.send_message(
                "You can't open your own gift!",
                ephemeral=True)
            return

        gift.status -= 1
        gift.holder = interaction.user

        await interaction.response.send_message(
            f"You unwrapped gift number {number}:",
            embed=gift.embed)

        await asyncio.sleep(3)

        try:
            game.active_user = next(game.turns)
        except StopIteration:
            game.active_user = game.first_player
            game.last_message = await interaction.channel.send(
                f"{game.active_user.mention}, you have the last turn! You can steal one last time, or react to this message with ❌ to end the game!")
            game.stage = GameStage.last
        else:
            await interaction.channel.send(
                f"{game.active_user.mention}, you can either steal or open a gift!",
                embed=game.embed)

    @discord.app_commands.command(
        name="steal",
        description="Steal a gift from another player.")
    async def gift_steal(
            self, interaction: discord.Interaction,
            number: int):

        try:
            game = self.bot.games[interaction.channel_id]
        except KeyError:
            await interaction.response.send_message(
                "There is no game in this channel!",
                ephemeral=True)
            return

        try:
            gift = game.gifts[number - 1]
        except IndexError:
            await interaction.response.send_message(
                "That's not a gift in the game!",
                ephemeral=True)
            return
        
        if interaction.user != game.active_user:
            await interaction.response.send_message(
                "It's not your turn!",
                ephemeral=True)
            return
        
        if gift.status == 3:
            await interaction.response.send_message(
                "That gift is not opened!",
                ephemeral=True)
            return

        if gift.status == 0:
            await interaction.response.send_message(
                "That gift is locked!",
                ephemeral=True)
            return  

        if interaction.user == gift.holder:
            await interaction.response.send_message(
                "You can't steal from yourself!",
                ephemeral=True)
            return

        if interaction.user == gift.buyer:
            await interaction.response.send_message(
                "You can't steal the gift you brought!",
                ephemeral=True)
            return

        if game.stage == GameStage.last:
            await interaction.response.send_message(
                f"You swapped gifts with {gift.holder.mention}. The game is now over!")

            # Swap holders of gifts
            user_gift = discord.utils.find(lambda g: g.holder == interaction.user, game.gifts)
            user_gift.holder, gift.holder = gift.holder, user_gift.holder

            await asyncio.sleep(3)

            # FIXME add summary embed.

            game.stage = GameStage.end
            return

        await interaction.response.send_message(
            f"You stole gift {number} from {gift.holder.mention}!")

        await asyncio.sleep(3)

        await interaction.channel.send(
            f"{gift.holder.mention}, you can either steal or open a gift!",
            embed=game.embed)

        gift.status -= 1
        game.active_user = gift.holder
        gift.holder = interaction.user

    @discord.app_commands.command(
        name="inspect",
        description="Take a closer look at a certain present.")
    async def gift_inspect(
            self, interaction: discord.Interaction,
            number: int):

        try:
            game = self.bot.games[interaction.channel_id]
        except KeyError:
            await interaction.response.send_message(
                "There is no game in this channel!",
                ephemeral=True)
            return

        try:
            gift = game.gifts[number - 1]
        except IndexError:
            await interaction.response.send_message(
                "That's not a gift in the game!",
                ephemeral=True)
            return

        if gift.status == 3:
            await interaction.response.send_message(
                "That gift is not opened!",
                ephemeral=True)
            return

        await interaction.response.send_message(
            f"Here is a better look at gift number {number}:",
            ephemeral=True,
            embed=gift.embed)


async def setup(bot: "GiftBot"):
    bot.tree.add_command(GameCommandGroup(bot))
    bot.tree.add_command(GiftCommandGroup(bot))

    @bot.event
    async def on_reaction_add(reaction: discord.Reaction, user: discord.User):

        try:
            game = bot.games[reaction.message.channel.id]
        except KeyError:
            return

        if (reaction.emoji != "❌"
            or game.stage != GameStage.last
            or user != game.active_user
            or reaction.message != game.last_message):
            return

        await reaction.message.channel.send(
            f"{user.mention} chose to end the game. The game is now over!")

        await asyncio.sleep(3)

        # FIXME add summary embed.
        game.stage = GameStage.end
