from flask import Flask
from database_worker import DatabaseWorker
from flask import render_template
from datetime import datetime, timedelta
from flask import request
from flask import make_response
from flask import redirect
from flask import url_for
from flask import Flask, request, render_template, redirect, url_for, make_response
from database_worker import make_hash, check_hash
from flask import session
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import schedule
import subprocess

app = Flask(__name__)
app.secret_key = 'very very secret key'

@app.route('/home')
def home():
    db = DatabaseWorker('database.db')
    posts = db.search("SELECT posts.*, threats.name, users.username FROM posts JOIN threats ON posts.threat_id = threats.id JOIN users ON posts.user_id = users.id", multiple=True)
    posts.reverse()
    return render_template('main.html', posts=posts)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        uname = request.form['uname']
        password = request.form['psw']
        db = DatabaseWorker('database.db')
        user = db.search(f"SELECT * FROM users WHERE username='{uname}'")
        if user:
            print(uname, password, user[2])
            if check_hash(password, user[3]):
                session['id'] = str(user[0])
                return redirect(url_for('home'))
        print('Wrong password or username')
        return redirect(url_for('login'))
    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        username = request.form['username']
        db = DatabaseWorker('database.db')
        print(email, make_hash(password), username)
        db.insert(f"INSERT INTO users (email, password, username) VALUES ('{email}', '{make_hash(password)}', '{username}')")
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.pop('id', None)
    return redirect(url_for('home'))

@app.route('/profile/<user_id>')
def profile(user_id):
    db = DatabaseWorker('database.db')
    user = db.search(f"SELECT * FROM users WHERE id={user_id}")
    posts = db.search(f"SELECT posts.*, threats.name FROM posts JOIN threats ON posts.threat_id = threats.id WHERE posts.user_id={user_id}", multiple=True)
    following = db.search(f"SELECT users.username FROM followers JOIN users ON followers.following_id = users.id WHERE follower_id={user_id}", multiple=True)
    following = ", ".join([f[0] for f in following])
    followers = db.search(f"SELECT users.username FROM followers JOIN users ON followers.follower_id = users.id WHERE following_id={user_id}", multiple=True)
    followers = ", ".join([f[0] for f in followers])
    threads = db.search(f"SELECT threats.name FROM memberships JOIN threats ON memberships.threat_id = threats.id WHERE user_id={user_id}", multiple=True)
    threads = ", ".join([t[0] for t in threads])
    posts.reverse()
    return render_template('profile.html', user=user, posts=posts, following=following, followers=followers, threads=threads)

@app.route('/thread/<thread_id>')
def thread(thread_id):
    db = DatabaseWorker('database.db')
    thread = db.search(f"SELECT * FROM threats WHERE id={thread_id}")
    posts = db.search(f"SELECT posts.*, users.username FROM posts JOIN users ON posts.user_id = users.id WHERE posts.threat_id={thread_id}", multiple=True)
    members = db.search(f"SELECT users.username FROM memberships JOIN users ON memberships.user_id = users.id WHERE threat_id={thread_id}", multiple=True)
    members = ", ".join([m[0] for m in members])
    posts.reverse()
    return render_template('thread.html', thread=thread, posts=posts, members=members)


@app.route('/create', methods=['GET', 'POST'])
def create_post():
    db = DatabaseWorker('database.db')
    threats = db.search("SELECT * FROM threats", multiple=True)
    user_id = session.get('id')
    if request.method == 'POST' and user_id is not None:
        title = request.form['title']
        content = request.form['content']
        threat = request.form['threat']
        file = request.files['image']
        if file:         
            file.save(f"static/user_images/{file.filename}")
            db.insert(f"INSERT INTO posts (title, body, threat_id, user_id, image_path) VALUES ('{title}', '{content}', {threat}, {user_id}, '{file.filename}')")
        else:
            db.insert(f"INSERT INTO posts (title, body, threat_id, user_id) VALUES ('{title}', '{content}', {threat}, {user_id})")
        return redirect(url_for('home'))
    elif user_id is None:
        return redirect(url_for('login'))
    return render_template('create.html', threats=threats)

@app.route('/post/<post_id>', methods=['GET', 'POST'])
def post(post_id):
    db = DatabaseWorker('database.db')
    post = db.search(f"SELECT posts.*, threats.name, users.username FROM posts JOIN threats ON posts.threat_id = threats.id JOIN users ON posts.user_id = users.id WHERE posts.id={post_id}", multiple=True)[0]
    user_id = session.get('id')
    if request.method == 'POST' and user_id is not None:
        content = request.form['content']
        db.insert(f"INSERT INTO comments (body, post_id, user_id) VALUES ('{content}', {post_id}, {user_id})") # fixed
        response = make_response(redirect(url_for('post', post_id=post_id)))
        db.run_query(f"UPDATE posts SET comments=comments+1 WHERE id={post_id}")
        return response
    elif user_id is None and request.method == 'POST':
        return redirect(url_for('login'))
    comments = db.search(f"SELECT comments.*, users.username FROM comments JOIN users ON comments.user_id = users.id WHERE comments.post_id={post_id}", multiple=True)
    return render_template('post.html', post=post, comments=comments)

