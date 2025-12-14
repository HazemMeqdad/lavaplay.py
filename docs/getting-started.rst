.. _getting-started:

===============
Getting Started
===============

The lavaplay.py package is designed to be used with the lavalink server

.. note::
    Support lavalink server version 4.x.x or newer

lavaplay.py can be installed using the following command:

windows: ``pip install lavaplay.py``
MacOS/Linux: ``pip3 install lavaplay.py``

and need to install `java 17 <https://www.oracle.com/java/technologies/javase/jdk17-archive-downloads.html>`_ *
LTS or newer required. and create a `application.yml <https://github.com/lavalink-devs/Lavalink/blob/master/LavalinkServer/application.yml.example>`_ file in the root of your project.
and choice the port and address of the server.

run the server use this command: ``java -jar Lavalink.jar``

and install lasted `lavalink.jar <https://github.com/lavalink-devs/Lavalink/releases>`_ version

after installing, you can use the lavaplay.py package in your code by importing it:

----

Starter bot
===============

Your first bot can be written in just a few lines of code:
:: 
    # importing the lavaplay.py package
    import lavaplay
    # import a discord client like: hikari, discord.py, etc...
    import hikari

    # create a hikari client to get a events
    bot = hikari.GatewayBot(
        "...",
        intents=hikari.Intents.ALL
    )

    # create a lavaplay client
    lavalink = lavaplay.Lavalink()
    node = lavalink.create_node(
        host="localhost",  # your lavalink host
        port=2333,  # your lavalink port
        password="youshallnotpass",  # your lavalink password
        user_id=0  # Will change later on the started event
    )

    # the started event is called when the client is ready
    @bot.listen(hikari.StartedEvent)
    async def started_event(event):
        # change the bot user id
        node.user_id = bot.get_me().id  
        # connect the lavaplay client to the hikari client
        node.connect()

    # the message event is called when a message is sent
    @bot.listen(hikari.GuildMessageCreateEvent)
    async def message_event(event: hikari.GuildMessageCreateEvent):
        if not event.message:
            return

        # This command to connect to your voice channel
        if event.message.content == "!join":
            # get the voice channel
            state = bot.cache.get_voice_state(event.guild_id, event.author_id)
            # check if the author is in a voice channel
            if not state:
                await bot.rest.create_message(event.channel_id, "You are not in a voice channel")
                return 
            
            # connect to the voice channel
            channel_id = state.channel_id
            # create a player for the guild
            player = node.create_player(event.guild_id)
            await bot.update_voice_state(event.guild_id, channel_id, self_deaf=True)
            await bot.rest.create_message(event.get_channel(), f"Connected to <#{channel_id}>")

        # This command to play a song
        elif event.message.content.startswith("!play"):
            # get a query from the message
            query = event.message.content.replace("!play", "")

            # check if the query is empty
            if not query:
                await bot.rest.create_message(event.channel_id, "Please provide a track to play")
                return
            
            # Search for the query
            try:
                result = await node.auto_search_tracks(query)
            except lavaplay.TrackLoadFailed:   # check if not found results
                await bot.rest.create_message(event.channel_id, "Failed to load the track")
                return
            
            # Get the player
            player = node.get_player(event.guild_id)

            # Play the first result
            await player.play(result[0], event.author_id)
            await bot.rest.create_message(event.channel_id, f"Playing {result[0].title}")


    # the voice_state_update event is called when a user changes voice channel
    @bot.listen(hikari.VoiceStateUpdateEvent)
    async def voice_state_update(event: hikari.VoiceStateUpdateEvent):
        player = node.get_player(event.guild_id)
        # Update the voice state of the player
        await player.raw_voice_state_update(event.state.user_id, event.state.session_id, event.state.channel_id)

    # the voice_server_update event is called when a user changes voice channel
    @bot.listen(hikari.VoiceServerUpdateEvent)
    async def voice_server_update(event: hikari.VoiceServerUpdateEvent):
        player = node.get_player(event.guild_id)
        # Update the voice server information of the player
        await player.raw_voice_server_update(event.raw_endpoint, event.token)

    # run the bot
    bot.run()

When you run the bot, you can use the following commands to play music:

!join - Connects the bot to your voice channel

!play <query> - Play a song

you can create other commands to control the music player. this is some other `examples <https://github.com/HazemMeqdad/lavaplay.py/tree/main/examples>`_

