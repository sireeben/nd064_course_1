import sqlite3
import logging
import sys
from datetime import datetime



from flask import Flask, jsonify, json, render_template, request, url_for, redirect, flash, logging as flog
from werkzeug.exceptions import abort


# Function to get a database connection.
# This function connects to database with the name `database.db`
def get_db_connection():
    connection = sqlite3.connect('database.db')
    connection.row_factory = sqlite3.Row
    get_db_connection.counter += 1 
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

get_db_connection.counter = 0

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
    current_time = datetime.now().strftime("%D %H:%M:%S")
    if post is None:
      app.logger.info('%s, 404 Error - Page Not Found!', current_time)
      return render_template('404.html'), 404
    else:
      title = post[2]
      app.logger.info('%s, Article "%s" retrieved successfully!', current_time, title)
      return render_template('post.html', post=post)

# Define the About Us page
@app.route('/about')
def about():
    current_time = datetime.now().strftime("%D %H:%M:%S")
    app.logger.info('%s, About Us page retrieved successfully!', current_time)
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

            current_time = datetime.now().strftime("%D %H:%M:%S")
            app.logger.info('%s, Article "%s" created', current_time, title)

            return redirect(url_for('index'))

    return render_template('create.html')

# Define the healthcheck endpoint
@app.route('/healthz')
def status():
    response = app.response_class(
            response=json.dumps({"result":"OK - healthy"}),
            status=200,
            mimetype='application/json'
    )
    return response

# Define the metrics endpoint
@app.route('/metrics')
def metrics():
    connection = get_db_connection()
    post_count = connection.execute('SELECT count(*) FROM posts').fetchone()[0]
    db_connection_count = get_db_connection.counter
    connection.close()
    response = app.response_class(
            response=json.dumps({"status":"success","code":0,"data":{"db_connection_count": db_connection_count, "post_count": post_count}}),
            status=200,
            mimetype='application/json'
    )
    return response

# start the application on port 3111
if __name__ == "__main__":
   logging.basicConfig(stream=sys.stdout,level=logging.DEBUG)
   app.run(host='0.0.0.0', port='3111')
