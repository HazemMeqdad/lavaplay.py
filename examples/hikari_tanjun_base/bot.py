import hikari
import tanjun
import lavaplay


TOKEN = "..."  # replace with your token

bot = hikari.GatewayBot(TOKEN, intents=hikari.Intents.ALL)
client = tanjun.Client.from_gateway_bot(bot)
lava = lavaplay.Lavalink()
lavalink = lava.create_node(
    host="localhost",  # Lavalink host
    port=2333,  # Lavalink port
    password="youshallnotpass",  # Lavalink password
    user_id=0  # Will be replaced with bot user id on start event
)

component = tanjun.Component()

@component.with_listener(hikari.StartedEvent)
async def on_start(event: hikari.StartedEvent):
    lavalink.user_id = bot.get_me().id
    lavalink.connect()

# ------------------------------- #
@component.with_command
@tanjun.as_slash_command("join", "Join a voice channel")
async def join(ctx: tanjun.abc.SlashContext):
    state = bot.cache.get_voice_state(ctx.guild_id, ctx.author.id)
    if not state or not state.channel_id:
        await ctx.respond("you are not in a voice channel")
        return
    channel_id = state.channel_id
    lavalink.create_player(ctx.guild_id)
    await bot.update_voice_state(ctx.guild_id, channel_id, self_deaf=True)
    await ctx.respond(f"done join to <#{channel_id}>")

@component.with_command
@tanjun.as_slash_command("leave", "Leave a voice channel")
async def leave(ctx: tanjun.abc.SlashContext):
    player = lavalink.get_player(ctx.guild_id)
    await bot.update_voice_state(ctx.guild_id, None)
    await player.destroy()
    await ctx.respond("done leave the voice channel")

@component.with_command
@tanjun.with_str_slash_option("query", "query to search")
@tanjun.as_slash_command("play", "Play command")
async def play(ctx: tanjun.abc.SlashContext, query: str):
    player = lavalink.get_player(ctx.guild_id)
    try:
        result = await lavalink.auto_search_tracks(query)  # search for the query
    except lavaplay.TrackLoadFailed:
        await ctx.respond("Track load failed, try again later.\n```{}```".format(result.message))
        return
    if not result:
        await ctx.respond("not found result for your query")
        return
    elif isinstance(result, lavaplay.PlayList):
        player.player(result.tracks, ctx.author.id)
        await ctx.respond(f"added {len(result.tracks)} tracks to queue")
        return 

    await player.play(result[0], ctx.author.id)  # play the first result
    await ctx.respond(f"[{result[0].title}]({result[0].uri})")  # send the embed

@component.with_command
@tanjun.as_slash_command("stop", "Stop command")
async def stop(ctx: tanjun.abc.SlashContext):
    player = lavalink.get_player(ctx.guild_id)
    await player.stop()
    await ctx.respond("done stop the music")

@component.with_command
@tanjun.as_slash_command("pause", "Pause command")
async def pause(ctx: tanjun.abc.SlashContext):
    player = lavalink.get_player(ctx.guild_id)
    await player.pause(True)
    await ctx.respond("done pause the music")

@component.with_command
@tanjun.as_slash_command("resume", "Resume command")
async def resume(ctx: tanjun.abc.SlashContext):
    player = lavalink.get_player(ctx.guild_id)
    await player.pause(False)
    await ctx.respond("done resume the music")

@component.with_command
@tanjun.with_int_slash_option("position", "position to seek")
@tanjun.as_slash_command("seek", "Seek command")
async def seek(ctx: tanjun.abc.SlashContext, position: int):
    player = lavalink.get_player(ctx.guild_id)
    await player.seek(position)
    await ctx.respond(f"done seek to {position}")

@component.with_command
@tanjun.with_int_slash_option("volume", "volume to set")
@tanjun.as_slash_command("volume", "Volume command")
async def volume(ctx: tanjun.abc.SlashContext, volume: int):
    player = lavalink.get_player(ctx.guild_id)
    await player.volume(volume)
    await ctx.respond(f"done set volume to {volume}")

@component.with_command
@tanjun.as_slash_command("queue", "Queue command")
async def queue(ctx: tanjun.abc.SlashContext):
    player = lavalink.get_player(ctx.guild_id)
    if not player or not player.queue:
        await ctx.respond("queue is empty")
        return
    await ctx.respond("```\n" + "\n".join([f"{i + 1}. {track.title}" for i, track in enumerate(player.queue)]) + "```")

@component.with_command
@tanjun.as_slash_command("np", "Now playing command")
async def np(ctx: tanjun.abc.SlashContext):
    player = lavalink.get_player(ctx.guild_id)
    if not player or not player.queue:
        await ctx.respond("nothing playing")
        return
    await ctx.respond(f"[{player.queue[0].title}]({player.queue[0].uri})")

@component.with_command
@tanjun.with_bool_slash_option("status", "status to set repeat mode")
@tanjun.as_slash_command("repeat", "Repeat command")
async def repeat(ctx: tanjun.abc.SlashContext, status: bool):
    player = lavalink.get_player(ctx.guild_id)
    player.repeat(status)
    await ctx.respond(f"done set repeat mode to {status}")

@component.with_command
@tanjun.as_slash_command("shuffle", "Shuffle command")
async def shuffle(ctx: tanjun.abc.SlashContext):
    player = lavalink.get_player(ctx.guild_id)
    player.shuffle()
    await ctx.respond("done shuffle the queue")
# ------------------------------- #

# the voice_state_update event is called when a user changes voice channel
@bot.listen(hikari.VoiceStateUpdateEvent)
async def voice_state_update(event: hikari.VoiceStateUpdateEvent):
    player = lavalink.get_player(event.guild_id)
    # Update the voice state of the player
    await player.raw_voice_state_update(event.state.user_id, event.state.session_id, event.state.channel_id)

# the voice_server_update event is called when a user changes voice channel
@bot.listen(hikari.VoiceServerUpdateEvent)
async def voice_server_update(event: hikari.VoiceServerUpdateEvent):
    player = lavalink.get_player(event.guild_id)
    # Update the voice server information of the player
    await player.raw_voice_server_update(event.raw_endpoint, event.token)

client.add_component(component)
bot.run()
