import discord
from discord.ext import commands
from rolling_implementation import *

class EncountersCog(discord.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.slash_command(description="Starts an encounter. Let your DM invoke this command.")
    async def startencounter(self, ctx,
        surprise: discord.Option(required = False, choices=[discord.OptionChoice(name="Players"), discord.OptionChoice(name="Enemies")])
    ):
        encounter = Encounter()
        print("encounter started")
        # STORE IN RAM
        initiativeview = InitiativeView()
        # (button) add character and initiative roll notation, optionally roll from saved dice
        # ^ use username by default?
        # ^ use saved dice "initiative" by default, roll if missing
        # ^ (button) dm add enemy/ies with initiative roll(s)
        # (button) edit character and initiative roll notation
        # (button?) cancel encounter

        # (button) roll for initiatives, sort characters by initiative, SURPRISE IS STATUS
        # ^ delete initiatives message and make new view for queue

        # add status effect with duration
        # track statuses with turn count
        # move between turns
        # remove characters from queue

        # reaction tracker would be great also

class InitiativeView(discord.ui.View):
    def __init__(self, encounter):
        self.encounter = encounter

    @discord.ui.button(label="Add player")
    async def addplayer(self, button, interaction):
        interaction.response.send_modal()

class CharacterModal(discord.ui.Modal):
    def __init__(self, name, initiativeroll, encounter, message, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.encounter = encounter
        self.message = message

        self.add_item(discord.ui.InputText(label="Character Name"), value = name)
        self.add_item(discord.ui.InputText(label="Initiative Roll"), value = initiativeroll)

    async def callback(self, interaction):
        # roll for initiative
        character = Character(self.children[0].value, self.children[1].value)
        await self.encounter.addcharacter(character)
        
class Encounter():
    def __init__(self):
        self.players = []
        self.enemies = []
        print("encounter made")

    async def addcharacter(self, character):
        if character.isplayer:
            self.players.append[character]
        else:
            self.enemies.append[character]

class Character():
    def __init__(self, name, initiativeroll, isplayer=True):
        self.name = name
        self.isplayer = isplayer
        self.initiativeroll = initiativeroll
        self.statuses = [] # status name, duration
    
    async def rollinitiative(self):
        outroll = await rollnotation(self.initiativeroll)
        self.initiative = outroll[2]
