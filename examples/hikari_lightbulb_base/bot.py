import lightbulb
import hikari
import lavaplayer
import logging
import os
import asyncio

SLASH_COMMAND = True  # if you want to use slash command, set True
PREFIX = "!"  # prefix for commands


class Bot(lightbulb.BotApp):
    def __init__(self, token: str, prefix: str) -> None:
        super().__init__(token, prefix=prefix)
        self.lavalink: lavaplayer.LavalinkClient = None
    
    # On shard ready the bot will connect to the lavalink node
    async def start_lavalink(self, event: hikari.ShardReadyEvent):
        self.lavalink = lavaplayer.LavalinkClient(
            host="localhost",  # Lavalink host
            port=2333,  # Lavalink port
            password="youshallnotpass",  # Lavalink password
            bot_id=self.get_me().id,  # Lavalink bot id
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


    def run(self):
        # discord gateway events listener
        self.event_manager.subscribe(hikari.ShardReadyEvent, self.start_lavalink)
        self.event_manager.subscribe(hikari.VoiceStateUpdateEvent, self.voice_state_update)
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

# bot client
bot = Bot(os.environ["TOKEN"], PREFIX)

implements = [lightbulb.commands.PrefixCommand] if not SLASH_COMMAND else [lightbulb.commands.PrefixCommand, lightbulb.commands.SlashCommand]

# Commands
# ------------------------------------- #
@bot.command()
@lightbulb.command(name="join", description="join voice channel")
@lightbulb.implements(*implements)
async def join_command(ctx: lightbulb.context.Context):
    states = bot.cache.get_voice_states_view_for_guild(ctx.guild_id)
    voice_state = [state async for state in states.iterator().filter(lambda i: i.user_id == ctx.author.id)]
    if not voice_state:
        await ctx.respond("you are not in a voice channel")
        return
    channel_id = voice_state[0].channel_id
    await bot.update_voice_state(ctx.guild_id, channel_id, self_deaf=True)
    await ctx.respond(f"done join to <#{channel_id}>")
    
@bot.command()
@lightbulb.option(name="query", description="query to search", required=True)
@lightbulb.command(name="play", description="Play command", aliases=["p"])
@lightbulb.implements(*implements)
async def play_command(ctx: lightbulb.context.Context):
    query = ctx.options.query  # get query from options
    result = await bot.lavalink.auto_search_tracks(query)  # search for the query
    if not result:
        await ctx.respond("not found result for your query")
        return
    await bot.lavalink.play(ctx.guild_id, result[0], ctx.author.id)  # play the first result
    await ctx.respond(f"[{result[0].title}]({result[0].uri})")  # send the embed
    
@bot.command()
@lightbulb.command(name="stop", description="Stop command", aliases=["s"])
@lightbulb.implements(*implements)
async def stop_command(ctx: lightbulb.context.Context):
    await bot.lavalink.stop(ctx.guild_id)
    await ctx.respond("done stop the music")


@bot.command()
@lightbulb.command(name="pause", description="Pause command")
@lightbulb.implements(*implements)
async def stop_command(ctx: lightbulb.context.Context):
    await bot.lavalink.pause(ctx.guild_id, True)
    await ctx.respond("The music is paused now")


@bot.command()
@lightbulb.command(name="resume", description="Resume command")
@lightbulb.implements(*implements)
async def stop_command(ctx: lightbulb.context.Context):
    await bot.lavalink.pause(ctx.guild_id, False)
    await ctx.respond("The music is resumed now")


@bot.command()
@lightbulb.option(name="position", description="Position to seek", required=True)
@lightbulb.command(name="seek", description="Seek command")
@lightbulb.implements(*implements)
async def seek_command(ctx: lightbulb.context.Context):
    position = ctx.options.position
    await bot.lavalink.seek(ctx.guild_id, position)
    await ctx.respond(f"done seek to {position}")


@bot.command()
@lightbulb.option(name="vol", description="Volume to set", required=True)
@lightbulb.command(name="volume", description="Volume command")
@lightbulb.implements(*implements)
async def volume_command(ctx: lightbulb.context.Context):
    volume = ctx.options.vol
    await bot.lavalink.volume(ctx.guild_id, volume)
    await ctx.respond(f"done set volume to {volume}%")

@bot.command()
@lightbulb.command(name="destroy", description="Destroy command")
@lightbulb.implements(*implements)
async def destroy_command(ctx: lightbulb.context.Context):
    await bot.lavalink.destroy(ctx.guild_id)
    await ctx.respond("done destroy the bot")

@bot.command()
@lightbulb.command(name="queue", description="Queue command")
@lightbulb.implements(*implements)
async def queue_command(ctx: lightbulb.context.Context):
    node = await bot.lavalink.get_guild_node(ctx.guild_id)
    embed = hikari.Embed(
        description="\n".join(
            [f"{n+1}- [{i.title}]({i.uri})" for n, i in enumerate(node.queue)])
    )
    await ctx.respond(embed=embed)

@bot.command()
@lightbulb.command(name="np", description="Now playing command")
@lightbulb.implements(*implements)
async def np_command(ctx: lightbulb.context.Context):
    node = await bot.lavalink.get_guild_node(ctx.guild_id)
    if not node.queue:
        await ctx.respond("nothing playing")
        return
    await ctx.respond(f"[{node.queue[0].title}]({node.queue[0].uri})")

@bot.command()
@lightbulb.command(name="repeat", description="Repeat command")
@lightbulb.implements(*implements)
async def repeat_command(ctx: lightbulb.context.Context):
    node = await bot.lavalink.get_guild_node(ctx.guild_id)
    stats = False if node.repeat else True
    await bot.lavalink.repeat(ctx.guild_id, stats)
    if stats:
        await ctx.respond("done repeat the music")
        return
    await ctx.respond("done stop repeat the music")

@bot.command()
@lightbulb.command(name="shuffle", description="Shuffle command")
@lightbulb.implements(*implements)
async def shuffle_command(ctx: lightbulb.context.Context):
    await bot.lavalink.shuffle(ctx.guild_id)
    await ctx.respond("done shuffle the music")

@bot.command()
@lightbulb.command(name="leave", description="Leave command")
@lightbulb.implements(*implements)
async def leave_command(ctx: lightbulb.context.Context):
    await bot.update_voice_state(ctx.guild_id, None)
    await ctx.respond("done leave the voice channel")
# ------------------------------------- #


if __name__ == "__main__":
    if os.name != "nt":
        import uvloop
        uvloop.install()
    bot.run()
