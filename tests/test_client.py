import pytest
import lavaplayer
from lavaplayer import Track
from lavaplayer.objects import Node

TEST_TRACK = Track(
    "QAAAhQIAClV3dSB2b2ljZSkAIU5vdEFlc3RoZXRpY2FsbHlIYW5uYWggaGlnaGxpZ2h0cwAAAAAAAGGoAAt4anJVM044TTRlbwABACtodHRwczovL3d3dy55b3V0dWJlLmNvbS93YXRjaD92PXhqclUzTjhNNGVvAAd5b3V0dWJlAAAAAAAAAAA=", 
    "xjrU3N8M4eo", False, "uwu", 12, False, 0, "uwu voice", "https://youtu.be/xjrU3N8M4eo", 123, "youtube", None)
client = lavaplayer.Lavalink(
    host="127.0.0.1",
    port=2333,
    password="youshallnotpass",
    user_id=123456789,
    num_shards=1,
    is_ssl=False,
)


def test_host():
    assert client.host is not None

def test_port():
    assert client.port is not None

def test_password():
    assert client.password is not None

def test_user_id():
    assert client.user_id is not None

def test_num_shards():
    assert client.num_shards is not None

def test_is_ssl():
    assert client.is_ssl is not None

@pytest.mark.asyncio
async def test_create_new_node():
    await client.create_new_node(123)
    assert client.nodes is not None

@pytest.mark.asyncio
async def test_get_guild_node():
    await client.create_new_node(123)
    assert (await client.get_guild_node(123)) is not None

@pytest.mark.asyncio
async def test_remove_guild_node():
    await client.create_new_node(123)
    await client.remove_guild_node(123)
    assert (await client.get_guild_node(123)) is None

@pytest.mark.asyncio
async def test_set_guild_node():
    await client.create_new_node(123)
    new_node = Node(123, [], 100)
    await client.set_guild_node(123, new_node)
    assert (await client.get_guild_node(123)) is not None

@pytest.mark.asyncio
async def test_remove():
    node = await client.create_new_node(123)
    node.queue.append(TEST_TRACK)
    await client.remove(123, 0)
    assert (await client.get_guild_node(123)).queue is not None

@pytest.mark.asyncio
async def test_index():
    node = await client.create_new_node(123)
    node.queue.append(TEST_TRACK)
    assert (await client.index(123, 0)) is not None

def test_nodes():
    assert client.nodes is not None
