import discord
from typing import Optional

"""
Store data relevant to the Bot's guild
"""

class GuildData:
    guild = None

    @classmethod
    def initialize(cls, bot: discord.Bot, guild_id):
        cls.guild = bot.get_guild(int(guild_id))

    @classmethod
    def get_guild(cls) -> Optional[discord.Guild]:
        return cls.guild
