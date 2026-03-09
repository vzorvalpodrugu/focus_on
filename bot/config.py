import os

from dotenv import load_dotenv

load_dotenv()

TG_TOKEN = os.getenv('TG_TOKEN')
actual_teacher_tg_ids = [
    "1437953101"
]