from django.apps import AppConfig
import threading
import time
from datetime import datetime
from django.conf import settings
import os

GREEN = "\033[92m"
RED = "\033[91m"
BLUE = "\033[94m"
RESET = "\033[0m"

class BeachesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'beaches'

    def ready(self):
        if os.environ.get('RUN_MAIN') != 'true':
            return

        from .utils import generate_daily_tasks

        def daily_scheduler():
            print()
            print(f"{GREEN} 🕒 Task scheduler started successfully. {GREEN}")
            print()
            while True:
                now = datetime.now()
                if now.hour == 0 and now.minute == 0:
                    print("⏰ Running daily task generator...")
                    try:
                        generate_daily_tasks()
                        print()
                        print(f"{GREEN}✅ Daily tasks updated successfully!{GREEN} {RESET}")
                        print()
                    except Exception as e:
                        print()
                        print(f"{RED}❌ Error {RED} {RESET}while assigning tasks: {e}{RESET}")
                        print()
                    time.sleep(61)
                time.sleep(60)
        print()
        print(f"{RESET}🚀 Running daily task generator on startup... {RESET}")
        print()
        try:
            generate_daily_tasks()
        except Exception as e:
            print(f"❌ Error on startup: {e}")

        thread = threading.Thread(target=daily_scheduler, daemon=True)
        thread.start()