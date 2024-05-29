# Project Unite 4
## Criteria C: Development
### Login System (similar to example solution, can be skipped)
My client required a login system for the application so that different users could have their unique `my feed` page, `profile` page, can like and comment on posts and follow different users of groups. I decided to use sessions to do so. The code below shows my first attempt and I will explain in detail below:
    
```python
if request.method == 'POST':
    uname = request.form['uname']  # Retrieve the username from the login form
    password = request.form['psw']  # Retrieve the password from the login form
    db = DatabaseWorker('database.db')  # Create an instance of the DatabaseWorker class to interact with the database
    user = db.search(f"SELECT * FROM users WHERE username='{uname}'")  # Search for the user in the database
    if user:  # If a user is found
        if check_hash(password, user[3]):  # If the hashed password matches the provided password
            session['id'] = str(user[0])  # Store the user's ID in the session
            return redirect(url_for('home'))  # Redirect the user to the home page
    return redirect(url_for('login'))  # Redirect the user back to the login page if the username or password is incorrect
```
In this code, when the server receives a POST request (`if request.method == 'POST'`), it retrieves the username (`uname`) and password (`password`) from the login form using the `request.form` dictionary. A DatabaseWorker object is created to interact with the database (`db = DatabaseWorker('database.db')`). The user is searched in the database using the provided username (`user = db.search(f"SELECT * FROM users WHERE username='{uname}'")`).

If a user is found and the hashed password matches the provided password (`if user and check_hash(password, user[3]):`), the user's ID is stored in the session (`session['id'] = str(user[0])`), and the user is redirected to the home page (`return redirect(url_for('home'))`). If the username or password is incorrect, the user is redirected back to the login page (`return redirect(url_for('login'))`).

Sessions store data, in this case signed users ID,  on the server. To use session variables securely, It's necessary to define a secret key in the Flask application, as shown below:

``` python
app = Flask(__name__)
app.secret_key = "randomtextwithnumbers1234567"
```
I use session to ensure that the users don't have access and can't change stored data to access other users' data. The session data is stored on the server, and only the ID is sent to the client in a cookie. Other safe option would be to store the user's hashed ID directly in a cookie.

### Comments
The application required a system for users to post comments on various posts. This system needed to ensure that only logged-in users could submit comments. The following code shows my implementation, which I will explain in detail:
``` python
user_id = session.get('id')  # Retrieve the user's ID from the session
if request.method == 'POST' and user_id is not None:  # Check if the request method is POST and the user is logged in
    content = request.form['content']  # Retrieve the comment content from the form
    db.insert(f"INSERT INTO comments (body, post_id, user_id) VALUES ('{content}', {post_id}, {user_id})")  # Insert the comment into the database
    response = make_response(redirect(url_for('post', post_id=post_id)))  # Create a response object to redirect the user to the post page
    db.run_query(f"UPDATE posts SET comments=comments+1 WHERE id={post_id}")  # Increment the number of comments for the post
    return response  # Return the response object
elif user_id is None and request.method == 'POST':  # If the user is not logged in and the request method is POST
    return redirect(url_for('login'))  # Redirect the user to the login page
```
In this code, the user's ID is retrieved from the session (`user_id = session.get('id')`). If the request method is POST and the user is logged in (`if request.method == 'POST' and user_id is not None:`), the comment information is retrieved from the form. The comment is inserted into the database using instance of `DatabaseWorker` class with the post ID and user ID (`db.insert(f"INSERT INTO comments (body, post_id, user_id) VALUES ('{content}', {post_id}, {user_id})")`).
After inserting the comment, the user is redirected to the post page and the number of comments for that post is updated in the database for specific post (`db.run_query(f"UPDATE posts SET comments=comments+1 WHERE id={post_id}")`).

There is also a requirements to delete comments. The following code shows my implementation, which I will explain in detail:
``` python
@app.route('/delete_comment/<comment_id>')
def delete_comment(comment_id):
    db = DatabaseWorker('database.db')  # Create an instance of the DatabaseWorker class to interact with the database
    user_id = db.search(f"SELECT user_id FROM comments WHERE id={comment_id}", multiple=True)[0][0]  # Retrieve the user ID who posted the comment
    post_id = db.search(f"SELECT post_id FROM comments WHERE id={comment_id}")  # Retrieve the post ID of the comment
    if session.get('id') == str(user_id):  # Check if the logged-in user is authorized to delete the comment
        db.run_query(f"UPDATE posts SET comments=comments-1 WHERE id={post_id[0]}")  # Decrement the number of comments for the post
        db.run_query(f"DELETE FROM comments WHERE id={comment_id}")  # Delete the comment from the database
    return redirect(url_for('post', post_id=post_id[0]))  # Redirect the user to the post page
```
when a delete button on the comment is clicked, the user is redirected to the `/delete_comment/<comment_id>` endpoint and `delete_comment` function is called. The comment ID is passed as a parameter to the function (`def delete_comment(comment_id):`). Function checks if the user is logged in and if the user ID matches the ID of the user who posted the comment (`if session.get('id') == str(user_id):`). If the user is authorized, the comment is deleted from the database (`db.run_query(f"DELETE FROM comments WHERE id={comment_id}")`), and the number of comments for the post is decremented (`db.run_query(f"UPDATE posts SET comments=comments-1 WHERE id={post_id[0]}")`). The user is then redirected to the post page (`return redirect(url_for('post', post_id=post_id[0]))`).

