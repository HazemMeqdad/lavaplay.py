import discord
from discord import app_commands
import logging
import time
import lavaplay
import json
import os

DEFAULT_GUILD_ENABLE = discord.Object(id=int(os.environ["GUILD_ID"]))  # ur guild id
TOKEN = os.environ["TOKEN"]  # ur token

LOG = logging.getLogger("discord.bot")


class MyClient(discord.Client):
    def __init__(self, *, intents: discord.Intents):
        super().__init__(intents=intents, enable_debug_events=True)
        self.tree = app_commands.CommandTree(self)
        self.lavalink: lavaplay.Node = None

    async def setup_hook(self):
        self.tree.copy_global_to(guild=DEFAULT_GUILD_ENABLE)
        await self.tree.sync(guild=DEFAULT_GUILD_ENABLE)
        lava = lavaplay.Lavalink()
        self.lavalink: lavaplay.Node = lava.create_node(
            host="localhost",  # Lavalink host
            port=2333,  # Lavalink port
            password="youshallnotpass",  # Lavlink password
            user_id=self.user.id,  # Your bot user id
        )
        self.lavalink.connect()
        self.lavalink.event_manager.add_listener(lavaplay.ReadyEvent, self.on_lava_ready)

    async def on_lava_ready(self, event: lavaplay.ReadyEvent):
        LOG.info(event)
        LOG.info("Lavalink is connected successfully!")


bot = MyClient(intents=discord.Intents.all())

@bot.event
async def on_ready():
    LOG.info("Logged in as %s", bot.user.name)

@bot.tree.command(name="ping", description="Get the latency of the bot")
async def ping(interaction: discord.Interaction):
    start = time.time()
    await interaction.response.send_message("Pong!")
    await interaction.edit_original_message(
        content="Gateway: `%dms`\nLatency: `%dms`"
        % (round(bot.latency * 1000), round((time.time() - start) * 1000))
    )

@bot.tree.command(name="help", description="Get the help of the bot")
async def help(interaction: discord.Interaction):
    commands = bot.tree.get_commands(guild=interaction.guild)
    embed = discord.Embed(title="Help", description="", color=interaction.user.color or discord.Color.random())
    embed.description = "\n".join(f"`/{command.name}`: {command.description}" for command in commands)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="join", description="Join a voice channel")
async def join(interaction: discord.Interaction):
    if not interaction.user.voice:
        await interaction.response.send_message("You are not in a voice channel!")
        return
    await interaction.guild.change_voice_state(
        channel=interaction.user.voice.channel, self_deaf=True, self_mute=False
    )
    player = bot.lavalink.create_player(interaction.guild_id)
    await interaction.response.send_message("Joined the voice channel.")

@bot.tree.command(name="leave", description="Leave the voice channel")
async def leave(interaction: discord.Interaction):
    await interaction.guild.change_voice_state(channel=None)
    player = bot.lavalink.get_player(interaction.guild_id)
    await player.destroy()
    await interaction.response.send_message("Left the voice channel.")

@bot.tree.command(name="search", description="Search for a song")
@app_commands.describe(query="Search for a song")
async def search(interaction: discord.Interaction, *, query: str):
    results = await bot.lavalink.auto_search_tracks(query)
    if not results:
        await interaction.response.send_message("No results found.")
        return
    embed = discord.Embed(title="Search results for `%s`" % query)
    results = results if isinstance(results, list) else results.tracks
    for result in results:
        embed.add_field(
            name=result.title,
            value="[%s](%s)" % (result.author, result.uri),
            inline=False,
        )
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="play", description="Play a song")
@app_commands.describe(query="The song to play")
async def play(interaction: discord.Interaction, *, query: str):
    tracks = await bot.lavalink.auto_search_tracks(query)
    player = bot.lavalink.get_player(interaction.guild_id)
    if not tracks:
        return await interaction.response.send_message("No results found.")
    elif isinstance(tracks, lavaplay.TrackLoadFailed):
        await interaction.response.send_message("Error loading track, Try again later.\n```%s```" % tracks.message)
        return
    elif isinstance(tracks, lavaplay.PlayList):
        await interaction.response.send_message(
            "Playlist found, Adding to queue, Please wait..."
        )
        player.add_to_queue(
            tracks.tracks, interaction.user.id
        )
        await interaction.edit_original_response(
            content="Added to queue, tracks: {}, name: {}".format(
                len(tracks.tracks), tracks.name
            )
        )
        return
    await player.play(tracks[0], interaction.user.id)
    await interaction.response.send_message(f"Now playing: {tracks[0].title}")

