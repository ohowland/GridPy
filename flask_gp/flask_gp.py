from flask import Flask, render_template, request, g, session, flash, redirect, url_for, abort, jsonify
import sqlite3
from pathlib import Path

app = Flask(__name__)            # Create application instance
app.config.from_object(__name__) # load config from this file, flaskr.py

# Load default config and override config from an environment variable
app.config.update(dict(
    DATABASE=(Path.cwd().parent / Path('GridPi/gridpi.sqlite')).as_posix(),
    SECRET_KEY='development key',
    USERNAME='admin',
    PASSWORD='default'
))

@app.route('/')
def show_entries():
    entries = update_status()
    return render_template('show_entries.html', entries=entries)

def update_status():
    db = get_db()
    entries = []
    cur = db.execute("SELECT * from asset_identity_table")
    assets = cur.fetchall()
    for id, _ in assets:
        cur = db.execute("SELECT asset_name, param_name, param_value FROM {tn1} "
                         "INNER JOIN {tn2} on {tn2}.asset_id = {tn1}.asset_id "
                         "WHERE {tn2}.asset_id = {oid} AND {tn1}.param_access = 0" \
                         .format(tn1='parameter_identity_table',
                                 tn2='asset_identity_table',
                                 oid=id))
        entries.append(cur.fetchall())
    return entries

@app.route('/control')
def show_control():
    db = get_db()
    entries = []
    cur = db.execute("SELECT * from asset_identity_table")
    assets = cur.fetchall()
    for id, _ in assets:
        cur = db.execute("SELECT asset_name, param_name, param_value, {tn1}.param_id FROM {tn1} "
                         "INNER JOIN {tn2} on {tn2}.asset_id = {tn1}.asset_id "
                         "WHERE {tn2}.asset_id = {oid} AND {tn1}.param_access = 1"\
                         .format(tn1='parameter_identity_table',
                                 tn2='asset_identity_table',
                                 oid=id))
        entries.append(cur.fetchall())
    print(entries)
    return render_template('show_control.html', entries=entries)

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != app.config['USERNAME']:
            error = 'Invalid username'
        elif request.form['password'] != app.config['PASSWORD']:
            error = 'Invalid password'
        else:
            session['logged_in'] = True
            flash('You were logged in')
            return redirect(url_for('show_entries'))
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect(url_for('show_entries'))

@app.route('/update', methods=['POST'])
def add_entry():
    if not session.get('logged_in'):
        abort(401)
    db = get_db()

    print(request.form['pid'], request.form['value'])
    db.execute('UPDATE parameter_identity_table SET param_value=(?) WHERE param_id=(?)',
               (request.form['value'], request.form['pid']))
    db.commit()
    flash('New entry was successfully posted')
    return redirect(url_for('show_control'))

''' -------- Database helpers ---------'''
def connect_db():
    """ Connects to the specific database.
    """
    rv = sqlite3.connect(app.config['DATABASE'])
    rv.row_factory = sqlite3.Row
    return rv

def get_db():
    """ Opens a new database connection if there is none yet for the current
        application context.
    """
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db

@app.teardown_appcontext
def close_db(error):
    """ Closes the database again at the end of the request.
    """

def init_db():
    db = get_db()
    with app.open_resource('schema.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()

@app.cli.command('initdb')
def initdb_command():
    """ Initializes the database.
    """
    init_db()
    print('Database initalized')

@app.route('/json_update_status', methods= ['GET'])
def stuff():
    entries = update_status()
    return jsonify(entries)
