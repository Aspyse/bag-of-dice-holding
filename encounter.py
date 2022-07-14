import discord
from rolling_implementation import *
from roll_aliases import *

encounter = discord.SlashCommandGroup("encounter", "Encounter commands from Bag of Dice Holding")

@encounter.command(description="Starts an encounter. Let your DM invoke this command.")
async def start(ctx, surprise: discord.Option(required = False, choices=[
    discord.OptionChoice(name="Players"),
    discord.OptionChoice(name="Enemies")])
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
    initiativeembed = InitiativeEmbed("Who's in the fight?", encounter)
    await ctx.respond("Encounter starting", embeds=initiativeembed, view=initiativeview)

class InitiativeEmbed(discord.Embed):
    def __init__(self, encounter, *args, **kwargs):
        super().__init__(*args,**kwargs)
        for character in encounter.characters:
            self.add_field(name=character.name, value=f"Initiative roll: {character.initiativeroll}")

#async def showinitiativeembed(encounter):
#    initiativeembed = discord.Embed(title="Who's in the fight?")
#    for character in encounter.characters:
#        initiativeembed.add_field(name=character.name, value=f"Initiative roll: {character.initiativeroll}")
#    return initiativeembed

class InitiativeView(discord.ui.View):
    def __init__(self, encounter):
        self.encounter = encounter

    @discord.ui.button(label="Add player")
    async def playercallback(self, button, interaction):
        await interaction.response.send_modal(await CharacterModal.create(interaction.user, self.encounter))
    
    @discord.ui.button(label="Add enemy")
    async def enemycallback(self, button, interaction):
        await interaction.response.send_modal(await CharacterModal.create(interaction.user, self.encounter, isplayer=False))

    @discord.ui.button(label="Begin encounter")
    async def begin(self, button, interaction):
        for character in self.encounter.characters:
            character.rollinitiative()
        queueembed = QueueEmbed(self.encounter)

    @discord.ui.button(label="Cancel")
    async def cancel(self, button, interaction):
        await interaction.response.defer()
        await interaction.followup.edit_message(interaction.message, "Encounter cancelled.", view=None, embeds=None)

class CharacterModal(discord.ui.Modal):
    # not sure if completely necessary, could move getdice outside and pass output through parameters
    @classmethod
    async def create(cls, user, encounter, isplayer=True, *args, **kwargs):
        self = CharacterModal()
        self.encounter = encounter

        saveddice = await getdice(user.id)
        initiativeroll = ''
        for dice in saveddice:
            if dice[1].lowercase == "initiative":
                initiativeroll = dice[2]
                break

        self.add_item(discord.ui.InputText(label="Character Name"), value = user.display_name)
        self.add_item(discord.ui.InputText(label="Initiative Roll"), value = initiativeroll)

        return self

    async def callback(self, interaction):
        character = Character(self.children[0].value, self.children[1].value, self.isplayer)
        await self.encounter.addcharacter(character)
        await interaction.response.send_message(f"{self.children[0]} has been created.", ephemeral=True)

        initiativeembed = InitiativeEmbed("Who's in the fight?", encounter)
        initiativeview = InitiativeView(self.encounter)
        await interaction.followup.edit_message(interaction.message, "Encounter starting", emebeds=initiativeembed, view=initiativeview)
    
class QueueEmbed(discord.Embed):
    def __init__(self, encounter, offset, *args, **kwargs):
        super().__init__(*args, **kwargs)
        #TODO: SORT ENCOUNTER.CHARACTERS BY INITIATIVE
        charactercount = len(encounter.characters)
        for i in range(charactercount):
            character = encounter.characters[(offset+i)%charactercount]
            self.add_field(name=character.name, value=f"Initiative: {character.initiative} Statuses: {character.statuses}")        

class Encounter():
    def __init__(self):
        self.characters = []
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

class Character():
    def __init__(self, name, initiativeroll, isplayer=True):
        self.name = name
        self.isplayer = isplayer
        self.initiativeroll = initiativeroll
        self.statuses = [] # status name, duration
    
    async def rollinitiative(self):
        outroll = await rollnotation(self.initiativeroll)
        self.initiative = outroll[2]
