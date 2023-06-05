import discord
import lavaplay


class LavalinkVoiceClient(discord.VoiceClient):
    """
    A voice client for Lavalink.
    https://discordpy.readthedocs.io/en/latest/api.html#voiceprotocol
    """
    def __init__(self, client: discord.Client, channel: discord.abc.Connectable):
        self.client = client
        self.channel = channel
        self.lavalink: lavaplay.Node = self.client.lavalink

    async def on_voice_server_update(self, data):
        player = self.lavalink.get_player(self.channel.guild.id)
        await player.raw_voice_server_update(data['endpoint'], data['token'])

    async def on_voice_state_update(self, data):
        player = self.lavalink.get_player(self.channel.guild.id)
        await player.raw_voice_state_update(int(data['user_id']), data['session_id'], int(data['channel_id']))

    async def connect(self, *, timeout: float, reconnect: bool, self_deaf: bool = False, self_mute: bool = False) -> None:
        self.player = self.lavalink.create_player(self.channel.guild.id)
        await self.channel.guild.change_voice_state(channel=self.channel, self_mute=self_mute, self_deaf=self_deaf)

    async def disconnect(self, *, force: bool = False) -> None:
        player = self.lavalink.get_player(self.channel.guild.id)
        if not force and not player.is_connected:
            return
        await self.channel.guild.change_voice_state(channel=None)
        player.channel_id = None
        self.cleanup()
