import argparse
import os
from typing import List

import yaml
from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    db_filename:            str = Field("zitate_db.sqlite", validation_alias="DATABASE_FILENAME")
    log_level:              str = Field("INFO", validation_alias="LOG_LEVEL")
    guilds:                 List[int] = Field(..., validation_alias="GUILDS")
    quotes_channel:         int = Field(..., validation_alias="QUOTES_CHANNEL")
    config_file:            str = Field(..., validation_alias="CONFIG_FILENAME")
    discord_token:          str = Field(..., validation_alias="DISCORD_TOKEN")
    upvote_emoji_name:      str = Field(..., validation_alias="UPVOTE_EMOJI_NAME")
    upvote_emoji_id:        int = Field(..., validation_alias="UPVOTE_EMOJI_ID")
    downvote_emoji_name:    str = Field(..., validation_alias="DOWNVOTE_EMOJI_NAME")
    downvote_emoji_id:      int = Field(..., validation_alias="DOWNVOTE_EMOJI_ID")
    quote_cooldown:         int = Field(10,  validation_alias="QUOTE_COOLDOWN")
    quote_permission_role:  int = Field(..., validation_alias="QUOTE_PERMISSION_ROLE")
    model_config = {
        "populate_by_name": True,
        "extra": "allow"
    }


def load_config() -> Settings:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config-file", type=str, default="config.yaml")
    args = parser.parse_args()

    # YAML Args
    yaml_data = {}
    if os.path.exists(str(args.config_file)):
        with open(args.config_file) as f:
            yaml_data = yaml.safe_load(f) or {}

    data = {}

    if os.getenv("DATABASE_FILENAME") or yaml_data.get("db_filename"):
        data["db_filename"] = os.getenv("DATABASE_FILENAME") or yaml_data.get("db_filename")

    if os.getenv("LOG_LEVEL") or yaml_data.get("log_level"):
        data["log_level"] = os.getenv("LOG_LEVEL") or yaml_data.get("log_level")

    if os.getenv("GUILDS") or yaml_data.get("guilds"):
        data["guilds"] = os.getenv("GUILDS") or yaml_data.get("guilds")

    if os.getenv("QUOTES_CHANNEL") or yaml_data.get("quotes_channel"):
        data["quotes_channel"] = os.getenv("QUOTES_CHANNEL") or yaml_data.get("quotes_channel")

    if args.config_file or os.getenv("CONFIG_FILENAME"):
        data["config_file"] = args.config_file or os.getenv("CONFIG_FILENAME")

    if os.getenv("DISCORD_TOKEN") or yaml_data.get("discord_token"):
        data["discord_token"] = os.getenv("DISCORD_TOKEN") or yaml_data.get("discord_token")

    if os.getenv("UPVOTE_EMOJI_NAME") or yaml_data.get("upvote_emoji_name"):
        data["upvote_emoji_name"] = os.getenv("UPVOTE_EMOJI_NAME") or yaml_data.get("upvote_emoji_name")

    if os.getenv("UPVOTE_EMOJI_ID") or yaml_data.get("upvote_emoji_id"):
        data["upvote_emoji_id"] = os.getenv("UPVOTE_EMOJI_ID") or yaml_data.get("upvote_emoji_id")

    if os.getenv("DOWNVOTE_EMOJI_NAME") or yaml_data.get("downvote_emoji_name"):
        data["downvote_emoji_name"] = os.getenv("DOWNVOTE_EMOJI_NAME") or yaml_data.get("downvote_emoji_name")

    if os.getenv("DOWNVOTE_EMOJI_ID") or yaml_data.get("downvote_emoji_id"):
        data["downvote_emoji_id"] = os.getenv("DOWNVOTE_EMOJI_ID") or yaml_data.get("downvote_emoji_id")

    if os.getenv("QUOTE_COOLDOWN") or yaml_data.get("quote_cooldown"):
        data["quote_cooldown"] = os.getenv("QUOTE_COOLDOWN") or yaml_data.get("quote_cooldown")

    if os.getenv("QUOTE_PERMISSION_ROLE") or yaml_data.get("quote_permission_role"):
        data["quote_permission_role"] = os.getenv("QUOTE_PERMISSION_ROLE") or yaml_data.get("quote_permission_role")
    # pydantic validation
    return Settings(**data)
