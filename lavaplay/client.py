import typing as t
import logging
from .node_manager import Node
import asyncio

_LOG = logging.getLogger("lavaplay.client")

class Lavalink:
    """
    The main class for managing nodes.
    side note: to make connection must be use :meth:`Lavalink.create_node` or :meth:`Lavalink.destroy_node`.
    """
    def __init__(self) -> None:
        self._nodes: t.List[Node] = []

    def create_node(self, host: str, port: int, password: str, user_id: int, *, name: str = None, shard_count: int = None, ssl: bool = False, resume_key: str = None, resume_timeout: int = None, loop: t.Optional[asyncio.AbstractEventLoop] = None) -> Node:
        """
        Create a node for lavalink.

        Parameters
        ---------
        host: :class:`str`
            ip address for lavalink server, default ip address for lavalink is `
        port: :class:`int`
            The port to use for websocket and REST connections.
        password: :class:`str`
            The password used for authentication.
        name: :class:`str`
            The name for the node.
        shard_count: :class:`int`
            The shard count for the node.
        ssl: :class:`bool`
            Is server using ssl
        resume_key: :class:`str`
            The resume key for the node.
        resume_timeout: :class:`int`
            The resume timeout for the node.
        loop: :class:`asyncio.AbstractEventLoop`
            The event loop for the node.
        """
        node = Node(host=host, port=port, password=password, user_id=user_id, name=name, shard_count=shard_count, resume_key=resume_key, resume_timeout=resume_timeout, is_ssl=ssl, loop=loop)
        self._nodes.append(node)
        return node
    
    def destroy_node(self, node: Node):
        """
        Destroy a node for lavalink.

        Parameters
        ---------
        node: :class:`Node`
            The node to destroy.
        """
        node.close()
        self.nodes.remove(node)


    @property
    def nodes(self) -> t.List[Node]:
        """
        A list of nodes.
        """
        return self._nodes

    @property
    def default_node(self) -> Node:
        """
        The default node.
        """
        return self._nodes[0]
