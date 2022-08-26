import discord
from rolling_implementation import *
from roll_aliases import *

class DiceCog(discord.Cog):
    def __init__(self, bot):
        self.bot = bot

    dice = discord.SlashCommandGroup("dice", "Dice and bag commands from Bag of Dice Holding")

    @dice.command(description="Roll using dice notation.")
    async def roll(self, ctx, dice: discord.Option(str)):
        outroll = await rollnotation(dice)
        await ctx.respond(f"{ctx.author.display_name}'s {outroll[0]}: `{outroll[1]}` = {outroll[2]}")

    @dice.command(description="Save a die to your bag.")
    async def save(self, ctx, alias: discord.Option(str), dice: discord.Option(str), emoji: discord.Option(str, required=False)):
        try:
            await storedice(ctx.author.id, alias, dice, emoji)
            await ctx.respond(f"Dice **{alias}** saved: `{dice}`", ephemeral=True)
        except Exception:
            await ctx.respond(f"Sorry, you can't have more than 25 dice stored at once. Please free up your bag with `/deletedice`, or edit an existing die with `/editdice`.", ephemeral=True)

    @dice.command(description="Delete all saved dice.")
    async def clear(self, ctx):
        clearview = discord.ui.View(timeout=120)
        yes = discord.ui.Button(label="Clear All Dice", operation=1)
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
        
        await ctx.respond("Are you sure you want to **delete all of your dice**?", view=clearview, ephemeral=True)

    @dice.command(description="Open your bag of saved dice.")
    async def bag(self, ctx):
        bagview = DiceBag(timeout=300)
        await bagview.create(ctx.user.id, operation=0)
        await ctx.respond(f"**{ctx.user.display_name}'s dice bag**", view=bagview, ephemeral=True)
        
    @dice.command(description="Delete selected dice from bag.")
    async def delete(self, ctx):
        deleteview = DiceBag(timeout=120)
        await deleteview.create(ctx.user.id, operation=1)
        if len(deleteview.children) > 1:
            await ctx.respond(f"**Deleting from {ctx.user.display_name}'s dice bag**", view=deleteview, ephemeral=True)
        else:
            await ctx.respond(f"{ctx.user.display_name}'s dice bag is empty.", ephemeral=True)

    @dice.command(description="Edit existing dice from bag.")
    async def edit(self, ctx):
        editview = DiceBag(timeout=120)
        await editview.create(ctx.user.id, operation=2)
        await ctx.respond(f"**Editing {ctx.user.display_name}'s dice**", view=editview, ephemeral=True)

