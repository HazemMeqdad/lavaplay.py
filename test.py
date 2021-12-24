from discord import channel
import lavaplayer
import hikari
import logging
import lightbulb

bot = hikari.GatewayBot(
    "ODkzMzg1MzUxMzYyNjcwNTkz.YVar8g.r5jJKskrVStHNq-hEjbmuBe-6bg",  # token
)

lavalink = lavaplayer.LavalinkClient(
    host="localhost",
    port=8888,
    password="password",
    bot_id=893385351362670593
)


@bot.listen(hikari.ShardReadyEvent)
async def on_shard_shard(event: hikari.ShardReadyEvent):
    await lavalink.connect()


@bot.listen(hikari.VoiceStateUpdateEvent)
async def voice_state_update(v: hikari.VoiceStateUpdateEvent):
    @bot.listen(hikari.VoiceServerUpdateEvent)
    async def voice_server_update(event: hikari.VoiceServerUpdateEvent) -> None:
        if not event.endpoint:
            logging.warning("Endpoint should never be None!")
            return
        await lavalink._ws.send({
            "op": "voiceUpdate",
            "guildId": str(v.state.guild_id),
            "sessionId": v.state.session_id,
            "event": {
                "token": event.token,
                "guild_id": str(event.guild_id),
                "endpoint": event.raw_endpoint,
            }
        })


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
        result = await lavalink.search_youtube(event.message.content.replace("!play ", ""))
        await lavalink.play(event.guild_id, result[0])
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
        await lavalink.seek(event.guild_id, 100)
        embed = hikari.Embed(
            description="seeked"
        )
        await bot.rest.create_message(event.get_channel(), embed=embed)

    elif event.message.content.startswith("!volume"):
        vol = event.message.content.split(" ")[1]
        await lavalink.volume(event.guild_id, int(vol))
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
    
    elif event.message.content == "!help":
        embed = hikari.Embed(
            description="!join, !play <query>, !stop, !pause, !resume, !seek, !volume, !destroy"
        )
        await bot.rest.create_message(event.get_channel(), embed=embed)

@lavalink.listner(lavaplayer.TrackStartEvent)
async def track_start_event(event: lavaplayer.TrackStartEvent):
    logging.info(f"start track: {event.track.title}")


@lavalink.listner(lavaplayer.TrackEndEvent)
async def track_end_event(event: lavaplayer.TrackEndEvent):
    logging.info(f"track end: {event.track.title}")


@lavalink.listner(lavaplayer.WebSocketClosedEvent)
async def web_soket_closed_event(event: lavaplayer.WebSocketClosedEvent):
    logging.error(f"error with websoket {event.reason}")

bot.run()
