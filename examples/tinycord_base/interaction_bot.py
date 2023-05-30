import tinycord
import lavaplay
import datetime

TOKEN = ""
client = tinycord.interactions.ApplicationCommandClient(
    token=TOKEN,
    intents=tinycord.Intents.all()
)
lavalink = lavaplay.LavalinkClient(
    host="127.0.0.1",
    port=8888,
    password="password",
    user_id=923934845502124093
)

@client.event
async def on_ready(shard: "tinycord.Gateway") -> None:
    print("Ready!")
    await client.load()

@client.event
async def on_voice_server_update(guild, data):
    if data["endpoint"] is not None:
        await lavalink.raw_voice_server_update(
             int(data['guild_id']), data['endpoint'], data['token'])

@client.event
async def on_voice_state_update(guild, before, after: tinycord.VoiceState):
    await lavalink.raw_voice_state_update(
        after.guild_id, after.user_id, after.session_id, after.channel_id)

@client.event
async def on_interaction_create(ctx: "tinycord.Interaction") -> None:
    await client.process_command(ctx)

@client.add('join', ["all"], "Join a voice channel")
@tinycord.interactions.add_option(
    tinycord.ApplicationCommandOption(
        name="channel",
        description="The channel to join",
        type=tinycord.ApplicationCommandOptionType.CHANNEL,
    )
)
async def join(ctx: "tinycord.Interaction") -> None:
    channel: tinycord.VoiceChannel = (client.get_channel(
        ctx.get_option("channel").value) if "channel" in ctx.data.options else ctx.author.voice_state.channel)

    if channel is None:
        await ctx.reply(4, tinycord.MessageCallback(
            content="You are not in a voice channel"
        ))
    
    if ctx.guild.me.voice_state is not None:
        return await ctx.reply(4, tinycord.MessageCallback(
            content="I am already in a voice channel"
        ))

    await channel.connect(self_deaf=True)
    # Join a voice channel

    await ctx.reply(4, tinycord.MessageCallback(
        content="Joined the voice channel"
    ))

@client.add('leave', ["all"], "Leave the voice channel")
async def leave(ctx: "tinycord.Interaction") -> None:
    if ctx.guild.voice_server is None:
        await ctx.reply(4, tinycord.MessageCallback(
            content="I am not in a voice channel"
        ))

    await ctx.guild.me.voice_state.channel.disconnect()
    # Leave the voice channel

    await ctx.reply(4, tinycord.MessageCallback(
        content="I have left the voice channel"
    ))

@client.add('play', ["all"], "Play a song")
@tinycord.interactions.add_option(
    tinycord.ApplicationCommandOption(
        name="song",
        description="The song to play",
        type=tinycord.ApplicationCommandOptionType.STRING,
        required=True
    )
)
async def play(ctx: "tinycord.Interaction") -> None:
    if ctx.guild.voice_server is None:
        await ctx.reply(4, tinycord.MessageCallback(
            content="I am not in a voice channel"
        ))

        await ctx.guild.me.voice_state.channel.connect()

    if ctx.user not in ctx.guild.me.voice_state.channel.users:
        await ctx.reply(4, tinycord.MessageCallback(
            content="You are not in the voice channel"
        ))

    song = ctx.get_option("song").value

    result = await lavalink.auto_search_tracks(song)
    # Play a song

    if len(result) == 0:
        await ctx.reply(4, tinycord.MessageCallback(
            content="No results found"
        ))

    if isinstance(result, lavaplay.PlayList):
        await lavalink.add_to_queue(ctx.guild_id, result.tracks, ctx.user.id)
        # Play a playlist

    queue = await lavalink.queue(ctx.guild_id)
    if len(queue) == 0:
        message = f"Now playing: {result[0].title} "
    else:
        message = f"Added to queue: {result[0].title}"

    await lavalink.play(ctx.guild_id, result[0], ctx.user.id)

    embed = tinycord.Embed(
        title="Now playing",
        description=result[0].title,
        color=0x00ff00
    )

    embed.add_field(
        'Duration', 
        datetime.timedelta(seconds=result[0].length).__str__(), 
        inline=True
    )
    embed.add_field('Author', result[0].author, inline=True)
    embed.add_field('Requester', ctx.user.username, inline=True)

    await ctx.reply(4, tinycord.MessageCallback(
        content=message,
        embeds=[
            embed
        ]
    ))

