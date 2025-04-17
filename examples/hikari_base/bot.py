import lavaplay
import hikari
import logging
import os


PREFIX = ","  # Replace with your prefix
TOKEN = os.environ["TOKEN"]  # Replace with your token

class Bot(hikari.GatewayBot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._lavalink: lavaplay.Node = None

    @property
    def lavalink(self) -> lavaplay.Node:
        return self._lavalink

    async def on_start(self, event: hikari.StartedEvent):
        lava = lavaplay.Lavalink()
        self._lavalink = lava.create_node(
            host="localhost",  # Lavalink host
            port=2333,  # Lavalink port
            password="youshallnotpass",  # Lavalink password
            user_id=self.get_me().id,  # Your bot user id
        )
        self.lavalink.connect()
        self.lavalink.event_manager.add_listener(lavaplay.ReadyEvent, self.on_lava_ready)
        self.lavalink.event_manager.add_listener(lavaplay.TrackStartEvent, self.track_start_event)
        self.lavalink.event_manager.add_listener(lavaplay.TrackEndEvent, self.track_end_event)
        self.lavalink.event_manager.add_listener(lavaplay.WebSocketClosedEvent, self.web_socket_closed_event)

    def run(self):
        self.event_manager.subscribe(hikari.StartedEvent, self.on_start)
        super().run()
    # -------------------------------- #
    # Lavalink events
    async def on_lava_ready(self, event: lavaplay.ReadyEvent):
        logging.info(event)
        logging.info("Lavalink is connected successfully!")

    # track start event
    async def track_start_event(event: lavaplay.TrackStartEvent):
        logging.info(f"start track: {event.track.title}")


    # track end event
    async def track_end_event(event: lavaplay.TrackEndEvent):
        logging.info(f"track end: {event.track.title}")


    # web socket closed event
    async def web_socket_closed_event(event: lavaplay.WebSocketClosedEvent):
        logging.error(f"error with websocket {event.reason}")
    # -------------------------------- #


bot = Bot(TOKEN, intents=hikari.Intents.ALL)

# https://github.com/vicky5124/lavasnek_rs/blob/master/examples/pure_hikari_basic_queue/bot.py#L16
def is_command(cmd_name: str, content: str) -> bool:
    """Check if the message sent is a valid command."""
    return content.startswith(f"{PREFIX}{cmd_name}")

# On voice state update the bot will update the lavalink node
@bot.listen(hikari.VoiceStateUpdateEvent)
async def voice_state_update(event: hikari.VoiceStateUpdateEvent):
    player = bot.lavalink.get_player(event.guild_id)
    await player.raw_voice_state_update(event.state.user_id, event.state.session_id, event.state.channel_id)

@bot.listen(hikari.VoiceServerUpdateEvent)
async def voice_server_update(event: hikari.VoiceServerUpdateEvent):
    player = bot.lavalink.get_player(event.guild_id)
    await player.raw_voice_server_update(event.endpoint, event.token)

# On message create the bot will play the audio and other commands
@bot.listen(hikari.GuildMessageCreateEvent)
async def message_create(event: hikari.GuildMessageCreateEvent):

    if not event.message.content:
        return
    lavalink = bot.lavalink
    player = lavalink.get_player(event.guild_id)
    if is_command("join", event.content):
        state = bot.cache.get_voice_state(event.guild_id, event.author_id)
        if not state or not state.channel_id:
            await event.message.respond("You are not in a voice channel")
            return
        lavalink.create_player(event.guild_id)
        channel_id = state.channel_id
        await bot.update_voice_state(event.guild_id, channel_id, self_deaf=True)
        await event.message.respond(f"Joined <#{channel_id}>")

    elif is_command("leave", event.content):
        await bot.update_voice_state(event.guild_id, None)
        await player.destroy()
        await event.message.respond("The bot has left the voice channel")

    elif is_command("position", event.content):
        await event.message.respond(f"Position: {player.queue[0].position}s")

    elif is_command("play", event.content):
        result = await lavalink.auto_search_tracks(event.content.replace(f"{PREFIX}play ", ""))

        if not result:
            await event.message.respond("No results found.")
            return
        elif isinstance(result, lavaplay.TrackLoadFailed):
            await event.message.respond(f"Could not load track: {result.message}")
            return
        elif isinstance(result, lavaplay.PlayList):
            await player.add_to_queue(result.tracks, event.author_id)
            await player.play_playlist(result.tracks)
            await event.message.respond(f"Added playlist {result.name}")
            return
        await player.play(result[0], event.author_id)
        await event.message.respond(f"Now playing {result[0].title}")

    elif is_command("pause", event.content):
        await player.pause(True)
        await event.message.respond("The player has paused")

    elif is_command("resume", event.content):
        await player.pause(False)
        await event.message.respond("The player has resumed")
    
    elif is_command("stop", event.content):
        await player.stop()
        await event.message.respond("The player has stopped")

    elif is_command("skip", event.content):
        await player.skip()
        await event.message.respond("The player has skipped the current song")

    elif is_command("queue", event.content):
        await event.message.respond("\n".join([f"{i + 1}. {track.title}" for i, track in enumerate(player.queue)]))

    elif is_command("volume", event.content):
        volume = int(event.content.removeprefix(f"{PREFIX}volume "))
        await player.volume(volume)
        await event.message.respond(f"The player has set the volume to {volume}")

    elif is_command("np", event.content):
        if not player.queue:
            await event.message.respond("Nothing playing.")
            return
        await event.message.respond(f"Now playing {player.queue[0].title}")

    elif is_command("shuffle", event.content):
        player.shuffle()
        await event.message.respond("The bot has shuffled the queue")
    
    elif is_command("repeat", event.content):
        player.repeat(True)
        await event.message.respond("The bot has set the queue to repeat")
    
    elif is_command("norepeat", event.content):
        player.repeat(False)
        await event.message.respond("The player has set the queue to not repeat")

    elif is_command("list_repeat", event.content):
        player.queue_repeat(True)
        await event.message.respond("The bot has set the queue to repeat")

    elif is_command("search", event.content):
        try:
            result = await lavalink.auto_search_tracks(event.conetnt.removeprefix(f"{PREFIX}search "))
        except lavaplay.TrackLoadFailed as exc:
            return await event.message.respond(f"Error loading track: {exc}") 
        if not result:
            await event.message.respond("No results found.")
            return
        if isinstance(result, lavaplay.PlayList):
            await event.message.respond(f"Playlist {result.name}")
            return
        await event.message.respond(f"{result[0].title}")

    elif is_command("seek", event.content):
        try:
            position = int(event.message.content.split(" ")[1])
        except IndexError:
            await event.message.respond("Please specify a position.")
            return
        except ValueError:
            await event.message.respond("Please specify a valid position.")
            return

        await player.seek(position)
        await event.message.respond("The track has been seeked.")

    elif is_command("destroy", event.content):
        await player.destroy()
        await event.message.respond("The player has been destroyed.")

    elif is_command("filter", event.content):
        filters = lavaplay.Filters()
        filters.low_pass(50)
        await player.filters(filters)

    elif is_command("help", event.content):
        commands = [
            "join", "leave", "play", "pause",
            "resume", "stop", "skip", "queue",
            "volume", "np", "shuffle", "repeat",
            "norepeat", "search", "seek", "destroy",
            "filter", "list_repeat"
        ]
        await event.message.respond(", ".join([f"`{PREFIX}{command}`" for command in commands]))

if __name__ == "__main__":
    if os.name != "nt":
        import uvloop

        uvloop.install()
    bot.run()
