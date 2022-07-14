import discord
from discord.ext import commands, pages

class HelpCog(discord.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.sections = [
            discord.Embed(title="How to Use Your Bag of Tricks", description="These are the commands you will need to get started with your Bag of Tricks."),
            discord.Embed(title="Dice Commands", description="Roll dice and manage your dice inventory. All of these commands may be accessed through or prefixed with `/dice`."),
            discord.Embed(title="Encounter Commands", description="Manage and track encounters and initiative. All of these may be accessed through or prefixed with `/encounter`."),
            discord.Embed(title="Chance Commands", description="Calculate chance or probabilties. All of these may be accessed through or prefixed with `/chance`."),
            discord.Embed(title="Utility Commands", description="Miscellaneous utility commands. All of these may be accessed through or prefixed with `/utility`."),
            discord.Embed(title="Help Commands", description="Pop up the Bag of Tricks help manual and its different sections. All must be prefixed with `/help`")
        ]
        for section in self.sections:
            section.color = discord.Color.from_rgb(255, 201, 14)
            section.set_footer(text="Buy me a coffee! https://ko-fi.com/aspyse")

        self.sections[1].add_field(name="`/bag`", value="The main command you will be using. Opens an inventory for creating and rolling saved dice.")   
        self.sections[1].add_field(name="`/roll`", value="Manually make a roll using dice notation.")
        self.sections[1].add_field(name="`/save`", value="Manually save a die to your bag.")
        self.sections[1].add_field(name="`/edit`", value="Edit existing dice saved in your bag.")
        self.sections[1].add_field(name="`/delete`", value="Delete existing dice saved in your bag.")
        self.sections[1].add_field(name="`/clear`", value="Clears all dice saved in your bag.")
        self.sections[1].add_field(name="Notation", value="Follows standard D&D dice notation, with an optional capital A at the start for advantage, or D for disadvantage. A saved die can use addition (+) or subtraction (-), as well as use multiple dice in one save slot.\nEx: **Disadvantaged Precision Attack Roll**: `D1d20+6+1d8`", inline=False)
        self.sections[1].add_field(name="Limitations", value="Currently, the Bag of Tricks can only hold a maximum of 25 dice at once.\nInteractable commands expire after 2 minutes (Interaction fails).", inline=False)

        self.sections[2].add_field(name="/start", value="Start an encounter.")
        self.sections[2].add_field(name="Initiative", value="Bag of Tricks begins an encounter with a screen which collates the characters (players and enemies) which are involved in the encounter when it begins, alongside their corresponding initiative dice. Once the characters are complete, initiatives are rolled and the characters are sorted accordingly.", inline=False)
        self.sections[2].add_field(name="Surprise", value="`/encounter start` has an optional parameter `surprise` which identifies if the players or enemies are surprised at the beginning of the encounter.", inline=False)
        self.sections[2].add_field(name="Queue", value="Shows which character is currently taking their turn, and the following characters in their initiative order. Skips surprised characters on the first round.", inline=False)
        self.sections[2].add_field(name="Statuses", value="Apply statuses to characters with their respective durations, and Bag of Tricks will track when it expires.", inline=False)

        self.sections[3].add_field(name="`/hit`", value="Calculate probability in percent to for an attack roll to hit given Attack Bonus and Armor Class.")

        self.sections[4].add_field(name="`/deathsaves`", value="Roll and track death saves.")

        self.sections[5].add_field(name="`/help` or `/help tricks`", value="Pops up the Bag of Tricks help manual starting at the cover.")
        self.sections[5].add_field(name="`/help dice`", value="Dice section of the Bag of Tricks help manual.")
        self.sections[5].add_field(name="`/help encounter`", value="Encounter section of the Bag of Tricks help manual.")
        self.sections[5].add_field(name="`/help chance`", value="Chance section of the Bag of Tricks help manual.")
        self.sections[5].add_field(name="`/help utility`", value="Utility section of the Bag of Tricks help manual.")
        self.sections[5].add_field(name="`/help help`", value="Help directory of the Bag of Tricks help manual.")

    @commands.slash_command(description="Pop up the Bag of Tricks help manual.")
    async def help(self, ctx, section: discord.Option(int, required=False, choices=[
        discord.OptionChoice(name="tricks", value=0),
        discord.OptionChoice(name="dice", value=1),
        discord.OptionChoice(name="encounter", value=2),
        discord.OptionChoice(name="chance", value=3),
        discord.OptionChoice(name="utility", value=4),
        discord.OptionChoice(name="help", value=5)
    ])):
        paginator = pages.Paginator(pages=self.sections)
        await paginator.respond(ctx.interaction, ephemeral=True)

def setup(bot):
    bot.add_cog(HelpCog(bot))