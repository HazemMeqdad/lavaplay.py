import discord
from discord.ext import commands
import json
import lavaplay
import logging

PREFIX = ","  # Change this to your prefix
TOKEN = "..."  # Change this to your token

LOG = logging.getLogger("discord.bot")

bot = commands.Bot(commands.when_mentioned_or(PREFIX), enable_debug_events=True, intents=discord.Intents.all())
lavalink = lavaplay.Lavalink(
    host="localhost",  # Lavalink host
    port=2333,  # Lavalink port
    password="youshallnotpass"  # Lavlink password
)
bot.remove_command("help")

@bot.event
async def close():
	for guild in bot.guilds:
		await guild.change_voice_state(channel=None)

@bot.event
async def on_ready():
    lavalink.set_user_id(bot.user.id)
    lavalink.set_event_loop(bot.loop)
    lavalink.connect()
    LOG.info("Logged in as %s", bot.user.name)

@bot.command(name="help", aliases=["commands"], help="Shows all commands.")
async def help_commmand(ctx: commands.Context):
    embed = discord.Embed(title="Help", description="This is a help command", color=0x00ff00)
    embed.description = "\n".join(f"`{PREFIX}{command.name}`: {command.help}" for command in bot.commands)
    await ctx.send(embed=embed)

@bot.command(help="Join the voice channel")
async def join(ctx: commands.Context):
	await ctx.guild.change_voice_state(channel=ctx.author.voice.channel, self_deaf=True, self_mute=False)
	await lavalink.wait_for_connection(ctx.guild.id)
	await ctx.send("Joined the voice channel.")

@bot.command(help="Leave the voice channel")
async def leave(ctx: commands.Context):
	await ctx.guild.change_voice_state(channel=None)
	await lavalink.wait_for_remove_connection(ctx.guild.id)
	await ctx.send("Left the voice channel.")

@bot.command(help="Play a song")
async def play(ctx: commands.Context, *, query: str):
    tracks = await lavalink.auto_search_tracks(query)

    if not tracks:
        return await ctx.send("No results found.")
    elif isinstance(tracks, lavaplay.TrackLoadFailed):
        await ctx.send("Track load failed. Try again.\n```" + tracks.message + "```")
    # Playlist
    elif isinstance(tracks, lavaplay.PlayList):
        msg = await ctx.send("Playlist found, Adding to queue, Please wait...")
        await lavalink.add_to_queue(ctx.guild.id, tracks.tracks, ctx.author.id)
        await msg.edit(content="Added to queue, tracks: {}, name: {}".format(len(tracks.tracks), tracks.name))
        return
    await lavalink.play(ctx.guild.id, tracks[0], ctx.author.id)
    await ctx.send(f"Now playing: {tracks[0].title}")

@bot.command(help="Pause the current song")
async def pause(ctx: commands.Context):
	await lavalink.pause(ctx.guild.id, True)
	await ctx.send("Paused the track.")

@bot.command(help="Resume the current song")
async def resume(ctx: commands.Context):
	await lavalink.pause(ctx.guild.id, False)
	await ctx.send("Resumed the track.")

@bot.command(help="Stop the current song")
async def stop(ctx: commands.Context):
	await lavalink.stop(ctx.guild.id)
	await ctx.send("Stopped the track.")

@bot.command(help="Skip the current song")
async def skip(ctx: commands.Context):
	await lavalink.skip(ctx.guild.id)
	await ctx.send("Skipped the track.")

@bot.command(help="Get queue info")
async def queue(ctx: commands.Context):
	queue = lavalink.queue(ctx.guild.id)
	if not queue:
		return await ctx.send("No tracks in queue.")
	tracks = [f"**{i + 1}.** {t.title}" for (i, t) in enumerate(queue)]
	await ctx.send("\n".join(tracks))

@bot.command(help="Set the volume")
async def volume(ctx: commands.Context, volume: int):
	await lavalink.volume(ctx.guild.id, volume)
	await ctx.send(f"Set the volume to {volume}%.")

@bot.command(help="Seek to a position")
async def seek(ctx: commands.Context, seconds: int):
	await lavalink.seek(ctx.guild.id, seconds)
	await ctx.send(f"Seeked to {seconds} seconds.")

@bot.command(help="Get the current song")
async def shuffle(ctx: commands.Context):
	await lavalink.shuffle(ctx.guild.id)
	await ctx.send("Shuffled the queue.")

@bot.command(help="Get the current song")
async def remove(ctx: commands.Context, index: int):
	await lavalink.remove(ctx.guild.id, index)
	await ctx.send(f"Removed track {index}.")

@bot.command(help="Get the current song")
async def clear(ctx: commands.Context):
	await lavalink.clear(ctx.guild.id)
	await ctx.send("Cleared the queue.")

@bot.command(help="Get the current song")
async def repeat(ctx: commands.Context, status: bool):
	await lavalink.repeat(ctx.guild.id, status)
	await ctx.send("Repeated the queue.")
	
@bot.command(name="filter", help="Get the current song")
async def filter_command(ctx: commands.Context):
    filters = lavaplay.Filters()
    filters.rotation(0.2)
    filters.equalizer([0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5])
    await lavalink.filters(ctx.guild.id, filters)
    await ctx.send("Filter applied.")
	
@bot.event
async def on_socket_raw_receive(msg):
	data = json.loads(msg)
	
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

bot.run(TOKEN)
