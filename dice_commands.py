import discord
from rolling_implementation import *
from roll_aliases import *

intents = discord.Intents.default()
activity = discord.Activity(type=discord.ActivityType.listening, name="/helpbag")
bot = discord.Bot(activity=activity)
from help import HelpCog
bot.add_cog(HelpCog(bot))

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} (ID: {bot.user.id})")
    print("------")

@bot.slash_command(description="Roll using dice notation.")
async def roll(ctx, dice: discord.Option(str)):
    outroll = await rollnotation(dice)
    await ctx.respond(f"{ctx.author.display_name}'s {outroll[0]}: `{outroll[1]}` = {outroll[2]}")

@bot.slash_command(description="Save a die to your bag.")
async def savedice(ctx, alias: discord.Option(str), dice: discord.Option(str)):
    saveexit = await storedice(ctx.author.id, alias, dice)
    if saveexit == None:
        await ctx.respond(f"Sorry, you can't have more than 25 dice stored at once. Please free up your bag with `/deletedice`, or edit an existing die with `/editdice`.", ephemeral=True)
    else:
        await ctx.respond(f"Dice **{saveexit[0]}** saved: `{saveexit[1]}`", ephemeral=True)

@bot.slash_command(description="Delete all saved dice.")
async def cleardice(ctx):
    clearview = discord.ui.View(timeout=300)
    yes = discord.ui.Button(label="Clear All Dice", style=discord.ButtonStyle.danger)
    async def confirm(interaction):
        await deletealldice(interaction.user.id)
        await interaction.response.send_message(f"{interaction.user.display_name} dumped their dice bag.", ephemeral=True)
    yes.callback = confirm
    clearview.add_item(yes)

    no = discord.ui.Button(label="Cancel")
    async def cancel(interaction):
        await interaction.response.defer()
        await interaction.followup.edit_message(interaction.message.id, content="Cancelled deletion.", view=None)
    no.callback = cancel
    clearview.add_item(no)
    
    await ctx.response.send_message("Are you sure you want to **delete all of your dice**?", view=clearview, ephemeral=True)

@bot.slash_command(description="Open your bag of saved dice.")
async def dicebag(ctx):
    bagview = await showdicebag(ctx.user.id)
    await ctx.respond(f"**{ctx.user.display_name}'s dice bag**", view=bagview, ephemeral=True)

async def showdicebag(user):
    await check_db()
    saveddice = await getdice(user)
    #SHOULD BE THE LONGEST TIMEOUT
    bagview = discord.ui.View(timeout=300)
    for die in saveddice:
        bagview.add_item(DiceButton(label=die[1], command=die[2], style=discord.ButtonStyle.green))

    if len(saveddice) < 25:
        addbutton = discord.ui.Button(emoji="➕")
        async def adddice(interaction):
            await interaction.response.send_modal(StoreModal(interaction.message.id, title="Save new dice"))
        addbutton.callback = adddice
        bagview.add_item(addbutton)

    return bagview

