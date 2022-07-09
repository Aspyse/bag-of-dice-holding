from logging import PlaceHolder
import discord
from rolling_implementation import *
from roll_aliases import *

intents = discord.Intents.default()
bot = discord.Bot()

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} (ID: {bot.user.id})")
    print("------")

@bot.slash_command(description="Rolls using dice notation.")
async def roll(ctx, dice: discord.Option(str)):
    outroll = await rollnotation(dice)
    await ctx.respond(f"{ctx.author.display_name}'s {outroll[0]}: `{outroll[1]}` = {outroll[2]}")

@bot.slash_command(description="Stores dice notation for faster reuse.")
async def storedice(ctx, alias: discord.Option(str), dice: discord.Option(str)):
    saveexit = await savedice(ctx.author.id, alias, dice)
    await ctx.respond(f"Dice **{saveexit[0]}** saved: `{saveexit[1]}`", ephemeral=True)

@bot.slash_command(description="Deletes all stored dice.")
async def cleardice(ctx):
    clearview = discord.ui.View()
    yes = discord.ui.Button(label="Clear All Dice", style=discord.ButtonStyle.danger)
    async def confirm(interaction):
        await deletealldice(interaction.user.id)
        await interaction.response.send_message(f"{interaction.user.display_name} dumped their dice bag.", delete_after=30)
    yes.callback = confirm
    clearview.add_item(yes)

    no = discord.ui.Button(label="Cancel")
    async def cancel(interaction):
        await interaction.response.defer()
        await interaction.followup.delete_message(interaction.message.id)
    no.callback = cancel
    clearview.add_item(no)
    
    await ctx.response.send_message("Are you sure you want to **delete all of your dice**?", view=clearview, delete_after=30)

@bot.slash_command(description="Opens your bag of saved dice.")
async def dicebag(ctx):
    bagview = await showdicebag(ctx.user.id)
    await ctx.respond(f"**{ctx.user.display_name}'s dice bag**", view=bagview, delete_after=300)

async def showdicebag(user):
    await check_db()
    saveddice = await getdice(user)
    bagview = discord.ui.View()
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
        self.outroll = await rollnotation(self.command)
        await interaction.response.send_message(f"{interaction.user.display_name}'s **{self.label}** ({self.command}): `{self.outroll[1]}` = {self.outroll[2]}")

class StoreModal(discord.ui.Modal):
    def __init__(self, message, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.message = message

        self.add_item(discord.ui.InputText(label="Name"))
        self.add_item(discord.ui.InputText(label="Dice Roll"))

    async def callback(self, interaction):
        saveexit = await savedice(interaction.user.id, self.children[0].value, self.children[1].value)
        await interaction.response.send_message(f"Dice **{saveexit[0]}** saved: `{saveexit[1]}`", ephemeral=True)

        bagview = await showdicebag(interaction.user.id)
        await interaction.followup.send(f"**{interaction.user.display_name}'s dice bag**", view=bagview, delete_after=300)
        await interaction.followup.delete_message(self.message)

@bot.slash_command(description="Delete selected dice from bag.")
async def deletedice(ctx):
    deleteview = await showdeletebag(ctx.user.id)
    if len(deleteview.children) > 1:
        await ctx.respond(f"**Deleting from {ctx.user.display_name}'s dice bag**", view=deleteview, delete_after=30)
    else:
        await ctx.respond(f"{ctx.user.display_name}'s dice bag is empty.", delete_after=30)

async def showdeletebag(user):
    await check_db()
    saveddice = await getdice(user)
    deleteview = discord.ui.View()
    for die in saveddice:
        deleteview.add_item(DeleteButton(label=die[1], style=discord.ButtonStyle.danger))

    donebutton = discord.ui.Button(label="Done")
    async def done(interaction):
        await interaction.response.defer()
        await interaction.followup.delete_message(interaction.message.id)
    donebutton.callback = done
    deleteview.add_item(donebutton)

    return deleteview

class DeleteButton(discord.ui.Button): 
    async def callback(self, interaction):
        confirmation = discord.ui.View()
        yes = discord.ui.Button(label="Delete", style=discord.ButtonStyle.danger)
        async def confirm(ctx):
            await removedice(ctx.user.id, self.label)
            await ctx.response.send_message(f"**{self.label}** has been deleted.", ephemeral=True)

            deleteview = await showdeletebag(interaction.user.id)
            if len(deleteview.children) > 1:
                await ctx.followup.send(f"**Deleting from {ctx.user.display_name}'s dice bag**", view=deleteview, delete_after=30)
            else:
                await ctx.followup.send(f"{ctx.user.display_name}'s dice bag is empty.", delete_after=30)

            await interaction.followup.delete_message(interaction.message.id)
            await ctx.followup.delete_message(ctx.message.id)   
        yes.callback = confirm
        confirmation.add_item(yes)

        no = discord.ui.Button(label="Cancel")
        async def cancel(ctx):
            await ctx.response.defer()
            await ctx.followup.delete_message(ctx.message.id)
        no.callback = cancel
        confirmation.add_item(no)
        
        await interaction.response.send_message(f"Are you sure you want to delete **{self.label}**?", view=confirmation, delete_after=30)

@bot.slash_command(description="Edit dice from bag.")
async def editdice(ctx):
    editview = await showeditbag(ctx.user.id)
    await ctx.respond(f"**Editing {ctx.user.display_name}'s dice**", view=editview, delete_after=30)

async def showeditbag(user):
    await check_db()
    saveddice = await getdice(user)
    editview = discord.ui.View()
    for die in saveddice:
        editview.add_item(EditButton(label=die[1], command=die[2], style=discord.ButtonStyle.blurple))

    donebutton = discord.ui.Button(label="Done")
    async def done(interaction):
        await interaction.response.defer()
        await interaction.followup.delete_message(interaction.message.id)
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
        self.alias = alias
        self.command = command
        self.message = message

        self.add_item(discord.ui.InputText(label="Name", placeholder=self.alias))
        self.add_item(discord.ui.InputText(label="Dice Roll", placeholder=self.command))

    async def callback(self, interaction):
        await updatedice(interaction.user.id, self.alias, self.children[0].value, self.children[1].value)
        if self.alias == self.children[0].value:
            await interaction.response.send_message(f"Dice **{self.children[0].value}** updated: `{self.children[1].value}`", ephemeral=True)
        else:
            await interaction.response.send_message(f"Dice **{self.alias}** updated to **{self.children[0].value}**: `{self.children[1].value}`", ephemeral=True)
        
        editview = await showeditbag(interaction.user.id)
        await interaction.followup.send(f"**Editing {interaction.user.display_name}'s dice**", view=editview, delete_after=30)
        await interaction.followup.delete_message(self.message)

if __name__ == '__main__':
    import config
    bot.run(config.token)