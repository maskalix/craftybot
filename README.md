# Crafty Controller Bot | Discord Bot to control (turn on/off; restart) server and display basic info
*Unofficial, fan project, not affiliated with Crafty Controller*

- used to control https://craftycontrol.com servers
- docker image on [maskalicz/craftybot](https://hub.docker.com/r/maskalicz/craftybot)

## How it works?
- slash command /serverinfo in any Discord channel you invited your bot to :)
  
## What is needed?
- crafty username
- crafty password
- crafty URL/IP (with http(s), port if IP and without / at the end)
- crafty server ID (found in URL when you go to server overview - server_detail?id=XXXXXXXXX)
- discord bot token

## Usage
docker-compose.yml
```
services:
  discord-bot:
    image: maskalicz/craftybot:latest
    container_name: craftybot
    restart: unless-stopped
    env_file:
      - .env
```
.env
```
BOT_TOKEN=
CRAFTY_API_BASE_URL= # with protocol (http://), without end slash (/), if IP use port also
CRAFTY_SERVER_ID=
CRAFTY_USERNAME=
CRAFTY_PASSWORD=
CRAFTY_SERVER_URL= # Info for users, IP/URL of the server
CRAFTY_SERVER_TYPE= # Info for users, fill here Forge, Spigot or whatever you running
```

then just ``docker compose up -d``
