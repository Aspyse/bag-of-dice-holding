import discord

chance = discord.SlashCommandGroup("chance", "Probability calculators from Bag of Dice Holding")

@chance.command(description="Calculate probability to hit.")
async def hit(ctx):
    print("probably misses tbh")