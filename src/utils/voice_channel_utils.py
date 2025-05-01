import discord
from database.models import VoiceChannels
from utils.guild_data import GuildData
from utils.logger import Logger

"""
Invite links to private voice channels that are to be used for
the groups to communicate and check/delete old, unused voice channels
"""

class VoiceChannelUtils:
    @staticmethod
    async def create_invite(interaction: discord.Interaction):
        """Returns invite link for group creator and new voice channel id"""
        guild = GuildData.get_guild()
        channel_name = interaction.user.name + "'s group"
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(connect=False), # deny access for everyone else
            interaction.user: discord.PermissionOverwrite(connect=True), # creator can join
        }

        voice_channel = await guild.create_voice_channel(channel_name, overwrites=overwrites)
        invite_link = await voice_channel.create_invite()
        
        return VoiceChannelMeta(invite_link, voice_channel.id)
    
    @staticmethod
    async def relay_invite(interaction: discord.Interaction, group_id: str) -> discord.Invite:
        """Returns invite link with updated permissions for the invitee to join"""
        channel_id = VoiceChannels.get_record_by_id(group_id)
        found_channel = None

        for channel in GuildData.get_guild().voice_channels:
            # found the channel we need to update permissions for to send invite
            if int(channel_id) == channel.id:
                found_channel = channel
                break

        if found_channel == None:
            Logger.get_logger().error(f"Could not find channel relating to the group with id {group_id} user needs invite link for")
            return None
        
        # perform overwrites for users already members of the guild
        nue_overwrites = found_channel.overwrites
        nue_overwrites[interaction.user] = discord.PermissionOverwrite(connect=True)
        await found_channel.edit(overwrites=nue_overwrites)

        return await found_channel.create_invite()
    
    @staticmethod
    async def update_permission_new_member(member: discord.Member):
        """Cannot perform permission overwrites for non-guild members, have to update upon joining guild"""
        open_group_id = VoiceChannels.get_joined_group_id_for_member_or_creator(member.name)

        if open_group_id is not None:
            open_group_id = open_group_id[0]
            channel_id = VoiceChannels.get_record_by_id(open_group_id)
            found_channel = None

            for channel in GuildData.get_guild().voice_channels:
                # found the channel we need to update permissions for, user joined from voice channel invite link
                if int(channel_id) == channel.id:
                    found_channel = channel
                    break

            if found_channel != None:
                nue_overwrites = found_channel.overwrites
                nue_overwrites[member] = discord.PermissionOverwrite(connect=True)
                await found_channel.edit(overwrites=nue_overwrites)
        
    @staticmethod
    async def check_and_delete_voice_channels():
        old_vcs = VoiceChannels.get_old_voice_channels()
        old_channel_ids = [tup[1] for tup in old_vcs]
        deleted_channel_ids = []

        for channel in GuildData.get_guild().voice_channels:
            curr_channel_id = channel.id
            # nobody in the voice channel and channel been alive > 4 hours
            if not channel.members and curr_channel_id in old_channel_ids:
                deleted_channel_ids.append(curr_channel_id)
                await discord.VoiceChannel.delete(channel)

        # reflect deleted voice channels in the db
        VoiceChannels.delete_voice_channels(deleted_channel_ids)

class VoiceChannelMeta:
    def __init__(self, invite_link: discord.Invite, channel_id: str):
        self.invite_link = invite_link
        self.channel_id = channel_id
        