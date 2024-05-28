# Project Unite 4
## Criteria C: Development
### Login System
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

