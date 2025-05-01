import discord

"""
Explain to the user how the bot works and explain commands
"""

class HelpOutput:

    @staticmethod
    async def get_embed() -> discord.Embed:        
        embed = discord.Embed(
            title="📫 Need help? Here are all of my commands:",
            description="""
                *Purpose:* this Discord bot is designed to help gamers easily create and join 
                **Looking for Group (LFG)** posts for a variety of video games. Users can create 
                custom posts specifying the game and preferred number of people for their group. 
                Simple commands are used to find and join these groups, leading to the
                placement of the group into the same voice channel to start playing 😎
            """,
            fields=[
                discord.EmbedField(
                    name="***/lfg create***", value="Start a group that you want others to join", inline=True
                ),
                discord.EmbedField(
                    name="***/lfg join***", value="Look for an open group to join", inline=True
                ),
                discord.EmbedField(
                    name="***/lfg available***", value="See the top 10 most recent groups created", inline=True
                ),
                discord.EmbedField(
                    name="***/lfg delete***", value="Close your group to create another or make it not possible for others to join the group you created", inline=True
                ),
                discord.EmbedField(
                    name="***/lfg rate***", value="Post or view ratings for users and games", inline=True
                ),
                discord.EmbedField(
                    name="***/lfg help***", value="Show this message again for help", inline=True
                ),
                discord.EmbedField(
                    name="***Link to invite bot: ***", value="https://discord.com/oauth2/authorize?client_id=1319859544624463892&permissions=3072&integration_type=0&scope=bot", inline=False
                )
            ],
            color=discord.Color.random()
        )
        return embed
    