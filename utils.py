import logging
from config import ADMINS

logging.basicConfig(
    filename="bot.log",
    level=logging.INFO,
    format="%(asctime)s - %(message)s"
)

def log(text):
    logging.info(text)


def is_admin(uid):
    return uid in ADMINS