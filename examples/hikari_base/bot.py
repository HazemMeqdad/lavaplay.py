import lavaplayer
import hikari
import logging
import os


TOKEN = "..."  # Replace with your token

bot = hikari.GatewayBot(TOKEN)
lavalink = lavaplayer.LavalinkClient(
    host="localhost",  # Lavalink host
    port=2333,  # Lavalink port
    password="youshallnotpass",  # Lavalink password
    user_id=123,  # Lavalink bot id
)


# On voice state update the bot will update the lavalink node
@bot.listen(hikari.VoiceStateUpdateEvent)
async def voice_state_update(event: hikari.VoiceStateUpdateEvent):
    await lavalink.raw_voice_state_update(event.guild_id, event.state.user_id, event.state.session_id, event.state.channel_id)

@bot.listen(hikari.VoiceServerUpdateEvent)
async def voice_server_update(event: hikari.VoiceServerUpdateEvent):
    await lavalink.raw_voice_server_update(event.guild_id, event.endpoint, event.token)

# On message create the bot will play the audio and other commands
@bot.listen(hikari.GuildMessageCreateEvent)
async def message_create(event: hikari.GuildMessageCreateEvent):
    if not event.message.content:
        return
    if event.message.content == "!join":
        states = bot.cache.get_voice_states_view_for_guild(event.guild_id)
        voice_state = [state async for state in states.iterator().filter(lambda i: i.user_id == event.author_id)]
        channel_id = voice_state[0].channel_id
        await bot.update_voice_state(event.guild_id, channel_id, self_deaf=True)
        embed = hikari.Embed(
            description=f"done join to <#{channel_id}>"
        )
        await bot.rest.create_message(event.get_channel(), embed=embed)

    elif event.message.content.startswith("!play"):
        result = await lavalink.auto_search_tracks(event.message.content.replace("!play ", ""))
        await lavalink.play(event.guild_id, result[0], event.author_id)
        embed = hikari.Embed(
            description=f"[{result[0].title}]({result[0].uri})"
        )
        await bot.rest.create_message(event.get_channel(), embed=embed)

    elif event.message.content == "!stop":
        await lavalink.stop(event.guild_id)
        embed = hikari.Embed(
            description="stoped"
        )
        await bot.rest.create_message(event.get_channel(), embed=embed)

    elif event.message.content == "!pause":
        await lavalink.pause(event.guild_id, True)
        embed = hikari.Embed(
            description="paused"
        )
        await bot.rest.create_message(event.get_channel(), embed=embed)

    elif event.message.content == "!resume":
        await lavalink.pause(event.guild_id, False)
        embed = hikari.Embed(
            description="resumed"
        )
        await bot.rest.create_message(event.get_channel(), embed=embed)

    elif event.message.content == "!seek":
        try:
            position = int(event.message.content.split(" ")[1])
        except IndexError:
            await bot.rest.create_message(event.get_channel(), "please enter a position")
            return
        except ValueError:
            await bot.rest.create_message(event.get_channel(), "please enter a number")
            return

        await lavalink.seek(event.guild_id, position)
        embed = hikari.Embed(
            description="seeked"
        )
        await bot.rest.create_message(event.get_channel(), embed=embed)

    elif event.message.content.startswith("!volume"):
        try:
            vol = int(event.message.content.split(" ")[1])
        except IndexError:
            await bot.rest.create_message(event.get_channel(), "please enter a volume")
            return
        except ValueError:
            await bot.rest.create_message(event.get_channel(), "please enter a number")
            return
        await lavalink.volume(event.guild_id, vol)
        embed = hikari.Embed(
            description=f"volume choose to {vol}%"
        )
        await bot.rest.create_message(event.get_channel(), embed=embed)

    elif event.message.content == "!destroy":
        await lavalink.destroy(event.guild_id)
        embed = hikari.Embed(
            description="destroy"
        )
        await bot.rest.create_message(event.get_channel(), embed=embed)

    elif event.message.content == "!queue":
        node = await lavalink.get_guild_node(event.guild_id)
        embed = hikari.Embed(
            description="\n".join(
                [f"{n+1}- [{i.title}]({i.uri})" for n, i in enumerate(node.queue)])
        )
        await bot.rest.create_message(event.get_channel(), embed=embed)

    elif event.message.content == "!repeat":
        node = await lavalink.get_guild_node(event.guild_id)
        await lavalink.repeat(event.guild_id, True)

    elif event.message.content == "!filter":
        filters = lavaplayer.Filters()
        filters.lowPass(50)
        await lavalink.filters(event.guild_id, filters)

    elif event.message.content == "!help":
        embed = hikari.Embed(
            description="!join, !play <query>, !stop, !pause, !resume, !seek, !volume, !destroy, !queue, !repeat"
        )
        await bot.rest.create_message(event.get_channel(), embed=embed)


# -------------------------------- #
# track start event
@lavalink.listen(lavaplayer.TrackStartEvent)
async def track_start_event(event: lavaplayer.TrackStartEvent):
    logging.info(f"start track: {event.track.title}")


# track end event
@lavalink.listen(lavaplayer.TrackEndEvent)
async def track_end_event(event: lavaplayer.TrackEndEvent):
    logging.info(f"track end: {event.track.title}")


# web socket closed event
@lavalink.listen(lavaplayer.WebSocketClosedEvent)
async def web_socket_closed_event(event: lavaplayer.WebSocketClosedEvent):
    logging.error(f"error with websocket {event.reason}")
# -------------------------------- #


if __name__ == "__main__":
    if os.name != "nt":
        import uvloop

        uvloop.install()
    lavalink.connect()
    bot.run()