@app.route('/delete/<post_id>')
def delete_post(post_id):
    db = DatabaseWorker('database.db')
    user_id = session.get('id')
    if user_id is None:
        return redirect(url_for('post', post_id=post_id))
    if user_id == str(db.search(f"SELECT user_id FROM posts WHERE id={post_id}")[0]):
        db.run_query(f"DELETE FROM posts WHERE id={post_id}")
        db.run_query(f"DELETE FROM comments WHERE post_id={post_id}")
        db.run_query(f"DELETE FROM likes WHERE post_id={post_id}")
    return redirect(url_for('home'))

@app.route('/delete_comment/<comment_id>')
def delete_comment(comment_id):
    db = DatabaseWorker('database.db')
    user_id = db.search(f"SELECT user_id FROM comments WHERE id={comment_id}", multiple=True)[0][0]
    print(user_id)
    post_id = db.search(f"SELECT post_id FROM comments WHERE id={comment_id}")
    if session.get('id') == str(user_id):
        db.run_query(f"UPDATE posts SET comments=comments-1 WHERE id={post_id[0]}")        
        db.run_query(f"DELETE FROM comments WHERE id={comment_id}")
        print(post_id)
    return redirect(url_for('post', post_id=post_id[0]))

@app.route('/like/<post_id>')
def like_post(post_id):
    db = DatabaseWorker('database.db')
    id = session.get('id')
    if id is None:
        return redirect(url_for('login'))
    res = db.search(f"SELECT * FROM likes WHERE user_id={id} AND post_id={post_id}")
    if not res:
        db.run_query(f"INSERT INTO likes (user_id, post_id) VALUES ({id}, {post_id})")
        db.run_query(f"UPDATE posts SET likes=likes+1 WHERE id={post_id}")
    else:
        db.run_query(f"DELETE FROM likes WHERE user_id={id} AND post_id={post_id}")
        db.run_query(f"UPDATE posts SET likes=likes-1 WHERE id={post_id}")
    return redirect(url_for('home'))

@app.route('/follow/thread/<thread_id>')
def follow_threat(thread_id):
    db = DatabaseWorker('database.db')
    user_id = session.get('id')
    if user_id is None:
        return redirect(url_for('login'))
    if not db.search(f"SELECT * FROM memberships WHERE user_id={user_id} AND threat_id={thread_id}"):
        db.run_query(f"INSERT INTO memberships (user_id, threat_id) VALUES ({user_id}, {thread_id})")
    else:
        db.run_query(f"DELETE FROM memberships WHERE user_id={user_id} AND threat_id={thread_id}")
    return redirect(url_for('thread', thread_id=thread_id))

@app.route('/follow/user/<user_id>')
def follow_user(user_id):
    db = DatabaseWorker('database.db')
    id = session.get('id')
    if id is None:
        return redirect(url_for('login'))
    if not db.search(f"SELECT * FROM followers WHERE follower_id={id} AND following_id={user_id}"):
        db.run_query(f"INSERT INTO followers (follower_id, following_id) VALUES ({id}, {user_id})")
    else:
        db.run_query(f"DELETE FROM followers WHERE follower_id={id} AND following_id={user_id}")
    return redirect(url_for('profile', user_id=user_id))

@app.route('/my_feed')
def my_feed():
    user_id = session.get('id')
    if user_id is None:
        return redirect(url_for('login'))
    db = DatabaseWorker('database.db')
    posts = db.search(f"SELECT posts.*, threats.name, users.username FROM posts JOIN threats ON posts.threat_id = threats.id JOIN users ON posts.user_id = users.id WHERE posts.threat_id IN (SELECT threat_id FROM memberships WHERE user_id = {user_id}) OR posts.user_id IN (SELECT following_id FROM followers WHERE follower_id = {user_id})", multiple=True)
    return render_template('main.html', posts=posts)

@app.route('/thread')
def thread_summary():
    db = DatabaseWorker('database.db')
    threads = db.search("SELECT * FROM threats", multiple=True)
    return render_template('summary.html', content=threads, type='thread')

@app.route('/profile')
def user_summary():
    db = DatabaseWorker('database.db')
    users = db.search("SELECT * FROM users", multiple=True)
    return render_template('summary.html', content=users, type='profile')

def send_email(user, posts):
    fromaddr = "EMAIL"
    toaddr = user[2]
    body = """\
    Subject: Here are this week posts\n\n""" # followed by two newlines (\n) to ensures that 'here are this week posts' is a subject
    for post in posts:
        body += f"Title: {post[1]}\nContent: {post[2]}\n\n"

    # server = smtplib.SMTP(`smt server`, `port`)
    # server.starttls()
    # server.login(fromaddr, "PASSWORD")
    # server.sendmail(fromaddr, toaddr, body)
    # server.quit()

def job():
    db = DatabaseWorker('database.db')
    users = db.search("SELECT * FROM users", multiple=True)
    for user in users:
        one_week_ago = datetime.now() - timedelta(weeks=1)
        posts = db.search(f"SELECT * FROM posts WHERE user_id={user[0]} AND created_at > '{one_week_ago}'", multiple=True)
        if posts:
            send_email(user, posts)
    
scheduler = BackgroundScheduler()
scheduler.add_job(func=job, trigger="interval", weeks=1)
scheduler.start()

if __name__ == '__main__':
    app.run(debug=True)
