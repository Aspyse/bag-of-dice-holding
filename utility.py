import discord
from rolling_implementation import *

utility = discord.SlashCommandGroup("utility", "Utility commands from Bag of Dice Holding")

@utility.command(description="Roll for death saves.")
async def deathsaves(ctx, character: discord.Option(str, default='')):
    if character == '':
        character = ctx.user.display_name
    successes = 0
    failures = 0
    deathview = discord.ui.View()
    rollbutton = discord.ui.Button(label="Roll")
    async def rollcallback(interaction):
        interaction.response.defer()
        roll = rollnotation("1d20")
        await interaction.response.send_message(f"{character}'s **death save** ([1d20]): {roll[2]}")
        if roll == 20:
            successes = 3
            await interaction.followup.edit_message(interaction.message.id, content=f"")
        elif roll >= 10:
            successes += 1
        elif roll > 1:
            failures += 1
        else:
            failures += 2
        if successes == 3:
            await interaction.response.edit_message(interaction.message.id, content=f"{character} lives!")
        if failures == 3:
            await interaction.response.edit_message(interaction.message.id, content=f"{character} has died.")
    rollbutton.callback = rollcallback
    deathview.add_item(rollbutton)
    await ctx.respond(f"**{character} is rolling to cheat death**\nSuccesses: :white_small_square::white_small_square::white_small_square: Failures: :white_small_square::white_small_square::white_small_square:", view=deathview)