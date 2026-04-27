# ============================================================
#  bot.py  —  Asosiy bot logikasi
# ============================================================

import logging
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ChatJoinRequestHandler,
    ContextTypes,
)
from telegram.error import TelegramError

import database as db
from config import (
    BOT_TOKEN,
    REQUIRED_CHANNELS,
    FINAL_CHANNEL_LINK,
    REFERRAL_REQUIRED,
)

logging.basicConfig(
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


# ══════════════════════════════════════════════════════════════
#  YORDAMCHI FUNKSIYALAR
# ══════════════════════════════════════════════════════════════

async def check_membership(bot, user_id: int) -> list[bool]:
    """
    Har bir kanal uchun foydalanuvchi a'zoligini tekshiradi.
    True  → a'zo (yoki tekshirilmaydigan kanal)
    False → a'zo emas
    Eslatma: verify=False bo'lgan kanallar har doim True qaytaradi.
    """
    results = []
    for ch in REQUIRED_CHANNELS:
        if not ch.get("verify", True):
            results.append(True)  # tekshirilmaydi → har doim "a'zo" deb hisoblanadi
            continue
        try:
            member = await bot.get_chat_member(ch["id"], user_id)
            results.append(member.status not in ("left", "kicked"))
        except TelegramError:
            results.append(False)
    return results


def build_subscription_keyboard(membership: list[bool]) -> InlineKeyboardMarkup:
    """
    Kanallar ro'yxati + pastda 'Tekshirish' tugmasi.
    A'zo bo'lgan → ✅, bo'lmagan → ❌
    Tekshirilmaydigan kanallarda ✅/❌ o'rniga 🔗 ko'rsatiladi.
    """
    buttons = []
    for ch, joined in zip(REQUIRED_CHANNELS, membership):
        if not ch.get("verify", True):
            icon = "🔗"
        else:
            icon = "✅" if joined else "❌"
        buttons.append([InlineKeyboardButton(
            f"{icon}  {ch['name']}",
            url=ch["link"],
        )])
    buttons.append([InlineKeyboardButton(
        "🔄  A'zolikni tekshirish",
        callback_data="check_subs",
    )])
    return InlineKeyboardMarkup(buttons)


def referral_link(bot_username: str, user_id: int) -> str:
    return f"https://t.me/{bot_username}?start=ref{user_id}"


# ══════════════════════════════════════════════════════════════
#  /start BUYRUG'I
# ══════════════════════════════════════════════════════════════

async def start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user    = update.effective_user
    user_id = user.id
    args    = ctx.args  # /start <arg> bo'lsa

    # ── Referral parametrini ajratib olish ─────────────────────
    referrer_id = None
    if args and args[0].startswith("ref"):
        try:
            referrer_id = int(args[0][3:])
            if referrer_id == user_id:
                referrer_id = None  # o'zini o'zi taklif qilolmaydi
        except ValueError:
            pass

    # ── Foydalanuvchini DBga yozish ────────────────────────────
    already_exists = db.get_user(user_id) is not None
    db.add_user(
        user_id   = user_id,
        username  = user.username or "",
        full_name = user.full_name,
        referred_by = referrer_id,
    )

    # ── Referralni qayd etish va taklif qilganga xabar ─────────
    if referrer_id and not already_exists:
        # Taklif qiluvchi hali ham barcha kanallarga a'zo bo'lishi shart.
        # Aks holda referral hisobga olinmaydi va mukofot berilmaydi.
        referrer_membership = await check_membership(ctx.bot, referrer_id)

        if all(referrer_membership):
            db.add_referral(referrer_id, user_id)
            ref_count = db.count_referrals(referrer_id)

            # Taklif qilganga bildirish
            try:
                await ctx.bot.send_message(
                    chat_id=referrer_id,
                    text=(
                        f"🎉 Do'stingiz <b>{user.full_name}</b> sizning havolangiz "
                        f"orqali botga qo'shildi!\n\n"
                        f"📊 Sizning referrallaringiz: <b>{ref_count}/{REFERRAL_REQUIRED}</b>"
                    ),
                    parse_mode="HTML",
                )
            except TelegramError:
                pass

            # Agar yetarli to'lgan bo'lsa → final linkni yuborish
            if ref_count >= REFERRAL_REQUIRED and not db.is_rewarded(referrer_id):
                db.mark_rewarded(referrer_id)
                try:
                    await ctx.bot.send_message(
                        chat_id=referrer_id,
                        text=(
                            f"🏆 <b>Tabriklaymiz!</b> Siz {REFERRAL_REQUIRED} ta do'stingizni taklif qildingiz!\n\n"
                            "🔓 Maxsus kanal linki:\n"
                            f"{FINAL_CHANNEL_LINK}"
                        ),
                        parse_mode="HTML",
                    )
                except TelegramError:
                    pass
        else:
            # Taklif qiluvchi kanallardan chiqib ketgan — eslatib qo'yamiz.
            try:
                keyboard = build_subscription_keyboard(referrer_membership)
                await ctx.bot.send_message(
                    chat_id=referrer_id,
                    text=(
                        "⚠️ Sizning havolangiz orqali yangi foydalanuvchi keldi, "
                        "lekin siz majburiy kanallardan chiqib ketgansiz.\n\n"
                        "Referral hisobga olinishi uchun quyidagi kanallarga "
                        "qayta a'zo bo'ling va <b>«A'zolikni tekshirish»</b> tugmasini bosing."
                    ),
                    parse_mode="HTML",
                    reply_markup=keyboard,
                )
            except TelegramError:
                pass

    # ── Yangi foydalanuvchi uchun a'zolik tekshiruvi ───────────
    membership = await check_membership(ctx.bot, user_id)

    if all(membership):
        await send_referral_message(update, ctx)
    else:
        keyboard = build_subscription_keyboard(membership)
        await update.message.reply_text(
            text=(
                "👋 <b>Xush kelibsiz!</b>\n\n"
                "Botdan foydalanish uchun quyidagi 3 ta kanalga a'zo bo'ling:\n"
                "A'zo bo'lgandan so'ng <b>«A'zolikni tekshirish»</b> tugmasini bosing."
            ),
            parse_mode="HTML",
            reply_markup=keyboard,
        )


# ══════════════════════════════════════════════════════════════
#  "A'ZOLIKNI TEKSHIRISH" TUGMASI (callback)
# ══════════════════════════════════════════════════════════════

async def check_subs_callback(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query   = update.callback_query
    user_id = query.from_user.id
    await query.answer()  # loading indikatorini o'chirish

    membership = await check_membership(ctx.bot, user_id)

    if all(membership):
        # Eski xabarni o'chirish
        await query.message.delete()
        # Referral xabarini yuborish
        await send_referral_message(update, ctx)
    else:
        keyboard = build_subscription_keyboard(membership)
        not_joined = [ch["name"] for ch, ok in zip(REQUIRED_CHANNELS, membership) if not ok]
        text = (
            "❗ Siz hali quyidagi kanallarga a'zo bo'lmagansiz:\n"
            + "\n".join(f"  • {name}" for name in not_joined)
            + "\n\nA'zo bo'lib, <b>«A'zolikni tekshirish»</b> ni bosing."
        )
        try:
            await query.edit_message_text(
                text=text,
                parse_mode="HTML",
                reply_markup=keyboard,
            )
        except TelegramError:
            # Xabar o'zgarmagan bo'lsa (foydalanuvchi qayta-qayta bosgan) — e'tiborga olmaymiz
            pass


# ══════════════════════════════════════════════════════════════
#  REFERRAL XABARI
# ══════════════════════════════════════════════════════════════

async def send_referral_message(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Foydalanuvchiga uning shaxsiy referral havolasini yuborish."""
    if update.callback_query:
        user_id   = update.callback_query.from_user.id
        full_name = update.callback_query.from_user.full_name
        send_fn   = update.callback_query.message.reply_text
    else:
        user_id   = update.effective_user.id
        full_name = update.effective_user.full_name
        send_fn   = update.message.reply_text

    me         = await ctx.bot.get_me()
    ref_link   = referral_link(me.username, user_id)
    ref_count  = db.count_referrals(user_id)

    # Agar allaqachon mukofot olgan bo'lsa
    if db.is_rewarded(user_id):
        await send_fn(
            text=(
                "✅ Siz barcha shartlarni bajardingiz!\n\n"
                f"🔓 Maxsus kanal: {FINAL_CHANNEL_LINK}"
            ),
        )
        return

    await send_fn(
        text=(
            f"✅ <b>Ajoyib, {full_name}!</b> Barcha kanallarga a'zo bo'ldingiz.\n\n"
            f"📨 Endi <b>{REFERRAL_REQUIRED} ta do'stingizni</b> botga taklif qiling:\n\n"
            f"🔗 Sizning shaxsiy havolangiz:\n{ref_link}\n\n"
            f"👥 Taklif qilinganlar: <b>{ref_count}/{REFERRAL_REQUIRED}</b>\n\n"
            f"{REFERRAL_REQUIRED} ta do'stingiz botga qo'shilgandan so'ng sizga maxsus kanal linki yuboriladi 🎁"
        ),
        parse_mode="HTML",
    )


# ══════════════════════════════════════════════════════════════
#  /referral BUYRUG'I  (ixtiyoriy — havolani qayta ko'rish)
# ══════════════════════════════════════════════════════════════

async def my_referral(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user_id    = update.effective_user.id
    membership = await check_membership(ctx.bot, user_id)

    if not all(membership):
        await update.message.reply_text(
            "❗ Avval barcha kanallarga a'zo bo'lishingiz kerak.\n"
            "/start ni bosib tekshiruv tugmasidan foydalaning."
        )
        return

    me        = await ctx.bot.get_me()
    ref_link  = referral_link(me.username, user_id)
    ref_count = db.count_referrals(user_id)

    if db.is_rewarded(user_id):
        await update.message.reply_text(
            f"🏆 Siz allaqachon mukofot oldingiz!\n🔓 {FINAL_CHANNEL_LINK}"
        )
        return

    await update.message.reply_text(
        text=(
            f"🔗 Sizning havolangiz:\n<code>{ref_link}</code>\n\n"
            f"👥 Taklif qilinganlar: <b>{ref_count}/{REFERRAL_REQUIRED}</b>"
        ),
        parse_mode="HTML",
    )


# ══════════════════════════════════════════════════════════════
#  KANALGA QO'SHILISH SO'ROVINI AVTOMATIK TASDIQLASH
# ══════════════════════════════════════════════════════════════

async def approve_join_request(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """
    Foydalanuvchi majburiy kanallarning birortasiga 'qo'shilish so'rovi'
    yuborsa, bot uni avtomatik tasdiqlaydi.
    Bot kanalda admin bo'lishi va 'Add Members' huquqiga ega bo'lishi shart.
    """
    req = update.chat_join_request
    chat_id = req.chat.id
    user_id = req.from_user.id

    # Faqat sozlamalardagi kanallar uchun ishlasin
    allowed_ids = {ch["id"] for ch in REQUIRED_CHANNELS}
    if chat_id not in allowed_ids:
        return

    try:
        await ctx.bot.approve_chat_join_request(chat_id=chat_id, user_id=user_id)
        logger.info(
            "Approved join request: user=%s chat=%s", user_id, chat_id
        )
    except TelegramError as e:
        logger.warning(
            "Could not approve join request user=%s chat=%s: %s",
            user_id, chat_id, e,
        )


# ══════════════════════════════════════════════════════════════
#  MAIN
# ══════════════════════════════════════════════════════════════

def main():
    db.init_db()
    logger.info("Ma'lumotlar bazasi tayyor.")

    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start",    start))
    app.add_handler(CommandHandler("referral", my_referral))
    app.add_handler(CallbackQueryHandler(check_subs_callback, pattern="^check_subs$"))
    app.add_handler(ChatJoinRequestHandler(approve_join_request))

    logger.info("Bot ishga tushdi ✅")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
