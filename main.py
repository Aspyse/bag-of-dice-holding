import discord

intents = discord.Intents.default()
activity = discord.Activity(type=discord.ActivityType.listening, name="/help tricks")
bot = discord.Bot(activity=activity)

#from dice import dice
#bot.add_application_command(dice)

bot.load_extension('dice')

#from encounter import encountergroup
#bot.add_application_command(encountergroup)

bot.load_extension('encounter')

from chance import chance
bot.add_application_command(chance)

from utility import utility
bot.add_application_command(utility)

bot.load_extension('help')

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} (ID: {bot.user.id})")
    print("------")

if __name__ == '__main__':
    import config
    bot.run(config.token)