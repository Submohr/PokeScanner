from app.discord import bot
from config import Config

client = bot.get_client()
token = Config.DISCORD_TOKEN
client.run(token)
