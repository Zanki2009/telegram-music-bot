import os
import glob
import telebot
import yt_dlp

TOKEN = '8273009596:AAHn-LquYR5lwN1SwpPtOEG1ngCRlJDzyvM'
bot = telebot.TeleBot(TOKEN)
bot.remove_webhook()

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "မင်္ဂလာပါ ဘရို! ကျနော့်ကို သီချင်းနာမည် ရိုက်ပို့လိုက်ပါ။ အင်တာနက်ကနေ ရှာပြီး သီချင်းပုံစံ ပို့ပေးပါမယ်။ 🎶")

@bot.message_handler(func=lambda message: True)
def search_and_send_song(message):
    query = message.text.strip()
    processing_msg = bot.reply_to(message, f"🔍 '{query}' ကို ရှာနေပါပြီ ဘရို၊ ခဏစောင့်ပါ...")

    try:
        # ဟောင်းနေတဲ့ song_file များကို အရင်ရှင်းထုတ်ရန်
        for f in glob.glob("song_file.*"):
            try:
                os.remove(f)
            except:
                pass

        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': 'song_file.%(ext)s',
            'default_search': 'ytsearch1',
            'noplaylist': True,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(query, download=True)
            # YouTube ဗီဒီယို၏ ခေါင်းစဉ်နှင့် အဆိုတော်နာမည်ကို ယူရန်
            title = info.get('title', query)
            uploader = info.get('uploader', 'Unknown Artist')

        # ဖိုင်အမှန်ကို ရှာယူရန်
        files = glob.glob("song_file.*")
        if not files:
            raise Exception("ဖိုင် ဒေါင်းလုဒ်ဆွဲ၍ မရပါ")
        
        filename = files[0]

        # Telegram သို့ သီချင်းဖိုင်အစစ် (Music Player ပုံစံဖြင့်) ပို့ခြင်း
        with open(filename, 'rb') as audio:
            bot.send_audio(
                message.chat.id, 
                audio, 
                title=title, 
                performer=uploader, 
                caption=f"🎵 {title}"
            )

        # ပို့ပြီးပါက ဖိုင်ကို ဖျက်ထုတ်ရန်
        os.remove(filename)
        bot.delete_message(message.chat.id, processing_msg.message_id)

    except Exception as e:
        print(f"Error: {e}")
        bot.edit_message_text(f"❌ အမှားတစ်ခု ဖြစ်သွားပါတယ် ဘရို: {e}", message.chat.id, processing_msg.message_id)

print("Bot စတင်အလုပ်လုပ်နေပါပြီ...")
bot.infinity_polling()
