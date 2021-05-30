import sqlite3
import logging
import sys
from datetime import datetime
from flask import Flask, jsonify, json, render_template, request, url_for, redirect, flash
from werkzeug.exceptions import abort

db_connection_count = 0

# Function to get a database connection.
# This function connects to database with the name `database.db`
def get_db_connection():
    global db_connection_count
    connection = sqlite3.connect('database.db')
    connection.row_factory = sqlite3.Row
    db_connection_count += 1
    return connection

# Function to get a post using its ID
def get_post(post_id):
    connection = get_db_connection()
    post = connection.execute('SELECT * FROM posts WHERE id = ?',
                        (post_id,)).fetchone()
    connection.close()
    return post

# Define the Flask application
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your secret key'

# Define the main route of the web application 
@app.route('/')
def index():
    connection = get_db_connection()
    posts = connection.execute('SELECT * FROM posts').fetchall()
    connection.close()
    return render_template('index.html', posts=posts)

# Define how each individual article is rendered 
# If the post ID is not found a 404 page is shown
@app.route('/<int:post_id>')
def post(post_id):
    post = get_post(post_id)
    if post is None:
      datestamp = datetime.now()
      timestamp = datestamp.strftime("%d-%b-%Y (%H:%M:%S.%f)")
      app.logger.error("TimeStampe " + timestamp + " Failed to access article: " + str(post_id))
      return render_template('404.html'), 404
    else:
      datestamp = datetime.now()
      timestamp = datestamp.strftime("%d-%b-%Y (%H:%M:%S.%f)")
      app.logger.info("TimeStampe " + timestamp + " Article acccessed: " + str(post_id))
      return render_template('post.html', post=post)

# Define the About Us page
@app.route('/about')
def about():
    app.logger.info('About us page is retrieved')
    return render_template('about.html')

# Define the post creation functionality 
@app.route('/create', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']

        if not title:
            flash('Title is required!')
        else:
            connection = get_db_connection()
            connection.execute('INSERT INTO posts (title, content) VALUES (?, ?)',
                         (title, content))
            connection.commit()
            connection.close()
            datestamp = datetime.now()
            timestamp = datestamp.strftime("%d-%b-%Y (%H:%M:%S.%f)")
            app.logger.info("TimeStampe " + timestamp + " Article created: " + str(title))
            return redirect(url_for('index'))

    return render_template('create.html')

@app.route('/metrics')
def metrics():
    connection = get_db_connection()
    postCount = connection.execute('SELECT * FROM posts').fetchall()
    Posts = len(postCount)
    connection.close()
    response = app.response_class(
        response=json.dumps(
            {"status":"success","code":0,"data":{"db_connection_count": db_connection_count, "post_count": Posts}}
            ),
        status=200,
        mimetype='application/json'
    )
    return response

@app.route('/healthz')
def healthz():
    response = app.response_class(
        response=json.dumps({"result": "OK - healthy"}),
        status=200,
        mimetype='application/json'
    )
    return response

# start the application on port 3111
if __name__ == "__main__":

   # set logger to handle STDOUT and STDERR 
   stdout_handler = logging.StreamHandler(sys.stdout)
   stderr_handler =  logging.StreamHandler(sys.stderr) 
   handlers = [stderr_handler, stdout_handler]
   # format output
   format_output = "%(asctime)s:%(levelname)s: %(message)s"
   ## stream logs to app.log file
   logging.basicConfig(filename='app.log', level=logging.DEBUG, format=format_output, handlers=handlers)
   app.run(host='0.0.0.0', port='3111')
