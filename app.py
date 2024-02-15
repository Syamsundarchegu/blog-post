from flask import Flask, request,redirect,render_template,url_for,session,jsonify

import mysql.connector

from datetime import timedelta

my_db = mysql.connector.connect(host='localhost',user='root',password='Syamsundar@1234',database='user_data')
my_cursor = my_db.cursor()





app = Flask(__name__)


app.secret_key = "syamsundar"
app.permanent_session_lifetime = timedelta(hours=1)

@app.route('/',methods=['GET','POST'])
def home():
    return render_template('home.html')






@app.route('/register',methods=['GET','POST'])
def register():
    if request.method == 'POST':
        
        username = request.form['username']
        password = request.form['password']
        my_cursor.execute('select * from blog_post_register where username = %s',(username,))
        exist_user = my_cursor.fetchone()
        print(exist_user)
        if exist_user:
            return redirect(url_for('login'))
        else:
            my_cursor.execute('insert into blog_post_register(username,password) value(%s , %s)',(username,password))
            my_db.commit()
            return redirect(url_for('login'))    
    return render_template('register.html')




@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user' in session:
        return redirect(url_for('profile'))
    if request.method == 'POST':  # Check if request method is POST
        session.permanent = True  # Setting session to be permanent
        username = request.form['username']  # Extracting username from form data
        password = request.form['password']  # Extracting password from form data

        # Executing a SQL query to select user data based on the provided username
        my_cursor.execute('select * from blog_post_register where username = %s', (username,))
        exist_user = my_cursor.fetchone()  # Fetching the user record from the database

        # Checking if the user exists and the password matches
        if exist_user and password:
            session['user'] = username  # Storing the username in the session
            return redirect(url_for('profile'))  # Returning success message

    return render_template('login.html')  # Rendering the login template for GET requests or failed login attempts


@app.route('/profile',methods=['GET','POST'])
def profile():
    if 'user' in session:
        my_cursor.execute('select * from blog_post_register where username = %s', (session['user'],))
        user_details = my_cursor.fetchone()
        b= {}
        for i in user_details:
            b[user_details.index(i)] = i
        print(b)
        return render_template('profile.html',b=b)
    return redirect(url_for('login'))


@app.route('/logout')
def logout():
    if 'user' in session:
        session.pop('user')
        return redirect(url_for('login'))
  
    return redirect(url_for('login'))


@app.route('/update/<int:user_id>',methods=['GET','POST'])
def update(user_id):
    if 'user' in session:
        my_cursor.execute('select * from blog_post_register where id = %s',(user_id,))
        user_details = my_cursor.fetchone()
        c = {'id':user_details[0],'username':user_details[1],'password':user_details[2]}

        if request.method == "POST":
            username = request.form['username']
            password = request.form['password']
            session['user'] = username
            my_cursor.execute('UPDATE blog_post_register SET username = %s, password = %s WHERE id = %s', (username, password, user_id))

            my_db.commit()
            return redirect(url_for('profile'))
        return render_template('update.html',c=c)
    
    return redirect(url_for('login'))
        


@app.route('/create-post', methods=['GET', 'POST'])
def create_post():
    if 'user' in session:
        my_cursor.execute('select * from blog_post_register where username = %s',(session['user'],))
        current_user_id = my_cursor.fetchone()[0]
        if request.method == 'POST':
        # Get form data
            title = request.form['title']
            content = request.form['content']
            author = request.form['author']
            category = request.form['category']
            status = request.form['status']
            date = request.form['date']
            my_cursor.execute("INSERT INTO blog_posts_create (title, content, author, category, status, date,current_user_id ) VALUES (%s, %s, %s, %s, %s, %s,%s)", (title, content, author, category, status, date,current_user_id))
            my_db.commit()
            return redirect(url_for('myposts'))
    return render_template('create_post.html')
    
    
    
    
@app.route('/myposts', methods=['GET', 'POST'])
def myposts():
    if 'user' in session:
        my_cursor.execute('SELECT * FROM blog_post_register WHERE username = %s', (session['user'],))
        user_data = my_cursor.fetchone()
        if user_data:
            user_id = user_data[0]  # Assuming the user ID is the first column
            my_cursor.execute('SELECT * FROM blog_posts_create WHERE current_user_id = %s', (user_id,))
            current_user_posts = my_cursor.fetchall()
            
            return render_template('my_posts.html', current_user_posts=current_user_posts)
        else:
            # Handle the case when user data is not found
            return "User data not found"
    return redirect(url_for('login'))



@app.route('/all_posts',methods=['GET','POST'])
def all_posts():
    if 'user' in session:
        my_cursor.execute('select * from blog_post_register where username = %s',(session['user'],))
        c = my_cursor.fetchone()[0]
        my_cursor.execute('select * from blog_posts_create')
        a = my_cursor.fetchall()
        my_cursor.execute('SELECT comments.post_id,comments.comment,comments.commenter_name FROM blog_posts_create JOIN comments ON blog_posts_create.id = comments.post_id;')
        r = my_cursor.fetchall()
        return render_template('all_posts.html',a=a,c=c,r=r)
    return redirect(url_for('login'))



@app.route('/add_comment',methods=['GET','POST'])
def add_comment():
    if 'user' in session:
        my_cursor.execute('select * from blog_post_register where username = %s',(session['user'],))
        c = my_cursor.fetchone()[0]
        commenter_name = request.form['commenter_name']
        comment_content = request.form['comment_content']
        post_id  = request.form['post_id']
        user_id = c
        my_cursor.execute('insert into comments(post_id,user_id,comment,commenter_name) values(%s,%s,%s,%s)',(post_id,user_id,comment_content,commenter_name))
        my_db.commit()
        return redirect(url_for('all_posts'))
    
    return redirect(url_for('login'))

if __name__ == "__main__":
    app.run(debug=True)
