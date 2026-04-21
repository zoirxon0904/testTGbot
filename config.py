# ============================================================
#  config.py  —  Bot sozlamalari (faqat shu faylni o'zgartiring)
# ============================================================

# 1. @BotFather dan olgan token
BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"

# 2. Majburiy kanallar
#    id  →  bot admin bo'lishi kerak bo'lgan kanal ID
#    Kanal ID ni qanday topish: pastdagi README ga qarang
REQUIRED_CHANNELS = [
    {
        "id": -3998098831,          # <-- kanal ID (manfiy son)
        "link": "https://t.me/+ejBT7_TK4oZhZmVi",
        "name": "Kanal 3",
    },
    {
        "id": -3979529915,          # <-- kanal ID
        "link": "https://t.me/+QIwOlZTn-hxhOWEy",
        "name": "Kanal 2",
    },
    {
        "id": -3950616100,          # <-- kanal ID
        "link": "https://t.me/+8i6gEFq-ZcpjMjAy",
        "name": "Kanal 1",
    },
]

# 3. Oxirida yuboriladigan kanal linki
FINAL_CHANNEL_LINK = "https://t.me/Welcome_toHell_z"

# 4. Nechta do'st taklif qilish kerak
REFERRAL_REQUIRED = 3

# 5. SQLite fayl nomi
DB_FILE = "bot.db"
