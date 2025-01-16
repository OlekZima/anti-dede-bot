# Anti Dede Bot

Bot that deletes messages with attachments from specific user in specific channel, if the message is older than 5 minutes.

## Usage

1. Create `.env` file with the following content:

   ```.env
   DISCORD_TOKEN=...
   DEDE_ID=...
   CHANNEL_ID=...
   ```

2. Run the bot:

```bash
uv run python anti_dede_bot.py
```
