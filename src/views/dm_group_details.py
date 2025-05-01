import discord
from database.models import OpenRequests
from utils.voice_channel_utils import VoiceChannelUtils

"""
Drop down for the user to select the group they want to join and a button to
refresh the available group options. ui.Select/Button carry a reference to their 
respective view, which simplifies logic here
"""

class GroupDetailsDM(discord.ui.View):
    def __init__(self, game: str, dialog: str):
        super().__init__(timeout=300, disable_on_timeout=True)
        self.game = game
        refresh_button = RefreshButton(dialog)
        self.add_item(refresh_button)
        # need to pass button to dropdown to allow for it to be disabled eventually
        self.dropdown = GroupsDropdown(refresh_button)
        self.add_item(self.dropdown)
        self.update_dropdown_options()

    def update_dropdown_options(self):
        select_options = GroupsDropdown.get_select_options(OpenRequests.get_top_open_requests(self.game))
        if not select_options:
            self.dropdown.disabled = True
            self.dropdown.placeholder = "No currently open groups. Try \"/lfg create\""
            self.dropdown.options = [discord.SelectOption(label="None")]
        else:
            self.dropdown.disabled = False
            self.dropdown.placeholder = "Choose the group you want to join"
            # all options need to be unique, hence the numbering
            # also, description is limited to 100 characters
            self.dropdown.options = [
                                discord.SelectOption(label="{}. People Still Needed - {}, Requested Group Size - {}"
                                .format(index + 1, option["people_needed"], option["group_size"]), 
                                description=option["description"][:100], value=str(option["id"]))
                                for index, option in enumerate(select_options)
                                ]

class GroupsDropdown(discord.ui.Select):
    def __init__(self, refresh_button: discord.ui.Button):
        super().__init__(
            min_values=1,
            max_values=1
        )
        self.refresh_button = refresh_button

    async def callback(self, interaction: discord.Interaction):
        # disable all ui elements
        self.disabled = True
        self.refresh_button.disabled = True
        await interaction.message.edit(view=self.view) # needed to update the fields as disabled
        username = interaction.user.name
        group_id = self.values[0]

        if OpenRequests.user_joined_group(group_id, username):
            invite_link = await VoiceChannelUtils.relay_invite(interaction, group_id)
            if invite_link != None:
                embed = discord.Embed(
                    fields=[
                        discord.EmbedField(
                            name="Group Voice Channel Invite", 
                            value="""Join the voice channel to start talking with your group :) It's possible not all members have joined yet""", 
                            inline=True
                        )
                    ], color=discord.Color.random()
                )
                await interaction.response.send_message(content=invite_link, embed=embed)
        else:
            embed = discord.Embed(
                fields=[
                    discord.EmbedField(
                        name="Error", value="**{}** you have already joined or created that group. \
                        Refer to your dms for the invite link".format(username), inline=True
                    )
                ]
            )
            await interaction.response.send_message(embed=embed)

    @staticmethod
    def get_select_options(queried_groups):
        games = []
        num_options = min(len(queried_groups), 10)
        for i in range(num_options):
            # indices map to position of the record in the table row respectively
            games.append({"id": queried_groups[i][0], "group_size": queried_groups[i][3], 
                          "people_needed": queried_groups[i][4], "description": queried_groups[i][5]})

        return games

class RefreshButton(discord.ui.Button):
    def __init__(self, dialog: str):
        self.dialog = dialog
        self.update_count = 0
        super().__init__(row=1, label="Refresh options", style=discord.ButtonStyle.blurple)

    async def callback(self, interaction: discord.Interaction):
        self.update_count += 1
        self.view.update_dropdown_options() # check for possible new groups created
        await interaction.response.edit_message(content=self.dialog + ": refresh # " + str(self.update_count), view=self.view)
