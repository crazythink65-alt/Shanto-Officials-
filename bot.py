import os
import threading
from flask import Flask
import telebot
import requests

app = Flask('')

@app.route('/')
def home():
    return "Bot is running!"

def run_flask():
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)

TELEGRAM_TOKEN = '8920844441:AAEJfiziyjO5LcQyPWRommGpf_Ow1IJvZx8'
GEMINI_API_KEY 

bot = telebot.TeleBot(TELEGRAM_TOKEN)

# ব্যবহারকারীদের আগের চ্যাট হিস্ট্রি রাখার জন্য মেমোরি ডিকশনারি
user_history = {}

@bot.message_handler(commands=['start'])
def send_welcome(message):
    first_name = message.from_user.first_name or "বন্ধু"
    text = (
        f"স্বাগতম {first_name}! 🌐\n\n"
        "আমাদের ওয়েবসাইট:\nhttps://crazythink65-alt.github.io/Shanto-Officials-/\n\n"
        "আমাদের ফেসবুক পেজ:\nhttps://www.facebook.com/shanto6571"
    )
    bot.send_message(message.chat.id, text)

@bot.message_handler(func=lambda message: True)
def ai_reply(message):
    try:
        user_id = message.chat.id
        # টেলিগ্রাম থেকে ব্যবহারকারীর নাম নেওয়া
        first_name = message.from_user.first_name or "ব্যবহারকারী"
        username = message.from_user.username or "নাই"

        # নতুন ইউজার হলে হিস্ট্রি শুরু করা
        if user_id not in user_history:
            user_history[user_id] = []

        # ব্যবহারকারীর মেসেজ হিস্ট্রিতে যোগ করা
        user_history[user_id].append({"role": "user", "parts": [{"text": message.text}]})

        # শুধুমাত্র সাম্প্রতিক ৫টি মেসেজ মনে রাখবে (মেমোরি ঠিক রাখার জন্য)
        if len(user_history[user_id]) > 10:
            user_history[user_id] = user_history[user_id][-10:]

        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.8-flash:generateContent?key={GEMINI_API_KEY}"
        
        system_instruction = (
            f"তুমি Shanto Officials-এর একজন বন্ধুত্বপূর্ণ সহকারী। "
            f"তুমি যার সাথে কথা বলছ তার নাম '{first_name}' (টেলিগ্রাম ইউজারনেম: @{username})। "
            f"তাকে নাম ধরে সম্বোধন করবে এবং সহজ ও স্বাভাবিক বাংলায় কথা বলবে।"
        )

        payload = {
            "system_instruction": {"parts": [{"text": system_instruction}]},
            "contents": user_history[user_id]
        }
        
        headers = {'Content-Type': 'application/json'}
        response = requests.post(url, json=payload, headers=headers)
        res_data = response.json()
        
        if 'candidates' in res_data:
            ai_text = res_data['candidates'][0]['content']['parts'][0]['text']
            # বটের উত্তর হিস্ট্রিতে যোগ করা
            user_history[user_id].append({"role": "model", "parts": [{"text": ai_text}]})
            bot.reply_to(message, ai_text)
        else:
            bot.reply_to(message, f"দুঃখিত {first_name}, আমি বুঝতে পারিনি।")
    except Exception as e:
        print(f"Error: {e}")
        bot.reply_to(message, "কোথাও কোনো সমস্যা হয়েছে!")

if __name__ == '__main__':
    threading.Thread(target=run_flask).start()
    print("AI Bot with Memory is running...")
    bot.infinity_polling()
