import telebot
import requests
import logging
import time

BOT_TOKEN = "8259860669:AAHYX_xP89PODqAP95v0SW22S0Y-kHyp2xQ"
ADMIN_ID = 7482359374

API_URL = "https://royalthakur.xyz/api/add_task.php"
HEADERS = {
    "User-Agent": "ROYALTHAKUR royal"
}

# logs (SOUL style)
logging.basicConfig(
    filename="bot.log",
    level=logging.INFO,
    format="%(asctime)s | BOT | %(message)s"
)

bot = telebot.TeleBot(BOT_TOKEN)
cooldown = {}

COOLDOWN_SECONDS = 30


def check_cooldown(uid):
    if uid in cooldown and time.time() - cooldown[uid] < COOLDOWN_SECONDS:
        return False
    cooldown[uid] = time.time()
    return True


@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(
        message,
        "👑 ROYAL SOUL BOT READY\n\n"
        "Command:\n"
        "/game IP PORT TIME\n\n"
        "Example:\n"
        "/game 1.1.1.1 80 120"
    )
    logging.info(f"START user={message.from_user.id}")


@bot.message_handler(commands=['game'])
def game(message):
    uid = message.from_user.id

    if not check_cooldown(uid):
        bot.reply_to(message, "⏳ Cooldown active, wait 30 seconds")
        logging.warning(f"COOLDOWN user={uid}")
        return

    try:
        args = message.text.split()
        if len(args) != 4:
            bot.reply_to(message, "❌ Usage: /game IP PORT TIME")
            return

        ip = args[1]
        port = args[2]
        time_sec = args[3]

        data = {
            "ip": ip,
            "port": port,
            "time": time_sec
        }

        r = requests.post(API_URL, headers=HEADERS, data=data, timeout=10)

        if r.status_code == 200:
            res = r.json()
            if res.get("status") == "OK":
                bot.reply_to(
                    message,
                    f"✅ TASK QUEUED\n\nIP: {ip}\nPORT: {port}\nTIME: {time_sec}s"
                )
                logging.info(
                    f"TASK_ADDED user={uid} ip={ip} port={port} time={time_sec}"
                )
            else:
                bot.reply_to(message, "❌ API DENIED")
                logging.error(f"API_DENIED response={res}")
        else:
            bot.reply_to(message, f"❌ HTTP ERROR {r.status_code}")
            logging.error(f"HTTP_ERROR code={r.status_code}")

    except Exception as e:
        logging.exception("BOT_EXCEPTION")
        bot.reply_to(message, "❌ INTERNAL ERROR")


print("ROYAL SOUL BOT RUNNING…")
bot.infinity_polling()