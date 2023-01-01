# VTF Bot

## Discord bot for [Variety.TF](https://variety.tf/).

## Setup

1. Create a new Discord application at: https://discord.com/developers/applications
2. Go to the `Bot` menu to create a bot, then enable the `Server Members` and `Message Content` intents.
3. Consider disabling the `Public Bot` option. Click `Reset Token` and copy the bot's token.
4. Copy `sample-config.ini` to `config.ini`, insert your token, and add a guild and channel ID to send debug logging to.
5. Edit `tmux.sh` to reflect the location you've cloned the repository to.
6. Start the bot via `./tmux.sh` or run it directly: `cd src && ./bot.py`
