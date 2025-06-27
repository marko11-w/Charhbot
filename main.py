import telebot
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
import json
import os
from flask import Flask, request

# ========== CONFIG ==========
TOKEN = "8005206366:AAFgMzmZzSLqRlN5uN09PKpJKjHzczKWr3c"
ADMIN_ID = 5397568684
CHANNEL_USERNAME = "MARK01i"
DATA_FILE = "data.json"
# ============================

bot = telebot.TeleBot(TOKEN)

# تحميل البيانات
if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, "w") as f:
        json.dump({"users": [], "admins": [ADMIN_ID]}, f)

def load_data():
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f)

def is_admin(user_id):
    data = load_data()
    return user_id in data["admins"]

def check_subscription(user_id):
    try:
        res = bot.get_chat_member(f"@{CHANNEL_USERNAME}", user_id)
        return res.status in ["member", "creator", "administrator"]
    except:
        return False

def main_menu(user_id):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("🎮 ببجي", "🔥 فري فاير")
    markup.add("🌀 فورتنايت", "💰 روبلوكس")
    markup.add("🎁 بطاقات شحن")
    if is_admin(user_id):
        markup.add("⚙️ إدارة البوت")
    return markup

@bot.message_handler(commands=["start"])
def start(message):
    user_id = message.from_user.id
    data = load_data()
    if user_id not in data["users"]:
        data["users"].append(user_id)
        save_data(data)
    if not check_subscription(user_id):
        join_btn = InlineKeyboardMarkup()
        join_btn.add(InlineKeyboardButton("اشترك في القناة 📢", url=f"https://t.me/{CHANNEL_USERNAME}"))
        bot.send_message(user_id, "يجب عليك الاشتراك في القناة أولاً لاستخدام البوت", reply_markup=join_btn)
        return
    bot.send_message(user_id, "مرحباً بك في بوت الشحن المجاني! اختر اللعبة:", reply_markup=main_menu(user_id))

@bot.message_handler(func=lambda m: m.text in ["🎮 ببجي", "🔥 فري فاير", "🌀 فورتنايت", "💰 روبلوكس", "🎁 بطاقات شحن"])
def fake_charge(message):
    user_id = message.from_user.id
    if not check_subscription(user_id):
        join_btn = InlineKeyboardMarkup()
        join_btn.add(InlineKeyboardButton("اشترك في القناة 📢", url=f"https://t.me/{CHANNEL_USERNAME}"))
        bot.send_message(user_id, "يجب عليك الاشتراك أولاً لاستخدام هذا الزر", reply_markup=join_btn)
        return
    msg = bot.send_message(user_id, "🔢 أرسل معرف الحساب أو رقم اللاعب:")
    bot.register_next_step_handler(msg, process_id)

def process_id(message):
    user_id = message.from_user.id
    bot.send_message(user_id, "🔄 جاري الاتصال بالسيرفر...")
    bot.send_message(user_id, "✅ تم الشحن بنجاح!
❗ هذا مجرد بوت وهمي للترفيه فقط.")

@bot.message_handler(func=lambda m: m.text == "⚙️ إدارة البوت")
def admin_panel(message):
    if not is_admin(message.from_user.id):
        return
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("👥 عدد المستخدمين", "📢 رسالة جماعية")
    markup.add("➕ إضافة أدمن", "➖ حذف أدمن")
    markup.add("↩️ رجوع")
    bot.send_message(message.chat.id, "🛠️ لوحة التحكم:", reply_markup=markup)

@bot.message_handler(func=lambda m: m.text == "👥 عدد المستخدمين")
def user_count(message):
    if not is_admin(message.from_user.id): return
    data = load_data()
    bot.send_message(message.chat.id, f"عدد المستخدمين: {len(data['users'])}")

@bot.message_handler(func=lambda m: m.text == "📢 رسالة جماعية")
def broadcast(message):
    if not is_admin(message.from_user.id): return
    msg = bot.send_message(message.chat.id, "📨 أرسل الرسالة الآن:")
    bot.register_next_step_handler(msg, process_broadcast)

def process_broadcast(message):
    data = load_data()
    for uid in data["users"]:
        try:
            bot.send_message(uid, message.text)
        except:
            continue
    bot.send_message(message.chat.id, "✅ تم إرسال الرسالة.")

@bot.message_handler(func=lambda m: m.text == "➕ إضافة أدمن")
def add_admin(message):
    if message.from_user.id != ADMIN_ID: return
    msg = bot.send_message(message.chat.id, "🆔 أرسل آيدي الأدمن الجديد:")
    bot.register_next_step_handler(msg, process_add_admin)

def process_add_admin(message):
    data = load_data()
    try:
        new_admin = int(message.text)
        if new_admin not in data["admins"]:
            data["admins"].append(new_admin)
            save_data(data)
            bot.send_message(message.chat.id, "✅ تم إضافة الأدمن.")
        else:
            bot.send_message(message.chat.id, "⚠️ هذا المستخدم موجود مسبقاً.")
    except:
        bot.send_message(message.chat.id, "❌ فشل في الإضافة.")

@bot.message_handler(func=lambda m: m.text == "➖ حذف أدمن")
def remove_admin(message):
    if message.from_user.id != ADMIN_ID: return
    msg = bot.send_message(message.chat.id, "🆔 أرسل آيدي الأدمن للحذف:")
    bot.register_next_step_handler(msg, process_remove_admin)

def process_remove_admin(message):
    data = load_data()
    try:
        remove_id = int(message.text)
        if remove_id in data["admins"] and remove_id != ADMIN_ID:
            data["admins"].remove(remove_id)
            save_data(data)
            bot.send_message(message.chat.id, "✅ تم حذف الأدمن.")
        else:
            bot.send_message(message.chat.id, "❌ لا يمكن حذف هذا المستخدم.")
    except:
        bot.send_message(message.chat.id, "❌ فشل في الحذف.")

@bot.message_handler(func=lambda m: m.text == "↩️ رجوع")
def back(message):
    bot.send_message(message.chat.id, "✅ عدنا إلى القائمة الرئيسية", reply_markup=main_menu(message.from_user.id))

# Webhook
app = Flask(__name__)

@app.route("/", methods=["GET"])
def index():
    return "Bot Running."

@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    json_string = request.get_data().decode("utf-8")
    update = telebot.types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return "OK"

bot.remove_webhook()
bot.set_webhook(url="https://found.up.railway.app/" + TOKEN)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