### Likes
My client required a system for users to like posts. This system needed to ensure that only logged-in users could like posts and that each user could only like a post once. The following code shows my implementation, which I will explain in detail:
``` python
def like_post(post_id):
    db = DatabaseWorker('database.db')  # Create an instance of the DatabaseWorker class to interact with the database
    id = session.get('id')  # Retrieve the user's ID from the session
    if id is None:  # Check if the user is not logged in
        return redirect(url_for('login'))  # Redirect the user to the login page
    res = db.search(f"SELECT * FROM likes WHERE user_id={id} AND post_id={post_id}")  # Check if the user has already liked the post
    if not res:  # If the user has not liked the post
        db.run_query(f"INSERT INTO likes (user_id, post_id) VALUES ({id}, {post_id})")  # Insert a new like record into the database
        db.run_query(f"UPDATE posts SET likes=likes+1 WHERE id={post_id}")  # Increment the number of likes for the post
    else:  # If the user has already liked the post
        db.run_query(f"DELETE FROM likes WHERE user_id={id} AND post_id={post_id}")  # Remove the like record from the database
        db.run_query(f"UPDATE posts SET likes=likes-1 WHERE id={post_id}")  # Decrement the number of likes for the post
    return redirect(url_for('home'))  # Redirect the user to the home page
```
In this code, after checking if the user is logged in, the function runs a search query to check if the user has already liked the post (`res = db.search(f"SELECT * FROM likes WHERE user_id={id} AND post_id={post_id}")`). If the user has not liked the post (`if not res:`), a new like record is inserted into the database (`db.run_query(f"INSERT INTO likes (user_id, post_id) VALUES ({id}, {post_id})"`), and the number of likes for the post is incremented (`db.run_query(f"UPDATE posts SET likes=likes+1 WHERE id={post_id}")`). In the opposite case (`else:`), the like record is removed from the database, and the number of likes for the post is decremented this time using `DELETE` instead of `INSERT` (`db.run_query(f"DELETE FROM likes WHERE user_id={id} AND post_id={post_id}")`). The user is then redirected to the home page (`return redirect(url_for('home'))`).
It was necessary to set up multiple tables and relationships between them to implement the like system. Here is the SQL code for creating the necessary tables I will explain in detail:
``` sql
CREATE TABLE IF NOT EXISTS likes (
    id INTEGER PRIMARY KEY,
    post_id INT,
    user_id INT,
    FOREIGN KEY (post_id) REFERENCES posts(id),
    FOREIGN KEY (user_id) REFERENCES users(id)
);
```
In this code, a new table named `likes` is created with three columns: `id`, `post_id`, and `user_id`. The `post_id` and `user_id` columns are foreign keys that reference the `id` columns of the `posts` and `users` tables, respectively. This relationship ensures that each like record is associated with a specific post and user. This table connects the `posts` and `users` tables that have a many-to-many relationship. 

