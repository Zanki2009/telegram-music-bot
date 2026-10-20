import os
import glob
import telebot
from flask import Flask, request

TOKEN = os.environ.get('TOKEN')
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

@app.route(f'/{TOKEN}', methods=['POST'])
def webhook():
    if request.headers.get('content-type') == 'application/json':
        json_string = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return '', 200
    else:
        return 'Forbidden', 403

@app.route('/')
def index():
    return "Telegram Music Bot is running on Vercel!", 200

# /start command
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "မင်္ဂလာပါ ဘရို! ကျေးဇူးတင်ပါတယ်။ သီချင်းနာမည် သို့မဟုတ် တေးသံသာကို ရိုက်ပို့လိုက်ပါ၊ အင်တာနက်ကနေ ရှာပြီး ပို့ပေးပါမယ်။")

# သီချင်းရှာပြီး ပို့ပေးသည့် အပိုင်း (yt-dlp)
@bot.message_handler(func=lambda message: True)
def search_and_send_song(message):
    query = message.text.strip()
    processing_msg = bot.reply_to(message, f"🔍 '{query}' ကို ရှာနေပြီနော်၊ ခဏစောင့်ပါ...")

    try:
        # ပိုနေတဲ့ song_file ဖိုင်ဟောင်းများ ရှင်းထုတ်ရန်
        for f in glob.glob("song_file.*"):
            try:
                os.remove(f)
            except:
                pass

        import yt_dlp
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': 'song_file.%(ext)s',
            'default_search': 'ytsearch1',
            'noplaylist': True,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(query, download=True)
            title = info.get('title', query)
            uploader = info.get('uploader', 'Unknown Artist')

        # Download လုပ်ထားသော ဖိုင်ကို ရှာရန်
        downloaded_files = glob.glob("song_file.*")
        if downloaded_files:
            audio_file_path = downloaded_files[0]
            with open(audio_file_path, 'rb') as audio:
                bot.send_audio(
                    message.chat.id, 
                    audio, 
                    caption=f"🎵 {title}\n🎤 {uploader}",
                    title=title,
                    performer=uploader
                )
            bot.delete_message(message.chat.id, processing_msg.message_id)
        else:
            bot.edit_message_text("❌ သီချင်းဖိုင် ဒေါင်းလုဒ်လုပ်မရလို့ပါ ဘရို၊ တခြားနာမည်နဲ့ ထပ်စမ်းကြည့်ပါဦး။", message.chat.id, processing_msg.message_id)

    except Exception as e:
        bot.edit_message_text(f"❌ အမှားအယွင်း တစ်စုံတစ်ရာ ရှိသွားပါတယ် ဘရို - {str(e)}", message.chat.id, processing_msg.message_id)
