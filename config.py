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
        "id": -1002265625081,  # <-- kanal ID (manfiy son)
        "link": "https://t.me/+WcdtRNyDSlE2MTkx",
        "name": "𝑁𝑜𝑧𝑎 | 𝑁𝑒𝑤 𝑌𝑜𝑟𝑘",
    },
    {
        "id": -1001989513167,  # <-- kanal ID
        "link": "https://t.me/Dilbarkhon_Mansurovna",
        "name": "Dilbar Mansurovna| Global Insights",
    },
    {
        "id": -1002568551776,  # <-- kanal ID
        "link": "https://t.me/+b0_CsM93ckljMTA6",
        "name": "Experiencia | by Dilbar",
    },
]

# 3. Oxirida yuboriladigan kanal linki
FINAL_CHANNEL_LINK = "https://t.me/+sn2GKZ-oZX9lM2Qy"

# 4. Nechta do'st taklif qilish kerak
REFERRAL_REQUIRED = 5

# 5. SQLite fayl nomi
DB_FILE = "bot.db"
