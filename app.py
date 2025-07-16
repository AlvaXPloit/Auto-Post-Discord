from flask import Flask, render_template, request, redirect, session, url_for
import os, json, threading, time, requests, random

app = Flask(__name__)
app.secret_key = 'alvaxploit_secret'

USER_FILE = "users.json"
CONFIG_DIR = "configs"
if not os.path.exists(CONFIG_DIR):
    os.mkdir(CONFIG_DIR)

posting_threads = {}

sad_quotes = [
    "Aku tersenyum, tapi hatiku sudah mati sejak lama.",
    "Kadang, diam adalah satu-satunya cara untuk menahan luka.",
    "Yang paling menyakitkan adalah berpura-pura tidak sakit.",
    "Aku capek jadi kuat terus, boleh nggak aku rapuh sebentar aja?",
    "Mereka bilang waktu menyembuhkan segalanya, tapi nyatanya tidak semua luka bisa sembuh.",
    "Aku baik-baik saja, itu kebohongan yang paling sering kuucap.",
    "Sendiri dalam ramai, sepi dalam sorak... itu aku.",
    "Kalau aku menghilang, mungkin tidak ada yang peduli.",
    "Aku hanya rindu... versi bahagia dari diriku.",
    "Tak semua tangis bisa terdengar... beberapa hanya terasa di dada."
]

def send_log(config, message, channel_id=None, success=True):
    log_webhook = config.get("log_webhook", "").strip()
    if not log_webhook:
        return

    try:
        now = time.strftime("%d %B %Y %I:%M:%S %p")
        embed = {
            "title": "🌃 AUTO POST LOGNYA LE",
            "description": f"```prolog\n{random.choice(sad_quotes)}\n```",
            "color": 0x8a2be2 if success else 0xff2f92,
            "fields": [
                {
                    "name": "💔 Status",
                    "value": f"> ✅ **Terkirim**" if success else f"> ❌ **Gagal dikirim**",
                    "inline": True
                },
                {
                    "name": "📡 Target",
                    "value": f"> <#{channel_id}>" if channel_id else "> Tidak Diketahui",
                    "inline": True
                },
                {
                    "name": "💬 Isi Pesan",
                    "value": f"```{message}```"
                },
                {
                    "name": "🕒 Waktu",
                    "value": f"> {now}",
                    "inline": True
                },
                {
                    "name": "🧪 Mode",
                    "value": "> Webhook" if config.get("use_webhook") else "> Token",
                    "inline": True
                }
            ],
            "footer": {
                "text": "「AutoPoster by AlvaXPloit」 - Semua luka tercatat",
                "icon_url": "https://cdn.discordapp.com/attachments/1222659397477097572/1226427380985126922/image.png"
            },
            "thumbnail": {
                "url": "https://pncakar.bigsentinel.asia/alva1.png"
            },
            "image": {
                "url": "https://pncakar.bigsentinel.asia/alva1.png"
            }
        }
        requests.post(log_webhook, json={"embeds": [embed]})
    except:
        pass

def get_config_path(username):
    return os.path.join(CONFIG_DIR, f"config_{username}.json")

def load_users():
    if not os.path.exists(USER_FILE):
        return {}
    with open(USER_FILE, "r") as f:
        return json.load(f)

def save_users(users):
    with open(USER_FILE, "w") as f:
        json.dump(users, f, indent=4)

def load_config(username):
    path = get_config_path(username)
    if os.path.exists(path):
        with open(path, "r") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return {"token": "", "use_webhook": False, "webhook_url": "", "log_webhook": "", "channels": []}
    return {"token": "", "use_webhook": False, "webhook_url": "", "log_webhook": "", "channels": []}

def save_config(username, config):
    with open(get_config_path(username), "w") as f:
        json.dump(config, f, indent=4)

def post_to_channel(ch, token, config, username):
    while posting_threads.get(username, False):
        try:
            if ch.get("message") and ch.get("id"):
                url = f"https://discord.com/api/v10/channels/{ch['id']}/messages"
                headers = {
                    "Authorization": token,
                    "Content-Type": "application/json"
                }
                data = { "content": ch["message"] }
                res = requests.post(url, headers=headers, json=data)
                success = res.status_code == 200
                send_log(config, ch["message"], ch["id"], success)
        except Exception as e:
            print(f"[ERROR] {e}")
            send_log(config, str(e), ch.get("id"), False)
        time.sleep(ch.get("interval", 60))

def start_posting(username):
    if posting_threads.get(username):
        return
    posting_threads[username] = True
    config = load_config(username)
    for ch in config.get("channels", []):
        threading.Thread(target=post_to_channel, args=(ch, config["token"], config, username), daemon=True).start()

def stop_posting(username):
    posting_threads[username] = False

@app.route("/", methods=["GET", "POST"])
def login():
    users = load_users()
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        if username in users and users[username] == password:
            session["user"] = username
            return redirect("/panel")
        return "Login gagal."
    return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    users = load_users()
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        if username in users:
            return "User sudah ada."
        users[username] = password
        save_users(users)
        return redirect("/")
    return render_template("login.html", mode="register")

@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect("/")

@app.route("/panel", methods=["GET", "POST"])
def panel():
    if "user" not in session:
        return redirect("/")
    username = session["user"]
    config = load_config(username)

    if request.method == "POST":
        token = request.form.get("token", "").strip()
        webhook_url = request.form.get("webhook_url", "").strip()
        log_webhook = request.form.get("log_webhook", "").strip()
        use_webhook = True if request.form.get("use_webhook") else False
        action = request.form.get("action")

        if token:
            config["token"] = token
        config["webhook_url"] = webhook_url
        config["log_webhook"] = log_webhook
        config["use_webhook"] = use_webhook

        channel_id = request.form.get("channel_id", "").strip()
        message = request.form.get("message", "").strip()
        try:
            hours = int(request.form.get("hours") or 0)
            minutes = int(request.form.get("minutes") or 0)
            seconds = int(request.form.get("seconds") or 0)
        except:
            hours = minutes = seconds = 0
        interval = hours * 3600 + minutes * 60 + seconds

        if action == "add" and channel_id and message:
            config["channels"].append({"id": channel_id, "message": message, "interval": interval})
        elif action == "edit":
            for ch in config["channels"]:
                if ch["id"] == channel_id:
                    ch["message"] = message
                    ch["interval"] = interval
        elif action == "remove":
            config["channels"] = [ch for ch in config["channels"] if ch["id"] != channel_id]
        elif action == "start":
            start_posting(username)
        elif action == "stop":
            stop_posting(username)

        save_config(username, config)
        return redirect("/panel")

    return render_template("index.html", config=config, config_json=json.dumps(config, indent=4))

@app.route("/test-webhook", methods=["POST"])
def test_webhook():
    if "user" not in session:
        return redirect("/")
    username = session["user"]
    config = load_config(username)
    if config.get("log_webhook"):
        send_log(config, "🧪 Test webhook berhasil oleh user: " + username, None, True)
    return redirect("/panel")

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
