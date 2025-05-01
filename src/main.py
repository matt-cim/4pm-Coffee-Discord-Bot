import discord
import os
from database.models import Helpers
from discord.commands import option
from discord.ext import tasks
from dotenv import load_dotenv
from utils.available_groups import AvailableGroups
from utils.group_delete import GroupDelete
from utils.guild_data import GuildData
from utils.help_output import HelpOutput
from utils.logger import Logger
from utils.voice_channel_utils import VoiceChannelUtils
from views.game_select import SelectView
from views.rate_select import RateOptionsView

"""
Initializes & runs the bot while setting up event handler methods
"""

# init client (to Discord server)
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
GUILD_ID = os.getenv("GUILD_ID")
intents = discord.Intents.default()
intents.members = True
bot = discord.Bot(intents=intents)

JOIN = "join"
CREATE = "create"
DELETE = "delete"
AVAILABLE = "available"
RATE = "rate"
HELP = "help"
ACTIONS = [JOIN, CREATE, DELETE, AVAILABLE, RATE, HELP]

async def action_autocomplete(ctx: discord.AutocompleteContext):
    """Returns list of ACTIONS that begin with the characters entered so far"""
    return [action for action in ACTIONS if action.startswith(ctx.value.lower())]

@tasks.loop(hours=2)
async def open_post_cleaner():
    """Deletes posts that have been open for 2 hours (checks every 2 hours too)"""
    Helpers.delete_expired_requests()

@tasks.loop(hours=4)
async def open_voice_channel_cleaner():
    """Deletes voice channels that have been open for 4 hours and are empty (checks every 4 hours too)"""
    await VoiceChannelUtils.check_and_delete_voice_channels()

@bot.event
async def on_ready():
    GuildData.initialize(bot, GUILD_ID) # init variables for the bot's guild
    Logger.initialize() # init logging capability
    Logger.get_logger().info(f'{bot.user} has successfully started')
    open_post_cleaner.start()
    open_voice_channel_cleaner.start()

@bot.event
async def on_member_join(member: discord.Member):
    """Determine if new member needs permissions to join their groups voice channel"""
    await VoiceChannelUtils.update_permission_new_member(member)

@bot.slash_command(name="lfg")
@option("action", description="Choose what group action you'd like to take", autocomplete=action_autocomplete)
async def lfg_base(ctx: discord.ApplicationContext, action: str):
    """
    Join an existing group or create a new one!
    """
    action = action.lower()
    if action == JOIN: # subcommand "/lfg join" that instantiates the process to join a group
        await ctx.interaction.response.send_message("Select the game you want to join a group for:", 
                                                    view=SelectView(is_join=True), ephemeral=True)
    elif action == CREATE: # subcommand "/lfg create" that instantiates the creation of a lfg post
        await ctx.interaction.response.send_message("Select the game for your group:", 
                                                    view=SelectView(is_join=False), ephemeral=True)
    elif action == DELETE: # subcommand "/lfg delete" that deletes the owner's open group
        embed = await GroupDelete.try_delete(ctx.interaction.user.name)
        await ctx.interaction.response.send_message(embed=embed, ephemeral=True)
    elif action == AVAILABLE: # subcommand "/lfg available" that shows max(9) open groups
        embed = await AvailableGroups.get_groups()
        await ctx.interaction.response.send_message(embed=embed, ephemeral=False)
    elif action == RATE: # subcommand "/lfg rate" that lets you score games and users
        await ctx.interaction.response.send_message("Choose what you would like to do:", 
                                                    view=RateOptionsView(), ephemeral=True)
    elif action == HELP: # subcommand "/lfg help" that tells you how to use this bot
        embed = await HelpOutput.get_embed()
        await ctx.interaction.response.send_message(embed=embed, ephemeral=False)
    else: # unknown subcommand
       await ctx.interaction.response.send_message("Please specify a subcommand. Use ***/lfg help*** for more information",
                                                   ephemeral=True)


bot.run(BOT_TOKEN)
