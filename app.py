from flask import Flask, render_template, request, redirect, url_for, session, flash, send_file
import json, os, subprocess
from io import BytesIO
from werkzeug.utils import secure_filename
from subprocess import Popen, TimeoutExpired

app = Flask(__name__)
app.secret_key = 'hallo'

CATS_FILE = 'cats.json'
SETTINGS_FILE = 'settings.json'
UPLOAD_MODEL_FOLDER = 'models'
UPLOAD_IMAGE_FOLDER = 'data'
ALLOWED_MODEL_EXTENSIONS = {'keras'}
NUMBER_OF_PICTURES = 300

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

process = None

@app.route('/get_image_count/<cat_name>')
def get_image_count(cat_name):
    folder = os.path.join(UPLOAD_IMAGE_FOLDER, cat_name)
    if os.path.exists(folder):
        image_count = len([f for f in os.listdir(folder) if os.path.isfile(os.path.join(folder, f))])
        return {"image_count": image_count}
    return {"image_count": 0}

@app.route('/take_pictures_page')
def take_pictures_page():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    cat_name = request.args.get('cat_name', '').lower()
    image_count = None
    if cat_name and cat_name.isalpha():
        folder = os.path.join(UPLOAD_IMAGE_FOLDER, cat_name)
        if os.path.exists(folder):
            image_count = len([f for f in os.listdir(folder) if os.path.isfile(os.path.join(folder, f))])

    return render_template('take_pictures.html', image_count=image_count, cat_name=cat_name)

@app.route('/start_take_pictures', methods=['POST'])
def start_take_pictures():
    global process
    cat_name = request.form['cat_name'].lower()

    if not cat_name.isalpha():
        flash('Only lowercase letters allowed.')
        return redirect(url_for('take_pictures_page'))

    try:
        # Alten Prozess beenden falls vorhanden
        if process:
            try:
                process.terminate()
                process.wait(timeout=3)
            except TimeoutExpired:
                process.kill()

        # Neuen Prozess starten
        venv_python = "/home/lukasadmin/venvs/venv-maturaarbeit/bin/python"
        script_path = "/home/lukasadmin/automatic-feeding-automat-software/take_pictures.py"
        process = Popen(
            [venv_python, script_path, cat_name],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT
        )
        
        flash(f'Image capture started for {cat_name}.')
        
    except Exception as e:
        flash(f'Fehler: {str(e)}')
        if process:
            process_output = process.stdout.read().decode()
            flash(f'Process output: {process_output}')
    
    return redirect(url_for('take_pictures_page', cat_name=cat_name))

@app.route('/stop_take_pictures', methods=['POST'])
def stop_take_pictures():
    global process
    cat_name = request.form.get('cat_name', '').lower()
    if process:
        process.terminate()
        process = None
        flash(f'Image capture for {cat_name} stopped.')
    else:
        flash('No recording process is in progress.')
    return redirect(url_for('take_pictures_page', cat_name=cat_name))

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
    use_existing_images = 'use_existing_images' in request.form

    if not name or not ration_total.isdigit():
        flash("Name and ration must be stated correctly!")
        return redirect(url_for('index'))

    model = request.files.get('model')
    images = request.files.getlist('images')

    if use_existing_images:
        
        folder = os.path.join(UPLOAD_IMAGE_FOLDER, name)
        if os.path.exists(folder):
            image_count = len([f for f in os.listdir(folder) if os.path.isfile(os.path.join(folder, f))])
            if image_count < NUMBER_OF_PICTURES:
                flash(f"You have taken less than {NUMBER_OF_PICTURES} pictures for {name}")
                return redirect(url_for('index'))
        else:
            flash(f"You have not taken any pictures with the Raspberry Pi for {name}.")
            return redirect(url_for('index'))

        venv_python = "/home/lukasadmin/venvs/venv-maturaarbeit/bin/python"
        train_model_script = "/home/lukasadmin/automatic-feeding-automat-software/train_model.py"
        subprocess.Popen([venv_python, train_model_script, name])

        flash(f"Model training for {name} started.")

    elif model and allowed_model(model.filename):
        os.makedirs(UPLOAD_MODEL_FOLDER, exist_ok=True)
        filename = secure_filename(f"model_{name}.keras")
        model.save(os.path.join(UPLOAD_MODEL_FOLDER, filename))
        
    elif images and any(img.filename for img in images):
        new_images = len([img for img in images if img.filename])

        if new_images >= NUMBER_OF_PICTURES:
            folder = os.path.join(UPLOAD_IMAGE_FOLDER, name)
            os.makedirs(folder, exist_ok=True)
            for img in images:
                if img.filename:
                    filename = os.path.basename(img.filename)
                    img.save(os.path.join(folder, secure_filename(filename)))
        else:
            flash(f"There must be at least {NUMBER_OF_PICTURES} images. Currently, there would only be {new_images}.")
            return redirect(url_for('index'))
    else:
            flash("You need to upload something from the three options above.")
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
