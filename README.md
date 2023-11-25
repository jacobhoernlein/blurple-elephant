# blurple-elephant

A Discord bot written in Python that uses the [discord.py](https://github.com/Rapptz/discord.py) module. Allows users to create and play a White Elephant game through Discord with their friends. Completely plug and play. Just make sure you have an environment variable titled `BLURPLE` with your bot token.

## Commands
`/game create`: Creates a new game in the current channel.
`/game list`: Lists the users who have entered a gift into the channel's game.
`/game start`: Start the game in the current channel.
`/game delete`: Delete the game in the current channel.
`/gift add`: Add a gift to the game before it starts.
`/gift remove`: Remove your gift from the game before it starts.
`/gift open`: Open an unopened gift on your turn.
`/gift steal`: Steal a gift from another player.
`/gift inspect`: Take a closer look at a gift.
