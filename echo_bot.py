import logging 
from aiogram import Bot,Dispatcher,executor,types
from dotenv import load_dotenv
import os
load_dotenv()
TELEGRAM_BOT_TOKEN=os.getenv('TELEGRAM_BOT_TOKEN')
print(TELEGRAM_BOT_TOKEN)