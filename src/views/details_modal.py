import discord
from database.models import OpenRequests, Helpers
from datetime import datetime, timezone
from utils.voice_channel_utils import VoiceChannelUtils

"""
Modal dialog allowing the user to define details about the lfg post creation
docs: https://github.com/Pycord-Development/pycord/blob/master/examples/modal_dialogs.py
"""

class DetailsModal(discord.ui.Modal):
    def __init__(self, user: discord.user, *args, **kwargs) -> None:
        self.user = user
        super().__init__(
            discord.ui.InputText(
                label="Number of People Needed",
                placeholder="ex: 4",
                style=discord.InputTextStyle.short,
                min_length=1,
                max_length=2,
                required=True
            ),
            discord.ui.InputText(
                label="Description (optional)",
                placeholder="ex: casual players preferred",
                style=discord.InputTextStyle.long,
                max_length=300,
                required=False
            ),
            *args,
            **kwargs
        )

    async def callback(self, interaction: discord.Interaction):
        group_size = (self.children[0].value).strip()
        group_size_is_digit = group_size.isdigit()

        # malformed, non-numerical input or asking for 0 other people
        if not group_size_is_digit or (group_size_is_digit and int(group_size) == 0):
            embed = discord.Embed(
                fields=[
                    discord.EmbedField(
                        name="Error", value="Enter a non-zero number for *Number of People Needed*, you put **{}**"
                        .format(group_size), inline=True
                    )
                ]
            )
            await interaction.response.send_message(embeds=[embed])
        else:
            group_size = self.children[0].value
            description = self.children[1].value
            username = self.user.name
            game = self.title

            if Helpers.user_has_group_open(username=username):
                embed = discord.Embed(
                    fields=[
                        discord.EmbedField(
                            name="Error", value="**{}** you already have a group open, use **/lfg delete** to dismiss that group"
                            .format(username), inline=True
                        )
                    ]
                )
                await interaction.response.send_message(embeds=[embed])
            else:            
                thumbnail_file_name = "create_group_coffee.png"
                thumbnail_file = discord.File("resources/"+thumbnail_file_name)
                
                embed = discord.Embed(
                    title="Group Details",
                    description="*A dm was sent to you with the voice channel invite link*",
                    fields=[
                        discord.EmbedField(
                            name="Creator 🧐", value=username, inline=True
                        ),
                        discord.EmbedField(
                            name="Game 🕹️", value=game, inline=True
                        ),
                        discord.EmbedField(
                            name="Group Size 🔢", value=group_size, inline=True
                        ),
                        discord.EmbedField(
                            name="Description 💬", value=description, inline=False
                        )
                    ],
                    color=discord.Color.random()
                )
                embed.set_thumbnail(url="attachment://"+thumbnail_file_name)
                invite_data = await VoiceChannelUtils.create_invite(interaction=interaction)
                await interaction.user.send(invite_data.invite_link)
                await interaction.response.send_message(file=thumbnail_file, embeds=[embed])
                # people_needed = group_size bc nobody has ability to join atp
                OpenRequests.insert_request(game, username, group_size, group_size, description, invite_data.channel_id, datetime.now(timezone.utc))
