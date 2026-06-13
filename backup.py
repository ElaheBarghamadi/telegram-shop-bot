import shutil
from datetime import datetime

def backup_db():
    name = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
    shutil.copy("shop.db", name)
    return name