import queue
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
    # (button) delete character
    # DONE (button?) cancel encounter

    # DONE (button) roll for initiatives, sort characters by initiative, SURPRISE IS STATUS
    # DONE ^ delete initiatives message and make new view for queue

    # add status effect with duration
    # DONE track statuses with turn count
    # move between turns
    # remove characters from queue

    # reaction tracker would be great also

    encounter = Encounter(surprise)
    initiativeview = InitiativeView(encounter)
    initiativeembed = InitiativeEmbed(title="Who's in the fight?", encounter=encounter)
    await ctx.respond("Encounter starting", embeds=[initiativeembed], view=initiativeview)

class InitiativeEmbed(discord.Embed):
    def __init__(self, encounter, *args, **kwargs):
        super().__init__(*args,**kwargs)
        for character in encounter.characters:
            self.add_field(name=character.name, value=f"Initiative roll: `{character.initiativeroll}`")

class InitiativeView(discord.ui.View):
    def __init__(self, encounter, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.encounter = encounter

    @discord.ui.button(label="Add player", style=discord.ButtonStyle.blurple)
    async def playercallback(self, button, interaction):
        charactermodal = CharacterModal(self.encounter, title="Add Player to Encounter")
        await charactermodal.create(interaction.user)
        await interaction.response.send_modal(charactermodal)
    
    @discord.ui.button(label="Add enemy", style=discord.ButtonStyle.red)
    async def enemycallback(self, button, interaction):
        charactermodal = CharacterModal(self.encounter, isplayer=False, title="Add Enemy to Encounter")
        await charactermodal.create(interaction.user)
        await interaction.response.send_modal(charactermodal)

    @discord.ui.button(label="Begin encounter", style=discord.ButtonStyle.green)
    async def begin(self, button, interaction):
        if len(self.encounter.characters) > 0:
            for character in self.encounter.characters:
                await character.rollinitiative()
            await self.encounter.sortinitiative()

            queueembed = QueueEmbed(self.encounter)
            await queueembed.refresh()
            queueview = QueueView(self.encounter)
            await interaction.response.defer()
            await interaction.followup.edit_message(interaction.message.id, content=f"{queueembed.fields[0].name}'s turn!", view=queueview, embeds=[queueembed])
        else:
            await interaction.response.send_message("Please add a character first.", ephemeral=True)

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.gray)
    async def cancel(self, button, interaction):
        await interaction.response.defer()
        await interaction.followup.edit_message(interaction.message.id, content="Encounter cancelled.", view=None, embeds=[])