class StoreModal(discord.ui.Modal):
    def __init__(self, message, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.message = message

        self.add_item(discord.ui.InputText(label="Name"))
        self.add_item(discord.ui.InputText(label="Emoji", required=False, placeholder="ex. 🗡️ or <dagger:1012766679555641354>"))
        self.add_item(discord.ui.InputText(label="Dice Roll"))

    async def callback(self, interaction):
        await storedice(interaction.user.id, self.children[0].value, self.children[2].value, (self.children[1].value if self.children[1].value != "" else None))
        await interaction.response.defer()

        bagview = DiceBag(timeout=300)
        await bagview.create(interaction.user.id, operation=0)
        try:
            await interaction.followup.edit_message(self.message, view=bagview)
            await interaction.followup.send(f"Dice {self.children[1].value} **{self.children[0].value}** saved: `{self.children[2].value}`", ephemeral=True)
        except discord.errors.HTTPException: # if wrong emoji? idk
            await interaction.followup.send("Emoji was invalid. Type a backslash before the emoji and copy what is sent.", ephemeral=True)
            await removedice(interaction.user.id, self.children[0].value)

class EditModal(discord.ui.Modal):
    def __init__(self, alias, command, message, emoji, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.alias = alias
        self.message = message
        self.emoji = emoji

        self.add_item(discord.ui.InputText(label="Name", value=alias))
        self.add_item(discord.ui.InputText(label="Emoji", value=emoji, required=False, placeholder="ex. 🗡️ or <dagger:1012766679555641354>"))
        self.add_item(discord.ui.InputText(label="Dice Roll", value=command))

    async def callback(self, interaction):
        backupdice = await getdice(interaction.user.id)
        for die in backupdice:
            if die[1] == self.alias:
                backupdie = die
        await updatedice(interaction.user.id, self.alias, self.children[0].value, self.children[2].value, (self.children[1].value if self.children[1].value != "" else None))

        editview = DiceBag(timeout=120)
        await editview.create(interaction.user.id, operation=2)
        try:
            await interaction.followup.edit_message(self.message, view=editview)
            if self.alias == self.children[0].value:
                await interaction.response.send_message(f"Dice {self.emoji} **{self.alias}** updated: `{self.children[2].value}`", ephemeral=True)
            else:
                await interaction.response.send_message(f"Dice {self.emoji} **{self.alias}** updated to {self.children[1].value} **{self.children[0].value}**: `{self.children[2].value}`", ephemeral=True)
        except discord.errors.HTTPException: # again maybe if wrong emoji
            await interaction.followup.send("Emoji was invalid. Type a backslash before the emoji and copy what is sent.", ephemeral=True)
            await updatedice(interaction.user.id, self.children[0].value, self.alias, backupdie[2], backupdie[3])

class DiceBag(discord.ui.View):
    # needs to be async to use getdice from aiosqlite
    async def create(self, user, operation):
        saveddice = await getdice(user)
        for die in saveddice:
            self.add_item(DiceButton(label=die[1], emoji=die[3], command=die[2], operation=operation))
        if operation == 0:
            await self.addplusbutton()
        elif operation == 1:
            await self.adddonebutton("Deletion complete.")
        else:
            await self.adddonebutton("Editing complete.")

    async def addplusbutton(self):
        if len(self.children) < 25:
            addbutton = discord.ui.Button(emoji="➕")
            async def adddice(interaction):
                await interaction.response.send_modal(StoreModal(interaction.message.id, title="Save new dice"))
            addbutton.callback = adddice
            self.add_item(addbutton)

    async def adddonebutton(self, content):
        donebutton = discord.ui.Button(label="Done")
        async def done(interaction):
            await interaction.response.defer()
            await interaction.followup.edit_message(interaction.message.id, content=content, view=None)
        donebutton.callback = done
        self.add_item(donebutton)

class DiceButton(discord.ui.Button):
    def __init__(self, command, operation, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.command = command
        if operation == 0:
            self.style = discord.ButtonStyle.green
            self.callback = self.add_callback
        elif operation == 1:
            self.style = discord.ButtonStyle.red
            self.callback = self.delete_callback
        else:
            self.style = discord.ButtonStyle.blurple
            self.callback = self.edit_callback

    async def add_callback(self, interaction):
        outroll = await rollnotation(self.command)
        #SHOULD NOT BE EPHEMERAL
        await interaction.response.send_message(f"{interaction.user.display_name}'s **{self.label}** ({self.command}): `{outroll[1]}` = {outroll[2]}")

    async def delete_callback(self, interaction):
        confirmation = discord.ui.View(timeout=120)
        yes = discord.ui.Button(label="Delete", style=discord.ButtonStyle.red)
        async def confirm(confirminteraction):
            await removedice(confirminteraction.user.id, self.label)
            await confirminteraction.response.defer()

            if len(interaction.message.components) > 1:
                interaction.message.components.remove(self)
            else:
                await confirminteraction.followup.edit_message(interaction.message.id, content=f"{confirminteraction.user.display_name}'s dice bag is empty.", view=None)

            await confirminteraction.followup.edit_message(confirminteraction.message.id, content=f"**{self.label}** has been deleted.", view=None)   
        yes.callback = confirm
        confirmation.add_item(yes)

        no = discord.ui.Button(label="Cancel")
        async def cancel(confirminteraction):
            await confirminteraction.response.defer()
            await confirminteraction.followup.edit_message(confirminteraction.message.id, content="Cancelled deletion.", view=None)
        no.callback = cancel
        confirmation.add_item(no)
        
        await interaction.response.send_message(f"Are you sure you want to delete **{self.label}**?", view=confirmation, ephemeral=True)

    async def edit_callback(self, interaction):
        await interaction.response.send_modal(EditModal(alias=self.label, emoji=str(self.emoji), command=self.command, message=interaction.message.id, title="Edit dice values"))

def setup(bot):
    bot.add_cog(DiceCog(bot))