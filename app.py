from flask import Flask, render_template, request, redirect, url_for, session, flash, send_file
import json, os, subprocess
from io import BytesIO
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'hallo'

CATS_FILE = 'cats.json'
SETTINGS_FILE = 'settings.json'
UPLOAD_MODEL_FOLDER = 'models'
UPLOAD_IMAGE_FOLDER = 'data'
ALLOWED_MODEL_EXTENSIONS = {'keras'}

# Kamera initialisieren (wird hier nicht für Snapshot genutzt)
# CAMERA = cv2.VideoCapture(0, cv2.CAP_V4L2)

def load_json(path):
    if not os.path.exists(path) or os.stat(path).st_size == 0:
        with open(path, 'w') as f:
            json.dump({}, f)
    with open(path, 'r') as f:
        return json.load(f)

def save_json(path, data):
    with open(path, 'w') as f:
        json.dump(data, f, indent=2)

def allowed_model(fn):
    return '.' in fn and fn.rsplit('.', 1)[1].lower() in ALLOWED_MODEL_EXTENSIONS

@app.route('/', methods=['GET','POST'])
def login():
    error = False
    if request.method == 'POST':
        if request.form['password'] == app.secret_key:
            session['logged_in'] = True
            return redirect(url_for('index'))
        error = True
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('login'))

@app.route('/home')
def index():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    cats = load_json(CATS_FILE)
    settings = load_json(SETTINGS_FILE)
    return render_template('index.html', cats=cats, settings=settings)

@app.route('/add_cat', methods=['POST'])
def add_cat():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    name = request.form['name'].lower().strip()
    ration_total = request.form['ration_total']
    if not name or not ration_total.isdigit():
        flash("Name und Ration müssen korrekt angegeben werden!")
        return redirect(url_for('index'))

    model = request.files.get('model')
    images = request.files.getlist('images')

    if model and allowed_model(model.filename):
        os.makedirs(UPLOAD_MODEL_FOLDER, exist_ok=True)
        filename = secure_filename(f"model_{name}.keras")
        model.save(os.path.join(UPLOAD_MODEL_FOLDER, filename))
    elif images and any(img.filename for img in images):
        new_images = len([img for img in images if img.filename])

        if new_images >= 300:
            folder = os.path.join(UPLOAD_IMAGE_FOLDER, name)
            os.makedirs(folder, exist_ok=True)
            for img in images:
                if img.filename:
                  
                    filename = os.path.basename(img.filename)
                    img.save(os.path.join(folder, secure_filename(filename)))

         
            subprocess.Popen([
                "bash", "-lc",
                "source /home/lukasadmin/venvs/venv-maturaarbeit/bin/activate && python3 /home/lukasadmin/automatic-feeding-automat-software/train_model.py"
            ])
        else:
            flash(f"Es müssen mindestens 300 Bilder vorhanden sein. Aktuell wären es nur {new_images}.")
            return redirect(url_for('index'))

    else:
        flash("Bitte entweder ein Modell oder mindestens 300 Bilder hochladen!")
        return redirect(url_for('index'))

    cats = load_json(CATS_FILE)
    cats[name] = {'ration_total': int(ration_total), 'ration_left': int(ration_total)}
    save_json(CATS_FILE, cats)
    return redirect(url_for('index'))

@app.route('/delete_cat/<cat_name>')
def delete_cat(cat_name):
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    cats = load_json(CATS_FILE)
    key = cat_name.lower()
    if key in cats:
        del cats[key]
        save_json(CATS_FILE, cats)
    return redirect(url_for('index'))

@app.route('/update_settings', methods=['POST'])
def update_settings():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    split = 'split_ration' in request.form
    settings = {'split_ration': split}
    if split:
        m = request.form['time_morning']
        e = request.form['time_evening']
        if m.isdigit() and e.isdigit() and 0 <= int(m) <= 23 and 0 <= int(e) <= 23:
            settings['time_morning'] = int(m)
            settings['time_evening'] = int(e)
    save_json(SETTINGS_FILE, settings)
    return redirect(url_for('index'))

@app.route('/start_main')
def start_main():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    subprocess.Popen([
        "bash", "-lc",
        "source /home/lukasadmin/venvs/venv-maturaarbeit/bin/activate && python3 /home/lukasadmin/automatic-feeding-automat-software/main.py"
    ])
    return redirect(url_for('index'))

@app.route('/snapshot')
def snapshot():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    result = subprocess.run([
        'libcamera-jpeg',
        '-o', '-',
        '--timeout', '1',
        '--width', '640',
        '--height', '480'
    ], stdout=subprocess.PIPE)
    return send_file(BytesIO(result.stdout),
                    mimetype='image/jpeg',
                    max_age=0)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
