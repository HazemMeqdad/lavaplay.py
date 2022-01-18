import asyncio
import lavaplayer
import hikari
import logging
import os

class Bot(hikari.GatewayBot):
    def __init__(self, token: str) -> None:
        super().__init__(token)

    # On shard ready the bot will connect to the lavalink node
    async def start_lavalink(self, event: hikari.ShardReadyEvent):
        self.lavalink = lavaplayer.LavalinkClient(
            host="localhost",  # Lavalink host
            port=2333,  # Lavalink port
            password="youshallnotpass",  # Lavalink password
            bot_id=123,  # Lavalink bot id
        )
        await self.lavalink.connect()
        
        # add lavalink events listener
        self.lavalink.event_manger.add_listner(lavaplayer.TrackEndEvent, track_end_event)
        self.lavalink.event_manger.add_listner(lavaplayer.TrackStartEvent, track_start_event)
        self.lavalink.event_manger.add_listner(lavaplayer.WebSocketClosedEvent, web_soket_closed_event)

    # On voice state update the bot will update the lavalink node
    async def voice_state_update(self, v: hikari.VoiceStateUpdateEvent):
        try:
            event: hikari.VoiceServerUpdateEvent = await bot.wait_for(hikari.VoiceServerUpdateEvent, timeout=30)
        except asyncio.TimeoutError:
            return
        await self.lavalink.voice_update(v.guild_id, v.state.session_id, event.token, event.raw_endpoint, v.state.channel_id)

    # On message create the bot will play the audio and other commands
    async def message_create(self, event: hikari.GuildMessageCreateEvent):
        if not event.message.content:
            return
        if event.message.content == "!join":
            states = self.cache.get_voice_states_view_for_guild(event.guild_id)
            voice_state = [state async for state in states.iterator().filter(lambda i: i.user_id == event.author_id)]
            channel_id = voice_state[0].channel_id
            await self.update_voice_state(event.guild_id, channel_id, self_deaf=True)
            embed = hikari.Embed(
                description=f"done join to <#{channel_id}>"
            )
            await self.rest.create_message(event.get_channel(), embed=embed)

        elif event.message.content.startswith("!play"):
            result = await self.lavalink.auto_search_tracks(event.message.content.replace("!play ", ""))
            await self.lavalink.play(event.guild_id, result[0], event.author_id)
            embed = hikari.Embed(
                description=f"[{result[0].title}]({result[0].uri})"
            )
            await self.rest.create_message(event.get_channel(), embed=embed)

        elif event.message.content == "!stop":
            await self.lavalink.stop(event.guild_id)
            embed = hikari.Embed(
                description="stoped"
            )
            await self.rest.create_message(event.get_channel(), embed=embed)

        elif event.message.content == "!pause":
            await self.lavalink.pause(event.guild_id, True)
            embed = hikari.Embed(
                description="paused"
            )
            await self.rest.create_message(event.get_channel(), embed=embed)

        elif event.message.content == "!resume":
            await self.lavalink.pause(event.guild_id, False)
            embed = hikari.Embed(
                description="resumed"
            )
            await self.rest.create_message(event.get_channel(), embed=embed)

        elif event.message.content == "!seek":
            try:
                position = int(event.message.content.split(" ")[1])
            except IndexError:
                await self.rest.create_message(event.get_channel(), "please enter a position")
            except ValueError:
                await self.rest.create_message(event.get_channel(), "please enter a number")

            await self.lavalink.seek(event.guild_id, position)
            embed = hikari.Embed(
                description="seeked"
            )
            await self.rest.create_message(event.get_channel(), embed=embed)

        elif event.message.content.startswith("!volume"):
            vol = event.message.content.split(" ")[1]
            await self.lavalink.volume(event.guild_id, int(vol))
            embed = hikari.Embed(
                description=f"volume choose to {vol}%"
            )
            await self.rest.create_message(event.get_channel(), embed=embed)

        elif event.message.content == "!destroy":
            await self.lavalink.destroy(event.guild_id)
            embed = hikari.Embed(
                description="destroy"
            )
            await self.rest.create_message(event.get_channel(), embed=embed)

        elif event.message.content == "!quene":
            node = await self.lavalink.get_guild_node(event.guild_id)
            embed = hikari.Embed(
                description="\n".join(
                    [f"{n+1}- [{i.title}]({i.uri})" for n, i in enumerate(node.queue)])
            )
            await self.rest.create_message(event.get_channel(), embed=embed)

        elif event.message.content == "!repeat":
            node = await self.lavalink.get_guild_node(event.guild_id)
            await self.lavalink.repeat(event.guild_id, True)

        elif event.message.content == "!filter":
            filters = lavaplayer.Filters()
            filters.lowPass(50)
            await self.lavalink.filters(event.guild_id, filters)

        elif event.message.content == "!help":
            embed = hikari.Embed(
                description="!join, !play <query>, !stop, !pause, !resume, !seek, !volume, !destroy, !quene, !repeat"
            )
            await self.rest.create_message(event.get_channel(), embed=embed)

    def run(self):
        # discord gateway events listener
        self.event_manager.subscribe(hikari.ShardReadyEvent, self.start_lavalink)
        self.event_manager.subscribe(hikari.VoiceStateUpdateEvent, self.voice_state_update)
        self.event_manager.subscribe(hikari.GuildMessageCreateEvent, self.message_create)
        super().run()

# -------------------------------- #
# track start event
async def track_start_event(event: lavaplayer.TrackStartEvent):
    logging.info(f"start track: {event.track.title}")

# track end event
async def track_end_event(event: lavaplayer.TrackEndEvent):
    logging.info(f"track end: {event.track.title}")

# web socket closed event
async def web_soket_closed_event(event: lavaplayer.WebSocketClosedEvent):
    logging.error(f"error with websoket {event.reason}")
# -------------------------------- #


if __name__ == "__main__":
    if os.name != "nt":
        import uvloop

        uvloop.install()
    bot = Bot(os.environ["TOKEN"])
    bot.run()
