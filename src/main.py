import os
import asyncio
import discord
import logging
from discord.ext import commands
from dotenv import load_dotenv
from concurrent.futures import ThreadPoolExecutor
from spotipy.oauth2 import SpotifyClientCredentials
import spotipy
from trello import TrelloClient
from beefcommands.invocations.joker_score.sacred_words import load_sacred_words


try:
    load_dotenv()
except Exception:
    print("[CRITIAL] %(asctime)s - Environment vairables failed to load, either dotenv is not installed or there is no .env file.")
    exit()


# default log level is warning, overrides with env variable
log_level = os.getenv("LOG_LEVEL", "WARNING").upper()
logging.basicConfig(level=log_level, format="[%(levelname)s] %(asctime)s - %(message)s")

# verify the environemnt variables
environment_check()

sp_client = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials(client_id=os.getenv("SPOTIFYCLIENTID"),client_secret=os.getenv("SPOTIFYCLIENTSECRET"),))
# add a check to see if can the API endpoint be reached?

trello_client = TrelloClient(
api_key=os.getenv("TRELLOAPIKEY"),api_secret=os.getenv("TRELLOAPISECRET"),token=os.getenv("TRELLOTOKEN"),)
# add a check to see if can the API endpoint be reached?

bot_loop: asyncio.AbstractEventLoop | None = None

class BeefStew(commands.Bot):
    async def setup_hook(self):
        
        # sync the main bot event loop
        global bot_loop
        bot_loop = asyncio.get_running_loop()

        # load cogs
        await self.load_cogs()

        # sync commands
        await self.tree.sync()

        load_sacred_words()

        print("> setup complete")

    async def load_cogs(self):
        print("> registering cogs...")
        base = os.path.join("src", "beefcommands", "cogs")
        for filename in os.listdir(base):
            if not filename.endswith(".py"):
                continue
            
            # visage context menu is set up as an extention of the visage cog
            if filename == "visage_context_menu.py":
                continue
            ext = f"beefcommands.cogs.{filename[:-3]}"
            await self.load_extension(ext)


intents = discord.Intents.all()
intents.message_content = True

bot = BeefStew(command_prefix="/", intents=intents)

# executor for blocking apis like spotify & ytdl
bot.executor = ThreadPoolExecutor(max_workers=4)

kicked_members = set()
banned_members = set()

@bot.event
async def on_ready():
    await bot.change_presence(status=discord.Status.online,activity=discord.Activity(type=discord.ActivityType.watching,name="you...",),)
    print(f"> \033[1;91m{bot.user} is now online, may god help us all...\033[0m")


@bot.check
async def globally_block_dms(ctx):
    return ctx.guild is not None


async def _guild_only_interaction_check(interaction: discord.Interaction) -> bool:
    if interaction.guild is None:
        await interaction.response.send_message("NO DMS GRRR", ephemeral=True)
        return False
    return True
bot.tree.interaction_check = _guild_only_interaction_check


def environment_check(): 
    if not os.getenv("TOKEN"):
        logging.critical("Bot token is missing or invalid.")
        exit()
        
        # check if guild ID exists and matches the current server
        if bot.get_guild(int(os.getenv("GUILDID"))) != os.getenv("GUILDID"):
            logging.warning("Guild ID does not match the current guild, some features might not work.")
        
        # check if the client ID exists and matches the current bot application
        if bot.user.id != int(os.getenv("CLIENTID")):
            logging.warning("Client ID does not match the current bot application, some features might not work.")

        # check if postgres creds exist
        dbname=os.getenv("DBNAME")
        if dbname == "" or dbname == None:
            logging.error("Database name environemnt variable is missing, core features will not work.")
        user=os.getenv("DBUSER")
        if user == "" or user == None:
            logging.error("Database username environemnt variable is missing, core features will not work.")
        password=os.getenv("DBPASS")
        if password == "" or password == None:
            logging.error("Database password environemnt variable is missing, core features will not work.")
        host=os.getenv("DBHOST")
        if host == "" or host == None:
            logging.error("Database hostname environemnt variable is missing, core features will not work.")
        port=os.getenv("DBPORT")
        if port == "" or port == None:
            logging.error("Database port environemnt variable is missing, core features will not work.")

        # check if SMB creds exist
        user = os.getenv("SMBUSER")
        if user == "" or user == None:
            logging.warning("SMB username environemnt variable is missing, some features will not work.")
        password = os.getenv("SMBPASS")
        if password == "" or password == None:
            logging.warning("SMB password environemnt variable is missing, some features will not work.")
        host = os.getenv("SERVERIP")
        if host == "" or host == None:
            logging.warning("SMB server IP environemnt variable is missing, some features will not work.")

        host = os.getenv("HOSTNAME")
        if host == "" or host == None:
            logging.warning("File server hostname environemnt variable is missing, some features will not work.")

        # check the spotify API credentials
        spclientid = os.getenv("SPOTIFYCLIENTID")
        if spclientid == "" or spclientid == None:
            logging.warning("Spotify API Client ID is missing, some VC features like the music player or downloader might not work.")
        spsecret = os.getenv("SPOTIFYCLIENTSECRET")
        if spsecret == "" or spsecret == None:
            logging.warning("Spotify API Client Secret is missing, some VC features like the music player or downloader might not work.")
        
        # ytdl prerequisites check
        ffmpeg_path = os.getenv("FFMPEGEXE")
        if not ffmpeg_path or not os.path.exists(ffmpeg_path):
            logging.warning("Could not find ffmpeg executable, some VC features like the music player or downloader might not work.")
        jsruntime_path = os.getenv("JSRUNTIME")
        if not jsruntime_path or not os.path.exists(jsruntime_path):
            logging.warning("Could not find javascript runtime binary, some VC features like the music player or downloader might not work.")
        
        #check the trello API credentials & board ID
        trellokey = os.getenv("TRELLOAPIKEY")
        if trellokey == "" or trellokey == None:
            logging.warning("Trello API Key is missing, some features may not work.")
        trellosecret = os.getenv("TRELLOAPISECRET")
        if trellosecret == "" or trellosecret == None:
            logging.warning("Trello API Secret is missing, some features may not work.")
        trellotoken = os.getenv("TRELLOTOKEN")
        if trellotoken == "" or trellotoken == None:
            logging.warning("Trello API Token is missing, some features may not work.")
        trelloboard = os.getenv("BOARDID")
        if trelloboard == "" or trelloboard == None:
            logging.warning("Trello Board ID is missing, some features may not work.")
        
        #check the google API credentials
        googleengineid = os.getenv("SEARCHENGINEID")
        if googleengineid == "" or googleengineid == None:
            logging.warning("Google search engine ID is missing, some features may not work.")
        googleapikey = os.getenv("GOOGLEAPIKEY")
        if googleapikey == "" or googleapikey == None:
            logging.warning("Google search API Key is missing, some features may not work.")

        # check to see if there are any TTS voices installed
        
        #check if any packages are out of date?
        
        
    

# entrypoint
if __name__ == "__main__":
    bot.run(os.getenv("TOKEN"))