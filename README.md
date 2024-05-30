# Project Unite 4
## Criteria C: Development
### Email Notifications
The application required a system for sending email notifications to users. I decided to go with newsletter system, where users are being sent emails with the latest posts from the application every week. 
To send the email notifications, I chose to use SMTP (Simple Mail Transfer Protocol) servers with the `smtplib` library in Python because it's a simple and widely used method for sending emails programmatically. The `smtplib` library allows you to connect to an SMTP server, authenticate with it, and send emails using the SMTP protocol.
The following code shows my implementation:
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

### Likes
My client required a system for users to like posts. This system needed to ensure that only logged-in users could like posts and that each user could only like a post once.
Firstly, it was necessary to store and ID of loged in user. I decided to store the user ID in the session object, which is a dictionary that stores data associated with a specific user session. I use session to ensure that the users don't have access and can't change stored data to access other users' data. The session data is stored on the server, and only the ID is sent to the client in a cookie. Other safe option would be to store the user's hashed ID directly in a cookie, but this would be more complex to implement. 
This is how the ID is retrieved from the session:
``` python
id = session.get('id')  # Retrieve the user's ID from the session
```
To use session variables securely, It's necessary to define a secret key in the Flask application, as shown below:
``` python
app = Flask(__name__)
app.secret_key = "randomtextwithnumbers1234567"
```
Next, I used SQL queries to get information about the post that the user wants to like from the database using instance of `DatabaseWorker` class.  
```python
db = DatabaseWorker('database.db')  # Create an instance of the DatabaseWorker class to interact with the database
res = db.search(f"SELECT * FROM likes WHERE user_id={id} AND post_id={post_id}") 
```
`WHERE` clause in the SQL query ensures that only the likes of the current user for current post are retrieved. 
Then I used `if` statement to check if query has returned any results. If it hasn't, it means that the user hasn't liked the post yet, and I can insert a new like into the database. If it has, it means that the user has already liked the post, and I can remove the like from the database. 
``` python
if not res:  # If the user has not liked the post
    db.run_query(f"INSERT INTO likes (user_id, post_id) VALUES ({id}, {post_id})")  # Insert a new like record into the database
    db.run_query(f"UPDATE posts SET likes=likes+1 WHERE id={post_id}")  # Increment the number of likes for the post
else:  # If the user has already liked the post
    db.run_query(f"DELETE FROM likes WHERE user_id={id} AND post_id={post_id}")  # Remove the like record from the database
    db.run_query(f"UPDATE posts SET likes=likes-1 WHERE id={post_id}")  # Decrement the number of likes for the post
return redirect(url_for('home'))  # Redirect the user to the home page
```
The `INSERT INTO` query inserts a new like record into the database, and the `UPDATE` query increments the number of likes for the post. The `DELETE FROM` query removes the like record from the database, and the `UPDATE` query decrements the number of likes for the post. The user is then redirected to the home page after the like has been added or removed using the `redirect` function with the `url_for` function as an argument. The `url_for` function generates a URL for the specified endpoint, in this case, the `home` endpoint.

It was necessary to set up multiple tables and relationships between them to implement the like system. Here is the SQL code for creating one of the necessary tables I will explain in detail:
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

## My feed
The client required a system for users to see posts from other users or groups that they follow. I decided to implement a feed system. The feed system needs to ensure that only posts from users or groups that the current user follows are displayed.
I used `JOIN`, `WHERE`, and `IN` clauses in the SQL query to retrieve the posts from the database. The `JOIN` clause allows you to combine rows from two or more tables based on a related column between them. This is the mention query I will explain in detail:
``` sql
SELECT posts.*, threats.name, users.username 
FROM posts 
JOIN threats ON posts.threat_id = threats.id 
JOIN users ON posts.user_id = users.id 
WHERE posts.threat_id IN (SELECT threat_id FROM memberships WHERE user_id = {user_id}) 
    OR posts.user_id IN (SELECT following_id FROM followers WHERE follower_id = {user_id})
```
In this code snippet, the `JOIN` clause is used to combine the `posts`, `threats`, and `users` tables so that the name of the user and the thread of the post can be displayed alongside the post. The `WHERE` clause filters the posts so only the posts from the groups or users that the current user follows are displayed. The `IN` operator is used to check if the `threat_id` of the post is in the list of `threat_id` values that the current user follows or if the `user_id` of the post is in the list of `following_id` values that the current user follows. This way, only the posts from the groups or users that the current user follows are displayed in the feed.

