import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash

from kanbanr.db import get_db

bp = Blueprint('auth', __name__, url_prefix='/auth')

#associating the url with the function
@bp.route('/register', methods=('GET', 'POST'))
def register():
    #if the user submitted info, start validating inputs
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None

        #make sure the user submitted all info
        if not username:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'

        #if we have all the info
        if error is None:
            try:
                #insert the data into the user table
                db.execute(
                    "INSERT INTO user (username, password) VALUES (?, ?)",
                    (username, generate_password_hash(password)),
                )
                db.commit()
            #checks if the user is already registered
            except db.IntegrityError:
                error = f"User {username} is already registered."
                return redirect(url_for("auth.login"))
            else:
                return redirect(url_for("auth.login"))

        flash(error)
    #at the end of each function, there is the html render
    return render_template('auth/register.html')

@bp.route('/login', methods=('GET', 'POST'))
def login():
    #same logic as registed function
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None
        user = db.execute(
            'SELECT * FROM user WHERE username = ?', (username,)
        ).fetchone()

        if user is None:
            error = 'Incorrect username.'
        elif not check_password_hash(user['password'], password):
            error = 'Incorrect password.'

        if error is None:
            session.clear()
            session['user_id'] = user['id']
            return redirect(url_for('index'))

        flash(error)

    return render_template('auth/login.html')

@bp.before_app_request
def load_logged_in_user():
    #allows us to easily access id of the user in session
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute(
            'SELECT * FROM user WHERE id = ?', (user_id,)
        ).fetchone()

@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        #if the user is not in session
        #redirected back to login
        if g.user is None:
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view