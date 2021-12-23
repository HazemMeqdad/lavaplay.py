import lavaplayer
import hikari
import logging
import lightbulb

client = hikari.GatewayBot(
    "ODkzMzg1MzUxMzYyNjcwNTkz.YVar8g.xG6XYpNSb7-uxTi6TTc5VndkOT4",
)  

lavalink = lavaplayer.LavalinkClient(
    host="localhost", 
    port=8888, 
    password="password", 
    bot_id=893385351362670593
)

@client.listen(hikari.ShardReadyEvent)
async def on_shard_shard(event: hikari.ShardReadyEvent):
    await lavalink.connect()


@client.listen(hikari.VoiceStateUpdateEvent)
async def voice_state_update(v: hikari.VoiceStateUpdateEvent):
    @client.listen(hikari.VoiceServerUpdateEvent)
    async def voice_server_update(event: hikari.VoiceServerUpdateEvent) -> None:
        if not event.endpoint:
            logging.warning("Endpoint should never be None!")
            return
        x = {
            "op": "voiceUpdate",
            "guildId": str(v.state.guild_id),
            "sessionId": v.state.session_id,
            "event": {
            "token": event.token,
            "endpoint": event.endpoint,
            "guild_id": event.guild_id
        }
        }
        await lavalink._ws.send(x)

@client.listen(hikari.GuildMessageCreateEvent)
async def message_create(event: hikari.GuildMessageCreateEvent):
    if event.message.content == "!join":
        states = client.cache.get_voice_states_view_for_guild(event.guild_id)
        voice_state = [state async for state in states.iterator().filter(lambda i: i.user_id == event.author_id)]
        channel_id = voice_state[0].channel_id
        await client.update_voice_state(event.guild_id, channel_id, self_deaf=True)

    elif event.message.content == "!play":
        result = await lavalink.search_youtube("بس عشانك")
        await lavalink.play(event.guild_id, result[0])
    
    elif event.message.content == "!stop":
        await lavalink.stop(event.guild_id)

    elif event.message.content == "!pause":
        stats = event.message.content.split(" ")[1]
        await lavalink.pause(event.guild_id, True if stats == "true" else False)
    
    elif event.message.content == "!seek":
        await lavalink.seek(event.guild_id, 100)
    
    elif event.message.content == "!volume":
        await lavalink.volume(event.guild_id, 10)
    
    elif event.message.content == "!destroy":
        await lavalink.destroy(event.guild_id)

@lavalink.listner(lavaplayer.TrackStartEvent)
async def track_start_event(event: lavaplayer.TrackStartEvent):
    logging.info(f"start track: {event.track.title}")

@lavalink.listner(lavaplayer.TrackEndEvent)
async def track_end_event(event: lavaplayer.TrackEndEvent):
    logging.info(f"track end: {event.track.title}")

@lavalink.listner(lavaplayer.WebSocketClosedEvent)
async def web_soket_closed_event(event: lavaplayer.WebSocketClosedEvent):
    logging.error(f"error with websoket {event.reason}")

client.run()


