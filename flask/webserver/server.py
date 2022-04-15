#!/usr/bin/env python2.7

"""
Columbia W4111 Intro to databases
Example webserver
To run locally
    python server.py
Go to http://localhost:8111 in your browser
A debugger such as "pdb" may be helpful for debugging.
Read about it online.
"""

import os
import pdb
import requests
from sqlalchemy import *
from sqlalchemy.pool import NullPool
from flask import Flask, request, render_template, g, redirect, Response

tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
app = Flask(__name__, template_folder=tmpl_dir)

user_id = 0

# XXX: The Database URI should be in the format of: 
#
#     postgresql://USER:PASSWORD@<IP_OF_POSTGRE_SQL_SERVER>/<DB_NAME>
#
# For example, if you had username ewu2493, password foobar, then the following line would be:
#
#     DATABASEURI = "postgresql://ewu2493:foobar@<IP_OF_POSTGRE_SQL_SERVER>/postgres"
#
# For your convenience, we already set it to the class database

# Use the DB credentials you received by e-mail
DB_USER = "cam2406"
DB_PASSWORD = "8084"

DB_SERVER = "w4111.cisxo09blonu.us-east-1.rds.amazonaws.com"

#DATABASEURI = "postgresql://"+DB_USER+":"+DB_PASSWORD+"@"+DB_SERVER+"/w4111"
DATABASEURI = "postgresql://"+DB_USER+":"+DB_PASSWORD+"@"+DB_SERVER+"/proj1part2"

#
# This line creates a database engine that knows how to connect to the URI above
#
engine = create_engine(DATABASEURI)


# Here we create a test table and insert some values in it
engine.execute("""DROP TABLE IF EXISTS test;""")
engine.execute("""DROP TABLE IF EXISTS Users, Movies, Posts, Chooses, Rate, Comment, Post,
AddMovie_Likelist, AddMovie_Hatelist CASCADE;""");
engine.execute("""CREATE TABLE IF NOT EXISTS test (
  id serial,
  name text
);""")
engine.execute("""INSERT INTO test(name) VALUES ('grace hopper'), ('alan turing'), ('ada lovelace');""")

#USER table
engine.execute("""CREATE TABLE Users(
 uid int PRIMARY KEY,
 name text,
 email text UNIQUE,
 password text UNIQUE
);""");

engine.execute("""INSERT INTO Users(uid, name, email, password) VALUES (0,'John', 'john@gmail.com', 'johnny');""")
#MOVIES table
engine.execute("""CREATE TABLE Movies(
 mid int PRIMARY KEY,
 title text,
 year int,
 genre text
);;""");

engine.execute("""INSERT INTO Movies(mid, title, year, genre) VALUES (0, 'Spider Man', 2021, 'Action');""")
engine.execute("""INSERT INTO Movies(mid, title, year, genre) VALUES (1, 'tick...tick...BOOM', 2021, 'Mystery');""")
engine.execute("""INSERT INTO Movies(mid, title, year, genre) VALUES (2, 'The Quiet Place', 2021, 'Horror');""")
engine.execute("""INSERT INTO Movies(mid, title, year, genre) VALUES (3, 'Shang-Chi', 2021, 'Action');""")
engine.execute("""INSERT INTO Movies(mid, title, year, genre) VALUES (4, 'Coded Bias', 2021, 'Sci-Fi');""")


engine.execute("""CREATE TABLE Posts(
 pid serial PRIMARY KEY,
 genre text,
 post_title text,
 description text UNIQUE
);""");

engine.execute("""CREATE TABLE Chooses(
 uid int REFERENCES Users(uid),
 mid int REFERENCES Movies(mid),
 PRIMARY KEY(uid, mid)
);""");

engine.execute("""CREATE TABLE Rate(
 rating boolean,
 uid int REFERENCES Users(uid),
 pid int REFERENCES Posts(pid),
 PRIMARY KEY(uid, pid)
);""");

engine.execute("""CREATE TABLE Comment(
 commenttext text,
 cid serial,
 uid int REFERENCES Users(uid),
 pid int REFERENCES Posts(pid),
 PRIMARY KEY(cid, pid)
);""");

engine.execute("""CREATE TABLE Post(
 uid int NOT NULL,
 pid serial PRIMARY KEY,
 FOREIGN KEY(uid) REFERENCES Users(uid),
 FOREIGN KEY(pid) REFERENCES Posts(pid)
);""");

engine.execute("""CREATE TABLE AddMovie_Likelist(
 id serial,
 title text,
 year int,
 PRIMARY KEY(id, uid),
 uid int REFERENCES Users(uid)
 ON DELETE CASCADE
);""");

engine.execute("""CREATE TABLE AddMovie_Hatelist(
 id serial,
 title text,
 year int,
 PRIMARY KEY(id, uid),
 uid int REFERENCES Users(uid)
 ON DELETE CASCADE
);""");

