import asyncio
import sqlite3

from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton


TOKEN = "8888910798:AAFYtmw4O6XvzX5RuHZGrpoQpDpdY8JOfyc"


dp = Dispatcher()


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
            "yo‘naltirilgan mashg‘ulot dasturini tuzaman.\n\n\n\n"
            "**Sog'liging uchun egoist bo‘l!**\n\n"
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
            "chekni ushbu botga yuborishni unutmang. 🧾\n\n"
            "To‘lov tasdiqlangach, kursga kirish imkoniyati beriladi. ✅"
        )
    },


    "ru": {
        "welcome": (
            "Здравствуйте! 👋\n\n"
            "Меня зовут Бунёд Норматов. Я фитнес-тренер с 25-летним опытом "
            "в сфере спорта и здорового образа жизни. 💪\n\n"
            "Последние 4 года я профессионально работал спортивным тренером "
            "в Европе. 🇪🇺\n\n"
            "Теперь я запускаю свой персональный фитнес-курс. В рамках курса "
            "я работаю с каждым атлетом индивидуально, учитывая его цели "
            "и физические возможности.\n\n"
            "С каждым участником я работаю индивидуально и составляю "
            "программу тренировок, ориентированную на достижение результата.\n\n\n\n"
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
            "После оплаты обязательно отправьте чек "
            "в этот бот. 🧾\n\n"
            "После проверки оплаты вам будет предоставлен доступ к курсу. ✅"
        )
    },


    "en": {
        "welcome": (
            "Hello! 👋\n\n"
            "My name is Bunyod Normatov. I am a fitness trainer with 25 years "
            "of experience in sports and healthy living. 💪\n\n"
            "For the past 4 years, I have worked professionally as a sports "
            "coach in Europe. 🇪🇺\n\n"
            "I am now launching my own personal fitness course. Throughout "
            "the course, I work with every athlete individually, taking into "
            "account their goals and abilities.\n\n"
            "Every participant receives an individual approach and a training "
            "program focused on achieving their goals.\n\n\n\n"
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
            "After making the payment, please remember "
            "to send the payment receipt to this bot. 🧾\n\n"
            "After your payment is verified, you will receive access to the course. ✅"
        )
    }
}


# =========================
# LANGUAGE KEYBOARD
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


# =========================
# MAIN KEYBOARD
# =========================

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


# =========================
# PAYMENT KEYBOARD
# =========================

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


# =========================
# DATABASE
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


# =========================
# START
# =========================

@dp.message(CommandStart())
async def start(message: Message):

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
async def choose_uz(message: Message):

    save_language(message.from_user.id, "uz")

    await message.answer(
        TEXTS["uz"]["welcome"],
        reply_markup=main_keyboard("uz")
    )


@dp.message(F.text == "🇷🇺 Русский")
async def choose_ru(message: Message):

    save_language(message.from_user.id, "ru")

    await message.answer(
        TEXTS["ru"]["welcome"],
        reply_markup=main_keyboard("ru")
    )


@dp.message(F.text == "🇬🇧 English")
async def choose_en(message: Message):

    save_language(message.from_user.id, "en")

    await message.answer(
        TEXTS["en"]["welcome"],
        reply_markup=main_keyboard("en")
    )


# =========================
# SETTINGS
# =========================

@dp.message(F.text.in_([
    TEXTS["uz"]["settings"],
    TEXTS["ru"]["settings"],
    TEXTS["en"]["settings"]
]))
async def settings(message: Message):

    await message.answer(
        "🌐 Tilni tanlang / Выберите язык / Choose language:",
        reply_markup=language_keyboard()
    )


# =========================
# COURSE PAYMENT
# =========================

@dp.message(F.text.in_([
    TEXTS["uz"]["buy"],
    TEXTS["ru"]["buy"],
    TEXTS["en"]["buy"]
]))
async def buy_course(message: Message):

    lang = get_language(message.from_user.id)

    if not lang:
        return

    await message.answer(
        TEXTS[lang]["payment"],
        reply_markup=payment_keyboard(lang)
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

    bot = Bot(TOKEN)

    print("Fitness Trainer bot запущен...")

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())