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


sp_client = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials(client_id=os.getenv("SPOTIFYCLIENTID"),client_secret=os.getenv("SPOTIFYCLIENTSECRET"),))

trello_client = TrelloClient(
api_key=os.getenv("TRELLOAPIKEY"),api_secret=os.getenv("TRELLOAPISECRET"),token=os.getenv("TRELLOTOKEN"),)

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


async def environment_check():
    
    # check each env var, log a warning if its missing, and critial if the token or db is missing.
    
    if not os.getenv("TOKEN"):
        logging.critical("Bot token is missing or invalid.")
        exit()
        
        # check if guild ID matches the current server
        if bot.get_guild(int(os.getenv("GUILDID"))) != os.getenv("GUILDID"):
            logging.warning("Guild ID does not match the current guild, some features might not work.")
        
        # check if the client ID matches the current bot application
        if bot.user.id != int(os.getenv("CLIENTID")):
            logging.warning("Client ID does not match the current bot application, some features might not work.")

        # check if the postgres DB is reachable
        try:
            import psycopg2
            connection = psycopg2.connect(
                dbname=os.getenv("DBNAME"),
                user=os.getenv("DBUSER"),
                password=os.getenv("DBPASS"),
                host=os.getenv("DBHOST"),
                port=os.getenv("DBPORT")
            )
            connection.close()
        except Exception as e:
            logging.critical(f"Could not connect to PostgreSQL database: {e}")
            exit()
        
        # check if the SMB server is reachable
        from smb.SMBConnection import SMBConnection
        smb = SMBConnection(
            os.getenv("SMBUSER"), os.getenv("SMBPASS"), "local_client", os.getenv("SERVERIP"), use_ntlm_v2=True, is_direct_tcp=True)
        if not smb.connect(server, 445):
            logging.ERROR("Could not connect to SMB server, some features might not work.")
        
        # check the spotify API credentials
        
        #check the trello API credentials & board ID
        
        #check the google API credentials
        
        #check the wiki API credentials
        
        # check to see if there are any TTS voices installed
        
        #check if any packages are out of date?
        
        # ytdl prerequisites check
        ffmpeg_path = os.getenv("FFMPEGEXE")
        if not ffmpeg_path or not os.path.exists(ffmpeg_path):
            logging.warning("Could not find ffmpeg executable, some vc features like the music player or downloader might not work.")
        jsruntime_path = os.getenv("JSRUNTIME")
        if not jsruntime_path or not os.path.exists(jsruntime_path):
            logging.warning("Could not find javascript runtime binary, some vc features like the music player or downloader might not work.")
    

# entrypoint
if __name__ == "__main__":
    bot.run(os.getenv("TOKEN"))