<h1 align="center">
    <b>
        <a href="https://github.com/HazemMeqdad/lavaplay.py">
            lavaplay.py
        </a>
    </b>
</h1>


<p align="center">
    <a href="https://discord.gg/VcWRRphVQB">Support Guild</a> |
    <a href="https://github.com/HazemMeqdad/lavaplay.py/tree/main/examples">Examples</a> |
    <a href="https://lavaplay.readthedocs.io/en/latest/">Documentation</a> |
    <a href="https://github.com/HazemMeqdad/lavaplay.py">Source</a>
</p>

<br>

Its a lavalink nodes manger to make a music bots for discord with python.


# About

lavaplay.py is a nodes manager to connection with discord voice gateway, easy to create a music bot, you can use to anything async discord wrapper library

# Usage

example for create connecting with lavalink server using [hikari](https://github.com/hikari-py/hikari).

```python
import hikari
import lavaplay

bot = hikari.GatewayBot("token")

lavalink = lavaplay.Lavalink()
node = lavalink.create_node(
    host="localhost",
    port=2333,
    password="youshallnotpass",
    user_id=123
)

@bot.listen()
async def on_ready(event: hikari.ShardReadyEvent) -> None:
    await node.connect()

bot.run()
```

examples for some methods.
```python
# Auto search mix with track or query
await lavalink.auto_search_tracks("Rick Astley")

# Play track
await lavalink.play(guild_id, track)

# Skip
await lavalink.skip(guild_id)

# Pause
await lavalink.pause(guild_id, stats)

# Volume
await lavalink.volume(guild_id, volume)
```

# Features

- [ ] Spotify support
- [x] connection handler
- [x] Support youtube playlist
- [x] Add example for other discord wrapper library

# Installation

```shell
# Linux/OS X
$ pip3 install -U lavaplay.py

# Windows
$ pip install -U lavaplay.py
```