@app.before_request
def before_request():
  """
  This function is run at the beginning of every web request 
  (every time you enter an address in the web browser).
  We use it to setup a database connection that can be used throughout the request
  The variable g is globally accessible
  """
  try:
    g.conn = engine.connect()
  except:
    print ("uh oh, problem connecting to database")
    import traceback; traceback.print_exc()
    g.conn = None

@app.teardown_request
def teardown_request(exception):
  """
  At the end of the web request, this makes sure to close the database connection.
  If you don't the database could run out of memory!
  """
  try:
    g.conn.close()
  except Exception as e:
    pass


#
# @app.route is a decorator around index() that means:
#   run index() whenever the user tries to access the "/" path using a GET request
#
# If you wanted the user to go to e.g., localhost:8111/foobar/ with POST or GET then you could use
#
#       @app.route("/foobar/", methods=["POST", "GET"])
#
# PROTIP: (the trailing / in the path is important)
# 
# see for routing: http://flask.pocoo.org/docs/0.10/quickstart/#routing
# see for decorators: http://simeonfranklin.com/blog/2012/jul/1/python-decorators-in-12-steps/
#
@app.route('/')
def index():
  """
  request is a special object that Flask provides to access web request information:
  request.method:   "GET" or "POST"
  request.form:     if the browser submitted a form, this contains the data in the form
  request.args:     dictionary of URL arguments e.g., {a:1, b:2} for http://localhost?a=1&b=2
  See its API: http://flask.pocoo.org/docs/0.10/api/#incoming-request-data
  """

  # DEBUG: this is debugging code to see what request looks like
  print(request.args)


  #
  # example of a database query
  #
  #cursor = g.conn.execute("SELECT name FROM test")
  #names = []
  #for result in cursor:
  #  names.append(result['name'])  # can also be accessed using result[0]
  #cursor.close()

  #
  # Flask uses Jinja templates, which is an extension to HTML where you can
  # pass data to a template and dynamically generate HTML based on the data
  # (you can think of it as simple PHP)
  # documentation: https://realpython.com/blog/python/primer-on-jinja-templating/
  #
  # You can see an example template in templates/index.html
  #
  # context are the variables that are passed to the template.
  # for example, "data" key in the context variable defined below will be 
  # accessible as a variable in index.html:
  #
  #     # will print: [u'grace hopper', u'alan turing', u'ada lovelace']
  #     <div>{{data}}</div>
  #     
  #     # creates a <div> tag for each element in data
  #     # will print: 
  #     #
  #     #   <div>grace hopper</div>
  #     #   <div>alan turing</div>
  #     #   <div>ada lovelace</div>
  #     #
  #     {% for n in data %}
  #     <div>{{n}}</div>
  #     {% endfor %}
  #
  #context = dict(data = names)
  #print(context)


  #
  # render_template looks in the templates/ folder for files.
  # for example, the below file reads template/index.html
  #
  home()
  return render_template("login.html")#, **context)

#
# This is an example of a different path.  You can see it at
# 
#     localhost:8111/another
#
# notice that the functio name is another() rather than index()
# the functions for each app.route needs to have different names
#
@app.route('/another')
def another():
  return render_template("anotherfile.html")

#signup
@app.route('/login', methods=['POST'])
def signup():
    e=request.form['email']
    #email=request.form['email']
    psw=request.form['psw']
    #print(name, email, psw)
    #i= g.conn.execute(text(f'SELECT COUNT(*) FROM Users WHERE password = {psw};'))
    #if dup == 0:
    count = g.conn.execute("SELECT COUNT (*) FROM Users WHERE email=%s AND password=%s;", (e,psw))
    if count.mappings().all()[0]['count'] == 0:
        message = "WRONG PASSWORD OR EMAIL. TRY AGAIN"
        return render_template("/login.html", message=message)
    name = g.conn.execute("SELECT name FROM Users WHERE email=%s AND password=%s;", (e, psw))
    name = name.mappings().all()[0]['name']
    return render_template("/home.html",firstname=name)

@app.route('/makepost', methods=['GET'])
def makepost():
    return render_template("/make_post.html")

@app.route('/postpost', methods=['POST'])
def postpost():
    title=request.form['title']
    genre=request.form['genre']
    post_content=request.form['post_content']
    g.conn.execute("INSERT INTO Posts(genre, post_title, description) VALUES (%s,%s,%s);", (genre,title,post_content))
    pid = g.conn.execute("SELECT pid from Posts WHERE post_title=%s LIMIT 1;", (title)) 
    global user_id
    g.conn.execute(f"INSERT INTO Post(uid, pid) VALUES (0,{pid.mappings().all()[0]['pid']});")
    posts = g.conn.execute(text('SELECT * FROM Posts;'))
    info = []
    for _r in posts:
        info.append("{} {}\n {}".format(_r['genre'],_r['post_title'],_r['description']))

    context = dict(posts=info)
    return render_template("/home.html", **context)
    
@app.route('/comment', methods=['POST'])
def comment():
    comment=''
    comment=request.form['comment']
    global user_id
    g.conn.execute('INSERT INTO Comment(commenttext, uid, pid) VALUES (%s,0,1);',(comment))
    all_comments = g.conn.execute(text('SELECT commenttext FROM Comment;'))
    info = []
    for _r in all_comments:
        info.append(_r['commenttext'])

    context=dict(comments=info)
    print(info)
    return render_template("/home.html", **context)


