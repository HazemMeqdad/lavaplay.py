# lavaplayer

Represents a Lavalink client used to manage nodes and connections.

## setup

```shell
pip install lavaplayer
```
## setup lavalink

you need to java 11* LTS or newer required.

install [lavalink](https://github.com/freyacodes/Lavalink/releases/download/3.4/Lavalink.jar) last version, create [application.yml](https://github.com/freyacodes/Lavalink/blob/master/LavalinkServer/application.yml.example), run the server
```shell
java -jar Lavalink.jar
```
## config lavaplayer server info

from `.LavalinkClient()` set information connection
```python
host="127.0.0.1",  # server ip address
port=8888,  # port
password="password",  # password authentication
bot_id=123 # bot id
```

## license
take to [LICENSE](./LICENSE) file
