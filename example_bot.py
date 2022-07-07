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
    outroll = await rolldice(notation)
    await ctx.respond(f"{ctx.author.display_name}'s {outroll[0]}: `{outroll[1]}` = {outroll[2]}")

@bot.slash_command(description="Stores a dice notation under an alias for faster reuse.")
async def store(ctx, alias: discord.Option(str), notation: discord.Option(str)):
    print(alias, notation)
    saveexit = await savedice(ctx.author.id, alias, notation)
    await ctx.respond(f"Alias **{saveexit[0]}** created: `{saveexit[1]}`")

@bot.slash_command(description="Brings up an rollable list of saved dice notations.")
async def dicebag(ctx):
    saveddice = await getdice(ctx.user.id)
    print(saveddice)
    if len(saveddice) < 1:
        await ctx.respond(f"No dice :(")
    else:
        dicebag = discord.ui.View()
        for die in saveddice:
            bruh = DiceButton(ctx, die[1], die[2])
            dicebag.add_item(bruh)
        await ctx.respond(f"Opening {ctx.user.display_name}'s dice bag", view=dicebag) # Send a message with our View class that contains the button

class DiceButton(discord.ui.Button):
    def __init__(self, ctx, label, command):
        super().__init__(label=label, style=discord.ButtonStyle.primary)
        self.ctx = ctx
        self.command = command
    
    async def callback(self, interaction):
        self.outroll = await rolldice(self.command)
        await self.ctx.respond(f"{self.ctx.author.display_name}'s {self.label}: `{self.outroll[1]}` = {self.outroll[2]}")

if __name__ == '__main__':
    import config
    bot.run(config.token)