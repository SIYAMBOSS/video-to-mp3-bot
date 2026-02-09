import os
import subprocess
import http.server
import socketserver
import threading
import static_ffmpeg
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes

# FFmpeg সেটআপ
static_ffmpeg.add_paths()

# --- ১. Render-এর জন্য ফেক সার্ভার ---
def run_fake_server():
    PORT = int(os.environ.get("PORT", 8080))
    Handler = http.server.SimpleHTTPRequestHandler
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        httpd.serve_forever()

threading.Thread(target=run_fake_server, daemon=True).start()

# --- ২. বটের তথ্য ---
TOKEN = '8593565860:AAFz2U5TTLgu74E-JRnzHrVvmJvD4SYm_ho'
MY_ID = "7416528268"

async def video_to_mp3(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if str(update.message.from_user.id) != MY_ID:
        return

    msg = await update.message.reply_text("📥 ভিডিও থেকে অডিও বের করছি... একটু অপেক্ষা করুন।")
    v_path = "video.mp4"
    a_path = "audio.mp3"
    
    try:
        video_file = await update.message.video.get_file()
        await video_file.download_to_drive(v_path)
        
        # FFmpeg কমান্ড রান করা
        cmd = f"ffmpeg -i {v_path} -vn -ab 128k -ar 44100 -y {a_path}"
        subprocess.run(cmd, shell=True, check=True)

        if os.path.exists(a_path):
            with open(a_path, 'rb') as audio:
                await update.message.reply_audio(audio, caption="✅ MP3 তৈরি সম্পন্ন!")
            await msg.delete()
        else:
            await update.message.reply_text("❌ ফাইলটি কনভার্ট করা সম্ভব হয়নি।")
    except Exception as e:
        await update.message.reply_text(f"❌ এরর: {str(e)}")
    finally:
        if os.path.exists(v_path): os.remove(v_path)
        if os.path.exists(a_path): os.remove(a_path)

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(MessageHandler(filters.VIDEO, video_to_mp3))
    print("Bot is Live on Render...")
    app.run_polling()

if __name__ == '__main__':
    main()
