import asyncio
import hata
import os
import lavaplayer
from hata.ext.commands_v2 import checks, CommandContext
import logging


PREFIX = "!"
TOKEN = "ODkzMzg1MzUxMzYyNjcwNTkz.YVar8g.mJiNNJcaRrsDWhS1MSNmvqORxuk"

bot = hata.Client(TOKEN, extensions="commands_v2", prefix=PREFIX)
lavalink = lavaplayer.LavalinkClient(
    host="localhost",  # Lavalink host
    port=2333,  # Lavalink port
    password="youshallnotpass",  # Lavalink password
    user_id=893385351362670593,  # Lavalink bot id
)

@bot.events
async def launch(client):
    print("Bot is ready!")
    lavalink.event_manger.add_listner(lavaplayer.TrackEndEvent, track_end_event)
    lavalink.event_manger.add_listner(lavaplayer.TrackStartEvent, track_start_event)
    lavalink.event_manger.add_listner(lavaplayer.WebSocketClosedEvent, web_soket_closed_event)


# -------------------------------- #
# track start event
async def track_start_event(event: lavaplayer.TrackStartEvent):
    logging.info(f"start track: {event.track.title}")

# track end event


async def track_end_event(event: lavaplayer.TrackEndEvent):
    logging.info(f"track end: {event.track.title}")

# web socket closed event


async def web_soket_closed_event(event: lavaplayer.WebSocketClosedEvent):
    logging.error(f"error with websoket {event.reason}")
# -------------------------------- #


@bot.commands
@checks.guild_only()
async def join(ctx: CommandContext):
    voice_stats = ctx.voice_state
    if not voice_stats:
        await ctx.reply("you are not in a voice channel")
        return
    gateway = bot.gateway_for(ctx.guild_id)
    await gateway.change_voice_state(ctx.guild_id, voice_stats.channel.id, self_deaf=True)
    await lavalink.wait_for_connection(ctx.guild_id)
    await ctx.reply(f"done join to <#{voice_stats.channel.id}>")

@bot.commands
@checks.guild_only()
async def play(ctx: CommandContext, query: str):
    result = await lavalink.auto_search_tracks(query)
    if not result:
        await ctx.reply("not found result for your query")
        return
    await lavalink.play(ctx.guild_id, result[0], ctx.author.id)
    await ctx.respond(f"[{result[0].title}]({result[0].uri})")


@bot.events(name="voice_client_update")
@bot.events(name="voice_client_ghost")
@bot.events(name="voice_client_leave")
@bot.events(name="voice_client_join")
@bot.events(name="voice_client_move")
@bot.events(name="user_voice_update")
@bot.events(name="user_voice_leave")
@bot.events(name="user_voice_join")
@bot.events(name="user_voice_move")
async def voice_state_update(client, event, *_args):
    await lavalink.raw_voice_state_update(event.guild_id, event.user_id, event.session_id, event.channel_id)

@bot.events
async def voice_server_update(client, event):
    await lavalink.raw_voice_server_update(event.guild_id, event.endpoint, event.token)

lavalink.connect()
bot.start()