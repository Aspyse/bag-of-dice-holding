import discord
from discord.ext import commands

class HelpCog(discord.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(description="Pop up command list for Bag of Dice Holding.")
    async def helpbag(self, ctx):
        helpembed = discord.Embed(title="How to Use Your Bag of Dice Holding", description="Here are the commands and notation you will need to know to get started with Bag of Dice Holding:", color=discord.Color.from_rgb(255, 201, 14))
        helpembed.add_field(name="`/dicebag`", value="The main command you will be using. Opens an inventory for creating and rolling saved dice.")   
        helpembed.add_field(name="`/roll`", value="Manually make a roll using dice notation.")
        helpembed.add_field(name="`/storedice`", value="Manually save a die to your bag.")
        helpembed.add_field(name="`/editdice`", value="Edit existing dice saved in your bag.")
        helpembed.add_field(name="`/deletedice`", value="Delete existing dice saved in your bag.")
        helpembed.add_field(name="`/cleardice`", value="Clears all dice saved in your bag.")
        helpembed.add_field(name="Notation", value="Follows standard D&D dice notation, with an optional capital A at the start for advantage, or D for disadvantage. A saved die can use addition (+) or subtraction (-), as well as use multiple dice in one save slot.\nEx: **Disadvantaged Precision Attack Roll**: `D1d20+6+1d8`", inline=False)
        helpembed.add_field(name="Limitations", value="Currently, the Bag of Dice Holding can only hold a maximum of 25 dice at once.\nInteractable commands expire after 5 minutes (Interaction fails).", inline=False)
        helpembed.set_footer(text="If you'd like to support the project, buy me a coffee: https://ko-fi.com/aspyse")
        await ctx.respond(embeds=[helpembed], ephemeral=True)