@app.route('/rate', methods=['POST'])
def addrate():
    g.conn.execute("INSERT INTO Rate(rating, uid,pid) VALUES (TRUE, 0, 1) ON CONFLICT (uid, pid) DO NOTHING;")
    rating_count_for_post = g.conn.execute("SELECT COUNT (pid) FROM Rate WHERE pid=1;")
    rating=rating_count_for_post.mappings().all()[0]['count']
    print(rating)
    return render_template("/home.html",rating=rating)


@app.route('/choosemovies', methods=['GET'])
def choosemovies():
    return render_template("/choose_movies.html")

@app.route('/home', methods=['GET'])
def home():
    g.conn.execute('SELECT * FROM(SELECT * FROM Chooses WHERE uid=0) AS Userchoices;')
    wl = g.conn.execute('SELECT Movies.title FROM Movies, Chooses WHERE Chooses.uid=0 AND Chooses.mid=Movies.mid;')
    info = []
    for _r in wl:
        info.append(_r['title'])

    context = dict(watchlist=info)
    
    ll = g.conn.execute('SELECT AddMovie_Likelist.title, AddMovie_LikeList.year FROM AddMovie_LikeList WHERE uid=0;')
    info_1 = []
    for _r in ll:
        info_1.append([_r['title'],_r['year']])

    context1 = dict(likelist=info_1)
    
    hl = g.conn.execute('SELECT AddMovie_Hatelist.title, AddMovie_HateList.year FROM AddMovie_HateList WHERE uid=0;')
    info_2 = []
    for _r in hl:
        info_2.append([_r['title'],_r['year']])
    
    context2 = dict(hatelist=info_2)
    
    com = g.conn.execute('SELECT commenttext FROM Comment WHERE uid=0')
    info_3=[]
    for _r in com:
        info_3.append(_r['commenttext'])

    context3=dict(comments=info_3)

    full_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates/images/no_profile_pic.png')
    print(full_path)

    posts = g.conn.execute(text('SELECT * FROM Posts;'))
    info = []
    for _r in posts:
        info.append("{} {}\n {}".format(_r['genre'],_r['post_title'],_r['description']))
    context4 = dict(posts=info)


    return render_template("/home.html", **context, **context1, **context2, **context3, **context4, profpic=full_path)

@app.route('/submitmovies', methods=['POST'])
def submitmovies():
    mid=request.form['movie']    
    global user_id
    g.conn.execute("INSERT INTO Chooses(uid, mid) VALUES ({},{});".format(0,int(mid)))
    print(mid)
    return render_template("/choose_movies.html");

@app.route('/likelist', methods=['GET'])
def liklistpage():
    return render_template("/likelist.html")

@app.route('/hatelist', methods=['GET'])
def hatelistpage():
    return render_template("/hatelist.html")

@app.route('/addll', methods=['POST'])
def addtoll():
    title=request.form['title']
    year=request.form['year']
    if year.isdigit() == False or int(year) > 2022:
        message="NOT A VALID YEAR"
        return render_template("/likelist.html", message=message)
    g.conn.execute("INSERT INTO AddMovie_Likelist(title, year, uid) VALUES (%s,%s,0);",(title, year))
    return render_template("/likelist.html")

@app.route('/addhl', methods=['POST'])
def addtohl():
    title=request.form['title']
    year=request.form['year']
    if year.isdigit() == False or int(year) > 2022:
        message="NOT A VALID YEAR"
        return render_template("/likelist.html", message=message)
    g.conn.execute("INSERT INTO AddMovie_Hatelist(title, year, uid) VALUES (%s,%s,0);",(title, year))
    return render_template("/hatelist.html")

@app.route('/rating', methods=['POST'])
def rate():
    g.conn.execute("INSERT INTO")

@app.route('/add', methods=['POST'])
def add():
  name = request.form['name']
  print(name)
  cmd = 'INSERT INTO test(name) VALUES (:name1), (:name2);'
  g.conn.execute(text(cmd), name1 = name, name2 = name);
  test_table = g.conn.execute(text('SELECT * FROM test;'))
  for _r in test_table:
   print(_r)
  return redirect('/')


@app.route('/login')
def login():
    abort(401)
    this_is_never_executed()


if __name__ == "__main__":
  import click

  @click.command()
  @click.option('--debug', is_flag=True)
  @click.option('--threaded', is_flag=True)
  @click.argument('HOST', default='0.0.0.0')
  @click.argument('PORT', default=8111, type=int)
  def run(debug, threaded, host, port):
    """
    This function handles command line parameters.
    Run the server using
        python server.py
    Show the help text using
        python server.py --help
    """

    HOST, PORT = host, port
    print("running on %s:%d" % (HOST, PORT))
    app.run(host=HOST, port=PORT, debug=debug, threaded=threaded)


  pdb.run(run())
