# Project Unite 4
## Criteria C: Development
### Login System
My client required a login system for the application so that different users could have their unique `my feed` page, `profile` page, can like and comment on posts and follow different users of groups. I decided to use sessions to do so. The code below shows my first attempt and I will explain in detail below:
''' python
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
'''
