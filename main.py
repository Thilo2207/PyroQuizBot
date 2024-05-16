from pyrogram import Client, filters
import os
from dotenv import load_dotenv

load_dotenv()
api_id = os.getenv("api_id")
api_hash = os.getenv("api_hash")
bot_token = os.getenv("bot_token")

plugins = dict(root="plugins") 

print("start")
bot = Client( 
    "SeaFloor",
    api_id,
    api_hash,
    bot_token,
    plugins= plugins
)

bot.run()
print("end")


