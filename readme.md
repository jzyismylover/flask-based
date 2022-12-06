# flask 应用搭建
Flask是一个使用 Python 编写的轻量级 Web 应用框架

## 安装

安装项目中直接使用 pypi channel 的方式，总体新建一个 flask 虚拟环境

```bash
$ conda create --name flask python=3.7.1
$ conda activate flask
$ pip install flask
$ conda list
```

## 调试模式

基本项目启动文件是 app.py（命名可任意）

```python
from flask import Flask, render_template
from flask import jsonify

# 创建一个类实例
app = Flask(__name__)

@app.route('/')
def index():
    dict1 = {"index": "haha"}
    return jsonify(dict1)


if __name__ == '__main__':
    app.run(debug=True, host=0.0.0.0, port=5000)

```

这是 flask 一种调试的开启模式，具备更改代码自动 reload 的功能，但是有一个不好的地方在于当在代码编写过程中可能如果存在编写错误的话这个调试程序在终端就会退出了，使用体验没有那么好，因此实际官网提供的 debug 方式是通过脚本直接运行。

```bash
$ export FALSK_APP=app.py # 指定启动文件
$ export FLASK_ENV=development # 当前 flask 版本显示已废弃
$ export FLASK_DEBUG=1 对于上面废弃环境变量的补充
# 设置 host 是为了使得当前机器操作系统监听所有公开的 IP（localhost, 192.168.xxxx）
$ flask run --host=0.0.0.0 --port=5000
```



## 基本语法



### 路由

```python
@app.route('/')
def index():
    dict1 = {"index": "hahaha"}
    print(request)
    return jsonify(dict1)


@app.route('/students', methods=['post'])
def students():
    print(request.args)
    print(request.form)
    for key in request.form:
        print('key', key)
    return request
```

flask 通过 route 装饰器将函数绑定到 URL，支持设定对于路径匹配的请求方法，具体的值为一个 list。 

flask 支持动态 URL，形式为 `<converter:variable_name>`

```python
# 对应可以匹配 /user/<string>
@app.route('/user/<username>')
def show_user_profile(username):
    return 'User %s' % escape(username)

# 对应可以匹配 /post/<int>
@app.route('/post/<int:post_id>')
def show_post(post_id):
    return 'Post %d' % post_id
```

| `string` | （默认值） 接受任何不包含斜杠的文本 |
| -------- | ----------------------------------- |
| `int`    | 接受正整数                          |
| `float`  | 接受正浮点数                        |
| `path`   | 类似 `string` ，但可以包含斜杠      |
| `uuid`   | 接受 UUID 字符串                    |



### URL 构建

`url_for` 函数用于构建指定函数的  URL。

- 将函数名称作为第一个参数，
- 可以接受任意个关键字参数每个关键字对应 `URL中的变量`
- 存在未知函数将添加到 URL 中作为查询参数。 

```python
@app.route('/')
def index():
    return 'index'

@app.route('/login')
def login():
    return 'login'

@app.route('/user/<username>')
def profile(username):
    return '{}\'s profile'.format(escape(username))

with app.test_request_context():
    print(url_for('index'))
    print(url_for('login'))
    print(url_for('login', next='/'))
    print(url_for('profile', username='John Doe'))
```

```markdown
/
/login
/login?next=/
/user/John%20Doe
```



### 静态文件

在根目录（当前包 | 库所在路径下）指定 `static` 文件夹即可

```python
# static/style.css
url_for('static', filename='style.css')
```



### request

`request`  主要用于获取用户请求相关信息



### 文件上传

- 文件上传后一般存储在内存或文件系统的临时位置
- 可通过 `request` 的 `files` 属性访问上传的文件
- 对应 files 上存在一个 `save` 方法保存上传文件到文件 系统

## 应用工厂

在应用比较简单的情况下创建一个全局 flask 实例是可行的，但是当应用越来越大，需要提供的服务越来越多的时候几乎所有的代码都继承在一个文件里面就显得非常臃肿了。

由此引出`应用工厂` ，可以再一个函数内部创建 Flask 实例来代替创建全局实例，应用的配置、注册和其他设置都会在函数内部完成，说起来有点抽象不是特别容易理解，下以具体例子说明

> 对于 __init\__.py ，文件的作用是将文件夹变为一个 python 模块，实际我们导入模块的时候是导入了 \__init\__.py 文件，因此可以在这里导入我们所需要的模块

```python
# package
# __init__.py
import re
import urllib
import sys
import os

# a.py
import package 
print(package.re, package.urllib, package.sys, package.os)
```

```python
# __init__.py
__all__ = ['os', 'sys', 're', 'urllib']

# a.py
from package import *
```

>  内部实现创建不同应用实例的工厂方法

```python
"""
__init__.py
"""
def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
    )

    if test_config is None:
        app.config.from_pyfile('config.py', silent=True)
    else:
        app.config.from_mapping(test_config)

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    """
    app 实例初始化完成后挂载业务路由
    """
    @app.route('/hello')
    def hello():
        return 'Hello, World!'
    
    """
    初始化 SQLSite
    """
    from . import db
    db.init_app(app=app)

    return app
```



- 启动应用工厂

```bash
$ export FLASK_APP=flaskr
$ export FLASK_DEBUG=1
$ flask run --host=0.0.0.0
```

`注意事项`

- `__init__.py` 内的方法名默认是 `create_app`，否则会出现以下脚本运行错误

