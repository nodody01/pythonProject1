from flask import Flask, render_template, request, jsonify
import qrcode
import sqlite3
import uuid
from datetime import datetime
import pytz
from flask_sslify import SSLify
import barcode
from barcode.writer import ImageWriter
from io import BytesIO as BinaryIO



app = Flask(__name__)
sslify = SSLify(app)

# === Инициализация БД ===
def get_db():
    return sqlite3.connect('database.db')

def init_db():
    conn = get_db()
    c = conn.cursor()

    # Таблица активных QR-кодов
    c.execute('''CREATE TABLE IF NOT EXISTS qr_codes
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  uuid TEXT UNIQUE,
                  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                  used INTEGER DEFAULT 0,
                  promoter_id INTEGER)''')

    # Таблица использованных QR-кодов
    c.execute('''CREATE TABLE IF NOT EXISTS used_qr_codes
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  qr_uuid TEXT,
                  scanned_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                  promoter_id INTEGER)''')
    conn.commit()
    conn.close()

# === Генерация QR-кода ===
def generate_barcode(uuid_str):
    # Используем формат CODE128
    code128 = barcode.get_barcode_class('code128')
    writer = ImageWriter()
    barcode_obj = code128(uuid_str, writer=writer)

    # Сохраняем как PNG
    filename = f"static/barcode_{uuid_str}"
    barcode_obj.save(filename)
    return f"{filename}.png"
# === Маршруты ===
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/promoter/<int:promoter_id>')
def promoter(promoter_id):
    if not (1 <= promoter_id <= 5):
        return "Неверный промоутер", 404

    new_uuid = str(uuid.uuid4())

    # Получаем текущее время в Москве
    moscow_tz = pytz.timezone('Europe/Moscow')
    current_time = datetime.now(moscow_tz).strftime('%Y-%m-%d %H:%M:%S')

    conn = get_db()
    c = conn.cursor()
    try:
        c.execute("INSERT INTO qr_codes (uuid, created_at, promoter_id) VALUES (?, ?, ?)",
                  (new_uuid, current_time, promoter_id))
        conn.commit()

        # Генерируем штрих-код
        barcode_path = generate_barcode(new_uuid)
    except sqlite3.IntegrityError as e:
        return f"Ошибка генерации штрих-кода: {str(e)}", 500
    finally:
        conn.close()

    return render_template('promoter.html', barcode_url=barcode_path, promoter_id=promoter_id)

@app.route('/qr/<uuid_str>.png')
def serve_qr(uuid_str):
    return open(f"static/qr_{uuid_str}.png", 'rb').read(), 200, {'Content-Type': 'image/png'}

@app.route('/scan')
def scan_page():
    return render_template('scan.html')

# @app.route('/api/scan', methods=['POST'])
# def scan_qr():
#     data = request.json
#     qr_uuid = data.get('uuid')
#
#     conn = get_db()
#     c = conn.cursor()
#
#     # Проверяем, есть ли такой QR и не использован ли он
#     c.execute("SELECT * FROM qr_codes WHERE uuid=? AND used=0", (qr_uuid,))
#     result = c.fetchone()
#
#     if result:
#         promoter_id = result[4]
#         # Переносим в used_qr_codes и помечаем как использованный
#         c.execute("INSERT INTO used_qr_codes (qr_uuid, promoter_id) VALUES (?, ?)", (qr_uuid, promoter_id))
#         c.execute("UPDATE qr_codes SET used=1 WHERE uuid=?", (qr_uuid,))
#         conn.commit()
#         conn.close()
#         return jsonify({"status": "success", "message": "QR-код активирован!"})
#     else:
#         conn.close()
#         return jsonify({"status": "error", "message": "QR-код уже был использован или не существует."})

@app.route('/api/scan', methods=['POST'])
def scan_qr():
    data = request.json
    qr_uuid = data.get('uuid')

    conn = get_db()
    c = conn.cursor()

    # Проверяем, есть ли такой QR и не использован ли он
    c.execute("SELECT * FROM qr_codes WHERE uuid=? AND used=0", (qr_uuid,))
    result = c.fetchone()

    if result:
        promoter_id = result[4]
        # Переносим в used_qr_codes и помечаем как использованный
        c.execute("INSERT INTO used_qr_codes (qr_uuid, promoter_id) VALUES (?, ?)", (qr_uuid, promoter_id))
        c.execute("UPDATE qr_codes SET used=1 WHERE uuid=?", (qr_uuid,))
        conn.commit()
        conn.close()
        return jsonify({"status": "success", "message": "QR-код активирован!"})
    else:
        conn.close()
        return jsonify({"status": "error", "message": "QR-код уже был использован или не существует."})


@app.route('/test-time')
def test_time():
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT created_at FROM qr_codes ORDER BY id DESC LIMIT 1")
    row = c.fetchone()
    conn.close()

    if row:
        db_time_str = row[0]
        moscow_tz = pytz.timezone('Europe/Moscow')
        utc_time = datetime.strptime(db_time_str, '%Y-%m-%d %H:%M:%S').replace(tzinfo=pytz.utc)
        local_time = utc_time.astimezone(moscow_tz)
        return f"Время из БД: {db_time_str} → Переведено в МСК: {local_time.strftime('%d.%m.%Y %H:%M:%S')}"
    else:
        return "Нет записей"


# === Запуск ===
if __name__ == '__main__':
    init_db()
    print("✅ Сервер готов к запуску...")
    app.run(host='0.0.0.0',port=5000, debug=True)