import discord
from database.models import OpenRequests

"""
Methods pertaining to the process of group creators deleting their groups
"""

class GroupDelete:
    @staticmethod
    async def try_delete(username: str) -> discord.Embed:
        group_deleted = OpenRequests.delete_open_group(username)
        
        if group_deleted:
           return discord.Embed(
                fields=[
                    discord.EmbedField(
                        name="Success", value="Your open group was deleted", inline=True
                    )
                ],
                color=discord.Color.brand_green()
            )
        else:
           return discord.Embed(
                fields=[
                    discord.EmbedField(
                        name="Error", value="You had no group open to delete", inline=True
                    )
                ]
            )