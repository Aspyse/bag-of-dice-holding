import discord
from rolling_implementation import *
from roll_aliases import *

class MyClient(discord.Client):
    async def on_ready(self):
        print(f"Logged in as {self.user} (ID: {self.user.id})")
        print("------")

    async def on_message(self, message: discord.Message):
        # Make sure we won't be replying to ourselves.
        if message.author.id == self.user.id:
            return

        if message.content.startswith("!roll"):
            outroll = roll(message.content.replace("!roll ", ''))
            await message.channel.send(f"{message.author.display_name}'s {outroll[0]}: `{outroll[1]}` = {outroll[2]}")

        if message.content.startswith("!savedice"):
            #FORMAT OUTPUT MESSAGE HERE INSTEAD
            saveexit = savedice(message.content.replace("!savedice ", ''), message.author.id)
            await message.channel.send(f"Alias *{saveexit[0]}* created: `{saveexit[1]}`")

intents = discord.Intents.default()
intents.message_content = True

client = MyClient(intents=intents)
if __name__ == '__main__':
    import config
    client.run(config.token)