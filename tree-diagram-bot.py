import discord
import asyncio
import html
from discord.ext import commands
from extensions import mal_search
from pyanimelist import PyAnimeList

tree_diagram = commands.Bot(command_prefix="!",
                            description='A discord bot that performs various functions depeding on its extensions')


@tree_diagram.event
async def on_ready():
    print("Logged in as")
    print(tree_diagram.user.name)


@tree_diagram.command(pass_context=True)
async def anime(context, *query):
    """searches myanimelist for the anime queried. It will return up to the top 10 results of the search. If there
    is more than one result, the user will be given 10 seconds to select the result desired"""
    query = " ".join(query)
    # mal = mal_search.MalSearcher()
    # result = mal.search_mal(query)
    file = open('mal-username.txt', 'r')
    username = file.read()
    file.close()
    file = open('mal-pw.txt', 'r')
    pw = file.read()
    file.close()

    searcher = PyAnimeList(username, pw)

    try:
        result = await searcher.search_all_anime(query)
    except BaseException:
        return await tree_diagram.say('Nothing found')
    else:
        result = dict(enumerate(result[:10]))

    if len(result) == 1:
        anime_info = result[0]
    elif len(result) > 1:
        message = "```Select an anime from the list using its number, you have 10 seconds: \n"
        message += '\n'.join([str(item[0] + 1) + ". " + item[1].title for item in result.items()])
        message += "```"
        await tree_diagram.send_message(destination=context.message.channel, content=message)
        response = await tree_diagram.wait_for_message(timeout=10.0, author=context.message.author)

        if not response:
            return

        key = int(response.content) - 1

        try:
            anime_info = result[key]
        except(ValueError, KeyError):
            return await tree_diagram.say("Invalid Selection")
    else:
        return await tree_diagram.say("Something else went wrong")

    embed = discord.Embed(title=anime_info.title,
                          color=0x379bff,
                          url="https://myanimelist.net/anime/" + anime_info.id + "/" +
                              anime_info.title.replace(" ", "%20"))

    embed.set_image(url=anime_info.image)
    embed.add_field(name='Episodes', value=anime_info.episodes, inline=True)
    embed.add_field(name='Status', value=anime_info.status, inline=True)
    embed.add_field(name='Type', value=anime_info.type, inline=True)
    embed.add_field(name='Air Dates',
                    value=f"{anime_info.start_date} to {'Present' if anime_info.end_date == '0000-00-00' else anime_info.end_date}")
    embed.add_field(name='Synopsis', value=html.unescape(anime_info.synopsis).split('\n\n')[0], inline=False)

    await tree_diagram.say(embed=embed)


## main method ##

token = open("token.txt")
token_txt = token.readlines()[0]
token.close()
tree_diagram.run(str(token_txt))
