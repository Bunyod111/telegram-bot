import logging
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types.web_app_info import WebAppInfo
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

API_TOKEN = '8764577774:AAG_OOAmS5RBnKPqXAcHOEn9vaK3d5wEX3A'
WEBAPP_URL = 'https://bunyod111.github.io/landing_obraz_n/'
ADMIN_ID = 123456789  # <--- ВСТАВЬТЕ СЮДА ВАШ TELEGRAM ID (цифры)

logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# 1. Запуск бота и выдача кнопки лендинга
@dp.message_handler(commands=['start'])
async def start_command(message: types.Message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton("✨ Открыть ПРЕОБРАЖЕНИЕ", web_app=WebAppInfo(url=WEBAPP_URL)))
    
    await message.answer(
        "Добро пожаловать в проект ПРЕОБРАЖЕНИЕ!\n\nНажмите на кнопку ниже, чтобы узнать подробности и выбрать формат участия 👇", 
        reply_markup=markup
    )

# 2. Ловим выбор тарифа из лендинга
@dp.message_handler(content_types=['web_app_data'])
async def web_app_data_handler(message: types.Message):
    tariff = message.web_app_data.data
    
    if tariff == "month_1":
        text = "Вы выбрали **Подписку на 1 месяц**.\nК оплате: **5 300 ₽**."
    elif tariff == "month_3":
        text = "Вы выбрали **Подписку на 3 месяца**.\nК оплате: **13 300 ₽**."
    elif tariff == "mentor":
        text = "Вы выбрали **Личное наставничество**.\nК оплате: **300 000 ₽**."
    else:
        return

    instruction = (
        f"{text}\n\n"
        "💳 **Для оплаты переведите сумму на карту Сбербанка:**\n"
        "`2202 2022 2222 2222` (Людмила Б.)\n"
        "или по номеру телефона: `+7 999 000-00-00` (Сбербанк)\n\n"
        "📸 **После перевода обязательно пришлите сюда скриншот чека.**"
    )
    await message.answer(instruction, parse_mode="Markdown")

# 3. Ловим скриншот чека от клиента и отправляем админу
@dp.message_handler(content_types=['photo'])
async def handle_receipt(message: types.Message):
    markup = InlineKeyboardMarkup()
    # Привязываем к кнопкам ID пользователя, чтобы знать, кому отвечать
    markup.add(
        InlineKeyboardButton("✅ Подтвердить", callback_data=f"approve_{message.from_user.id}"),
        InlineKeyboardButton("❌ Отклонить", callback_data=f"reject_{message.from_user.id}")
    )
    
    # Отправляем фото админу
    await bot.send_photo(
        ADMIN_ID, 
        message.photo[-1].file_id, 
        caption=f"🔔 Новый чек от пользователя @{message.from_user.username} (ID: {message.from_user.id})",
        reply_markup=markup
    )
    await message.answer("✅ Ваш чек отправлен на проверку! Ожидайте подтверждения и ссылку.")

# 4. Обрабатываем нажатие кнопок админом
@dp.callback_query_handler(lambda c: c.data.startswith('approve_') or c.data.startswith('reject_'))
async def process_admin_decision(callback_query: types.CallbackQuery):
    action, user_id = callback_query.data.split('_')
    
    if action == "approve":
        # Пока ставим заглушку. Позже добавим генерацию настоящей одноразовой ссылки
        await bot.send_message(user_id, "🎉 Ваша оплата успешно подтверждена!\n\nВот ваша ссылка на закрытый канал: https://t.me/+TEST_LINK")
        await callback_query.message.edit_caption(caption="✅ ЧЕК ПРИНЯТ И ССЫЛКА ОТПРАВЛЕНА")
    else:
        await bot.send_message(user_id, "❌ К сожалению, оплата не найдена. Пожалуйста, проверьте чек и отправьте снова.")
        await callback_query.message.edit_caption(caption="❌ ЧЕК ОТКЛОНЕН")
        
    await bot.answer_callback_query(callback_query.id)

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)