from faulthandler import disable
import discord
from rolling_implementation import *
from roll_aliases import *

encountergroup = discord.SlashCommandGroup("encounter", "Encounter commands from Bag of Dice Holding")

@encountergroup.command(description="Starts an encounter. Let your DM invoke this command.")
async def start(ctx, surprise: discord.Option(int, required = False, choices=[
    discord.OptionChoice(name="Players", value=1),
    discord.OptionChoice(name="Enemies", value=2)])
):
    print("encounter started")
    # STORE IN RAM

    # DONE (button) add character and initiative roll notation, optionally roll from saved dice
    # DONE ^ use username by default?
    # DONE ^ use saved dice "initiative" by default, roll if missing
    # DONE-ISH ^ (button) dm add enemy/ies with initiative roll(s)
    # (button) edit character and initiative roll notation
    # DONE (button?) cancel encounter

    # (button) roll for initiatives, sort characters by initiative, SURPRISE IS STATUS
    # ^ delete initiatives message and make new view for queue

    # add status effect with duration
    # track statuses with turn count
    # move between turns
    # remove characters from queue

    # reaction tracker would be great also

    encounter = Encounter()
    initiativeview = InitiativeView(encounter)
    initiativeembed = InitiativeEmbed(title="Who's in the fight?", encounter=encounter)
    await ctx.respond("Encounter starting", embeds=[initiativeembed], view=initiativeview)

class InitiativeEmbed(discord.Embed):
    def __init__(self, encounter, *args, **kwargs):
        super().__init__(*args,**kwargs)
        for character in encounter.characters:
            self.add_field(name=character.name, value=f"Initiative roll: `{character.initiativeroll}`")

#async def showinitiativeembed(encounter):
#    initiativeembed = discord.Embed(title="Who's in the fight?")
#    for character in encounter.characters:
#        initiativeembed.add_field(name=character.name, value=f"Initiative roll: {character.initiativeroll}")
#    return initiativeembed

class InitiativeView(discord.ui.View):
    def __init__(self, encounter, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.encounter = encounter

    @discord.ui.button(label="Add player", style=discord.ButtonStyle.blurple)
    async def playercallback(self, button, interaction):
        await interaction.response.send_modal(await CharacterModal.create(interaction.user, self.encounter, title="Add Player to Encounter"))
    
    @discord.ui.button(label="Add enemy", style=discord.ButtonStyle.red)
    async def enemycallback(self, button, interaction):
        await interaction.response.send_modal(await CharacterModal.create(interaction.user, self.encounter, isplayer=False, title="Add Enemy to Encounter"))

    @discord.ui.button(label="Begin encounter", style=discord.ButtonStyle.green)
    async def begin(self, button, interaction):
        if len(self.encounter.characters) > 0:
            for character in self.encounter.characters:
                await character.rollinitiative()
            await self.encounter.sortinitiative()
            queueembed = QueueEmbed(self.encounter)
            await interaction.response.defer()

            queueview = QueueView(self.encounter)
            await interaction.followup.edit_message(interaction.message.id, content=f"{queueembed.fields[0].name}'s turn!", view=queueview, embeds=[queueembed])
        else:
            await interaction.response.send_message("Please add a character first.", ephemeral=True)

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.gray)
    async def cancel(self, button, interaction):
        await interaction.response.defer()
        await interaction.followup.edit_message(interaction.message.id, content="Encounter cancelled.", view=None, embeds=[])

