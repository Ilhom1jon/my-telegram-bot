import telebot
import yt_dlp
from telebot import types

TOKEN = "9058008173:AAG57XcrjIIQaTeSID9Rb5aUDC-ctF_W0Nw"
bot = telebot.TeleBot(TOKEN)

# Вақтинчалик линкни сақлаб туриш учун луғат
user_links = {}

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Салом! Менга YouTube, Instagram ёки TikTok линкини юборинг ёки қўшиқ номини ёзинг.")

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    query = message.text.strip()
    if not query:
        return
        
    user_id = message.from_user.id
    user_links[user_id] = query
    
    markup = types.InlineKeyboardMarkup(row_width=2)
    btn_video = types.InlineKeyboardButton("📹 Видео", callback_data="dl_video")
    btn_audio = types.InlineKeyboardButton("🎵 Аудио (Мусиқа)", callback_data="dl_audio")
    markup.add(btn_video, btn_audio)
    
    bot.reply_to(message, "Қайси форматда юклаб олайлик?", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    user_id = call.from_user.id
    if user_id not in user_links:
        bot.answer_callback_query(call.id, "Эскирди, линкни қайтадан юборинг.")
        return
    
    query = user_links[user_id]
    bot.answer_callback_query(call.id, "Юклаб олиш бошланди, бироз кутинг...")
    
    # Қидирув ёки линкни аниқлаш
    if not query.startswith('http'):
        search_query = f"ytsearch1:{query}"
    else:
        search_query = query

    # Барча чекловларни четлаб ўтувчи ва мустаҳкам созламалар
    ydl_opts = {
        'format': 'best/bestvideo+bestaudio',
        'noplaylist': True,
        'outtmpl': '%(id)s.%(ext)s',
        'ignoreerrors': True,
        'no_warnings': True,
        'geo_bypass': True,
        'socket_timeout': 30,
    }
    
    if call.data == "dl_audio":
        ydl_opts['format'] = 'bestaudio/best'

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Маълумотни хатосиз суғуриб олиш
            info = ydl.extract_info(search_query, download=True)
            if info and 'entries' in info:
                # Қидирув натижасидаги биринчи элементни оламиз
                info = info['entries'][0]
            
            if not info:
                raise Exception("Файл маълумотларини олиб бўлмади.")
                
            filename = ydl.prepare_filename(info)
            
        # Файлни Телеграмга юбориш
        with open(filename, 'rb') as f:
            if call.data == "dl_video":
                bot.send_video(call.message.chat.id, f)
            else:
                bot.send_audio(call.message.chat.id, f)
                
    except Exception as e:
        bot.send_message(call.message.chat.id, f"Хатолик юз берди: Бу контент ёпиқ, мавжуд эмас ёки ҳавола нотўғри.")

bot.infinity_polling()