```bash
$ flask run --host=0.0.0.0
Usage: flask run [OPTIONS]      
Try 'flask run --help' for help.

Error: Failed to find Flask application or factory in module 'flaskr'. Use 'flaskr:name' to specify one.
```

如果想改方法名也是可以的，根据报错信息提示我们并没有在 flaskr 模块里面没有找到 `factory`，那么就意味着默认 `FLASK_APP=flaskr:create_app`，因此假如现在 `__init__.py` 内部的函数名为 `create_flaskr_app`，那么我们也可以通过更改环境变量的方式来正常启动，因此只要

```bash
$ export FLASK_APP=flaskr:create_flaskr_app
$ flask run --host=0.0.0.0
 * Serving Flask app 'flaskr:create_flask_app'
 * Debug mode: on
WARNING: This is a development server. Do not use it in a production deployment. 
Use a production WSGI server instead.
 * Running on http://127.0.0.1:5000
Press CTRL+C to quit
 * Restarting with stat
 * Debugger is active!
 * Debugger PIN: 141-417-990
```





## SQLSite

SQLSite 可以理解为是应用中的数据库，相对于传统的 client/server 数据库更加轻量

>  [应用情景](https://flask.net.cn/appcontext.html) 描述了 current_app 和 g 代理

```python
import sqlite3

# 连接数据库
def get_db():
  if 'db' not in g:
      g.db = sqlite3.connect(
          current_app.config['DATABASE'],
          detect_types=sqlite3.PARSE_DECLTYPES
      )
  g.db.row_factory = sqlite3.Row

  return g.db

# 关闭数据库
def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()
```

- `g` 是一个特殊对象，独立于每一个请求，按照官网的描述的话这是一个 `instance context` ，可以被每个请求访问到，可用于存储一些用户信息(session) 或者数据库连接



> 定义 SQL 语句

```sql
DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS post;

CREATE TABLE user (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT UNIQUE NOT NULL,
  password TEXT NOT NULL
);

CREATE TABLE post (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  author_id INTEGER NOT NULL,
  created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  title TEXT NOT NULL,
  body TEXT NOT NULL,
  FOREIGN KEY (author_id) REFERENCES user (id)
);
```

- 这中间有个问题，就是里面 sql `AUTOINCREMENT ` 如果是在 mysql 环境下执行的话会出现 `syntax error`，我猜测是 mysql 和 sqlite 是不是存在某些不兼容语法，这里先留个疑问。



> 基于上面的 `get_db` 和 `close_db`，我们可以定义 `init_db` 初始化数据库

```python
def init_db():
    db = get_db()
	
    # /flaskr/schema.sql
    with current_app.open_resource('schema.sql') as f:
        db.executescript(f.read().decode('utf8'))
```

- `current_app` 是一个特殊对象，指向处理请求的 Flask 应用，本质上可以理解为是 `app` | `应用工厂` 实例的代理对象，具有实例的方法，在代码中提供了访问实例的接口。



> 新建 flask cli 任务

```python
"""
flaskr/db.py
"""
@click.command('init-db')
@with_appcontext
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    click.echo('Initialized the database.')

"""
init_app 函数需要在 __init__.py 中调用
"""
def init_app(app):
  # 返回响应后进行清理的时候调用此函数
  app.teardown_appcontext(close_db)
  # 添加 flask cli 任务
  app.cli.add_command(init_db_command)
```

```bash
$ flask init-db
Initialized the database.
```



## 蓝图 & 视图

- 视图：可以理解为就是一个响应路径，/login，/regist……
- 蓝图：集合了若干视图，是一个总模块，比如说 auth 权限认证模块内部包含了登录、注册等视图

```python
"""
flaskr/auth.py
"""
import functools

from flask import Blueprint

# 生成一个蓝图实例
bp = Blueprint('auth', __name__, url_prefix='/auth')
```

```python
"""
flaskr/__init__.py
"""
def create_app():
    
    # 注册蓝图到应用实例
    from . import auth
    app.register_blueprint(auth.bp)

    return app
```

​	

> 定义视图

```python
@bp.route('/register', methods=('GET', 'POST'))
def register():
  if request.method == 'POST':
    items = request.form.items()
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
      status=200
    )
```

- 基于注册的视图，`register` 又叫做 `端点(endpoint)`，`url_for` 函数可根据端点生成 `path`
- 当前是使用 `jsonify` 来整体进行数据返回，对于数据校验也是手动校验。
  - 是否存在一些插件或者装饰器优化数据校验的过程需要探索
  - 对于数据返回应定义全局 `response`  函数
  - 目前状态码无法重新定义，无论是成功亦或是报错 status 依旧为 200（`abort`）

> 用户登录，挂载登录信息到 `g` 中，以便其他视图也可以用到相关信息

```python
"""
在视图执行前执行
"""
@bp.before_app_request
def load_logged_in_user():
  user_id = session.get('user_id')
  if user_id is None:
    g.user = None
  else:
    g.user = get_db().execute(
      'select * from user where id = ?', (user_id, )
    ).fetchone()
```





## Flask Restful

Flask-RESTful 是 Flask 的一个扩展，它添加了对快速构建 REST API 的支持。它是一个轻量级的抽象，可以与现有的 ORM库一起工作。Flask-RESTful 鼓励以最少的设置实现最佳实践。







## 网络封装



## 部署



## 日志记录
