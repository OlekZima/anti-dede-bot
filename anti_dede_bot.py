import datetime
import discord
from discord.ext import tasks
import logging
import dotenv
import os

dotenv.load_dotenv()
handler = logging.FileHandler(filename="discord_dede_delete.log", encoding="utf-8", mode="a")


class AntiDedeBot(discord.Client):
    def __init__(self, *, intents, **options):
        super().__init__(intents=intents, **options)

        self.messages: list[discord.Message] = []
        self.dede_id = 207196996669407233
        self.server_id = 1327588592301903954
        self.channel_id = 1327588593362931755

    async def setup_hook(self) -> None:
        self.delete_messages.start()

    async def on_ready(self) -> None:
        logging.info(f"Logged in as {self.user} (ID: {self.user.id})")

    @tasks.loop(seconds=10)
    async def delete_messages(self) -> None:
        await self.fetch_messages()
        for message in self.messages:
            if self.if_dede_message(message):
                logging.info(f"Deleting message from {message.author} in {message.channel}")
                await message.delete(delay=1)

    async def fetch_messages(self) -> None:
        await self.wait_until_ready()
        channel = self.get_channel(self.channel_id)

        logging.log(logging.INFO, f"Checking dede messages in channel: {channel.name}")
        history = channel.history(
            limit=20,
            after=datetime.datetime.now() - datetime.timedelta(minutes=5),
            oldest_first=False,
        )

        self.messages = [
            message async for message in history if await self.if_dede_message(message)
        ]
        print(datetime.datetime.now() - datetime.timedelta(minutes=5))

        logging.info(f"Found messages: {[message.content for message in self.messages]}")

    async def if_dede_message(self, message: discord.Message) -> bool:
        is_message_w_attachment = (
            len(message.attachments) >= 1 and message.author.id == self.dede_id
        )

        if message.reference is None:
            return is_message_w_attachment


        original_message = await message.channel.fetch_message(message.reference.message_id)
        is_original_attachment = len(original_message.attachments) >= 1

        return is_message_w_attachment or is_original_attachment



intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.guild_messages = True
intents.guilds = True

client = AntiDedeBot(intents=intents)
client.run(os.getenv("DISCORD_TOKEN"), log_handler=handler)
