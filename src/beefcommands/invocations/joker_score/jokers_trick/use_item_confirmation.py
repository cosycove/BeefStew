import discord

class ItemConfirmationView(discord.ui.View):
    def __init__(self, interaction: discord.Interaction, message: discord.InteractionMessage = None):
        super().__init__(timeout = 5)
        self.used = False
        self.interaction = interaction
        self.message = message
    
    async def on_timeout(self):
        await self.message.edit(content="ok u dont want to use it then i guess", embed=None, view=None)
        self.stop()

                    
    @discord.ui.button(label = "yea", style = discord.ButtonStyle.green)
    async def item1(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.used = True
        await interaction.response.edit_message(content="ok!!", embed=None, view=None)
        self.stop()

    @discord.ui.button(label = "no", style = discord.ButtonStyle.red)
    async def item2(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.used = False
        await interaction.response.edit_message(content="ok... sigh", embed=None, view=None)
        self.stop()

async def display_item_confirmation_open(interaction: discord.Interaction):
    used = await item_confirmation_embed(interaction)
    return used

async def item_confirmation_embed(interaction: discord.Interaction):
    item_confirmationembed = discord.Embed(title="u sure?", description="are u sure u want to use item?", color=discord.Color.blue())
    item_confirmationembed.set_image(url = "https://tenor.com/view/hi-gif-1459774218829111523")
    view = ItemConfirmationView(interaction)
    
    callback_response = await interaction.response.send_message(embed=item_confirmationembed, view=view, ephemeral=True)
    
    view.message = callback_response.resource
    await view.wait()
    
    return view.used