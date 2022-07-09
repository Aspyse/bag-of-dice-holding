import discord
from rolling_implementation import *
from roll_aliases import *

intents = discord.Intents.default()
bot = discord.Bot()

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} (ID: {bot.user.id})")
    print("------")

@bot.slash_command(description="Rolls the specified dice notation.")
async def roll(ctx, notation: discord.Option(str)):
    outroll = await rollnotation(notation)
    await ctx.respond(f"{ctx.author.display_name}'s {outroll[0]}: `{outroll[1]}` = {outroll[2]}")

@bot.slash_command(description="Stores a dice notation under an alias for faster reuse.")
async def store(ctx, alias: discord.Option(str), notation: discord.Option(str)):
    saveexit = await savedice(ctx.author.id, alias, notation)
    await ctx.respond(f"Alias **{saveexit[0]}** created: `{saveexit[1]}`")

@bot.slash_command(description="Deletes all stored dice.")
async def deleteall(ctx):
    await deletealldice(ctx.author.id)
    await ctx.respond(f"{ctx.author.display_name} dumped their dice bag.")

@bot.slash_command(description="Brings up an rollable list of saved dice notations.")
async def dicebag(ctx):
    bagview = await showdicebag(ctx.user.id)
    await ctx.respond(f"**{ctx.user.display_name}'s dice bag**", view=bagview)

async def showdicebag(user):
    saveddice = await getdice(user)
    bagview = discord.ui.View()
    for die in saveddice:
        bagview.add_item(DiceButton(die[1], die[2]))
    if len(saveddice) < 25:
        addbutton = discord.ui.Button(emoji="➕")
        async def button_callback(interaction):
            await interaction.response.send_modal(StoreView(title="Save new dice alias"))
        addbutton.callback = button_callback
        bagview.add_item(addbutton)
    return bagview

class DiceButton(discord.ui.Button):
    def __init__(self, label, command):
        super().__init__(label=label, style=discord.ButtonStyle.primary)
        self.command = command
    
    async def callback(self, interaction):
        self.outroll = await rollnotation(self.command)
        await interaction.response.send_message(f"{interaction.user.display_name}'s {self.label} ({self.command}): `{self.outroll[1]}` = {self.outroll[2]}")

class StoreView(discord.ui.Modal):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.add_item(discord.ui.InputText(label="Alias"))
        self.add_item(discord.ui.InputText(label="Notation"))

    async def callback(self, interaction):
        saveexit = await savedice(interaction.user.id, self.children[0].value, self.children[1].value)
        await interaction.response.send_message(f"Alias **{saveexit[0]}** created: `{saveexit[1]}`")

        bagview = await showdicebag(interaction.user.id)
        await interaction.followup.send(f"**{interaction.user.display_name}'s dice bag**", view=bagview, ephemeral=True)

if __name__ == '__main__':
    import config
    bot.run(config.token)