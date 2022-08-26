import queue
import discord
from discord.ext import commands
from rolling_implementation import *
from roll_aliases import *

# encountergroup = discord.SlashCommandGroup("encounter", "Encounter commands from Bag of Dice Holding")

class EncounterCog(discord.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(description="Starts an encounter. Let your DM invoke this command.")
    async def encounter(self, ctx, surprise: discord.Option(int, required = False, choices=[
        discord.OptionChoice(name="Players", value=1),
        discord.OptionChoice(name="Enemies", value=2)])
    ):
        print("encounter started")

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

    # TODO: REMOVE CHARACTER BUTTON

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

            queueview = QueueView(self.encounter)
            await queueview.queueembed.refresh()
            await interaction.response.defer()

            await interaction.followup.edit_message(interaction.message.id, content=f"{await queueview.queueembed.get_moving()} may move.", view=queueview, embeds=[queueview.queueembed])
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
        
        if quantity > 1 and len(self.encounter.characters) < 25:
            currentlength = len(self.encounter.characters)
            for i in range(quantity):
                self.character = Character(f"{self.children[0].value} {i+1}", self.children[1].value, self.isplayer)
                if (len(self.encounter.characters) < 25):
                    await self.encounter.addcharacter(self.character)
                else:
                    await interaction.response.send_message(f"Only {self.children[0].value} ({i+1}) have been added. Reached character cap.", ephemeral=True)
            if (25-currentlength <= quantity):
                await interaction.response.send_message(f"{self.children[0].value} ({quantity}) have been added.", ephemeral=True)
        elif quantity <= 1:
            self.character = Character(f"{self.children[0].value}", self.children[1].value, self.isplayer)
            await self.encounter.addcharacter(self.character)
            await interaction.response.send_message(f"{self.children[0].value} has been added.", ephemeral=True)
        else:
            await interaction.response.send_message("Character cap has already been reached. Please remove a character to proceed.", ephemeral=True)

        initiativeembed = InitiativeEmbed(title="Who's in the fight?", encounter=self.encounter) # TODO: IMPLEMENT A REFRESH
        #initiativeview = InitiativeView(self.encounter)
        #await interaction.followup.edit_message(interaction.message.id, content="Encounter starting", embeds=[initiativeembed], view=initiativeview)
    
class QueueEmbed(discord.Embed):
    def __init__(self, encounter, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.encounter = encounter
    
    async def refresh(self, delta): # TODO: MAKE MORE EFFICIENT?
        charactercount = len(self.encounter.characters)
        currentinitiative = 0
        moves  = 0

        for i in range(charactercount):
            index = (self.encounter.turns+i)%charactercount
            character = self.encounter.characters[index]
            statuses = [(status[0], str(status[1]+" turns")) for status in character.statuses if status[1] > 0]
            roundstatuses = [(status[0], str(status[1])+" rounds") for status in character.roundstatuses if status[1] > 0 and character is self.encounter.characters[self.encounter.current]]
            if character.initiative != currentinitiative:
                moves += 1
                currentinitiative = character.initiative
            self.add_field(name=f"{moves} - {character.name}", value=f"Initiative: {character.initiative} Attributes: `{statuses}{roundstatuses}`", inline=False)

    async def insert_character(self, character):
        index = 0
        currentinitiative = 0
        moves = 0
        while character.initiative <= self.encounter.characters[index].initiative:
            index += 1
            if character.initiative != currentinitiative:
                moves += 1
                currentinitiative = character.initiative

        statuses = [(status[0], str(status[1]+" turns")) for status in character.statuses if status[1] > 0]
        roundstatuses = [(status[0], str(status[1])+" rounds") for status in character.roundstatuses if status[1] > 0]
        self.insert_field_at(index-self.encounter.current, name=f"{moves} - {character.name}", value=f"Initiative: {character.initiative} Attributes: `{statuses}{roundstatuses}`", inline=False)

        if character.initiative != self.encounter.characters[index+1]:
            charactercount = len(self.encounter.characters)
            while index < charactercount:
                index += 1
                name = self.fields[(index-self.encounter.current)%charactercount].name.split(" ")
                name[0] = str(int(name[0])+1)
                self.fields[(index-self.encounter.current)%charactercount].name = " ".join(name)

    async def get_moving(self):
        # kinda ugly idk
        moving = []
        index = 0
        while self.fields[index].name.split(' ')[0] == self.fields[index+1].name.split(' ')[0]:
            moving.append(self.fields[index].name.split(' ')[-1])
            index += 1
        moving.append("and " + self.fields[index].name.split(' ')[-1])
        return ', '.join(moving)

class QueueView(discord.ui.View):
    def __init__(self, encounter, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.encounter = encounter
        self.queueembed = QueueEmbed(encounter)

        # TODO: UPDATE WHEN ADDING OR REMOVING CHARACTERS
        characters = []
        for i in range(len(encounter.characters)):
            characters.append(discord.SelectOption(label=encounter.characters[i].name, value=str(i))) # why str D:
        self.characterselect = discord.ui.Select(
            placeholder="Select Character",
            options=characters,
            row=0,
        )
        self.characterselect.callback = self.selectcallback

        self.add_item(self.characterselect)
    
    async def selectcallback(self, interaction):
        for child in self.children:
            if child.row == 1:
                child.disabled = False
        await interaction.response.edit_message(interaction.message.id, view=self)
    
    @discord.ui.button(label="Eliminate Character", row=1, style=discord.ButtonStyle.red, disabled=True)
    async def elimchar(self, button, interaction):
        if len(self.characterselect.values) > 0:
            character = self.encounter.characters[int(self.characterselect.values[0])]

            confirmation = discord.ui.View(timeout=120)
            yes = discord.ui.Button(label="Delete", style=discord.ButtonStyle.red)
            async def confirm(confirminteraction):
                self.encounter.characters.remove(character)
                await confirminteraction.response.defer()

                if len(interaction.message.components) > 1:
                    interaction.message.components.remove(self)
                else:
                    await confirminteraction.followup.edit_message(interaction.message.id, content=f"Encounter has no characters.", view=None)

                await confirminteraction.followup.edit_message(confirminteraction.message.id, content=f"**{character.name}** has been removed from the Encounter.", view=None)   
            yes.callback = confirm
            confirmation.add_item(yes)

            no = discord.ui.Button(label="Cancel")
            async def cancel(confirminteraction):
                await confirminteraction.response.defer()
                await confirminteraction.followup.edit_message(confirminteraction.message.id, content="Cancelled deletion.", view=None)
            no.callback = cancel
            confirmation.add_item(no)
            
            await interaction.response.send_message(f"Are you sure you want to eliminate **{character.name}**?", view=confirmation, ephemeral=True)

    @discord.ui.button(label="Add Status (Turns)", row=1, style=discord.ButtonStyle.blurple, disabled=True)
    async def applystatusturns(self, button, interaction):
        if len(self.characterselect.values) > 0:
            await interaction.response.send_modal(StatusModal(title="Apply status to character in turns", character=self.encounter.characters[int(self.characterselect.values[0])]))
        else:
            await interaction.response.send_message("Please select a character first.", ephemeral=True)

    @discord.ui.button(label="Add Status (Rounds)", row=1, style=discord.ButtonStyle.blurple, disabled=True)
    async def applystatusrounds(self, button, interaction):
        if len(self.characterselect.values) > 0:
            await interaction.response.send_modal(StatusModal(title="Apply status to character in rounds", character=self.encounter.characters[int(self.characterselect.values[0])]))
        else:
            await interaction.response.send_message("Please select a character first.", ephemeral=True)

    @discord.ui.button(label="<", row=2, disabled=True, style=discord.ButtonStyle.blurple)
    async def prevturn(self, button, interaction):
        await self.encounter.next(-1)

        self.queueembed.clear_fields()
        await self.queueembed.refresh()
        await interaction.response.defer()
        await interaction.followup.edit_message(interaction.message.id, content=f"{self.queueembed.fields[0].name}'s turn!", embeds=[self.queueembed])
        if (self.encounter.turns < 2):
            button.disabled = True
            self.children[5].label = f"Turn {self.encounter.turns+1}"
            await interaction.followup.edit_message(interaction.message.id, view=self)

    @discord.ui.button(label="Turn 1", row=2, disabled=True)
    async def turndisplay(self, button, interaction):
        await self.response.send_message(content="wtf u werent supposed to click that")

    @discord.ui.button(label=">", row=2, style=discord.ButtonStyle.blurple)
    async def nextturn(self, button, interaction):
        await self.encounter.next(1)

        self.queueembed.clear_fields()
        await self.queueembed.refresh()
        await interaction.response.defer()
        await interaction.followup.edit_message(interaction.message.id, content=f"{await self.queueembed.get_moving()} may move.", embeds=[self.queueembed])
        if (self.encounter.turns > 0):
            self.children[4].disabled = False # idiot way of finding previous turn button, wag tularan
            self.children[5].label = f"Turn {self.encounter.turns+1}"
            await interaction.followup.edit_message(interaction.message.id, view=self)

    @discord.ui.button(label="Player Join", row=3, style=discord.ButtonStyle.blurple)
    async def addplayer(self, button, interaction):
        charactermodal = CharacterModal(self.encounter, title="Add Player to Encounter")
        await charactermodal.create(interaction.user)
        await interaction.response.send_modal(charactermodal)
        await charactermodal.character.rollinitiative()

        self.queueembed.insert_character(charactermodal.character)
        await interaction.response.defer()
        await interaction.followup.edit_message(interaction.message.id, embeds=[self.queueembed])

    @discord.ui.button(label="Enemy Join", row=3, style=discord.ButtonStyle.red)
    async def addenemy(self, button, interaction):
        charactermodal = CharacterModal(self.encounter, isplayer=False, title="Add Enemy to Encounter")
        await charactermodal.create(interaction.user)
        await interaction.response.send_modal(charactermodal)

        self.queueembed.insert_character(charactermodal.character)
        await interaction.response.defer()
        await interaction.followup.edit_message(interaction.message.id, embeds=[self.queueembed])

class StatusModal(discord.ui.Modal):
    def __init__(self, queueembed, character, inrounds=False, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.queueembed = queueembed
        self.character = character
        self.add_item(discord.ui.InputText(label="Status Name"))
        if not inrounds:
            self.add_item(discord.ui.InputText(label="Duration in Turns"))
        else:
            self.add_item(discord.ui.InputText(label="Duration in Rounds"))

    async def callback(self, interaction):
        duration = re.sub("[^0-9]", "", self.children[1].value)
        if duration == None:
            await interaction.response.send_message("Please only input number in status duration.", ephemeral=True)
        else:
            self.character.statuses.append([self.children[0].value, duration])
            queueembed = QueueEmbed(self.encounter)
            await interaction.response.defer()
            await interaction.followup.edit_message(interaction.message.id, embeds=[self.queueembed])

class Encounter():
    def __init__(self, surprise):
        self.characters = []
        self.turns = 0
        self.current = 0 # SHOULD ALWAYS MATCH INDEX OF CHARACTER MOVING
        self.surprise = surprise
        print("encounter made")

    async def addcharacter(self, character):
        if self.characters.index(character) < self.current:
            self.current -= 1
        self.characters.append(character)

    async def removecharacter(self, character):
        if self.characters.index(character) < self.current:
            self.current += 1
        self.characters.remove(character)

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
        # count how many turns to move
        while self.characters[(self.current+delta)%charactercount-direction].initiative == self.characters[(self.current+delta)%charactercount].initiative and self.characters[0].initiative != self.characters[-1].initiative:
            delta += direction
            # index += direction 

        self.turns += delta
        self.current += delta
        self.current %= len(self.characters)

        # theres probably a better way to do this tbh
        for character in self.characters:
            character.statuses = [(status[0], status[1]-delta) for status in character.statuses]
            if character == self.characters[self.current]:
                character.roundstatuses = [(status[0], status[1]-1) for status in character.statuses]

class Character():
    def __init__(self, name, initiativeroll, isplayer=True):
        self.name = name
        self.isplayer = isplayer
        self.initiativeroll = initiativeroll
        self.initiative = 0
        self.statuses = [] # status name, duration in turns
        self.roundstatuses = [] # status name, duration in rounds
    
    async def rollinitiative(self):
        outroll = await rollnotation(self.initiativeroll)
        self.initiative = outroll[2]

def setup(bot):
    bot.add_cog(EncounterCog(bot))