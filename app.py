from flask import Flask, render_template, request, redirect, session, url_for
import os
import base64
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

UPLOAD_FOLDER = 'static/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# 仮のスタッフデータ
staff_users = {
    'staff1': 'password1',
    'staff2': 'password2'
}

# 仮の顧客データ
customers = [
    {'name': '山田 太郎', 'last_visit': '2025-04-01'},
    {'name': '佐藤 花子', 'last_visit': '2025-03-28'}
]

@app.route('/')
def index():
    if 'user' in session:
        return redirect(url_for('dashboard'))
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    if username in staff_users and staff_users[username] == password:
        session['user'] = username
        return redirect(url_for('dashboard'))
    return 'ログイン失敗！'

@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect(url_for('index'))
    return render_template('dashboard.html', customers=customers)

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('index'))

@app.route('/karte')
def karte():
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>カルテ入力</title>
        <style>
            canvas {
                border: 1px solid #ccc;
                touch-action: none;
            }
            button {
                margin: 10px;
                padding: 10px 20px;
                font-size: 16px;
            }
        </style>
    </head>
    <body>
        <h2>カルテをご記入ください</h2>
        <canvas id="canvas" width="500" height="400"></canvas><br>
        <button onclick="clearCanvas()">書き直す</button>
        <button onclick="submitCanvas()">送信</button>

        <form id="karteForm" method="POST" action="/save_karte">
            <input type="hidden" name="imageData" id="imageData">
        </form>

        <script>
            const canvas = document.getElementById('canvas');
            const ctx = canvas.getContext('2d');
            let drawing = false;

            canvas.addEventListener('pointerdown', (e) => {
                drawing = true;
                ctx.beginPath();
                ctx.moveTo(e.offsetX, e.offsetY);
            });

            canvas.addEventListener('pointermove', (e) => {
                if (!drawing) return;
                ctx.lineTo(e.offsetX, e.offsetY);
                ctx.stroke();
            });

            canvas.addEventListener('pointerup', () => {
                drawing = false;
            });

            function clearCanvas() {
                ctx.clearRect(0, 0, canvas.width, canvas.height);
            }

            function submitCanvas() {
                const imageData = canvas.toDataURL();
                document.getElementById('imageData').value = imageData;
                document.getElementById('karteForm').submit();
            }
        </script>
    </body>
    </html>
    '''

@app.route('/save_karte', methods=['POST'])
def save_karte():
    data_url = request.form['imageData']
    header, encoded = data_url.split(',', 1)
    binary_data = base64.b64decode(encoded)
    filename = datetime.now().strftime('%Y%m%d%H%M%S') + '.png'
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    with open(filepath, 'wb') as f:
        f.write(binary_data)
    return redirect(url_for('karte_list'))

@app.route('/karte_list')
def karte_list():
    if 'user' not in session:
        return redirect(url_for('index'))
    images = os.listdir(UPLOAD_FOLDER)
    images.sort(reverse=True)
    return render_template('karte_list.html', images=images)

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