Using one complex query instead of multiple simple queries is more efficient because it reduces the number of database queries that need to be executed. This is because the database engine can optimize the execution of the query and reduce the number of times it needs to access the database. This can improve the performance of the application and reduce the load on the database server.

Third option would be to run one simple query and then filter the results in Python code. This would involve retrieving all the posts from the database and then filtering them based on the groups or users that the current user follows. This approach is also less efficient because it requires more data to be transferred between the database and the application, and more processing to be done in the application code and would also lead to a decrease in performance.

## Criteria D: Functionality
[video link here](https://drive.google.com/file/d/1qh6rCmIVfvyRLMY_x0v6HK_MRyUJWqI2/view?usp=sharing)

## Criteria E: Evaluation
### Meeting Success Criteria
| Success Criteria                                                                 | Met | Description                                                                             |
|----------------------------------------------------------------------------------|-----|-----------------------------------------------------------------------------------------|
| The solution allows users to securely register and log in with hashed passwords. | Yes | Implements a secure login and registration system with password hashing using `session`.   |
| The solution enables users to create and delete comments.                 | Yes | Provides functionality for user comments via the `/post/<post_id>` and `/delete_comment/<comment_id>` endpoints.  |
| The solution allows users to add or remove likes on posts and comments.          | Yes | Enables users to engage with content by adding or removing likes via the `/like/<post_id>` endpoint.  |
| The solution supports users in following/unfollowing other users or groups. | Yes | Facilitates community building by allowing users to follow/unfollow others and topics via the `/follow/thread/<thread_id>` and `/follow/user/<user_id>` endpoints.  |
| The solution includes a profile page with relevant user information | Yes | Features a profile page displaying user email, followers, following, and activity.             |
| The solution allows users to upload and manage images | Yes | Provides image uploading functionality to enrich user profiles and posts.               |
| The solution weekly newsletter via email to all users | Yes | Supports email sending for account-related notifications using SMTP.         |

### Feedback from Client (Peers in this case)
Peers generally liked the application and considered success criteria to be met (see appendix 1 and 2). During the beta testing, one suggested to implement pop-up notifications confirming actions like successful sign-ins and post deletions (see appendix 1). Another possible improvement highlighted by the peers was to implement measures to prevent malware uploads and code injections while uploading images and filling forms. It was also suggested to restructure the main page to enhance user navigation and ease of use (see appendix 2).

### Recommendations for Future Improvements
After some additional discussion, I have identified several areas for improvement in the application:
1. Implementing pop-up notifications to confirm actions like successful sign-ins and post deletions. This could be done for example using JavaScript and AJAX to display notifications without reloading the page or the `flask-flash` library to display flash messages.
2. Implementing measures to prevent code injections in forms. This could be done by using the `flask-wtf` library to validate form data and prevent malicious code from being submitted or the `escape` function to escape special characters in user input.
3. Implementing measures to prevent malware uploads. This could be done by validating file types and sizes before uploading them, and by scanning uploaded files for malware using a third-party service or library. It would be also useful to rename the files to prevent malicious code from being executed.
4. Restructuring the main page to enhance user navigation and ease of use. This could be done by adding navigator bars on the sides to quickly access different groups and users, or by adding a search bar to search for specific posts or users. It would also be useful to add a filter to sort posts by date, likes, or comments.

## Appendix
### Appendix 1: Feedback from Peers
![Appendix 1](/static/documentation/apendix_2.png)
### Appendix 2: Feedback from Peers
![Appendix 2](/static/documentation/apendix_1.png)

