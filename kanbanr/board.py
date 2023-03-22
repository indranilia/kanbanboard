from flask import (Blueprint, flash, g, redirect, render_template, request, url_for, session)
from werkzeug.exceptions import abort
from kanbanr.auth import login_required
from kanbanr.db import get_db
bp = Blueprint('tasks', __name__)
@bp.route('/')
def index():
    #this is the main page
    #if user is logged in, they see their own tasks
    #if not, they only see the general outlin

    db = get_db()

    #sorting into 3 types of tasks for the type of display I chose
    not_started = db.execute(
        'SELECT t.id, title, deadline, task_type, author_id, username'
        ' FROM tasks t JOIN user u ON t.author_id = u.id'
        ' WHERE t.task_type = "not_started"'
        ' ORDER BY created DESC',
    ).fetchall()

    in_progress = db.execute(
        'SELECT t.id, title, deadline, task_type, author_id, username'
        ' FROM tasks t JOIN user u ON t.author_id = u.id'
        ' WHERE t.task_type = "in_progress"'
        ' ORDER BY created DESC',
    ).fetchall()


    completed = db.execute(
        'SELECT t.id, title, deadline, task_type, author_id, username'
        ' FROM tasks t JOIN user u ON t.author_id = u.id'
        ' WHERE t.task_type = "completed"'
        ' ORDER BY created DESC',
    ).fetchall()

    #index html renders the tasks by type
    return render_template('board/index.html', not_started = not_started, in_progress = in_progress, completed = completed)

@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
        #users input task, type, and deadline
        title = request.form.get('title')
        task_type = request.form.get('type')
        deadline = request.form.get('deadline')
        error = None

        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'INSERT INTO tasks (title, deadline, task_type, author_id)'
                ' VALUES (?, ?, ?, ?)',
                (title, deadline, task_type, g.user['id'])
            )
            db.commit()
            return redirect(url_for('index'))
    return render_template('board/index.html')

def get_task(id, check_author=True):
    #selects tasks from sql table by id
    tasks = get_db().execute(
        'SELECT t.id, title, created, author_id, username, task_type, deadline'
        ' FROM tasks t JOIN user u ON t.author_id = u.id'
        ' WHERE t.id = ?',
        (id,)
    ).fetchone()

    if tasks is None:
        abort(404, f"Task id {id} doesn't exist.")

    if check_author and tasks['author_id'] != g.user['id']:
        abort(403)

    return tasks

@bp.route('/update', methods=["POST"])
@login_required
def update():
    #function to update tasks that gets id and new status from user post
    if request.method == 'POST':
        task = request.form.get('task')
        task_type = request.form.get('updated')
        error = None

    if not task:
        error = 'Something went wrong.'

    if error is not None:
        flash(error)
    else:
        db = get_db()
        db.execute(
            'UPDATE tasks SET task_type = ?'
            ' WHERE id = ?',
            (task_type, task)
        )
        db.commit()
    return redirect('/')

@bp.route('/delete', methods=["POST"])
@login_required
def delete():
    #function to delete tasks that gets id user post
    if request.method == 'POST':
        task = request.form.get('task')
        error = None
    db = get_db()
    db.execute('DELETE FROM tasks WHERE id = ?', (task,))
    db.commit()
    return redirect('/')