### Follows
My client required a system for users to follow other users. This system needed to ensure that only logged-in users or groups. 
This system is implemented through two main endpoints: `/follow/user/<user_id>` and `follow/thread/<thread_id>` that call the `follow_user` and `follow_thread` functions. These functions are very similar to the `like_post` function described earlier, but they insert or delete follow records instead of like records. The follow records are stored in a new tables `followers` and `memberships` that have a many-to-many relationship with the `users` and `threads` tables, respectively.
An interesting feature related to follows is the ability to view the followers of a user or group. The following code shows my implementation, which I will explain in detail:
``` python
def thread(thread_id):
    db = DatabaseWorker('database.db')
    thread = db.search(f"SELECT * FROM threats WHERE id={thread_id}")
    posts = db.search(f"SELECT posts.*, users.username FROM posts JOIN users ON posts.user_id = users.id WHERE posts.threat_id={thread_id}", multiple=True)
    members = db.search(f"SELECT users.username FROM memberships JOIN users ON memberships.user_id = users.id WHERE threat_id={thread_id}", multiple=True)
    members = ", ".join([m[0] for m in members])
    return render_template('thread.html', thread=thread, posts=posts, members=members)
```
In this code, the `thread` function retrieves the group information from the database (`thread = db.search(f"SELECT * FROM threats WHERE id={thread_id}")`). It then retrieves the posts and members of the group from the database using a join query (`posts = db.search(f"SELECT posts.*, users.username FROM posts JOIN users ON posts.user_id = users.id WHERE posts.threat_id={thread_id}", multiple=True)` and `members = db.search(f"SELECT users.username FROM memberships JOIN users ON memberships.user_id = users.id WHERE threat_id={thread_id}", multiple=True)`). I then extracted members' usernames from the query results and joined into a single string using `join` function (`members = ", ".join([m[0] for m in members])`). This way all the formatting is done in the backend and only the final string is passed to the template.
The thread information, posts, and members are passed to the `thread.html` template for rendering.

### Profile
The application required a profile page for each user and group. This page needed to display the user's or group's information, posts, followers, and in the case of a user, the users they are following. 
There are two endpoints for the profile page: `/profile/<user_id>` and `/thread/<thread_id>` that call the `profile` and `thread` functions. I've already described the `thread` function in the previous section. The `profile` function is similar to the `thread` function but retrieves information about a user instead of a group. 
There are also two endpoints for the profile page: `/profile` and `/thread` that call the `user_summary` and `thread_summary` functions. Both of these functions render the `summary.html` template, which displays a summary of all the users or groups in the application. The following code shows my implementation:
``` python
@app.route('/profile')
def user_summary():
    db = DatabaseWorker('database.db')
    users = db.search("SELECT * FROM users", multiple=True)
    return render_template('summary.html', content=users, type='profile')
```
``` python
@app.route('/thread')
def thread_summary():
    db = DatabaseWorker('database.db')
    threads = db.search("SELECT * FROM threats", multiple=True)
    return render_template('summary.html', content=threads, type='thread')
```
In these codes, the `user_summary` and `thread_summary` functions retrieve all the users and groups from the database using a select query. The retrieved users and groups are passed to the `summary.html` template along with a type parameter that specifies whether the content is for users or groups (`return render_template('summary.html', content=users, type='profile')` and `return render_template('summary.html', content=threads, type='thread')`). I decide for this approach because it allows for code reuse and simplifies the rendering of the summary page.

### Images
The application required a system for users to upload images to their posts. This system needed to ensure that only logged-in users could upload images and that the images were stored securely on the server. The following code shows my implementation, which I will explain in detail:
``` python
if request.method == 'POST' and user_id is not None:
    title = request.form['title']
    content = request.form['content']
    threat = request.form['threat']
    file = request.files['image']
    if file:         
        file.save(f"static/user_images/{file.filename}")  # Save the uploaded image to the server
        db.insert(f"INSERT INTO posts (title, body, threat_id, user_id, image_path) VALUES ('{title}', '{content}', {threat}, {user_id}, '{file.filename}')")  # Insert the post information with the image path into the database
    else:
        db.insert(f"INSERT INTO posts (title, body, threat_id, user_id) VALUES ('{title}', '{content}', {threat}, {user_id})")  # Insert the post information without an image path into the database
    return redirect(url_for('home'))  # Redirect the user to the home page
```
This code takes care of crating new post and saving it to the database. If the user has uploaded an image, the image is saved to the `static/user_images` directory on the server (`file.save(f"static/user_images/{file.filename}")`). The image path is then stored in the database along with the post information (`db.insert(f"INSERT INTO posts (title, body, threat_id, user_id, image_path) VALUES ('{title}', '{content}', {threat}, {user_id}, '{file.filename}')")`). If the user has not uploaded an image, the post information is stored in the database without an image path (`db.insert(f"INSERT INTO posts (title, body, threat_id, user_id) VALUES ('{title}', '{content}', {threat}, {user_id})")`). The user is then redirected to the home page (`return redirect(url_for('home'))`).
File is retrieved from the form using `request.files['image']`. The html code for the form is shown below:
``` html
    <form action="/create" method="post" enctype=multipart/form-data>
        <label for="title">Name:</label><br>
        <input type="text" id="title" name="title" required><br>
        <label for="content">Description:</label><br>
        <textarea id="content" name="content" required></textarea><br>
        <label for="thread">Climbing Sector:</label><br>
        <select id="thread" name="threat" required>
            {% for threat in threats %}
                <option value="{{ threat[0] }}">{{ threat[1] }}</option>
            {% endfor %}
        </select><br>
        <label for="image">Image:</label><br>
        <input type="file" id="image" name="image" accept="image/*"><br> <!-- will accept any file type that falls under the image category, such as .jpeg, .png, .gif, etc -->
        <input type="submit" value="Create Post">
    </form>
```
I decide to use the `enctype=multipart/form-data` attribute in the form tag to allow file uploads. The `accept="image/*"` attribute in the input tag specifies that only image files can be uploaded such as .jpeg, .png, .gif, etc. The image input is also not set on required, so the user can create a post without an image.

