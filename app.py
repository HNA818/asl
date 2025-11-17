# -------------------------------------------------------------
#  Account Generator Web App (Flask) — Python
#  Includes:
#  ✔ User Panel
#  ✔ Admin Panel
#  ✔ Key System
#  ✔ email:password format
#  ✔ Dark Mode design
# -------------------------------------------------------------

from flask import Flask, request, render_template_string, send_file, session
import random
import json
import os

app = Flask(__name__)
app.secret_key = "SUPER_KEY_CHANGE"

KEYS_FILE = "keys.json"
ADMIN_PASS = "admin2025"

# Ensure keys file exists
if not os.path.exists(KEYS_FILE):
    with open(KEYS_FILE, "w") as f:
        json.dump({"keys": []}, f)


def load_keys():
    with open(KEYS_FILE, "r") as f:
        return json.load(f)

def save_keys(data):
    with open(KEYS_FILE, "w") as f:
        json.dump(data, f, indent=4)

# ------------------------
# User Panel HTML
# ------------------------
USER_HTML = """
<!DOCTYPE html>
<html>
<head>
<title>Account Generator</title>
<style>
body { background:#0d0d0d; color:white; font-family:Arial; text-align:center; }
.box { margin-top:120px; }
input, button { padding:10px; border-radius:8px; margin:8px; border:none; }
input { width:300px; }
button { background:#1e90ff; color:white; cursor:pointer; }
button:hover { background:#0099ff; }
textarea { width:90%; height:400px; background:#111; color:#1e90ff; padding:10px; border-radius:8px; }
.error { color:red; margin-top:10px; }
</style>
</head>
<body>
<div class='box'>
<h1>🎉 مولد حسابات email:password</h1>
<form method="POST">
<input name='key' placeholder='ادخل المفتاح' required><br>
<input name='count' type='number' placeholder='عدد الحسابات (حتى مليون)' required><br>
<input name='domains' placeholder='أكتب الدومينات (gmail.com, yahoo.com...)' required><br>
<button type='submit'>توليد الحسابات</button>
</form>
{% if error %}<p class='error'>{{error}}</p>{% endif %}
</div>
</body>
</html>
"""

# ------------------------
# Results HTML
# ------------------------
RESULTS_HTML = """
<!DOCTYPE html>
<html>
<head>
<title>النتائج</title>
<style>
body { background:#0d0d0d; color:white; font-family:Arial; text-align:center; }
textarea { width:90%; height:450px; background:#111; color:#1e90ff; padding:10px; border-radius:8px; margin-top:20px; }
</style>
</head>
<body>
<h1>📄 النتائج</h1>
<textarea readonly>{% for r in results %}{{r}}\n{% endfor %}</textarea><br>
<a href="/download">⬇️ تحميل الملف</a>
</body>
</html>
"""

# ------------------------
# Admin Panel HTML
# ------------------------
ADMIN_HTML = """
<!DOCTYPE html>
<html>
<head>
<title>Admin Panel</title>
<style>
body { background:#0d0d0d; color:white; font-family:Arial; text-align:center; }
button { background:#1e90ff; padding:10px 20px; border:none; color:white; border-radius:8px; cursor:pointer; margin:10px; }
button:hover { background:#0099ff; }
.key-box { background:#111; padding:10px; margin:10px auto; width:300px; border-radius:8px; color:#1e90ff; }
input { padding:10px; border-radius:8px; border:none; }
</style>
</head>
<body>
<h1>🔐 Admin Panel</h1>
<form method="POST">
<button name="create" value="1">إنشاء مفتاح جديد</button>
</form>
<h2>المفاتيح الحالية</h2>
{% for key in keys %}
<div class='key-box'>
{{key}}
<form method="POST">
<button name="delete" value="{{key}}">حذف</button>
</form>
</div>
{% endfor %}
</body>
</html>
"""

# ------------------------
# Routes
# ------------------------
@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "GET":
        return render_template_string(USER_HTML)

    key = request.form["key"]
    count = int(request.form["count"])
    domains = [d.strip() for d in request.form["domains"].split(",")]

    db = load_keys()

    if key not in db["keys"]:
        return render_template_string(USER_HTML, error="❌ المفتاح غير صالح")

    accounts = []
    for _ in range(min(count, 1_000_000)):
        user = "".join(random.choices("abcdefghijklmnopqrstuvwxyz0123456789", k=10))
        pwd = "".join(random.choices("ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%", k=12))
        domain = random.choice(domains)
        accounts.append(f"{user}@{domain}:{pwd}")

    with open("accounts.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(accounts))

    session["results"] = accounts
    return render_template_string(RESULTS_HTML, results=accounts)


@app.route("/download")
def download():
    return send_file("accounts.txt", as_attachment=True)


@app.route("/admin", methods=["GET", "POST"])
def admin():
    pw = request.args.get("pw")
    if pw != ADMIN_PASS:
        return "❌ ممنوع — كلمة المرور خاطئة"

    db = load_keys()

    if request.method == "POST" and "create" in request.form:
        new_key = "".join(random.choices("ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789", k=20))
        db["keys"].append(new_key)
        save_keys(db)

    if request.method == "POST" and "delete" in request.form:
        key_to_delete = request.form["delete"]
        if key_to_delete in db["keys"]:
            db["keys"].remove(key_to_delete)
            save_keys(db)

    return render_template_string(ADMIN_HTML, keys=db["keys"])

# ------------------------
# Run App
# ------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
