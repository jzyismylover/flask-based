from flask import Blueprint, abort, request, g, jsonify
from flaskr.db import get_db
from flaskr.auth import login_required

bp = Blueprint('blog', __name__)


@bp.route('/create', methods=['POST'])
def create():
  if request.method.lower() == 'post':
    title = request.form.get('title')
    body = request.form.get('body')
    error = None

    if not title:
      error = 'title is required'
    elif not body:
      error = 'body is required'

    if error is None:
      db = get_db()
      db.execute(
        '''
        insert into post(author_id, title, body)
        values(?, ?, ?, ?)
        ''', (g.user['id'], title, body)
      )
      db.commit()
      return jsonify(
        author_id=g.user['id'],
        title=title,
        body=body
      )
    else:
      abort(400, f'Bad Request: {error}')

  else:
    return 

def get_post(id: int, checl_author=True):
  db = get_db()
  post = db.execute(
        'SELECT p.id, title, body, created, author_id, username'
        ' FROM post p JOIN user u ON p.author_id = u.id'
        ' WHERE p.id = ?', (id, )).fetchone()
  if post is None:
    return "404"
  if checl_author and post['author_id'] != g.user['id']:
    return "403"
  
  return post

@bp.route('/update/<int:id>', methods=['POST'])
def update(id):
  post = get_post(id)
  if post == "404":
    return jsonify(code=10404)
  elif post == '403':
    return jsonify(code=10403) 

  if request.method == 'POST':
    title = request.form.get('title')
    body = request.form.get('body')
    error = None

    if not title:
      error = 'Title is required'
    else:
      db = get_db()
      db.execute(
        '''
        update post set title = ?, body = ?
        where id = ?
        ''', (title, body, id)
      )
      db.commit()

@bp.route('/delete/<int:id>')
def delete(id):
  post = get_post(id=id)
