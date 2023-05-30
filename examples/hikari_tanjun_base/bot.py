import hikari
import tanjun
import lavaplay
import asyncio


TOKEN = "..."  # replace with your token

bot = hikari.GatewayBot(TOKEN)
client = tanjun.Client.from_gateway_bot(bot)
lavalink = lavaplay.Lavalink(
    host="localhost",  # Lavalink host
    port=2333,  # Lavalink port
    password="youshallnotpass",  # Lavalink password
)

component = tanjun.Component()

@component.with_listener(hikari.StartedEvent)
async def on_start(event: hikari.StartedEvent):
    lavalink.set_user_id(bot.get_me().id)
    lavalink.set_event_loop(asyncio.get_event_loop())
    lavalink.connect()

# ------------------------------- #
@component.with_command
@tanjun.as_slash_command("join", "Join a voice channel")
async def join(ctx: tanjun.abc.SlashContext):
    states = bot.cache.get_voice_states_view_for_guild(ctx.guild_id)
    voice_state = [state async for state in states.iterator().filter(lambda i: i.user_id == ctx.author.id)]
    if not voice_state:
        await ctx.respond("you are not in a voice channel")
        return
    channel_id = voice_state[0].channel_id
    await bot.update_voice_state(ctx.guild_id, channel_id, self_deaf=True)
    await lavalink.wait_for_connection(ctx.guild_id)
    await ctx.respond(f"done join to <#{channel_id}>")

@component.with_command
@tanjun.as_slash_command("leave", "Leave a voice channel")
async def leave(ctx: tanjun.abc.SlashContext):
    await bot.update_voice_state(ctx.guild_id, None)
    await ctx.respond("done leave the voice channel")

@component.with_command
@tanjun.with_str_slash_option("query", "query to search")
@tanjun.as_slash_command("play", "Play command")
async def play(ctx: tanjun.abc.SlashContext, query: str):
    result = await lavalink.auto_search_tracks(query)  # search for the query
    if not result:
        await ctx.respond("not found result for your query")
        return
    elif isinstance(result, lavaplay.TrackLoadFailed):
        await ctx.respond("Track load failed, try again later.\n```{}```".format(result.message))
        return
    elif isinstance(result, lavaplay.PlayList):
        await lavalink.add_to_queue(ctx.guild_id, result.tracks, ctx.author.id)
        await ctx.respond(f"added {len(result.tracks)} tracks to queue")
        return 

    await lavalink.play(ctx.guild_id, result[0], ctx.author.id)  # play the first result
    await ctx.respond(f"[{result[0].title}]({result[0].uri})")  # send the embed

@component.with_command
@tanjun.as_slash_command("stop", "Stop command")
async def stop(ctx: tanjun.abc.SlashContext):
    await lavalink.stop(ctx.guild_id)
    await ctx.respond("done stop the music")

@component.with_command
@tanjun.as_slash_command("pause", "Pause command")
async def pause(ctx: tanjun.abc.SlashContext):
    await lavalink.pause(ctx.guild_id)
    await ctx.respond("done pause the music")

@component.with_command
@tanjun.as_slash_command("resume", "Resume command")
async def resume(ctx: tanjun.abc.SlashContext):
    await lavalink.resume(ctx.guild_id)
    await ctx.respond("done resume the music")

@component.with_command
@tanjun.with_int_slash_option("position", "position to seek")
@tanjun.as_slash_command("seek", "Seek command")
async def seek(ctx: tanjun.abc.SlashContext, position: int):
    await lavalink.seek(ctx.guild_id, position)
    await ctx.respond(f"done seek to {position}")

@component.with_command
@tanjun.with_int_slash_option("volume", "volume to set")
@tanjun.as_slash_command("volume", "Volume command")
async def volume(ctx: tanjun.abc.SlashContext, volume: int):
    await lavalink.volume(ctx.guild_id, volume)
    await ctx.respond(f"done set volume to {volume}")

@component.with_command
@tanjun.as_slash_command("queue", "Queue command")
async def queue(ctx: tanjun.abc.SlashContext):
    queue = await lavalink.queue(ctx.guild_id)
    if not queue:
        await ctx.respond("queue is empty")
        return
    await ctx.respond("```\n" + "\n".join([f"{i + 1}. {track.title}" for i, track in enumerate(queue)]) + "```")

@component.with_command
@tanjun.as_slash_command("np", "Now playing command")
async def np(ctx: tanjun.abc.SlashContext):
    node = await lavalink.get_guild_node(ctx.guild_id)
    if not node or not node.queue:
        await ctx.respond("nothing playing")
        return
    await ctx.respond(f"[{node.queue[0].title}]({node.queue[0].uri})")

@component.with_command
@tanjun.with_bool_slash_option("status", "status to set repeat mode")
@tanjun.as_slash_command("repeat", "Repeat command")
async def repeat(ctx: tanjun.abc.SlashContext, status: bool):
    await lavalink.repeat(ctx.guild_id, status)
    await ctx.respond(f"done set repeat mode to {status}")


@component.with_command
@tanjun.as_slash_command("shuffle", "Shuffle command")
async def shuffle(ctx: tanjun.abc.SlashContext):
    await lavalink.shuffle(ctx.guild_id)
    await ctx.respond("done shuffle the queue")
# ------------------------------- #

# On voice state update the bot will update the lavalink node
@component.with_listener(hikari.VoiceStateUpdateEvent)
async def voice_state_update(event: hikari.VoiceStateUpdateEvent):
    await lavalink.raw_voice_state_update(event.guild_id, event.state.user_id, event.state.session_id, event.state.channel_id)

@component.with_listener(hikari.VoiceServerUpdateEvent)
async def voice_server_update(event: hikari.VoiceServerUpdateEvent):
    await lavalink.raw_voice_server_update(event.guild_id, event.endpoint, event.token)


client.add_component(component)
bot.run()