@client.add('pause', ["all"], "Pause the player")
async def pause(ctx: "tinycord.Interaction") -> None:
    if ctx.guild.voice_server is None:
        await ctx.reply(4, tinycord.MessageCallback(
            content="I am not in a voice channel"
        ))

    if ctx.user not in ctx.guild.me.voice_state.channel.users:
        await ctx.reply(4, tinycord.MessageCallback(
            content="You are not in the voice channel"
        ))

    await lavalink.pause(ctx.guild_id, True)

    await ctx.reply(4, tinycord.MessageCallback(
        content="Paused the player"
    ))

@client.add('resume', ["all"], "Resume the player")
async def resume(ctx: "tinycord.Interaction") -> None:
    if ctx.guild.voice_server is None:
        await ctx.reply(4, tinycord.MessageCallback(
            content="I am not in a voice channel"
        ))

    if ctx.user not in ctx.guild.me.voice_state.channel.users:
        await ctx.reply(4, tinycord.MessageCallback(
            content="You are not in the voice channel"
        ))

    await lavalink.pause(ctx.guild_id, False)

    await ctx.reply(4, tinycord.MessageCallback(
        content="Resume the player"
    ))

@client.add('stop', ["all"], "Stop the player")
async def stop(ctx: "tinycord.Interaction") -> None:
    if ctx.guild.voice_server is None:
        await ctx.reply(4, tinycord.MessageCallback(
            content="I am not in a voice channel"
        ))

    if ctx.user not in ctx.guild.me.voice_state.channel.users:
        await ctx.reply(4, tinycord.MessageCallback(
            content="You are not in the voice channel"
        ))

    await lavalink.stop(ctx.guild_id)

    await ctx.reply(4, tinycord.MessageCallback(
        content="Stopped the player"
    ))

@client.add('skip', ["all"], "Skip the current song")
async def skip(ctx: "tinycord.Interaction") -> None:
    if ctx.guild.voice_server is None:
        await ctx.reply(4, tinycord.MessageCallback(
            content="I am not in a voice channel"
        ))

    if ctx.user not in ctx.guild.me.voice_state.channel.users:
        await ctx.reply(4, tinycord.MessageCallback(
            content="You are not in the voice channel"
        ))
    
    await lavalink.skip(ctx.guild_id)

    await ctx.reply(4, tinycord.MessageCallback(
        content="Skipped the current song"
    ))

@client.add('queue', ["all"], "Show the current queue")
async def queue(ctx: "tinycord.Interaction") -> None:
    if ctx.guild.voice_server is None:
        await ctx.reply(4, tinycord.MessageCallback(
            content="I am not in a voice channel"
        ))

    if ctx.user not in ctx.guild.me.voice_state.channel.users:
        await ctx.reply(4, tinycord.MessageCallback(
            content="You are not in the voice channel"
        ))

    queue = await lavalink.queue(ctx.guild_id)
    # Get the current queue

    embed = tinycord.Embed(
        description="\n".join(
            [f"{n+1}- [{i.title}]({i.uri})" for n, i in enumerate(queue)])
    )

    await ctx.reply(4, tinycord.MessageCallback(
        content="Current queue",
        embeds=[
            embed
        ]
    ))

