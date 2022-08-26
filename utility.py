import discord
from rolling_implementation import *

utility = discord.SlashCommandGroup("utility", "Utility commands from Bag of Dice Holding")

@utility.command(description="Roll for death saves.")
async def deathsaves(ctx, character: discord.Option(str, default='')):
    if character == '':
        character = ctx.user.display_name
    deathview = discord.ui.View()
    rollbutton = DeathButton(label="Roll", style=discord.ButtonStyle.blurple, character=character)
    deathview.add_item(rollbutton)
    await ctx.respond(f"**{character} is rolling to cheat death**\nSuccesses: :white_small_square::white_small_square::white_small_square: Failures: :white_small_square::white_small_square::white_small_square:", view=deathview)

class DeathButton(discord.ui.Button):
    def __init__(self, character, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.character = character
        self.successes = 0
        self.failures = 0

    async def callback(self, interaction):
        roll = await rollnotation("1d20")
        roll = roll[2]
        await interaction.response.send_message(f"{self.character}'s **Death Save** ([1d20]): {roll}")
        if roll == 20:
            self.successes = 3
            await interaction.followup.edit_message(interaction.message.id, content=f"")
        elif roll >= 10:
            self.successes += 1
        elif roll > 1:
            self.failures += 1
        else:
            self.failures += 2

        if self.successes == 3:
            await interaction.followup.edit_message(interaction.message.id, content=f"**:sparkles:{self.character} lives!:sparkles:**", view=None)
            
        elif self.failures == 3:
            await interaction.followup.edit_message(interaction.message.id, content=f"**:headstone:{self.character} has died.:headstone:**", view=None)
        else:
            await interaction.followup.edit_message(interaction.message.id, content=f"**{self.character} is rolling to cheat death**\nSuccesses: {':mending_heart:'*self.successes}{':white_small_square:'*(3-self.successes)} Failures: {':skull:'*self.failures}{':white_small_square:'*(3-self.failures)}")