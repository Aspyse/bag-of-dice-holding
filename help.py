import discord

help = discord.SlashCommandGroup("help", "Guides for using commands from Bag of Dice Holding")

@help.command(description="Dice-related command guide for Bag of Dice Holding.")
async def dice(ctx):
    helpembed = discord.Embed(title="How to Use Your Bag of Dice Holding", description="These are the dice commands added by Bag of Dice Holding. All of these may be accessed through or prefixed with `/dice`.", color=discord.Color.from_rgb(255, 201, 14))
    helpembed.add_field(name="`/bag`", value="The main command you will be using. Opens an inventory for creating and rolling saved dice.")   
    helpembed.add_field(name="`/roll`", value="Manually make a roll using dice notation.")
    helpembed.add_field(name="`/save`", value="Manually save a die to your bag.")
    helpembed.add_field(name="`/edit`", value="Edit existing dice saved in your bag.")
    helpembed.add_field(name="`/delete`", value="Delete existing dice saved in your bag.")
    helpembed.add_field(name="`/clear`", value="Clears all dice saved in your bag.")
    helpembed.add_field(name="Notation", value="Follows standard D&D dice notation, with an optional capital A at the start for advantage, or D for disadvantage. A saved die can use addition (+) or subtraction (-), as well as use multiple dice in one save slot.\nEx: **Disadvantaged Precision Attack Roll**: `D1d20+6+1d8`", inline=False)
    helpembed.add_field(name="Limitations", value="Currently, the Bag of Dice Holding can only hold a maximum of 25 dice at once.\nInteractable commands expire after 2 minutes (Interaction fails).", inline=False)
    helpembed.set_footer(text="Buy me a coffee! https://ko-fi.com/aspyse")
    await ctx.respond(embeds=[helpembed], ephemeral=True)

@help.command(description="Encounter guide for Bag of Dice Holding.")
async def encounter(ctx):
    print("doesnt exist yet lol")