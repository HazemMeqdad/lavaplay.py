import json
from discord.ext import commands
import lavaplayer

PREFIX = ","
TOKEN = "..."

bot = commands.Bot(PREFIX, enable_debug_events=True)
lavalink = lavaplayer.LavalinkClient(
    host="localhost",
    port=2333,
    password="youshallnotpass",
    user_id=893385351362670593
)


@bot.event
async def on_ready():
    print("Bot is ready.")

@bot.command()
async def join(ctx: commands.Context):
    await ctx.guild.change_voice_state(channel=ctx.author.voice.channel, self_deaf=True)
    await lavalink.wait_for_connection(ctx.guild.id)
    await ctx.send("Joined the voice channel.")


@bot.command()
async def leave(ctx: commands.Context):
    await ctx.guild.change_voice_state(channel=None)
    await lavalink.wait_for_remove_connection(ctx.guild.id)
    await ctx.send("Left the voice channel.")

@bot.command()
async def play(ctx: commands.Context, *, query: str):
    try:
        tracks = await lavalink.auto_search_tracks(query)
    except lavaplayer.TrackLoadFailed as exc:
        return await ctx.send(exc.message)

    if not tracks:
        return await ctx.send("No results found.")

    # Playlist
    if isinstance(tracks, lavaplayer.PlayList):
        msg = await ctx.send("Playlist found, Adding to queue, Please wait...")
        await lavalink.add_to_queue(ctx.guild.id, tracks.tracks, ctx.author.id)
        await msg.edit(content="Added to queue, tracks: {}, name: {}".format(len(tracks.tracks), tracks.name))
        return

    track = tracks[0]
    await lavalink.play(ctx.guild.id, track, ctx.author.id)
    await ctx.send(f"Now playing: {track.title}")


@bot.command()
async def pause(ctx: commands.Context, stats: bool):
    await lavalink.pause(ctx.guild.id, stats)
    await ctx.send("Paused the track.")

@bot.command()
async def resume(ctx: commands.Context):
    await lavalink.resume(ctx.guild.id)
    await ctx.send("Resumed the track.")

@bot.command()
async def stop(ctx: commands.Context):
    await lavalink.stop(ctx.guild.id)
    await ctx.send("Stopped the track.")

@bot.command()
async def skip(ctx: commands.Context):
    await lavalink.skip(ctx.guild.id)
    await ctx.send("Skipped the track.")

@bot.command()
async def queue(ctx: commands.Context):
    queue = lavalink.queue(ctx.guild.id)
    if not queue:
        return await ctx.send("No tracks in queue.")
    tracks = [f"**{i + 1}.** {t.title}" for (i, t) in enumerate(queue)]
    await ctx.send("\n".join(tracks))

@bot.command()
async def volume(ctx: commands.Context, volume: int):
    await lavalink.volume(ctx.guild.id, volume)
    await ctx.send(f"Set the volume to {volume}%.")

@bot.command()
async def seek(ctx: commands.Context, seconds: int):
    await lavalink.seek(ctx.guild.id, seconds)
    await ctx.send(f"Seeked to {seconds} seconds.")

@bot.command()
async def shuffle(ctx: commands.Context):
    await lavalink.shuffle(ctx.guild.id)
    await ctx.send("Shuffled the queue.")

@bot.command()
async def remove(ctx: commands.Context, index: int):
    await lavalink.remove(ctx.guild.id, index)
    await ctx.send(f"Removed track {index}.")

@bot.command()
async def clear(ctx: commands.Context):
    await lavalink.clear(ctx.guild.id)
    await ctx.send("Cleared the queue.")

@bot.command()
async def repeat(ctx: commands.Context, stats: bool):
    await lavalink.repeat(ctx.guild.id, stats)
    await ctx.send("Repeated the queue.")
    
@bot.command()
async def filter(ctx: commands.Context):
    filters = lavaplayer.Filters()
    filters.rotation(0.2)
    await lavalink.filters(ctx.guild.id, filters)
    await ctx.send("Filter applied.")
    
@bot.event
async def on_socket_raw_receive(data):
    data = json.loads(data)

    if not data or not data["t"]:
        return
    if data["t"] == "VOICE_SERVER_UPDATE":
        guild_id = int(data["d"]["guild_id"])
        endpoint = data["d"]["endpoint"]
        token = data["d"]["token"]

        await lavalink.raw_voice_server_update(guild_id, endpoint, token)

    elif data["t"] == "VOICE_STATE_UPDATE":
        if not data["d"]["channel_id"]:
            channel_id = None
        else:
            channel_id = int(data["d"]["channel_id"])

        guild_id = int(data["d"]["guild_id"])
        user_id = int(data["d"]["user_id"])
        session_id = data["d"]["session_id"]

        await lavalink.raw_voice_state_update(
            guild_id,
            user_id,
            session_id,
            channel_id,
        )

lavalink.connect()
bot.run(TOKEN)
