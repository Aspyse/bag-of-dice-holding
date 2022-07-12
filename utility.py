import discord

utility = discord.SlashCommandGroup("utility", "Utility commands from Bag of Dice Holding")

@utility.command(description="Roll for death saves.")
async def deathsaves():
    print("ur doomed")