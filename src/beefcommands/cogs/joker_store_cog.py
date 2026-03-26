import discord
from discord.ext import commands
from beefcommands.invocations.joker_score.jokers_trick import use_item_confirmation as use

class JokerStoreCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @discord.app_commands.command(name="use_item", description="use item test")
    async def use_item(self, 
                       interaction: discord.Interaction, 
                       item_name: str,
                       victim: discord.Optional[discord.Member] = None):
        
        used = await use.display_item_confirmation_open(interaction)
        if not used:
            return

        print("it worked lollll")

# cog startup
async def setup(bot):
    print("- \033[33mbeefcommands.cogs.joker_store_cog\033[0m")
    await bot.add_cog(JokerStoreCog(bot))


