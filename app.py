from flask import Flask, render_template, request, redirect, url_for, flash, session
import json, os, subprocess

app = Flask(__name__)
app.secret_key = 'dein_geheimes_sitzungs_schluessel'

CATS_FILE = 'cats.json'
SETTINGS_FILE = 'settings.json'
ADMIN_PASSWORD = '!'

def load_json(path):
    if not os.path.exists(path) or os.stat(path).st_size == 0:
        return {}
    with open(path, 'r') as f:
        return json.load(f)

def save_json(path, data):
    with open(path, 'w') as f:
        json.dump(data, f, indent=2)

def check_password(pw):
    return pw == ADMIN_PASSWORD

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        if check_password(request.form['password']):
            session['logged_in'] = True
            return redirect(url_for('index'))
        flash('Falsches Passwort', 'error')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('login'))

@app.route('/')
def index():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    cats = load_json(CATS_FILE)
    settings = load_json(SETTINGS_FILE)
    error = request.args.get('error')
    return render_template('index.html', cats=cats, settings=settings, error=error)

@app.route('/add_cat', methods=['POST'])
def add_cat():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    name = request.form['name'].strip().lower()
    total = request.form['ration_total']
    if not name or not total.isdigit():
        flash('Ungültige Eingabe', 'error')
        return redirect(url_for('index'))
    cats = load_json(CATS_FILE)
    cats[name] = {'ration_total': int(total), 'ration_left': int(total)}
    save_json(CATS_FILE, cats)
    flash(f'Katze "{name}" gespeichert', 'success')
    return redirect(url_for('index'))

@app.route('/delete_cat/<cat_name>', methods=['POST'])
def delete_cat(cat_name):
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    cats = load_json(CATS_FILE)
    key = cat_name.lower()
    if key in cats:
        del cats[key]
        save_json(CATS_FILE, cats)
        flash(f'Katze "{key}" gelöscht', 'success')
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
            settings['time_morning'], settings['time_evening'] = int(m), int(e)
        else:
            flash('Stunden müssen 0–23 sein', 'error')
            return redirect(url_for('index'))
    save_json(SETTINGS_FILE, settings)
    flash('Einstellungen gespeichert', 'success')
    return redirect(url_for('index'))

@app.route('/start_main', methods=['POST'])
def start_main():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    subprocess.Popen(['/home/lukasadmin/venvs/venv-maturaarbeit/bin/python', 'main.py'])
    flash('Programm gestartet', 'success')
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