class CharacterModal(discord.ui.Modal):
    def __init__(self, encounter, isplayer=True, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.encounter = encounter
        self.isplayer = isplayer
    
    async def create(self, user):
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

    async def callback(self, interaction):
        quantity = 1
        if len(self.children) > 2:
            quantity = int(self.children[2].value)
        
        if quantity > 1:
            for i in range(quantity):
                self.character = Character(f"{self.children[0].value} {i+1}", self.children[1].value, self.isplayer)
                await self.encounter.addcharacter(self.character)
            await interaction.response.send_message(f"{self.children[0].value} ({quantity}) have been added.", ephemeral=True)
        else:
            self.character = Character(f"{self.children[0].value}", self.children[1].value, self.isplayer)
            await self.encounter.addcharacter(self.character)
            await interaction.response.send_message(f"{self.children[0].value} has been added.", ephemeral=True)

        initiativeembed = InitiativeEmbed(title="Who's in the fight?", encounter=self.encounter)
        initiativeview = InitiativeView(self.encounter)
        await interaction.followup.edit_message(interaction.message.id, content="Encounter starting", embeds=[initiativeembed], view=initiativeview)
    
class QueueEmbed(discord.Embed):
    def __init__(self, encounter, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.encounter = encounter
    
    async def refresh(self):
        charactercount = len(self.encounter.characters)
        initiative = 0 #TODO: SETTLE TIES
        for i in range(charactercount):
            index = (self.encounter.turn+i)%charactercount
            character = self.encounter.characters[index]
            statuses = [status for status in character.statuses if status[1] > 0]
            self.add_field(name=f"{index+1} - {character.name}", value=f"Initiative: {character.initiative} Statuses: `{statuses}`", inline=False)

    async def insert_character(self, character):
        index = 0
        while character.initiative <= self.encounter.characters[index].initiative:
            index += 1
        self.insert_field_at(index, name=f"{index+1} - {character.name}", value=f"Initiative: {character.initiative} Statuses: `{character.statuses}`", inline=False)

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
        )
        self.characterselect.callback = self.selectcallback
        self.add_item(self.characterselect)
    
    async def selectcallback(self, interaction):
        await interaction.response.defer()
    
    @discord.ui.button(label="Previous Turn", row=2)
    async def prevturn(self, button, interaction):
        await self.encounter.next(-1)

        queueembed = interaction.message.embeds[0]
        await queueembed.refresh() # should be a bit more efficient
        await interaction.response.defer()
        await interaction.followup.edit_message(interaction.message.id, content=f"{queueembed.fields[0].name}'s turn!", embeds=[queueembed])

    @discord.ui.button(label="Next Turn", row=2)
    async def nextturn(self, button, interaction):
        await self.encounter.next(1)

        queueembed = interaction.message.embeds[0]
        await queueembed.refresh() # should be a bit more efficient
        await interaction.response.defer()
        await interaction.followup.edit_message(interaction.message.id, content=f"{queueembed.fields[0].name}'s turn!", embeds=[queueembed])

    @discord.ui.button(label="Apply Status", row=1)
    async def applystatus(self, button, interaction):
        if len(self.characterselect.values) > 0:
            await interaction.response.modal(StatusModal())
        else:
            await interaction.response.send_message("Please select a character first.", ephemeral=True)

    @discord.ui.button(label="Eliminate Character", row=1)
    async def elimchar(self, button, interaction):
        if len(self.characterselect.values) > 0:
            # pop up view (list of buttons with character names and 'none') to select killer
            await interaction.response.send_message(self.characterselect.values[0], ephemeral=True)
        else:
            await interaction.response.send_message("Please select a character first.", ephemeral=True)

    @discord.ui.button(label="Player Join", row=3)
    async def addplayer(self, button, interaction):
        charactermodal = CharacterModal(self.encounter, title="Add Enemy to Encounter")
        await charactermodal.create(interaction.user)
        await interaction.response.send_modal(charactermodal)
        await charactermodal.character.rollinitiative()

        queueembed = interaction.message.embeds[0]
        queueembed.insert_character(charactermodal.character)
        await interaction.response.defer()
        await interaction.followup.edit_message(interaction.message.id, embeds=[queueembed])

    @discord.ui.button(label="Enemy Join", row=3)
    async def addenemy(self, button, interaction):
        charactermodal = CharacterModal(self.encounter, isplayer=False, title="Add Enemy to Encounter")
        await charactermodal.create(interaction.user)
        await interaction.response.send_modal(charactermodal)

        queueembed = interaction.message.embeds[0]
        queueembed.insert_character(charactermodal.character)
        await interaction.response.defer()
        await interaction.followup.edit_message(interaction.message.id, embeds=[queueembed])

class StatusModal(discord.ui.Modal):
    def __init__(self, character, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.character = character
        self.add_item(discord.ui.InputText(label="Status Name"))
        self.add_item(discord.ui.InputText(label="Duration"))

    async def callback(self, interaction):
        duration = re.sub("[^0-9]", "", self.children[1].value)
        if duration == None:
            await interaction.response.send_message("Please input number of turns in status duration.", ephemeral=True)
        else:
            self.character.statuses.append([self.children[0].value, duration])
            queueembed = interaction.message.embeds[0]
            await queueembed.refresh()
            await interaction.response.defer()
            await interaction.followup.edit_message(interaction.message.id, embeds=[queueembed])

class Encounter():
    def __init__(self, surprise):
        self.characters = []
        self.turn = 0
        self.surprise = surprise
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
        for i in range(len(self.characters)):
            if self.characters[i].isplayer and self.surprise == 1 or not self.characters[i].isplayer and self.surprise == 2:
                self.characters[i].statuses.append(("Surprise", i+1))

    async def next(self, direction):
        charactercount = len(self.characters)
        delta = direction
        # index = self.turn+delta
        while self.encounter.characters[(self.turn+delta)%charactercount-direction].initiative == self.encounter.characters[(self.turn+delta)%charactercount].initiative and self.encounter.characters[0].initiative != self.encounter.characters[-1].initiative:
            delta += direction
            # index += direction 

        self.turn += delta

        # theres probably a better way to do this tbh
        for character in self.characters:
            character.statuses = [(status[0], status[1]-delta) for status in character.statuses]

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