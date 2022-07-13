import discord
from discord.ext import commands, sections

@commands.command(description="")
async def help(ctx, section: discord.Option(required=False, choices=[
    discord.OptionChoice(name="Dice"),
    discord.OptionChoice(name="Encounter"),
    discord.OptionChoice(name="Chance"),
    discord.OptionChoice(name="Utility"),
    discord.OptionChoice(name="Help")
])):
        sections = [
            discord.Embed(title="How to Use Your Bag of Tricks", description="These are the commands you will need to get started with your Bag of Tricks."),
            discord.Embed(title="Dice Commands", description="Roll dice and manage your dice inventory. All of these commands may be accessed through or prefixed with `/dice`."),
            discord.Embed(title="Encounter Commands", description="Manage and track encounters and initiative. All of these may be accessed through or prefixed with `/encounter`."),
            discord.Embed(title="Chance Commands", description="Calculate chances/probabilties. All of these may be accessed through or prefixed with `/chance`."),
            discord.Embed(title="Utility Commands", description="Miscellaneous utility commands. All of these may be accessed through or prefixed with `/utility`."),
            discord.Embed(title="Help Commands", description="Pop up the Bag of Tricks help manual and its different sections. ")
        ]
        for section in sections:
            section.color = discord.Color.from_rgb(255, 201, 14)
            section.set_footer(text="Buy me a coffee! https://ko-fi.com/aspyse")

        sections[1].add_field(name="`/bag`", value="The main command you will be using. Opens an inventory for creating and rolling saved dice.")   
        sections[1].add_field(name="`/roll`", value="Manually make a roll using dice notation.")
        sections[1].add_field(name="`/save`", value="Manually save a die to your bag.")
        sections[1].add_field(name="`/edit`", value="Edit existing dice saved in your bag.")
        sections[1].add_field(name="`/delete`", value="Delete existing dice saved in your bag.")
        sections[1].add_field(name="`/clear`", value="Clears all dice saved in your bag.")
        sections[1].add_field(name="Notation", value="Follows standard D&D dice notation, with an optional capital A at the start for advantage, or D for disadvantage. A saved die can use addition (+) or subtraction (-), as well as use multiple dice in one save slot.\nEx: **Disadvantaged Precision Attack Roll**: `D1d20+6+1d8`", inline=False)
        sections[1].add_field(name="Limitations", value="Currently, the Bag of Tricks can only hold a maximum of 25 dice at once.\nInteractable commands expire after 2 minutes (Interaction fails).", inline=False)

        sections[5].add_field(name="'/help'", value="Pops up the Bag of Tricks help manual starting at the cover.")
        sections[5].add_field(name="'/help dice'", value="Dice section of the Bag of Tricks help manual.")
        sections[5].add_field(name="'/help encounter'", value="Encounter section of the Bag of Tricks help manual.")
        sections[5].add_field(name="'/help chance'", value="Chance section of the Bag of Tricks help manual.")
        sections[5].add_field(name="'/help utility'", value="Utility section of the Bag of Tricks help manual.")
        sections[5].add_field(name="'/help help'", value="Help directory of the Bag of Tricks help manual.")

def setup(bot):
    bot.add_command(help)