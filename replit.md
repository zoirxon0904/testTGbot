# Telegram Referral Bot

## Overview
A Telegram bot (in Uzbek) that requires users to join 3 channels and refer 3 friends before unlocking access to a final private channel link.

## Tech Stack
- Python 3.12
- python-telegram-bot 21.3
- SQLite (local file `bot.db`, auto-created)

## Project Layout
- `bot.py` — main bot logic and handlers (`/start`, `/referral`, callback)
- `database.py` — SQLite operations
- `config.py` — channel IDs, referral count, reads `BOT_TOKEN` from env
- `requirements.txt` — Python dependencies

## Setup
- `BOT_TOKEN` is provided via Replit Secrets.
- Channel IDs and the final reward channel link are configured in `config.py`.
- The bot must be added as an admin to each required channel.

## Workflow
- `Telegram Bot` (console): `python bot.py` — runs the bot via long polling.

## Notes
- This project has no web frontend; it's a pure background polling worker.
- Fixed indentation issue in `bot.py` `start()` handler from the original import.
