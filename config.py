# ============================================================
#  config.py  —  Bot sozlamalari (faqat shu faylni o'zgartiring)
# ============================================================
import os

BOT_TOKEN = os.environ.get("BOT_TOKEN", "")

# 2. Majburiy kanallar
#    id  →  bot admin bo'lishi kerak bo'lgan kanal ID
#    Kanal ID ni qanday topish: pastdagi README ga qarang
REQUIRED_CHANNELS = [
    {
        "id": -1003998098831,  # <-- kanal ID (manfiy son)
        "link": "https://t.me/+WtepH9K9UKE3YzAy",
        "name": "Kanal 3",
    },
    {
        "id": -1003979529915,  # <-- kanal ID
        "link": "https://t.me/+CYFAMWL-IQI5MGNi",
        "name": "Kanal 2",
    },
    {
        "id": -1003950616100,  # <-- kanal ID
        "link": "https://t.me/+Nma3Ge6D_gJiYmIy",
        "name": "Kanal 1",
    },
]

# 3. Oxirida yuboriladigan kanal linki
FINAL_CHANNEL_LINK = "https://t.me/Welcome_toHell_z"

# 4. Nechta do'st taklif qilish kerak
REFERRAL_REQUIRED = 3

# 5. SQLite fayl nomi
DB_FILE = "bot.db"
