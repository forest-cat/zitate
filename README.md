# zitate - a simple discord bot for quotes

## Description
This project is a simple discord bot written in Python with pycord that sends when triggered with a command the quote into a configured channel. It needs the [SIS-API](https://github.com/forest-cat/simple-image-storage) as integration for profile images to work due to discords change to the lifetime of files.

## Installation
### Docker Compose (recommended)
1. Ensure your docker is set up correctly
2. Clone this repository: `git clone https://github.com/forest-cat/zitate.git`
3. Navigate into it: `cd zitate`
4. Configure a discord token via the `DISCORD_TOKEN` environment variable in the `docker-compose.yml`
5. Build the container with: `docker compose build`
6. Run the application using: `docker compose up -d`

### Manual Installation using uv
1. Ensure you have access to a working `uv` installation
2. Clone this repository: `git clone https://github.com/forest-cat/zitate.git`
3. Navigate into it: `cd zitate`
4. Run `uv sync` to ensure all packages are installed
5. Copy the `example_config.yaml` from this repository and set a discord token. You can change all other values or remove them because they're the default values and don't change anything
6. Start the application using `uv run app/main.py`

## Configuration
The bot needs additional configuration, see the tables below to find out which option needs to have which value
### Environment Variable (Docker Compose)

| Value                   | Example (Options)                               | Default                                                | Description                                                                                                                                                         |
| ----------------------- | ----------------------------------------------- | ------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `DATABASE_FILENAME`     | `zitate_db.sqlite`                              | `zitate_db.sqlite`                                     | The filename of the database                                                                                                                                        |
| `LOG_LEVEL`             | `CRITICAL`, `ERROR`, `WARNING`, `INFO`, `DEBUG` | `INFO`                                                 | The loglevel of the bot, `DEBUG` can cause larger logfiles and verbose output. `INFO` or something higher is a good choice                                          |
| `LOG_FORMAT`            | `%(levelname)s - %(message)s`                   | `%(asctime)s - %(levelname)s - %(name)s - %(message)s` | The logging format, check out the [python documentation](https://docs.python.org/3/library/logging.html#logrecord-attributes) for all available attributes          |
| `GUILDS`                | `[123456789, 987654321]`                        |                                                        | The IDs of the guilds the bot should register its commands on, it acts as a whitelist to ensure the bot only works on these specified guilds                        |
| `QUOTES_CHANNEL`        | `3478658734734685`                              |                                                        | The channel the bot should send the quotes to, currently only one channel is supported. For using the bot in multiple channels i recommend using multiple instances |
| `DISCORD_TOKEN`         | `NFDS763245nb1jhF8jhgdfkujds`                   |                                                        | Your discord bot token                                                                                                                                              |
| `SIS_API_TOKEN`         | `NFDS7632*27:uj12!abc`                          |                                                        | The token set in the SIS-API configuration, its needed to upload the users profile pictures                                                                         |
| `SIS_API_ENDPOINT`      | `https://example.com`                           |                                                        | The publicly reachable SIS-API endpoint                                                                                                                             |
| `UPVOTE_EMOJI_NAME`     | `upvote`                                        |                                                        | The name of the upvote emoji on any guild available to the bot                                                                                                      |
| `UPVOTE_EMOJI_ID`       | `1454568564572215110`                           |                                                        | The ID of the upvote emoji                                                                                                                                          |
| `DOWNVOTE_EMOJI_NAME`   | `downvote`                                      |                                                        | The name of the downvote emoji on any guild available to the bot                                                                                                    |
| `DOWNVOTE_EMOJI_ID`     | `1454568564572215111`                           |                                                        | The ID of the downvote emoji                                                                                                                                        |
| `QUOTE_COOLDOWN`        | `10`                                            | `5`                                                    | The cooldown in seconds for each user before they can use any quote feature again                                                                                   |
| `QUOTE_PERMISSION_ROLE` | `734865876438756384`                            |                                                        | The ID of the role that allows users to use the quote features                                                                                                      |

### Manual Installation using uv
The examples for the Docker Compose options work the same way, you have to create a `config.yaml` file and enter the values there. For help you can checkout the `example_config.yaml` to see how the configuration is done.

## Usage
Head into your discord and there the slash commands should show up.