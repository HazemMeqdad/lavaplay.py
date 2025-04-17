import lightbulb
import hikari
import lavaplay
import logging
import os
import asyncio

SLASH_COMMAND = True  # if you want to use slash command, set True
PREFIX = "="  # prefix for commands
TOKEN = os.environ["TOKEN"]  # token for bot
DEFAULT_ENABLED_GUILDS = ["DEBUG_GUILD"]  # list of guilds that the bot will create slash commands for (if you want to use slash command)
# you can keep empty list if you don't want to use guild slash command it create globally for all guilds


bot = lightbulb.BotApp(TOKEN, PREFIX, default_enabled_guilds=DEFAULT_ENABLED_GUILDS)
lava = lavaplay.Lavalink()
lavalink = lava.create_node(
    host="localhost",  # Lavalink host
    port=2333,  # Lavalink port
    password="youshallnotpass",  # Lavalink password
    user_id=0
)

@bot.listen(hikari.StartedEvent)
async def on_start(event: hikari.StartedEvent):
    lavalink.user_id = bot.get_me().id
    lavalink.set_event_loop(asyncio.get_event_loop())
    lavalink.connect()

# On voice state update the bot will update the lavalink node
@bot.listen(hikari.VoiceStateUpdateEvent)
async def voice_state_update(event: hikari.VoiceStateUpdateEvent):
    player = lavalink.get_player(event.guild_id)
    await player.raw_voice_state_update(event.state.user_id, event.state.session_id, event.state.channel_id)

@bot.listen(hikari.VoiceServerUpdateEvent)
async def voice_server_update(event: hikari.VoiceServerUpdateEvent):
    player = lavalink.get_player(event.guild_id)
    await player.raw_voice_server_update(event.endpoint, event.token)

implements = [lightbulb.commands.PrefixCommand] if not SLASH_COMMAND else [lightbulb.commands.PrefixCommand, lightbulb.commands.SlashCommand]

# Commands
# ------------------------------------- #
@bot.command()
@lightbulb.command(name="join", description="join voice channel")
@lightbulb.implements(*implements)
async def join_command(ctx: lightbulb.context.Context):
    voice_state = bot.cache.get_voice_state(ctx.guild_id, ctx.author.id)
    if not voice_state or not voice_state.channel_id:
        await ctx.respond("you are not in a voice channel")
        return
    lavalink.create_player(ctx.guild_id)
    channel_id = voice_state.channel_id
    await bot.update_voice_state(ctx.guild_id, channel_id, self_deaf=True)
    await ctx.respond(f"done join to <#{channel_id}>")

@bot.command()
@lightbulb.option(name="query", description="query to search", required=True)
@lightbulb.command(name="play", description="Play command", aliases=["p"])
@lightbulb.implements(*implements)
async def play_command(ctx: lightbulb.context.Context):
    query = ctx.options.query  # get query from options
    player = lavalink.get_player(ctx.guild_id)  # get player
    result = await lavalink.auto_search_tracks(query)  # search for the query
    if not result:
        await ctx.respond("not found result for your query")
        return
    elif isinstance(result, lavaplay.TrackLoadFailed):
        await ctx.respond("Track load failed, try again later.\n```{}```".format(result.message))
        return
    elif isinstance(result, lavaplay.PlayList):
        player.add_to_queue(result.tracks, ctx.author.id)
        await player.play_playlist(result.tracks)
        await ctx.respond(f"added {len(result.tracks)} tracks to queue")
        return 

    await player.play(result[0], ctx.author.id)  # play the first result
    await ctx.respond(f"[{result[0].title}]({result[0].uri})")  # send the embed

@bot.command()
@lightbulb.command(name="stop", description="Stop command", aliases=["s"])
@lightbulb.implements(*implements)
async def stop_command(ctx: lightbulb.context.Context):
    player = lavalink.get_player(ctx.guild_id)
    await player.stop()
    await ctx.respond("done stop the music")

@bot.command()
@lightbulb.command(name="pause", description="Pause command")
@lightbulb.implements(*implements)
async def pause_command(ctx: lightbulb.context.Context):
    player = lavalink.get_player(ctx.guild_id)
    await player.pause(True)
    await ctx.respond("The music is paused now")

