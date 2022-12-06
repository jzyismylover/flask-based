import functools

from flask import (
  Blueprint, flash, g, request, session, jsonify
)
from werkzeug.security import check_password_hash, generate_password_hash
from flaskr.db import get_db

bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/register', methods=('GET', 'POST'))
def register():
  if request.method == 'POST':
    username = request.form.get('username')
    password = request.form.get('password')
    db = get_db()
    error = None

    if not username:
      error = "Username is required"
    elif not password:
      error = "Password is required"
    elif db.execute(
      "select id from user where username = ?", (username, )
    ).fetchone() is not None:
      error = f'User {username} is already registered.'
    
    if error is None:
      db.execute(
        'insert into user (username, password) values(?, ?)', 
        (username, generate_password_hash(password))
      )
      db.commit()
      return jsonify(
        username=username,
        password=generate_password_hash(password=password),
        status=200
      )
    
    return jsonify(
      msg=error,
      status=400
    )

@bp.route('/login', methods=['POST'])
def login():
  db = get_db()
  username = request.form.get('username')
  password = request.form.get('password')
  error = None
  user = db.execute(
    '''
    select * from user
    where username = ?
    ''', (username,)
  ).fetchone()

  if user is None:
    error = 'Incorrect username'
  elif not check_password_hash(user['password'], password):
    error = 'Incorrect password'
  
  if error is None:
    session.clear()
    session['user_id'] = user['id']
    return jsonify(
      status=200,
      msg='Login success'
    )
  return jsonify(
    error=error
  )

@bp.route('/logout')
def logout():
  session.clear()


@bp.before_app_request
def load_logged_in_user():
  user_id = session.get('user_id')
  if user_id is None:
    g.user = None
  else:
    g.user = get_db().execute(
      'select * from user where id = ?', (user_id, )
    ).fetchone()


def login_required(view):
  """装饰器, 定义其余接口必须在 login 之后调用

  Args:
      view (_type_): _description_
  """
  @functools.wraps(view)
  def wrapped_view(**kwargs):
    if g.user is None:
      return
    else:
      return view(**kwargs)
  return wrapped_view