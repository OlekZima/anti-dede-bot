from datetime import datetime, timedelta
import discord
from discord.ext import tasks
import logging
from dotenv import load_dotenv
import os

load_dotenv()
logger = logging.getLogger("anti_dede_bot")
handler = logging.FileHandler(filename="anti_dede_bot.log", encoding="utf-8", mode="a")


class AntiDedeBot(discord.Client):
    def __init__(self, *, intents, **options):
        super().__init__(intents=intents, **options)

        self.messages: list[discord.Message] = []
        self.dede_id = int(os.getenv("DEDE_ID"))
        self.channel_id = int(os.getenv("CHANNEL_ID"))

    async def setup_hook(self) -> None:
        self.delete_messages.start()

    async def on_ready(self) -> None:
        logger.info(f"Logged in as {self.user} (ID: {self.user.id})")

    @tasks.loop(seconds=60)
    async def delete_messages(self) -> None:
        await self.fetch_messages()
        for message in self.messages:
            if await self.is_dede_message(message):
                logger.warning(f"Deleting message from {message.author} in {message.channel}")
                await message.delete(delay=1)

    async def fetch_messages(self) -> None:
        await self.wait_until_ready()
        channel = self.get_channel(self.channel_id)

        logger.info(f"Checking dede messages in channel: {channel.name}")
        history = channel.history(
            limit=20,
            after=datetime.now() - timedelta(minutes=5),
            oldest_first=False,
        )

        self.messages = [
            message async for message in history if await self.is_dede_message(message)
        ]

        logger.info(f"Found messages: {[message.content for message in self.messages]}")

    async def is_dede_message(self, message: discord.Message) -> bool:
        is_message_w_attachment = (
            len(message.attachments) >= 1 and message.author.id == self.dede_id
        )
        logger.info(f"Message contains attachment(s): {is_message_w_attachment}.")

        if message.reference is None:
            logger.info("Message does not contain a reference.")
            return is_message_w_attachment
        try:
            logger.info("Message contains a reference.")
            original_message = await message.channel.fetch_message(message.reference.message_id)
            is_reference_attachment = len(original_message.attachments) >= 1
            logger.info("Reference contains attachment(s).")

            return is_message_w_attachment or is_reference_attachment
        except discord.NotFound:
            logger.error("Original message not found.")
        except discord.Forbidden:
            logger.error("I have no permission to fetch message.")
        except discord.HTTPException:
            logger.error("An error occurred while fetching message.")
        return False


if __name__ == "__main__":
    intents = discord.Intents.default()
    intents.message_content = True
    intents.guilds = True
    intents.guild_messages = True
    intents.guilds = True

    client = AntiDedeBot(intents=intents)
    client.run(os.getenv("DISCORD_TOKEN"), log_handler=handler)
