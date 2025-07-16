# 🖤 AutoPoster by AlvaXPloit

AutoPoster multi-user untuk Discord. Bisa kirim pesan berkala via Token atau Webhook ke berbagai channel. Dibangun dengan Flask + HTML sad vibes aesthetic.

> “Aku hanya rindu... versi bahagia dari diriku.” – AlvaXPloit

---

## 🌐 Fitur Utama

* Multi Sender Discord
* Custom Delay 
* Can be Active For Up To A Year Unless The VPS is Down

---

## 🧠 Teknologi

* Python 3
* Flask
* HTML + CSS (dark aesthetic)
* Discord API

---

## 📦 Struktur Folder

```
.
├── app.py               # Backend utama Flask
├── templates/
│   ├── index.html       # UI Panel
│   └── login.html       # UI Login/Register
├── users.json           # Data user login
├── configs/             # Folder config per user
└── README.md            # Dokumentasi
```

---

## 🚀 Instalasi di VPS

1. **Upload ke VPS atau clone:**

```bash
git clone https://github.com/alvaxploit/autoposter.git
cd autoposter
```

2. **Install dependency Python:**

```bash
sudo apt update
sudo apt install python3 python3-pip -y
pip3 install flask requests
```

3. **Jalankan server:**

```bash
python3 app.py
```

4. **Akses di browser:**

```
http://YOUR-VPS-IP:5000
```
----------------------------------------------------------------
bisa juga kalian deploy pake gunicorn+Nginx+Domain ini cara2nya:
----------------------------------------------------------------
# 🚀 Deploy Flask App ke VPS (Gunicorn + Nginx + Domain)

Panduan singkat untuk menjalankan aplikasi Flask di VPS menggunakan **Gunicorn** sebagai application server dan **Nginx** sebagai reverse proxy. Dilengkapi dukungan domain dan SSL (opsional).

---

## 📦 Langkah-langkah Deploy

```bash
# 📁 1. Upload Project ke VPS
scp -P yourport autoposter1.zip username@yourdomain/ip:/var/www/html/

# 🔧 2. Setup di VPS
ssh -P yourport username@yourdomain/ip
cd /var/www/html/
unzip autoposter1.zip
cd autoposter

# 📦 3. Install Dependensi
sudo apt update && sudo apt install python3-pip nginx unzip -y
pip3 install flask gunicorn

# 🧱 4. Jalankan Gunicorn sebagai daemon
gunicorn --bind 127.0.0.1:5000 app:app --daemon

# 🚫 Jika Port 80 Sudah Dipakai Apache
# ❌ Matikan Apache jika aktif
sudo systemctl stop apache2
sudo systemctl disable apache2

# 🌐 5. Konfigurasi Nginx
sudo nano /etc/nginx/sites-available/yourdomain

# ✍️ Isi konfigurasi:
# --------------------------
server {
    listen 80;
    server_name yourdomain;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
# --------------------------

# 🔗 Aktifkan Konfigurasi Nginx
sudo ln -s /etc/nginx/sites-available/yourdomain /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx

# 🔒 (Opsional) Tambahkan HTTPS/SSL via Certbot
sudo apt install certbot python3-certbot-nginx -y
sudo certbot --nginx -d yourdomain


## 🧪 Cara Pakai

### 🔐 Login & Register

* Akses `/register` untuk buat akun
* Lalu login di `/`
* Setelah login, otomatis diarahkan ke `/panel`

### ⚙️ Pengaturan Panel

* Masukkan Token (atau centang "Use Webhook" dan isi URL)
* Masukkan Channel ID & pesan
* Atur interval dalam detik/menit/jam
* Klik **Add Channel**, lalu **Save Config**
* Klik **Start Auto Post**
* Webhook Log akan mencatat status

---

## 🧪 Quotes Sedih di Webhook Log

> "Aku baik-baik saja, itu kebohongan yang paling sering kuucap."
>
> "Kalau aku menghilang, mungkin tidak ada yang peduli."
>
> "Sendiri dalam ramai, sepi dalam sorak... itu aku."

Quotes ini muncul otomatis di embed webhook setiap kali proses autopost berjalan.

---

## 🖤 Credit & Support

> Dibuat dengan air mata dan semangat luka digital oleh:

### 👨‍💻 AlvaXPloit (Developer utama)

* Instagram: `@alvaxploit`
* Web Demo: [https://botwa.bigsentinel.asia](https://botwa.bigsentinel.asia)
* Pentest Tools Web/Tools Online : [https://pncakar.bigsentinel.asia/alva.php](https://pncakar.bigsentinel.asia/alva.php)
* Wa: +6283198153323

---

> “Mereka bilang waktu menyembuhkan segalanya, tapi nyatanya tidak semua luka bisa sembuh.”
> — AutoPoster by AlvaXPloit
