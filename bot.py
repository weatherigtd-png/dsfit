import asyncio
import sqlite3
from datetime import datetime

from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.types import (
    Message,
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    CallbackQuery,
)
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage


TOKEN = "8888910798:AAFYtmw4O6XvzX5RuHZGrpoQpDpdY8JOfyc"

# =========================
# CHAT IDs
# =========================

ADMIN_GROUP_ID = -1004320853444
PRIVATE_CHANNEL_ID = -1004337216248


# =========================
# BOT
# =========================

bot = Bot(TOKEN)
dp = Dispatcher(storage=MemoryStorage())


# =========================
# DATABASE
# =========================

db = sqlite3.connect("fitness_bot.db")
cursor = db.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    telegram_id INTEGER PRIMARY KEY,
    language TEXT NOT NULL
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS payments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    telegram_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    username TEXT,
    file_id TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending',
    admin_message_id INTEGER,
    created_at TEXT NOT NULL,
    approved_at TEXT
)
""")

db.commit()


# =========================
# TEXTS
# =========================

TEXTS = {

    "uz": {

        "welcome": (
            "Assalomu alaykum! 👋\n\n"
            "Mening ismim Bunyod Normatov. Men sport va sog‘lom turmush tarzi "
            "sohasida 25 yillik tajribaga ega fitness trenerman. 💪\n\n"
            "So‘nggi 4 yil davomida Yevropada sport murabbiysi sifatida "
            "professional faoliyat olib bordim. 🇪🇺\n\n"
            "Endilikda o‘z shaxsiy fitness kursimga asos soldim. Kurs davomida "
            "har bir atletning individual maqsadlari va imkoniyatlariga mos "
            "ravishda online mashg‘ulotlar olib boraman.\n\n"
            "Har bir ishtirokchi bilan individual ishlayman va natijaga "
            "yo‘naltirilgan mashg‘ulot dasturini tuzaman.\n\n\n"
            "*Sog'liging uchun egoist bo‘l!*\n\n"
            "Kursga qo‘shilish uchun quyidagi tugmani bosing 👇"
        ),

        "buy": "💳 Kursga yozilish",
        "settings": "⚙️ Sozlamalar",

        "payment": (
            "💳 KURS UCHUN TO‘LOV\n\n"
            "Kurs narxi: 200 000 so‘m\n\n"
            "💰 Karta raqami:\n"
            "5614 6820 9051 9101\n\n"
            "👤 Karta egasi:\n"
            "Normatov Bunyod\n\n"
            "To‘lovni amalga oshirgandan so‘ng, "
            "chekni ushbu botga yuboring. 🧾"
        ),

        "send_receipt": (
            "🧾 To‘lov chekini ushbu botga yuboring.\n\n"
            "Chekni rasm ko‘rinishida yuboring."
        ),

        "ask_name": (
            "📝 Chek qabul qilindi.\n\n"
            "Iltimos, ism va familiyangizni yozing:"
        ),

        "received": (
            "✅ Arizangiz qabul qilindi!\n\n"
            "To‘lovingiz administrator tomonidan tekshiriladi.\n"
            "Tasdiqlangandan so‘ng sizga kursga kirish havolasi yuboriladi."
        ),

        "approved": (
            "🎉 To‘lovingiz tasdiqlandi!\n\n"
            "Kursimizga xush kelibsiz! 💪\n\n"
            "🔐 Shaxsiy kirish havolangiz:\n"
        ),

        "rejected": (
            "❌ To‘lovingiz tasdiqlanmadi.\n\n"
            "Iltimos, to‘lov chekini qayta tekshirib, "
            "qaytadan yuboring."
        )
    },

    "ru": {

        "welcome": (
            "Здравствуйте! 👋\n\n"
            "Меня зовут Бунёд Норматов. Я фитнес-тренер с 25-летним опытом "
            "в сфере спорта и здорового образа жизни. 💪\n\n"
            "Последние 4 года я профессионально работал спортивным тренером "
            "в Европе. 🇪🇺\n\n"
            "Теперь я запускаю свой персональный фитнес-курс. "
            "В рамках курса я работаю с каждым атлетом индивидуально, "
            "учитывая его цели и физические возможности.\n\n"
            "С каждым участником я работаю индивидуально и составляю "
            "программу тренировок, ориентированную на достижение результата.\n\n\n"
            "**Будь эгоистом ради своего здоровья!**\n\n"
            "Чтобы присоединиться к курсу, нажмите кнопку ниже 👇"
        ),

        "buy": "💳 Записаться на курс",
        "settings": "⚙️ Настройки",

        "payment": (
            "💳 ОПЛАТА КУРСА\n\n"
            "Стоимость курса: 200 000 сум\n\n"
            "💰 Номер карты:\n"
            "5614 6820 9051 9101\n\n"
            "👤 Получатель:\n"
            "Normatov Bunyod\n\n"
            "После оплаты отправьте чек в этот бот. 🧾"
        ),

        "send_receipt": (
            "🧾 Отправьте чек об оплате в этот бот.\n\n"
            "Отправьте чек в виде фотографии."
        ),

        "ask_name": (
            "📝 Чек получен.\n\n"
            "Пожалуйста, напишите ваше имя и фамилию:"
        ),

        "received": (
            "✅ Ваша заявка принята!\n\n"
            "Оплата будет проверена администратором.\n"
            "После подтверждения вы получите ссылку на курс."
        ),

        "approved": (
            "🎉 Ваша оплата подтверждена!\n\n"
            "Добро пожаловать на курс! 💪\n\n"
            "🔐 Ваша персональная ссылка:\n"
        ),

        "rejected": (
            "❌ Оплата не подтверждена.\n\n"
            "Пожалуйста, проверьте чек и отправьте его повторно."
        )
    },

    "en": {

        "welcome": (
            "Hello! 👋\n\n"
            "My name is Bunyod Normatov. I am a fitness trainer with 25 years "
            "of experience in sports and healthy living. 💪\n\n"
            "For the past 4 years, I have worked professionally as a sports "
            "coach in Europe. 🇪🇺\n\n"
            "I am now launching my own personal fitness course. "
            "Throughout the course, I work with every athlete individually, "
            "taking into account their goals and abilities.\n\n"
            "Every participant receives an individual approach and a training "
            "program focused on achieving their goals.\n\n\n"
            "**Be selfish for your health!**\n\n"
            "To join the course, press the button below 👇"
        ),

        "buy": "💳 Join the course",
        "settings": "⚙️ Settings",

        "payment": (
            "💳 COURSE PAYMENT\n\n"
            "Course price: 200,000 UZS\n\n"
            "💰 Card number:\n"
            "5614 6820 9051 9101\n\n"
            "👤 Cardholder:\n"
            "Normatov Bunyod\n\n"
            "After payment, send the receipt to this bot. 🧾"
        ),

        "send_receipt": (
            "🧾 Please send your payment receipt to this bot.\n\n"
            "Send the receipt as a photo."
        ),

        "ask_name": (
            "📝 Receipt received.\n\n"
            "Please enter your first and last name:"
        ),

        "received": (
            "✅ Your application has been received!\n\n"
            "Your payment will be checked by an administrator.\n"
            "After approval, you will receive the course access link."
        ),

        "approved": (
            "🎉 Your payment has been approved!\n\n"
            "Welcome to the course! 💪\n\n"
            "🔐 Your personal access link:\n"
        ),

        "rejected": (
            "❌ Your payment was not approved.\n\n"
            "Please check your receipt and send it again."
        )
    }
}


# =========================
# STATES
# =========================

class PaymentStates(StatesGroup):
    waiting_receipt = State()
    waiting_name = State()


# =========================
# KEYBOARDS
# =========================

def language_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="🇺🇿 O‘zbekcha"),
                KeyboardButton(text="🇷🇺 Русский")
            ],
            [
                KeyboardButton(text="🇬🇧 English")
            ]
        ],
        resize_keyboard=True
    )


def main_keyboard(lang):
    t = TEXTS[lang]

    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text=t["buy"])
            ],
            [
                KeyboardButton(text=t["settings"])
            ]
        ],
        resize_keyboard=True
    )


def payment_keyboard(lang):
    t = TEXTS[lang]

    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text=t["buy"])
            ],
            [
                KeyboardButton(text=t["settings"])
            ]
        ],
        resize_keyboard=True
    )


def admin_keyboard(payment_id):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✅ Одобрить",
                    callback_data=f"approve:{payment_id}"
                ),
                InlineKeyboardButton(
                    text="❌ Отклонить",
                    callback_data=f"reject:{payment_id}"
                )
            ]
        ]
    )


# =========================
# DATABASE FUNCTIONS
# =========================

def get_language(telegram_id):
    cursor.execute(
        "SELECT language FROM users WHERE telegram_id = ?",
        (telegram_id,)
    )

    result = cursor.fetchone()

    if result:
        return result[0]

    return None


def save_language(telegram_id, language):
    cursor.execute(
        """
        INSERT INTO users (telegram_id, language)
        VALUES (?, ?)
        ON CONFLICT(telegram_id)
        DO UPDATE SET language = excluded.language
        """,
        (telegram_id, language)
    )

    db.commit()


def get_payment(payment_id):
    cursor.execute(
        """
        SELECT id, telegram_id, name, username, file_id, status
        FROM payments
        WHERE id = ?
        """,
        (payment_id,)
    )

    return cursor.fetchone()


# =========================
# START
# =========================

@dp.message(CommandStart())
async def start(message: Message, state: FSMContext):

    await state.clear()

    lang = get_language(message.from_user.id)

    if lang:

        await message.answer(
            TEXTS[lang]["welcome"],
            reply_markup=main_keyboard(lang)
        )

    else:

        await message.answer(
            "Fitness Trainer 💪\n\n"
            "Tilni tanlang / Выберите язык / Choose language:",
            reply_markup=language_keyboard()
        )


# =========================
# LANGUAGE
# =========================

@dp.message(F.text == "🇺🇿 O‘zbekcha")
async def choose_uz(message: Message, state: FSMContext):

    await state.clear()

    save_language(message.from_user.id, "uz")

    await message.answer(
        TEXTS["uz"]["welcome"],
        reply_markup=main_keyboard("uz")
    )


@dp.message(F.text == "🇷🇺 Русский")
async def choose_ru(message: Message, state: FSMContext):

    await state.clear()

    save_language(message.from_user.id, "ru")

    await message.answer(
        TEXTS["ru"]["welcome"],
        reply_markup=main_keyboard("ru")
    )


@dp.message(F.text == "🇬🇧 English")
async def choose_en(message: Message, state: FSMContext):

    await state.clear()

    save_language(message.from_user.id, "en")

    await message.answer(
        TEXTS["en"]["welcome"],
        reply_markup=main_keyboard("en")
    )


# =========================
# SETTINGS
# =========================

@dp.message(
    F.text.in_([
        TEXTS["uz"]["settings"],
        TEXTS["ru"]["settings"],
        TEXTS["en"]["settings"]
    ])
)
async def settings(message: Message, state: FSMContext):

    await state.clear()

    await message.answer(
        "🌐 Tilni tanlang / Выберите язык / Choose language:",
        reply_markup=language_keyboard()
    )


# =========================
# BUY COURSE
# =========================

@dp.message(
    F.text.in_([
        TEXTS["uz"]["buy"],
        TEXTS["ru"]["buy"],
        TEXTS["en"]["buy"]
    ])
)
async def buy_course(message: Message, state: FSMContext):

    lang = get_language(message.from_user.id)

    if not lang:
        return

    await state.set_state(PaymentStates.waiting_receipt)

    await message.answer(
        TEXTS[lang]["payment"],
        reply_markup=payment_keyboard(lang)
    )

    await message.answer(
        TEXTS[lang]["send_receipt"]
    )


# =========================
# RECEIVE RECEIPT
# =========================

@dp.message(PaymentStates.waiting_receipt, F.photo)
async def receive_receipt(message: Message, state: FSMContext):

    lang = get_language(message.from_user.id)

    if not lang:
        lang = "ru"

    photo = message.photo[-1]

    await state.update_data(
        file_id=photo.file_id
    )

    await state.set_state(PaymentStates.waiting_name)

    await message.answer(
        TEXTS[lang]["ask_name"]
    )


# =========================
# WRONG RECEIPT
# =========================

@dp.message(PaymentStates.waiting_receipt)
async def wrong_receipt(message: Message):

    lang = get_language(message.from_user.id)

    if not lang:
        lang = "ru"

    await message.answer(
        TEXTS[lang]["send_receipt"]
    )


# =========================
# RECEIVE NAME
# =========================

@dp.message(PaymentStates.waiting_name, F.text)
async def receive_name(message: Message, state: FSMContext):

    lang = get_language(message.from_user.id)

    if not lang:
        lang = "ru"

    data = await state.get_data()

    file_id = data.get("file_id")

    if not file_id:
        await state.clear()
        return

    name = message.text.strip()

    if len(name) < 2:
        await message.answer(
            TEXTS[lang]["ask_name"]
        )
        return

    username = message.from_user.username

    username_text = (
        f"@{username}"
        if username
        else "Нет username"
    )

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute(
        """
        INSERT INTO payments
        (
            telegram_id,
            name,
            username,
            file_id,
            status,
            created_at
        )
        VALUES (?, ?, ?, ?, 'pending', ?)
        """,
        (
            message.from_user.id,
            name,
            username,
            file_id,
            now
        )
    )

    payment_id = cursor.lastrowid

    db.commit()

    admin_text = (
        "🧾 НОВАЯ ЗАЯВКА НА ОПЛАТУ\n\n"
        f"👤 Имя: {name}\n"
        f"📱 Telegram: {username_text}\n"
        f"🆔 ID: `{message.from_user.id}`\n\n"
        "💰 Курс: 200 000 сум\n"
        "🕐 Статус: Ожидает проверки\n\n"
        f"📝 Заявка №{payment_id}"
    )

    sent_message = await bot.send_photo(
        chat_id=ADMIN_GROUP_ID,
        photo=file_id,
        caption=admin_text,
        parse_mode="Markdown",
        reply_markup=admin_keyboard(payment_id)
    )

    cursor.execute(
        """
        UPDATE payments
        SET admin_message_id = ?
        WHERE id = ?
        """,
        (
            sent_message.message_id,
            payment_id
        )
    )

    db.commit()

    await state.clear()

    await message.answer(
        TEXTS[lang]["received"],
        reply_markup=main_keyboard(lang)
    )


# =========================
# APPROVE PAYMENT
# =========================

@dp.callback_query(F.data.startswith("approve:"))
async def approve_payment(callback: CallbackQuery):

    payment_id = int(
        callback.data.split(":")[1]
    )

    payment = get_payment(payment_id)

    if not payment:
        await callback.answer(
            "Заявка не найдена.",
            show_alert=True
        )
        return

    (
        db_id,
        telegram_id,
        name,
        username,
        file_id,
        status
    ) = payment

    if status == "approved":

        await callback.answer(
            "Заявка уже одобрена.",
            show_alert=True
        )
        return

    if status == "rejected":

        await callback.answer(
            "Заявка уже отклонена.",
            show_alert=True
        )
        return

    try:

        invite_link = await bot.create_chat_invite_link(
            chat_id=PRIVATE_CHANNEL_ID,
            member_limit=1
        )

    except Exception as e:

        await callback.answer(
            "Не удалось создать ссылку.",
            show_alert=True
        )

        print("INVITE LINK ERROR:", e)

        return

    cursor.execute(
        """
        UPDATE payments
        SET status = 'approved',
            approved_at = ?
        WHERE id = ?
        """,
        (
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            payment_id
        )
    )

    db.commit()

    lang = get_language(telegram_id)

    if not lang:
        lang = "ru"

    await bot.send_message(
        chat_id=telegram_id,
        text=(
            TEXTS[lang]["approved"]
            + invite_link.invite_link
        )
    )

    try:

        await callback.message.edit_caption(
            caption=(
                "🧾 ЗАЯВКА НА ОПЛАТУ\n\n"
                f"👤 Имя: {name}\n"
                f"📱 Telegram: "
                f"@{username if username else 'нет'}\n"
                f"🆔 ID: `{telegram_id}`\n\n"
                "💰 Курс: 200 000 сум\n"
                "✅ Статус: ОДОБРЕНО\n\n"
                f"📝 Заявка №{payment_id}"
            ),
            parse_mode="Markdown"
        )

    except Exception as e:

        print("EDIT MESSAGE ERROR:", e)

    await callback.answer(
        "Оплата одобрена!",
        show_alert=True
    )


# =========================
# REJECT PAYMENT
# =========================

@dp.callback_query(F.data.startswith("reject:"))
async def reject_payment(callback: CallbackQuery):

    payment_id = int(
        callback.data.split(":")[1]
    )

    payment = get_payment(payment_id)

    if not payment:

        await callback.answer(
            "Заявка не найдена.",
            show_alert=True
        )

        return

    (
        db_id,
        telegram_id,
        name,
        username,
        file_id,
        status
    ) = payment

    if status == "approved":

        await callback.answer(
            "Заявка уже одобрена.",
            show_alert=True
        )

        return

    if status == "rejected":

        await callback.answer(
            "Заявка уже отклонена.",
            show_alert=True
        )

        return

    cursor.execute(
        """
        UPDATE payments
        SET status = 'rejected'
        WHERE id = ?
        """,
        (payment_id,)
    )

    db.commit()

    lang = get_language(telegram_id)

    if not lang:
        lang = "ru"

    await bot.send_message(
        chat_id=telegram_id,
        text=TEXTS[lang]["rejected"]
    )

    try:

        await callback.message.edit_caption(
            caption=(
                "🧾 ЗАЯВКА НА ОПЛАТУ\n\n"
                f"👤 Имя: {name}\n"
                f"📱 Telegram: "
                f"@{username if username else 'нет'}\n"
                f"🆔 ID: `{telegram_id}`\n\n"
                "💰 Курс: 200 000 сум\n"
                "❌ Статус: ОТКЛОНЕНО\n\n"
                f"📝 Заявка №{payment_id}"
            ),
            parse_mode="Markdown"
        )

    except Exception as e:

        print("EDIT MESSAGE ERROR:", e)

    await callback.answer(
        "Оплата отклонена.",
        show_alert=True
    )


# =========================
# UNKNOWN MESSAGES
# =========================


@dp.message()
async def other_messages(message: Message):

    lang = get_language(message.from_user.id)

    if not lang:

        await message.answer(
            "Avval tilni tanlang:",
            reply_markup=language_keyboard()
        )

        return

    await message.answer(
        TEXTS[lang]["welcome"],
        reply_markup=main_keyboard(lang)
    )


# =========================
# RUN
# =========================

async def main():

    print("Fitness Trainer bot запущен...")

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())