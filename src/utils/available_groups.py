import discord
from database.models import OpenRequests

"""
Methods pertaining to the process of showing open groups. Purposely shows
groups that are closets to being filled for the purpose of trying to
get these filled
"""

class AvailableGroups:
    game = "Game"
    owner = "Owner"
    group_size = "Group Size"
    people_needed = "People Needed"
    description = "Description"

    @staticmethod
    async def get_groups() -> discord.Embed:
        groups_tuple = OpenRequests.get_top_open_requests_all()
        groups_map = await AvailableGroups.groups_tuple_to_map(groups_tuple)
        
        if groups_tuple:
           return discord.Embed(
                fields=[
                    discord.EmbedField(
                        name="```{}```".format(group_map[AvailableGroups.game]), 
                        value="*People Needed:* **{}**\n*Group Size:* **{}**\n*Owner:* **{}**\n*Description:* **{}**"
                        .format(group_map[AvailableGroups.people_needed], 
                                group_map[AvailableGroups.group_size], 
                                group_map[AvailableGroups.owner],
                                group_map[AvailableGroups.description] 
                                if group_map[AvailableGroups.description] != "" else "None"), 
                        inline=True
                    ) for group_map in groups_map
                ],
                footer=discord.EmbedFooter(text="Note a maximum of 9 results are shown" 
                                           if len(groups_map) >= 9 else ""),
                color=discord.Color.brand_green()
            )
        else:
           return discord.Embed(
                fields=[
                    discord.EmbedField(
                        name="Notice", value="No groups open to show. Create one!", inline=True
                    )
                ]
            )
        
    @staticmethod
    async def groups_tuple_to_map(groups_tuple):
        groups_map = []
        for group in groups_tuple:
            inner_map = {AvailableGroups.game:group[1], AvailableGroups.owner:group[2], 
                         AvailableGroups.group_size:group[3], AvailableGroups.people_needed:group[4], 
                         AvailableGroups.description:group[5]}
            groups_map.append(inner_map)

        return groups_map
