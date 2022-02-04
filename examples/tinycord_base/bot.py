import tinycord
import lavaplayer

TOKEN = ""
client = tinycord.Client(
    token=TOKEN, 
    intents=tinycord.Intents.all()
)

lavalink = lavaplayer.LavalinkClient(
    host="127.0.0.1",
    port=8888,
    password="password",
    user_id=929021009665880174
)

@client.event
async def on_ready(shard):
    print(f"Shard {shard.id} ready.")

@client.event
async def on_voice_server_update(guild, data):
    if data["endpoint"] is not None:
        await lavalink.raw_voice_server_update(
             int(data['guild_id']), data['endpoint'], data['token'])

@client.event
async def on_voice_state_update(guild, before, after: tinycord.Voicestate):
    await lavalink.raw_voice_state_update(
        after.guild_id, after.user_id, after.session_id, after.channel_id)

@client.event
async def on_message(message: tinycord.Message):
    if message.content == '!join':

        if message.guild.me.voice_state is not None:
            return

        await message.author.voice_state.channel.connect()
        embed = tinycord.Embed(
            description=f"done join to <#{message.author.voice_state.channel_id}>"
        )
        await message.channel.send(embeds=[embed])
    
    if message.content == '!leave':
        if message.guild.me.voice_state is None:
            return
        await message.guild.me.voice_state.channel.disconnect()

        await lavalink.wait_for_remove_connection(message.guild.id)

        embed = tinycord.Embed(
            description=f"done leave from <#{message.author.voice_state.channel_id}>"
        )

        await message.channel.send(embeds=[embed])

    if message.content.startswith('!play'):
        track = await lavalink.auto_search_tracks(
            message.content.replace('!play', ''))

        await lavalink.play(message.guild_id, track[0], message.author.id)

        embed = tinycord.Embed(
            description=f"done play <{track[0].title}>"
        )

        await message.channel.send(embeds=[embed])

    if message.content.startswith('!pause'):
        await lavalink.pause(message.guild_id, True)

        embed = tinycord.Embed(
            description="done pause"
        )

        await message.channel.send(embeds=[embed])

    if message.content.startswith('!resume'):
        await lavalink.pause(message.guild_id, False)

        embed = tinycord.Embed(
            description="done resume"
        )

        await message.channel.send(embeds=[embed])

    if message.content.startswith('!stop'):
        await lavalink.stop(message.guild_id)

        embed = tinycord.Embed(
            description="done stop"
        )

        await message.channel.send(embeds=[embed])

    if message.content.startswith('!skip'):
        await lavalink.skip(message.guild_id)

        embed = tinycord.Embed(
            description="done skip"
        )

        await message.channel.send(embeds=[embed])

    if message.content.startswith('!queue'):
        queue = await lavalink.queue(message.guild_id)

        embed = tinycord.Embed(
                description="\n".join(
                    [f"{n+1}- [{i.title}]({i.uri})" for n, i in enumerate(queue)])
        )

        await message.channel.send(embeds=[embed])

    if message.content.startswith('!volume'):
        try:
            vol = int(message.content.split(" ")[1])
        except IndexError:
            return await message.channel.send("Please specify a volume")
        except ValueError:
            return await message.channel.send("Please specify a valid volume")

        await lavalink.volume(message.guild.id, vol)
        embed = tinycord.Embed(
            description=f"volume choose to {vol}%"
        )
        
        await message.channel.send(embeds=[embed])

    if message.content.startswith('!seek'):
        await lavalink.seek(message.guild.id, int(message.content.replace('!seek', '')))

        embed = tinycord.Embed(
            description=f"done seek {message.content.replace('!seek', '')}"
        )

        await message.channel.send(embeds=[embed])

    if message.content.startswith('!filter'):
        filters = lavaplayer.Filters()
        filters.lowPass(50)
        await lavalink.filters(message.guild_id, filters)


        embed = tinycord.Embed(
            description=f"done filter {message.content.replace('!filter', '')}"
        )

        await message.channel.send(embeds=[embed])

    if message.content.startswith('!repeat'):
        node = await lavalink.get_guild_node(message.guild_id)
        await node.repeat(message.guild_id, not node.repeat)

        embed = tinycord.Embed(
            description="done repeat"
        )

        await message.channel.send(embeds=[embed])
    
lavalink.connect()
client.connect()