### Email Notifications
The application required a system for sending email notifications to users. I decided to go with newsletter system, where users are being sent emails with the latest posts from the application every week. 
To send the email notifications, I chose to use SMTP (Simple Mail Transfer Protocol) servers with the `smtplib` library in Python. The following code shows my implementation:
``` python
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
```
This function takes a user object and a list of posts as parameters. It constructs the email body by iterating over the posts and adding their titles and content to the content of the email. The email would then be sent to the user's email address if the server was set up correctly using the `smtplib` library. The server would need to be set up with the correct SMTP server, port, and login credentials.
This function is then simply called for each user in the database to send them the email with the latest posts as shown below:
``` python
def job():
    db = DatabaseWorker('database.db')
    users = db.search("SELECT * FROM users", multiple=True)
    for user in users:
        one_week_ago = datetime.now() - timedelta(weeks=1) # Calculate the date one week ago
        # Retrieve the posts created by the user in the last week
        posts = db.search(f"SELECT * FROM posts WHERE user_id={user[0]} AND created_at > '{one_week_ago}'", multiple=True)
        if posts:  
            send_email(user, posts) # Send email to the user with the latest posts
```
It was necessary to select only post created in the last week. I achieved this by calculating the date one week ago using the `datetime` module and the `timedelta` class (`one_week_ago = datetime.now() - timedelta(weeks=1)`). I then retrieved the posts created by the user in the last week from the database using a select query (`posts = db.search(f"SELECT * FROM posts WHERE user_id={user[0]} AND created_at > '{one_week_ago}'", multiple=True)`) which allowed me to compare the `created_at` column in the database with the calculated date. 

Lastly it was necessary to automate this process every seven days. First I tried automating the email sending using the `schedule` library. The following code shows my implementation:
``` python
schedule.every().sunday.at("12:00").do(job)
```
This code schedules the `job` function to run every Sunday at 12:00. This way, the script only needs to be run once, and the `schedule` library will take care of running the function at the specified time. This solution has the problem that the `schedule` library might not work as expected. This is because a Flask application doesn't continuously execute Python code. Instead, it waits for HTTP requests, handles them by executing the appropriate Python code, and then goes back to waiting for more requests.
I tried to solve this problem by adding a while loop that continuously runs the `schedule.run_pending()` function and sleeps for one second between iterations. This way, the script would run continuously and check if there are any scheduled jobs to run. 
``` python
schedule.every().sunday.at("12:00").do(job)

while True:
    schedule.run_pending()
    time.sleep(1)
```
Unfortunately, this solution didn't work as expected because it blocked the Flask application from handling HTTP requests. This is because the while loop runs continuously and doesn't allow other code to be executed.
I had to decide between multiple other options: 
1. using a separate script that runs continuously alongside your Flask application to handle the scheduling. This script could use the `schedule` library to run tasks at regular intervals, and could interact with your Flask application as needed by for example, making HTTP requests to it, or by directly accessing the same database.
2. using a task scheduler like `cron` to run the script at regular intervals. This would involve setting up a `cron` job on my server to execute the script every Sunday at 12:00. This option is more reliable and doesn't require the script to be running continuously.
3. using task scheduling services like `Celery` or `APScheduler` to handle the scheduling of tasks. This is my implementation of `APScheduler`:
``` python
scheduler = BackgroundScheduler()
scheduler.add_job(func=job, trigger="interval", weeks=1)
scheduler.start()
```
An instance of APScheduler runs in the background as a separate thread which allows Flask application to continue handling requests while the scheduler runs. It doesn't require the Flask application to be running continuously, because the scheduler runs in a separate thread and can wake up to run jobs even when the Flask application is idle.

The second option would be the most reliable because it's not dependant on the Python script at all but is complex to setup as knowledge of `cron` an terminal is required. This is why I decided for the third option which is also a good choice as it can be integrated with the Flask application easily, however, if the python process is killed, the scheduler will stop running.

