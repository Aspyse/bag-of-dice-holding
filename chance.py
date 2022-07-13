import discord

chance = discord.SlashCommandGroup("chance", "Probability calculators from Bag of Dice Holding")

@chance.command(description="Calculate probability to hit.")
async def hit(ctx, attackbonus: discord.Option(int), armorclass: discord.Option(int)):
    phit = max(0, 1-((armorclass-attackbonus)/20))
    await ctx.respond(f"The chance for an attack roll of `1d20+{attackbonus}` to hit an AC of `{armorclass}` is {round(phit*100)}%.", ephemeral=True)