import discord
from views.details_modal import DetailsModal
from views.dm_group_details import GroupDetailsDM

"""
Drop down to select the game pertaining to the lfg
docs: https://github.com/Pycord-Development/pycord/blob/master/examples/views/dropdown.py
"""

games = [
    {"label": "Marvel Rivals", "emoji": "🦹"},
    {"label": "League of Legends", "emoji": "🪄"},
    {"label": "Dota 2", "emoji": "⚔️"},
    {"label": "Counter-Strike 2", "emoji": "🔫"},
    {"label": "ROBLOX", "emoji": "🅱️"},
    {"label": "Fortnite", "emoji": "🏆"},
    {"label": "Overwatch 2", "emoji": "🦍"},
    {"label": "Rust", "emoji": "⚠️"},
    {"label": "Elden Ring", "emoji": "🧙‍♂️"},
    {"label": "Rocket League", "emoji": "🚀"},
    {"label": "Minecraft", "emoji": "⛏️"},
]

class SelectView(discord.ui.View):
    def __init__(self, is_join: bool):
        super().__init__(timeout=180, disable_on_timeout=True)
        self.is_join = is_join # joining or creating a group

    @discord.ui.select(
        placeholder="Game Selection...",
        min_values=1, # min number of values allowed to be selected
        max_values=1, # restricts user to picking one game
        options=[
            discord.SelectOption(label=game["label"], emoji=game["emoji"])
            for game in games
        ]
    )
    # method called after game selection
    async def select_callback(self, select: discord.ui.Select, interaction: discord.Interaction):
        if self.is_join:
            dm_embed = discord.Embed(
                description="Sent you ({}) a dm with group information".format(interaction.user.display_name),
                color=discord.Color.random()
            )
            # ephemeral=True makes the message hidden from everyone except the button presser.
            await interaction.response.send_message(embed=dm_embed, ephemeral=True)
            # send dm to user w/ group details
            game = select.values[0]
            dialog = "Showing available groups for " + game
            group_details_dm = GroupDetailsDM(game=game, dialog=dialog)
            await interaction.user.send(dialog, view=group_details_dm)
        else:
            modal = DetailsModal(interaction.user, title=select.values[0])
            await interaction.response.send_modal(modal)
