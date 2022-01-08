.. _getting-started:

===============
Getting Started
===============

The lavaplayer package is designed to be used with the lavalink server

Lavaplayer can be installed using the following command:

windows: ``pip install lavaplayer``

MacOS/Linux: ``pip3 install lavaplayer``

and need to install `java 11 <https://www.oracle.com/java/technologies/javase/jdk11-archive-downloads.html>`_ * 
LTS or newer required. and create a `application.yml <https://github.com/freyacodes/Lavalink/blob/master/LavalinkServer/application.yml.example>`_ file in the root of your project.

and choice the port and address of the server.

run the server use this command: ``java -jar Lavalink.jar``

and install lasted `lavalink.jar <https://github.com/freyacodes/Lavalink/releases/download/3.4/Lavalink.jar>`_ version

after installing, you can use the lavaplayer package in your code by importing it:

----

Create your custom music bot:
===============

Your first bot can be written in just a few lines of code:
:: 
    # importing the lavaplayer package
    import lavaplayer
    # import a discord client like: hikari, discord.py, etc...
    import hikari

    # create a hikari client to get a events
    bot = hikari.GatewayBot("...")

    # create a lavaplayer client
    lavalink = lavaplayer.LavalinkClient(
        host="localhost",  # your lavalink host
        port=2333,  # your lavalink port
        password="youshallnotpass",  # your lavalink password
        bot_id=123  # your bot id
    )

    # the started event is called when the client is ready
    @bot.listen(hikari.StartedEvent)
    async def started_event(event):
        # connect the lavaplayer client to the hikari client
        await lavalink.connect()

    # the message event is called when a message is sent
    @bot.listen(hikari.GuildMessageCreateEvent)
    async def message_event(event: hikari.GuildMessageCreateEvent):
        if not event.message:
            return

        # This command to connect to your voice channel
        if event.message.content == "!join":
            # get the voice channel
            states = bot.cache.get_voice_states_view_for_guild(event.guild_id)
            voice_state = [state async for state in states.iterator().filter(lambda i: i.user_id == event.author_id)]
            
            # check if the author is in a voice channel
            if not voice_state:
                await bot.rest.create_message(event.channel_id, "You are not in a voice channel")
                return 
            
            # connect to the voice channel
            channel_id = voice_state[0].channel_id
            await bot.update_voice_state(event.guild_id, channel_id, self_deaf=True)
            await bot.rest.create_message(event.get_channel(), f"Connected to <#{channel_id}>")

        # This command to play a song
        elif event.message.content.startswith("!play"):
            # get a query from the message
            query = event.message.content.replace("!play", "")

            # check if the query is empty
            if not query:
                await bot.rest.create_message(event.channel.id, "Please provide a track to play")
                return
            
            # Search for the query
            result = await lavalink.auto_search_tracks(query)
            
            # check if not found results
            if not result:
                await bot.rest.create_message(event.channel.id, "No results found")
                return

            # Play the first result
            await lavalink.play(event.guild_id, result[0], event.author_id)
            await bot.rest.create_message(event.channel.id, f"Playing {result[0].title}")


    # the voice_state_update event is called when a user changes voice channel
    @bot.listen(hikari.VoiceStateUpdateEvent)
    async def voice_state_update(v: hikari.VoiceStateUpdateEvent):
        try:
            event: hikari.VoiceServerUpdateEvent = await bot.wait_for(hikari.VoiceServerUpdateEvent, timeout=30)
        except :
            return
        # Update the lavaplayer client with the new voice server
        await lavalink.voice_update(v.guild_id, v.state.session_id, event.token, event.raw_endpoint)


    # run the bot
    bot.run()

When you run the bot, you can use the following commands to play music:

!join - Connects the bot to your voice channel

!play <query> - Play a song

you can create other commands to control the music player. this is some other `examples <https://github.com/HazemMeqdad/lavaplayer/tree/main/examples>`_