class CharacterModal(discord.ui.Modal):
    # not sure if completely necessary, could move getdice outside and pass output through parameters
    @classmethod
    async def create(cls, user, encounter, isplayer=True, *args, **kwargs):
        self = CharacterModal(*args, **kwargs)
        self.encounter = encounter
        self.isplayer = isplayer

        saveddice = await getdice(user.id)
        initiativeroll = '1d20'
        for dice in saveddice:
            if dice[1].lower() == "initiative":
                initiativeroll = dice[2]
                break
        
        if self.isplayer:
            self.add_item(discord.ui.InputText(label="Character Name", value=user.display_name))
            self.add_item(discord.ui.InputText(label="Initiative Roll", value=initiativeroll))
        else:
            self.add_item(discord.ui.InputText(label="Character Name"))
            self.add_item(discord.ui.InputText(label="Initiative Roll", value='1d20'))
            self.add_item(discord.ui.InputText(label="Quantity", value=1))

        return self

    async def callback(self, interaction):
        quantity = 1
        if len(self.children) > 2:
            quantity = int(self.children[2].value)
        
        if quantity > 1:
            for i in range(quantity):
                character = Character(f"{self.children[0].value} {i+1}", self.children[1].value, self.isplayer)
                await self.encounter.addcharacter(character)
            await interaction.response.send_message(f"{self.children[0].value} ({quantity}) have been added.", ephemeral=True)
        else:
            character = Character(f"{self.children[0].value}", self.children[1].value, self.isplayer)
            await self.encounter.addcharacter(character)
            await interaction.response.send_message(f"{self.children[0].value} has been added.", ephemeral=True)

        initiativeembed = InitiativeEmbed(title="Who's in the fight?", encounter=self.encounter)
        initiativeview = InitiativeView(self.encounter)
        await interaction.followup.edit_message(interaction.message.id, content="Encounter starting", embeds=[initiativeembed], view=initiativeview)
    
class QueueEmbed(discord.Embed):
    def __init__(self, encounter, *args, **kwargs):
        super().__init__(*args, **kwargs)
        charactercount = len(encounter.characters)
        initiative = 0 #TODO: SETTLE TIES
        for i in range(charactercount):
            index = (encounter.turn+i)%charactercount
            character = encounter.characters[index]
            self.add_field(name=f"{index+1} - {character.name}", value=f"Initiative: {character.initiative} Statuses: `{character.statuses}`", inline=False)

class QueueView(discord.ui.View):
    def __init__(self, encounter, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.encounter = encounter

        characters = []
        for character in encounter.characters:
            characters.append(discord.SelectOption(label=character.name))
        self.characterselect = discord.ui.Select(
            placeholder="Select Character",
            options=characters,
            row=0,
            disabled=True
        )
        self.characterselect.callback = self.selectcallback
        self.add_item(self.characterselect)
    
    async def selectcallback(self, interaction):
        await interaction.response.defer()
    
    @discord.ui.button(label="Print Character Name", row=1, disabled=True)
    async def printchar(self, button, interaction):
        if len(self.characterselect.values) > 0:
            await interaction.response.send_message(self.characterselect.values[0], ephemeral=True)
        else:
            await interaction.response.send_message("Please select a character first.", ephemeral=True)

    @discord.ui.button(label="Next Turn", row=1)
    async def nextturn(self, button, interaction):
        await self.encounter.next()
        queueembed = QueueEmbed(self.encounter) # inefficient asf wtf lmao
        await interaction.response.defer()
        await interaction.followup.edit_message(interaction.message.id, content=f"{queueembed.fields[0].name}'s turn!", embeds=[queueembed])

class Encounter():
    def __init__(self):
        self.characters = []
        self.turn = 0
        print("encounter made")

    async def addcharacter(self, character):
        self.characters.append(character)

    async def getplayers(self):
        players = []
        for character in self.characters:
            if character.isplayer:
                players.append(character)
        return players

    async def getenemies(self):
        enemies = []
        for character in self.characters:
            if not character.isplayer:
                enemies.append(character)
        return enemies

    async def sortinitiative(self):
        self.characters.sort(key=lambda x: x.initiative, reverse=True)

    async def next(self):
        self.turn += 1

        # theres probably a better way to do this tbh
        for character in self.characters:
            character.statuses = [status.duration-1 for status in character.statuses]

class Character():
    def __init__(self, name, initiativeroll, isplayer=True):
        self.name = name
        self.isplayer = isplayer
        self.initiativeroll = initiativeroll
        self.initiative = 0
        self.statuses = [] # status name, duration
    
    async def rollinitiative(self):
        outroll = await rollnotation(self.initiativeroll)
        self.initiative = outroll[2]