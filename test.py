import asyncio
import lavaplayer
import hikari
import logging

client = hikari.GatewayBot(token="")  # set your token
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
    if event.message.content == "join":
        states = client.cache.get_voice_states_view_for_guild(event.guild_id)
        voice_state = [state async for state in states.iterator().filter(lambda i: i.user_id == event.author_id)]
        channel_id = voice_state[0].channel_id
        await client.update_voice_state(event.guild_id, channel_id, self_deaf=True)

    elif event.message.content == "play":
        result = await lavalink.get_tracks("https://youtu.be/BJUNK3eJDoM")
        await lavalink.play(event.guild_id, result[0])


@lavalink.listner(lavaplayer.TrackStartEvent)
async def track_start_event(event: lavaplayer.TrackStartEvent):
    print(event.track.title)

client.run()


