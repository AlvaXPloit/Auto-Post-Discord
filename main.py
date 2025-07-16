from flask import Flask, render_template, request, redirect
import json, time, threading, os, requests

app = Flask(__name__)
CONFIG_DIR = "configs"
os.makedirs(CONFIG_DIR, exist_ok=True)
posting_active = {}

def get_user_config(name):
    path = os.path.join(CONFIG_DIR, f"{name}.json")
    if os.path.exists(path):
        with open(path, "r") as f:
            return json.load(f)
    return {"token": "", "use_webhook": False, "webhook_url": "", "log_webhook": "", "channels": []}

def save_user_config(name, config):
    path = os.path.join(CONFIG_DIR, f"{name}.json")
    with open(path, "w") as f:
        json.dump(config, f, indent=4)

@app.route("/", methods=["GET", "POST"])
def index():
    name = request.args.get("name", "default")
    config = get_user_config(name)
    return render_template("index.html", config=config, config_json=json.dumps(config, indent=4), name=name)

@app.route("/save-config", methods=["POST"])
def save():
    name = request.args.get("name", "default")
    config = get_user_config(name)

    config["token"] = request.form.get("token", "").strip()
    config["webhook_url"] = request.form.get("webhook_url", "").strip()
    config["log_webhook"] = request.form.get("log_webhook", "").strip()
    config["use_webhook"] = True if request.form.get("use_webhook") else False

    channel_id = request.form.get("channel_id")
    message = request.form.get("message")
    try:
        interval = int(request.form.get("hours") or 0) * 3600 + int(request.form.get("minutes") or 0) * 60 + int(request.form.get("seconds") or 0)
    except:
        interval = 0

    action = request.form.get("action")
    if action == "add" and channel_id and message:
        config["channels"].append({"id": channel_id, "message": message, "interval": interval})
    elif action == "edit":
        for ch in config["channels"]:
            if ch["id"] == channel_id:
                ch["message"] = message
                ch["interval"] = interval
    elif action == "remove":
        config["channels"] = [ch for ch in config["channels"] if ch["id"] != channel_id]

    save_user_config(name, config)
    return redirect(f"/?name={name}")

@app.route("/load-config", methods=["POST"])
def load():
    name = request.args.get("name", "default")
    get_user_config(name)
    return redirect(f"/?name={name}")

@app.route("/start", methods=["POST"])
def start():
    name = request.args.get("name", "default")
    config = get_user_config(name)
    if not posting_active.get(name):
        posting_active[name] = True
        threading.Thread(target=auto_post, args=(name, config), daemon=True).start()
    return redirect(f"/?name={name}")

@app.route("/stop", methods=["POST"])
def stop():
    name = request.args.get("name", "default")
    posting_active[name] = False
    return redirect(f"/?name={name}")

@app.route("/test-webhook", methods=["POST"])
def test_webhook():
    name = request.args.get("name", "default")
    config = get_user_config(name)
    send_log("Test webhook berhasil dikirim 🎯", config=config)
    return redirect(f"/?name={name}")

def send_log(message, channel_id=None, success=True, config=None):
    if config and config.get("log_webhook"):
        try:
            now = time.strftime("%d %B %Y %I:%M:%S %p")
            embed = {
                "title": "✨ Auto Poster Log ✨",
                "description": "**📢 Log Message from Auto Poster**",
                "color": 65280 if success else 16711680,
                "fields": [
                    {"name": "📶 Status", "value": "✅ Success" if success else "❌ Failed", "inline": True},
                    {"name": "📺 Channel", "value": f"<#{channel_id}>" if channel_id else "-", "inline": True},
                    {"name": "📄 Message", "value": message, "inline": False},
                    {"name": "🕓 Time", "value": now, "inline": False}
                ],
                "footer": {"text": "Auto Poster by AlvaXPloit", "icon_url": "https://pncakar.bigsentinel.asia/alva1.png"}
            }
            requests.post(config["log_webhook"], json={"embeds": [embed]})
        except Exception as e:
            print("Log error:", e)

def post_to_channel(user, ch):
    config = get_user_config(user)
    while posting_active.get(user):
        try:
            url = f"https://discord.com/api/v10/channels/{ch['id']}/messages"
            headers = {
                "Authorization": config["token"],
                "Content-Type": "application/json"
            }
            data = {"content": ch["message"]}
            res = requests.post(url, headers=headers, json=data)
            if res.status_code in [200, 204]:
                send_log(f"Pesan terkirim ke <#{ch['id']}>.", ch["id"], True, config)
            else:
                send_log(f"Gagal kirim ke <#{ch['id']}>: {res.status_code} - {res.text}", ch["id"], False, config)
        except Exception as e:
            send_log(f"Error saat kirim ke <#{ch['id']}>: {e}", ch["id"], False, config)
        time.sleep(ch["interval"])

def auto_post(user, config):
    for ch in config["channels"]:
        threading.Thread(target=post_to_channel, args=(user, ch), daemon=True).start()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