@bot.command()
@lightbulb.command(name="resume", description="Resume command")
@lightbulb.implements(*implements)
async def resume_command(ctx: lightbulb.context.Context):
    player = lavalink.get_player(ctx.guild_id)
    await player.pause(False)
    await ctx.respond("The music is resumed now")

@bot.command()
@lightbulb.option(name="position", description="Position to seek", required=True)
@lightbulb.command(name="seek", description="Seek command")
@lightbulb.implements(*implements)
async def seek_command(ctx: lightbulb.context.Context):
    position = ctx.options.position
    player = lavalink.get_player(ctx.guild_id)
    await player.seek(position)
    await ctx.respond(f"done seek to {position}")

@bot.command()
@lightbulb.option(name="vol", description="Volume to set", required=True)
@lightbulb.command(name="volume", description="Volume command")
@lightbulb.implements(*implements)
async def volume_command(ctx: lightbulb.context.Context):
    volume = ctx.options.vol
    player = lavalink.get_player(ctx.guild_id)
    await player.volume(volume)
    await ctx.respond(f"done set volume to {volume}%")

@bot.command()
@lightbulb.command(name="destroy", description="Destroy command")
@lightbulb.implements(*implements)
async def destroy_command(ctx: lightbulb.context.Context):
    player = lavalink.get_player(ctx.guild_id)
    await player.destroy()
    await ctx.respond("done destroy the bot")

@bot.command()
@lightbulb.command(name="queue", description="Queue command")
@lightbulb.implements(*implements)
async def queue_command(ctx: lightbulb.context.Context):
    player = lavalink.get_player(ctx.guild_id)
    if not player or not player.queue:
        await ctx.respond("nothing in the queue")
        return
    embed = hikari.Embed(
        description="\n".join(
            [f"{n+1}- [{i.title}]({i.uri})" for n, i in enumerate(player.queue)])
    )
    await ctx.respond(embed=embed)

@bot.command()
@lightbulb.command(name="np", description="Now playing command")
@lightbulb.implements(*implements)
async def np_command(ctx: lightbulb.context.Context):
    player = lavalink.get_player(ctx.guild_id)
    if not player or not player.queue:
        await ctx.respond("nothing playing")
        return
    await ctx.respond(f"[{player.queue[0].title}]({player.queue[0].uri})")

@bot.command()
@lightbulb.command(name="repeat", description="Repeat command")
@lightbulb.implements(*implements)
async def repeat_command(ctx: lightbulb.context.Context):
    player = lavalink.get_player(ctx.guild_id)
    stats = False if player._repeat else True
    player.repeat(stats)
    if stats:
        await ctx.respond("done repeat the music")
        return
    await ctx.respond("done stop repeat the music")

@bot.command()
@lightbulb.command(name="shuffle", description="Shuffle command")
@lightbulb.implements(*implements)
async def shuffle_command(ctx: lightbulb.context.Context):
    player = lavalink.get_player(ctx.guild_id)
    player.shuffle()
    await ctx.respond("done shuffle the music")

@bot.command()
@lightbulb.command(name="leave", description="Leave command")
@lightbulb.implements(*implements)
async def leave_command(ctx: lightbulb.context.Context):
    player = lavalink.get_player(ctx.guild_id)
    await bot.update_voice_state(ctx.guild_id, None)
    player.destroy()
    await ctx.respond("done leave the voice channel")
# ------------------------------------- #

@lavalink.listen(lavaplay.TrackStartEvent)
async def track_start_event(event: lavaplay.TrackStartEvent):
    logging.info(f"start track: {event.track.title}")

@lavalink.listen(lavaplay.TrackEndEvent)
async def track_end_event(event: lavaplay.TrackEndEvent):
    logging.info(f"track end: {event.track.title}")

@lavalink.listen(lavaplay.WebSocketClosedEvent)
async def web_socket_closed_event(event: lavaplay.WebSocketClosedEvent):
    logging.error(f"error with websocket {event.reason}")


if __name__ == "__main__":
    if os.name != "nt":
        import uvloop
        uvloop.install()
    bot.run()
