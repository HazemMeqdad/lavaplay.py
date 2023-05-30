import asyncio
import lavaplay
import hikari
import logging
import os


PREFIX = ","  # Replace with your prefix
TOKEN = "..."  # Replace with your token

bot = hikari.GatewayBot(TOKEN)
lavalink = lavaplay.LavalinkClient(
    host="localhost",  # Lavalink host
    port=2333,  # Lavalink port
    password="youshallnotpass",  # Lavalink password
)

@bot.listen(hikari.StartedEvent)
async def on_start(event: hikari.StartedEvent):
    lavalink.set_user_id(bot.get_me().id)
    lavalink.set_event_loop(asyncio.get_event_loop())
    lavalink.connect()

# https://github.com/vicky5124/lavasnek_rs/blob/master/examples/pure_hikari_basic_queue/bot.py#L16
def is_command(cmd_name: str, content: str) -> bool:
    """Check if the message sent is a valid command."""
    return content.startswith(f"{PREFIX}{cmd_name}")

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

    if is_command("join", event.content):
        states = bot.cache.get_voice_states_view_for_guild(event.guild_id)
        voice_state = [state async for state in states.iterator().filter(lambda i: i.user_id == event.author_id)]
        channel_id = voice_state[0].channel_id
        await bot.update_voice_state(event.guild_id, channel_id, self_deaf=True)
        await lavalink.wait_for_connection(event.guild_id)
        await event.message.respond(f"Joined <#{channel_id}>")

    elif is_command("leave", event.content):
        await bot.update_voice_state(event.guild_id, None)
        await event.message.respond("The bot has left the voice channel")

    elif is_command("position", event.content):
        node = await lavalink.get_guild_node(event.guild_id)
        await event.message.respond(f"Position: {node.queue[0].position}s")

    elif is_command("play", event.content):
        print(event.content.replace(f"{PREFIX}play ", ""))
        result = await lavalink.auto_search_tracks(event.content.replace(f"{PREFIX}play ", ""))

        if not result:
            await event.message.respond("No results found.")
            return
        elif isinstance(result, lavaplay.TrackLoadFailed):
            await event.message.respond(f"Could not load track: {result.message}")
            return
        elif isinstance(result, lavaplay.PlayList):
            await lavalink.add_to_queue(event.guild_id, result.tracks, event.author_id)
            await event.message.respond(f"Added playlist {result.name}")
            return
        await lavalink.play(event.guild_id, result[0], event.author_id)
        await event.message.respond(f"Now playing {result[0].title}")

    elif is_command("pause", event.content):
        await lavalink.pause(event.guild_id, True)
        await event.message.respond("The player has paused")

    elif is_command("resume", event.content):
        await lavalink.pause(event.guild_id, False)
        await event.message.respond("The player has resumed")
    
    elif is_command("stop", event.content):
        await lavalink.stop(event.guild_id)
        await event.message.respond("The player has stopped")

    elif is_command("skip", event.content):
        await lavalink.skip(event.guild_id)
        await event.message.respond("The player has skipped the current song")

    elif is_command("queue", event.content):
        queue = await lavalink.queue(event.guild_id)
        await event.message.respond("\n".join([f"{i + 1}. {track.title}" for i, track in enumerate(queue)]))

    elif is_command("volume", event.content):
        volume = int(event.content.removeprefix(f"{PREFIX}volume "))
        await lavalink.volume(event.guild_id, volume)
        await event.message.respond(f"The player has set the volume to {volume}")

    elif is_command("np", event.content):
        queue = await lavalink.queue(event.guild_id)
        if not queue:
            await event.message.respond("Nothing playing.")
            return
        await event.message.respond(f"Now playing {queue[0].title}")

    elif is_command("shuffle", event.content):
        await lavalink.shuffle(event.guild_id)
        await event.message.respond("The bot has shuffled the queue")
    
    elif is_command("repeat", event.content):
        await lavalink.repeat(event.guild_id, True)
        await event.message.respond("The bot has set the queue to repeat")
    
    elif is_command("norepeat", event.content):
        await lavalink.repeat(event.guild_id, False)
        await event.message.respond("The player has set the queue to not repeat")

    elif is_command("list_repeat", event.content):
        await lavalink.queue_repeat(event.guild_id, True)
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

        await lavalink.seek(event.guild_id, position)
        await event.message.respond("The track has been seeked.")

    elif is_command("destroy", event.content):
        await lavalink.destroy(event.guild_id)
        await event.message.respond("The player has been destroyed.")

    elif is_command("filter", event.content):
        filters = lavaplay.Filters()
        filters.low_pass(50)
        await lavalink.filters(event.guild_id, filters)

    elif is_command("help", event.content):
        commands = [
            "join", "leave", "play", "pause",
            "resume", "stop", "skip", "queue",
            "volume", "np", "shuffle", "repeat",
            "norepeat", "search", "seek", "destroy",
            "filter", "list_repeat"
        ]
        await event.message.respond(", ".join([f"`{PREFIX}{command}`" for command in commands]))

# -------------------------------- #
# track start event
@lavalink.listen(lavaplay.TrackStartEvent)
async def track_start_event(event: lavaplay.TrackStartEvent):
    logging.info(f"start track: {event.track.title}")


# track end event
@lavalink.listen(lavaplay.TrackEndEvent)
async def track_end_event(event: lavaplay.TrackEndEvent):
    logging.info(f"track end: {event.track.title}")


# web socket closed event
@lavalink.listen(lavaplay.WebSocketClosedEvent)
async def web_socket_closed_event(event: lavaplay.WebSocketClosedEvent):
    logging.error(f"error with websocket {event.reason}")
# -------------------------------- #


if __name__ == "__main__":
    if os.name != "nt":
        import uvloop

        uvloop.install()
    bot.run()