@client.add("volume", ["all"], "Set the volume")
@tinycord.interactions.add_option(
    tinycord.ApplicationCommandOption(
        name="volume",
        description="The volume to set",
        type=tinycord.ApplicationCommandOptionType.INTEGER,
        required=True
    )
)
async def volume(ctx: "tinycord.Interaction") -> None:
    if ctx.guild.voice_server is None:
        await ctx.reply(4, tinycord.MessageCallback(
            content="I am not in a voice channel"
        ))

    if ctx.user not in ctx.guild.me.voice_state.channel.users:
        await ctx.reply(4, tinycord.MessageCallback(
            content="You are not in the voice channel"
        ))

    volume = ctx.get_option("volume").value

    await lavalink.volume(ctx.guild_id, int(volume))

    await ctx.reply(4, tinycord.MessageCallback(
        content=f"Set the volume to {volume}"
    ))

@client.add("repeat", ["all"], "Reset the player")
async def repeat(ctx: "tinycord.Interaction") -> None:
    if ctx.guild.voice_server is None:
        await ctx.reply(4, tinycord.MessageCallback(
            content="I am not in a voice channel"
        ))

    if ctx.user not in ctx.guild.me.voice_state.channel.users:
        await ctx.reply(4, tinycord.MessageCallback(
            content="You are not in the voice channel"
        ))

    node = await lavalink.get_guild_node(ctx.guild_id)
    await node.repeat(ctx.guild_id, not node.repeat)

    await ctx.reply(4, tinycord.MessageCallback(
        content="Set the repeat to " + ("on" if node.repeat else "off")
    ))

@client.add("seek", ["all"], "Seek to a specific time")
@tinycord.interactions.add_option(
    tinycord.ApplicationCommandOption(
        name="time",
        description="The time to seek to",
        type=tinycord.ApplicationCommandOptionType.INTEGER,
        required=True
    )
)
async def seek(ctx: "tinycord.Interaction") -> None:
    if ctx.guild.voice_server is None:
        await ctx.reply(4, tinycord.MessageCallback(
            content="I am not in a voice channel"
        ))

    if ctx.user not in ctx.guild.me.voice_state.channel.users:
        await ctx.reply(4, tinycord.MessageCallback(
            content="You are not in the voice channel"
        ))

    await lavalink.seek(ctx.guild_id, int(ctx.get_option("time").value))

@client.add("shuffle", ["all"], "Shuffle the queue")
async def shuffle(ctx: "tinycord.Interaction") -> None:
    if ctx.guild.voice_server is None:
        await ctx.reply(4, tinycord.MessageCallback(
            content="I am not in a voice channel"
        ))

    if ctx.user not in ctx.guild.me.voice_state.channel.users:
        await ctx.reply(4, tinycord.MessageCallback(
            content="You are not in the voice channel"
        ))
    
    await lavalink.shuffle(ctx.guild_id)

    await ctx.reply(4, tinycord.MessageCallback(
        content="Shuffled the queue"
    ))

@client.add("now_playing", ["all"], "Show the current song")
async def nowplaying(ctx: "tinycord.Interaction") -> None:
    if ctx.guild.voice_server is None:
        await ctx.reply(4, tinycord.MessageCallback(
            content="I am not in a voice channel"
        ))

    node = await lavalink.get_guild_node(ctx.guild_id)
    # Get the current node

    if len(node.queue) == 0:
        await ctx.reply(4, tinycord.MessageCallback(
            content="I am not playing anything"
        ))

    song = node.queue[0]
    requester = ctx.guild.get_user(song.requester)

    embed = tinycord.Embed(
        description=f"[{song.title}]({song.uri})"
    )
    embed.set_footer(
        text=f"Requested by {ctx.user.username}"
    )
    embed.add_field(
        'Duration', 
        datetime.timedelta(seconds=song.length).__str__(), 
        inline=True
    )
    embed.add_field('Author', song.author, inline=True)
    embed.add_field('Requester', requester.username, inline=True)

    await ctx.reply(4, tinycord.MessageCallback(
        content="Now playing",
        embeds=[
            embed
        ]
    ))

lavalink.connect()
client.connect()