class DiceButton(discord.ui.Button):
    def __init__(self, command, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.command = command
    
    async def callback(self, interaction):
        outroll = await rollnotation(self.command)
        #SHOULD NOT BE EPHEMERAL
        await interaction.response.send_message(f"{interaction.user.display_name}'s **{self.label}** ({self.command}): `{outroll[1]}` = {outroll[2]}")

class StoreModal(discord.ui.Modal):
    def __init__(self, message, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.message = message

        self.add_item(discord.ui.InputText(label="Name"))
        self.add_item(discord.ui.InputText(label="Dice Roll"))

    async def callback(self, interaction):
        saveexit = await storedice(interaction.user.id, self.children[0].value, self.children[1].value)
        await interaction.response.send_message(f"Dice **{saveexit[0]}** saved: `{saveexit[1]}`", ephemeral=True)

        bagview = await showdicebag(interaction.user.id)
        await interaction.followup.edit_message(self.message, view=bagview)

@bot.slash_command(description="Delete selected dice from bag.")
async def deletedice(ctx):
    deleteview = await showdeletebag(ctx.user.id)
    if len(deleteview.children) > 1:
        await ctx.respond(f"**Deleting from {ctx.user.display_name}'s dice bag**", view=deleteview, ephemeral=True)
    else:
        await ctx.respond(f"{ctx.user.display_name}'s dice bag is empty.", ephemeral=True)

async def showdeletebag(user):
    await check_db()
    saveddice = await getdice(user)
    deleteview = discord.ui.View(timeout=300)
    for die in saveddice:
        deleteview.add_item(DeleteButton(label=die[1], style=discord.ButtonStyle.danger))

    donebutton = discord.ui.Button(label="Done")
    async def done(interaction):
        await interaction.response.defer()
        await interaction.followup.edit_message(interaction.message.id, content="Deletion complete.", view=None)
    donebutton.callback = done
    deleteview.add_item(donebutton)

    return deleteview

class DeleteButton(discord.ui.Button): 
    async def callback(self, interaction):
        confirmation = discord.ui.View(timeout=300)
        yes = discord.ui.Button(label="Delete", style=discord.ButtonStyle.danger)
        async def confirm(ctx):
            await removedice(ctx.user.id, self.label)
            await ctx.response.send_message(f"**{self.label}** has been deleted.", ephemeral=True)

            deleteview = await showdeletebag(interaction.user.id)
            if len(deleteview.children) > 1:
                await ctx.followup.edit_message(interaction.message.id, view=deleteview)
            else:
                await ctx.followup.edit_message(interaction.message.id, content=f"{ctx.user.display_name}'s dice bag is empty.", view=None)

            await ctx.followup.edit_message(ctx.message.id, content="Deletion confirmed.", view=None)   
        yes.callback = confirm
        confirmation.add_item(yes)

        no = discord.ui.Button(label="Cancel")
        async def cancel(ctx):
            await ctx.response.defer()
            await ctx.followup.edit_message(ctx.message.id, content="Cancelled deletion.", view=None)
        no.callback = cancel
        confirmation.add_item(no)
        
        await interaction.response.send_message(f"Are you sure you want to delete **{self.label}**?", view=confirmation, ephemeral=True)

@bot.slash_command(description="Edit existing dice from bag.")
async def editdice(ctx):
    editview = await showeditbag(ctx.user.id)
    await ctx.respond(f"**Editing {ctx.user.display_name}'s dice**", view=editview, ephemeral=True)

async def showeditbag(user):
    await check_db()
    saveddice = await getdice(user)
    editview = discord.ui.View(timeout=300)
    for die in saveddice:
        editview.add_item(EditButton(label=die[1], command=die[2], style=discord.ButtonStyle.blurple))

    donebutton = discord.ui.Button(label="Done")
    async def done(interaction):
        await interaction.response.defer()
        await interaction.followup.edit_message(interaction.message.id, content="Editing complete.", view=None)
    donebutton.callback = done
    editview.add_item(donebutton)

    return editview

class EditButton(discord.ui.Button):
    def __init__(self, command, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.command = command
    
    async def callback(self, interaction):
        await interaction.response.send_modal(EditModal(alias=self.label, command=self.command, message=interaction.message.id, title="Edit dice values"))

class EditModal(discord.ui.Modal):
    def __init__(self, alias, command, message, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.message = message

        self.add_item(discord.ui.InputText(label="Name", value=alias))
        self.add_item(discord.ui.InputText(label="Dice Roll", value=command))

    async def callback(self, interaction):
        await updatedice(interaction.user.id, self.alias, self.children[0].value, self.children[1].value)
        if self.alias == self.children[0].value:
            await interaction.response.send_message(f"Dice **{self.children[0].value}** updated: `{self.children[1].value}`", ephemeral=True)
        else:
            await interaction.response.send_message(f"Dice **{self.alias}** updated to **{self.children[0].value}**: `{self.children[1].value}`", ephemeral=True)
        
        editview = await showeditbag(interaction.user.id)
        await interaction.followup.edit_message(self.message, view=editview)

if __name__ == '__main__':
    import config
    bot.run(config.token)