@bot.tree.command(name="pause", description="Pause the current track")
async def pause(interaction: discord.Interaction):
    player = bot.lavalink.get_player(interaction.guild_id)
    await player.pause(True)
    await interaction.response.send_message("Paused the track.")

@bot.tree.command(name="resume", description="Resume the track")
async def resume(interaction: discord.Interaction):
    player = bot.lavalink.get_player(interaction.guild_id)
    await player.pause(False)
    await interaction.response.send_message("Resumed the track.")

@bot.tree.command(name="stop", description="Skip the current track")
async def stop(interaction: discord.Interaction):
    player = bot.lavalink.get_player(interaction.guild_id)
    await player.stop()
    await interaction.response.send_message("Stopped the track.")

@bot.tree.command(name="skip", description="Skip the current track")
async def skip(interaction: discord.Interaction):
    player = bot.lavalink.get_player(interaction.guild_id)
    await player.skip()
    await interaction.response.send_message("Skipped the track.")

@bot.tree.command(name="queue", description="Get the queue")
async def queue(interaction: discord.Interaction):
    player = bot.lavalink.get_player(interaction.guild_id)
    if not player.queue:
        return await interaction.response.send_message("No tracks in queue.")
    tracks = [f"**{i + 1}.** {t.title}" for (i, t) in enumerate(player.queue)]
    await interaction.response.send_message("\n".join(tracks))

@bot.tree.command(name="volume", description="Set the volume of the player")
@app_commands.describe(volume="Set the volume to a number between 0 and 100")
async def volume(interaction: discord.Interaction, volume: int):
    player = bot.lavalink.get_player(interaction.guild_id)
    await player.volume(volume)
    await interaction.response.send_message(f"Set the volume to {volume}%.")

@bot.tree.command(name="seek", description="Seek to a specific time")
@app_commands.describe(position="The time to seek to")
async def seek(interaction: discord.Interaction, position: int):
    player = bot.lavalink.get_player(interaction.guild_id)
    await player.seek(position)
    await interaction.response.send_message(f"Seeked to {position} position.")

@bot.tree.command(name="shuffle", description="Shuffle the queue")
async def shuffle(interaction: discord.Interaction):
    player = bot.lavalink.get_player(interaction.guild_id)
    player.shuffle()
    await interaction.response.send_message("Shuffled the queue.")

@bot.tree.command(name="repeat", description="Repeat the current track")
@app_commands.describe(repeat="Repeat status", queue="Repeat the queue")
async def repeat(interaction: discord.Interaction, repeat: bool, queue: bool = False):
    player = bot.lavalink.get_player(interaction.guild_id)
    if queue:
        player.queue_repeat(repeat)
    else:
        player.repeat(repeat)
    await interaction.response.send_message("Repeated the queue.")

@bot.tree.command(name="filter", description="Filter the queue")
async def _filter(interaction: discord.Interaction):
    filters = lavaplay.Filters()
    filters.rotation(0.2)
    player = bot.lavalink.get_player(interaction.guild_id)
    await player.filters(filters)
    await interaction.response.send_message("Filter applied.")

@bot.event
async def on_socket_raw_receive(msg):
    data = json.loads(msg)

    if not data or not data["t"]:
        return
    if data["t"] == "VOICE_SERVER_UPDATE":
        guild_id = int(data["d"]["guild_id"])
        endpoint = data["d"]["endpoint"]
        token = data["d"]["token"]
        player = bot.lavalink.get_player(guild_id)
        if not player:
            player  = bot.lavalink.create_player(guild_id)
        await player.raw_voice_server_update(endpoint, token)

    elif data["t"] == "VOICE_STATE_UPDATE":
        if not data["d"]["channel_id"]:
            channel_id = None
        else:
            channel_id = int(data["d"]["channel_id"])

        guild_id = int(data["d"]["guild_id"])
        user_id = int(data["d"]["user_id"])
        session_id = data["d"]["session_id"]

        player = bot.lavalink.get_player(guild_id)
        if not player:
            player  = bot.lavalink.create_player(guild_id)
        await player.raw_voice_state_update(
            user_id,
            session_id,
            channel_id,
        )


bot.run(TOKEN)