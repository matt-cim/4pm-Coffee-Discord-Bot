import discord
from database.models import UserRatings, GameRatings
from views.game_select import games

"""
Views containing buttons, dropdowns, and modals to rate games or users, or see ratings.
"""

RATINGS = [
    {"label": "1", "emoji": "😖"},
    {"label": "2", "emoji": "🙄"},
    {"label": "3", "emoji": "😐"},
    {"label": "4", "emoji": "🫡"},
    {"label": "5", "emoji": "😁"},
]
QUERY_RATING_STR = "Rating for *{}* is: **{}**"
QUERY_RATING_NONE_STR = "No rating for *{}*, submit one!"

def get_username_err_msg(username: str) -> str | None:
    if ' ' in username: # space within username (could be after trailing & leading whitespace removed)
        return "No spaces within the *Username*, you put **{}**"
    return None

class RateOptionsView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=90, disable_on_timeout=True)

    @discord.ui.button(row=0, label="View ratings for games", style=discord.ButtonStyle.green)
    async def view_game_rating_callback(self, button: discord.ui.Button, interaction: discord.Interaction):
        await interaction.response.send_message(view=QueryGameRatingView(), ephemeral=True)

    @discord.ui.button(row=0, label="View ratings for users", style=discord.ButtonStyle.green)
    async def view_user_rating_callback(self, button: discord.ui.Button, interaction: discord.Interaction):
        await interaction.response.send_modal(QueryUserRatingModal(title="Get User Rating"))

    @discord.ui.button(row=1, label="Submit rating for game", style=discord.ButtonStyle.blurple)
    async def submit_game_rating_callback(self, button: discord.ui.Button, interaction: discord.Interaction):
        await interaction.response.send_message(view=GameRatingView(), ephemeral=True)

    @discord.ui.button(row=1, label="Submit rating for user", style=discord.ButtonStyle.blurple)
    async def submit_user_rating_callback(self, button: discord.ui.Button, interaction: discord.Interaction):
        await interaction.response.send_modal(UserRatingModal(title="Rate User"))


class QueryUserRatingModal(discord.ui.Modal):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(
            discord.ui.InputText(
                label="Username",
                placeholder="ex: lfg_user_42",
                style=discord.InputTextStyle.short,
                min_length=1,
                max_length=32,
                required=True
            ),
            *args,
            **kwargs
        )

    async def callback(self, interaction: discord.Interaction):
        username = (self.children[0].value).strip()
        usernameErrMsg = get_username_err_msg(username)

        if usernameErrMsg:
            embed = discord.Embed(
                fields=[
                    discord.EmbedField(
                        name="Error", value=usernameErrMsg.format(username), inline=True
                    )
                ]
            )
            await interaction.response.send_message(embeds=[embed])
        else:
            rating = UserRatings.get_rating(username)

            rating_embed = discord.Embed(
                description=(QUERY_RATING_NONE_STR if rating is None else QUERY_RATING_STR).format(username, rating),
                color=discord.Color.random()
            )
            await interaction.response.send_message(embed=rating_embed, ephemeral=True)


class QueryGameRatingView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=90, disable_on_timeout=True)

    @discord.ui.select(
        row = 0,
        placeholder = "Choose a game...",
        min_values = 1,
        max_values = 1,
        options = [
            discord.SelectOption(label=game["label"], emoji=game["emoji"])
            for game in games
        ]
    )
    async def select_game_callback(self, select: discord.ui.Select, interaction: discord.Interaction):
        game = select.values[0]
        rating = GameRatings.get_rating(game)

        rating_embed = discord.Embed(
            description=(QUERY_RATING_NONE_STR if rating is None else QUERY_RATING_STR).format(game, rating),
            color=discord.Color.random()
        )
        await interaction.response.send_message(embed=rating_embed, ephemeral=True)


class GameRatingView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=90, disable_on_timeout=True)

    @discord.ui.select(
        row = 0,
        placeholder = "Choose a game...",
        min_values = 1,
        max_values = 1,
        options = [
            discord.SelectOption(label=game["label"], emoji=game["emoji"])
            for game in games
        ]
    )
    async def select_game_callback(self, select: discord.ui.Select, interaction: discord.Interaction):
        await interaction.response.defer() # ignore for now, only respond after "Submit" clicked

    @discord.ui.select(
        row = 1,
        placeholder = "Choose a rating...",
        min_values = 1,
        max_values = 1,
        options = [
            discord.SelectOption(label=rating["label"], emoji=rating["emoji"])
            for rating in RATINGS
        ]
    )
    async def select_rating_callback(self, select: discord.ui.Select, interaction: discord.Interaction):
        await interaction.response.defer()

    @discord.ui.button(row=2, label="Submit", style=discord.ButtonStyle.blurple)
    async def view_game_rating_callback(self, button: discord.ui.Button, interaction: discord.Interaction):
        game = self.children[0].values[0]
        game_rating = self.children[1].values[0]
        self.disable_all_items()
        self.stop()
        GameRatings.insert_rating(game, game_rating)
        await interaction.response.send_message("Your game rating has been recorded", ephemeral=True)


class UserRatingModal(discord.ui.Modal):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(
            discord.ui.InputText(
                label="Username",
                placeholder="ex: lfg_user_42",
                style=discord.InputTextStyle.short,
                min_length=1,
                max_length=32, # max length for Discord username is 32 characters
                required=True
            ),
            discord.ui.InputText(
                label="Rate the user from 1 (worst) to 5 (best)",
                placeholder="ex: 5",
                style=discord.InputTextStyle.short,
                min_length=1,
                max_length=1,
                required=True
            ),
            *args,
            **kwargs
        )

    async def callback(self, interaction: discord.Interaction):
        username = (self.children[0].value).strip()
        user_rating = (self.children[1].value).strip()
        username_err_msg = get_username_err_msg(username)
        rating_err_msg = None

        if not user_rating.isdigit():
            rating_err_msg = "Enter a number"
        elif int(user_rating) < 1 or int(user_rating) > 5:
            rating_err_msg = "Enter a number between 1 and 5"

        if username_err_msg or rating_err_msg:
            embed = discord.Embed(title="Error")
            if username_err_msg:
                embed.add_field(name="Username Error", value=username_err_msg.format(username), inline=True)
            if rating_err_msg:
                embed.add_field(name="Rating Error", value=rating_err_msg+" for *User Rating*, you put **{}**"
                                .format(user_rating), inline=True)
            await interaction.response.send_message(embeds=[embed])
        else:
            UserRatings.insert_rating(username, user_rating)
            await interaction.response.send_message("Your user rating has been recorded", ephemeral=True)
