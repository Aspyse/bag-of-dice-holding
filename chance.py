import discord

chance = discord.SlashCommandGroup("chance", "Probability calculators from Bag of Dice Holding")

@chance.command(description="Calculate probability to hit.")
async def hit(ctx):
    hitmodal = HitModal(title="Calculate chance to hit")
    await ctx.send_modal(hitmodal)

class HitModal(discord.ui.Modal):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.add_item(discord.ui.InputText(label="Target Armor Class"))
        self.add_item(discord.ui.InputText(label="Attacker Attack Bonus"))

    async def callback(self, interaction):
        attackbonus = int(self.children[1].value)
        armorclass = int(self.children[0].value)

        phit = max(0, 1-((armorclass-attackbonus)/20))
        await interaction.response.send_message(f"The chance for an attack roll of `1d20+{attackbonus}` to hit an AC of `{armorclass}` is {round(phit*100)}%.", ephemeral=True)