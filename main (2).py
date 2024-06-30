from flask import Flask, request
import telebot
from telebot import types

API_TOKEN = '6512295390:AAHTDsqzM0IQoP5I1pV8rkjEoJIb3iILJTc'  # استبدل بتوكن البوت الخاص بك هنا
bot = telebot.TeleBot(API_TOKEN)

# هيكلية البيانات لتخزين مواقع الويب والمشاهدات والنقاط والمستخدمين
websites = {}
user_points = {}
users = {}

# قائمة معرفات الأدمن
ADMIN_IDS = [6814152338]  # استبدل هذه بالقيم الفعلية لمعرفات الأدمن

app = Flask(__name__)

# وظيفة لبدء المحادثة
@app.route('/start', methods=['POST'])
def start_message():
    message = request.get_json()
    chat_id = message['message']['chat']['id']
    users[chat_id] = message['message']['chat']['username']
    print(f"User ID: {chat_id}")  # طباعة معرف المستخدم
    markup = types.ReplyKeyboardMarkup(row_width=2)
    add_btn = types.KeyboardButton('إدخال رابط موقع الويب')
    view_btn = types.KeyboardButton('مشاهدة مواقع الويب')
    points_btn = types.KeyboardButton('النقاط')
    if chat_id in ADMIN_IDS:
        admin_btn = types.KeyboardButton('لوحة الإدارة')
        markup.add(add_btn, view_btn, points_btn, admin_btn)
    else:
        markup.add(add_btn, view_btn, points_btn)
    bot.send_message(chat_id, "أهلاً بك! اختر أحد الخيارات التالية:", reply_markup=markup)

    return "OK"

# وظيفة لإدخال رابط موقع الويب وعدد المشاهدات
@app.route('/add_website', methods=['POST'])
def add_website():
    message = request.get_json()
    chat_id = message['message']['chat']['id']
    msg = bot.send_message(chat_id, "أدخل رابط موقع الويب:")
    bot.register_next_step_handler(msg, process_website)

    return "OK"

def process_website(message):
    chat_id = message.chat.id
    url = message.text
    msg = bot.send_message(chat_id, "أدخل عدد المشاهدات:")
    bot.register_next_step_handler(msg, process_views, url)

def process_views(message, url):
    try:
        views = int(message.text)
        websites[url] = views
        bot.send_message(message.chat.id, f"تم إضافة الموقع: {url} بعدد مشاهدات: {views}")
    except ValueError:
        bot.send_message(message.chat.id, "يرجى إدخال عدد صحيح للمشاهدات.")

# وظيفة لمشاهدة مواقع الويب المدخلة
@app.route('/view_websites', methods=['POST'])
def view_websites():
    message = request.get_json()
    chat_id = message['message']['chat']['id']
    if websites:
        for url, views in websites.items():
            bot.send_message(chat_id, f"الموقع: {url}\nالمشاهدات المتبقية: {views}")
    else:
        bot.send_message(chat_id, "لا توجد مواقع ويب مضافة بعد.")

    return "OK"

# وظيفة لعرض النقاط
@app.route('/show_points', methods=['POST'])
def show_points():
    message = request.get_json()
    chat_id = message['message']['chat']['id']
    user_id = chat_id
    points = user_points.get(user_id, 0)
    bot.send_message(chat_id, f"لديك {points} نقطة.")

    return "OK"

# وظيفة لحساب النقاط عند مشاهدة موقع ويب
@app.route('/visit_website', methods=['POST'])
def visit_website():
    message = request.get_json()
    call = telebot.types.CallbackQuery.de_json(message)
    url = call.data.split('_')[1]
    if websites[url] > 0:
        websites[url] -= 1
        user_id = call.from_user.id
        user_points[user_id] = user_points.get(user_id, 0) + 1
        bot.send_message(call.message.chat.id, f"تم مشاهدة الموقع: {url}. لقد حصلت على نقطة!")
    else:
        bot.send_message(call.message.chat.id, "لم يتبقى مشاهدات لهذا الموقع.")

    return "OK"

# وظيفة لعرض لوحة الإدارة
@app.route('/admin_panel', methods=['POST'])
def admin_panel():
    message = request.get_json()
    chat_id = message['message']['chat']['id']
    if chat_id in ADMIN_IDS:
        admin_markup = types.ReplyKeyboardMarkup(row_width=2)
        add_points_btn = types.KeyboardButton('إضافة نقاط للمستخدم')
        view_users_btn = types.KeyboardButton('عرض المستخدمين والنقاط')
        admin_markup.add(add_points_btn, view_users_btn)
        bot.send_message(chat_id, "أهلاً بك في لوحة الإدارة! اختر أحد الخيارات التالية:", reply_markup=admin_markup)
    else:
        bot.send_message(chat_id, "ليس لديك صلاحيات للوصول إلى لوحة الإدارة.")

    return "OK"

# وظيفة لعرض أسماء المستخدمين والنقاط
@app.route('/view_users', methods=['POST'])
def view_users():
    message = request.get_json()
    chat_id = message['message']['chat']['id']
    if users:
        for user_id, username in users.items():
            points = user_points.get(user_id, 0)
            bot.send_message(chat_id, f"المستخدم: {username}\nالنقاط: {points}")
    else:
        bot.send_message(chat_id, "لا يوجد مستخدمون مسجلون بعد.")

    return "OK"

# وظيفة لإضافة نقاط للمستخدمين
@app.route('/add_points', methods=['POST'])
def add_points():
    message = request.get_json()
    chat_id = message['message']['chat']['id']
    msg = bot.send_message(chat_id, "أدخل اسم المستخدم:")
    bot.register_next_step_handler(msg, process_user)

    return "OK"

def process_user(message):
    username = message.text
    user_id = None
    for uid, uname in users.items():
        if uname == username:
            user_id = uid
            break
    if user_id:
        msg = bot.send_message(message.chat.id, "أدخل عدد النقاط:")
        bot.register_next_step_handler(msg, process_points, user_id)
    else:
        bot.send_message(message.chat.id, "اسم المستخدم غير موجود.")

def process_points(message, user_id):
    try:
        points = int(message.text)
        user_points[user_id] = user_points.get(user_id, 0) + points
        bot.send_message(message.chat.id, f"تم إضافة {points} نقطة للمستخدم {users[user_id]}.")
    except ValueError:
        bot.send_message(message.chat.id, "يرجى إدخال عدد صحيح للنقاط.")

# بدء البوت
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)
