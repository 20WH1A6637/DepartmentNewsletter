from flask import Flask, render_template, request, redirect, url_for, g, send_file, session, render_template_string, flash
import sqlite3
import subprocess
import pyrebase
from flask import current_app
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)

import firebase_admin
from firebase_admin import credentials, auth
from email.mime.image import MIMEImage

# Initialize Firebase Admin SDK (replace 'path/to/your/serviceAccountKey.json' with your actual JSON key)
cred = credentials.Certificate('departmentnewsletterandr-8a645-firebase-adminsdk-qj8kv-fa87aaaae1.json')
firebase_admin.initialize_app(cred)

from flask_mail import Mail, Message
from apscheduler.schedulers.background import BackgroundScheduler
import os

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USERNAME'] = '20wh1a6637@bvrithyderabad.edu.in'
app.config['MAIL_PASSWORD'] = '20WH1A6637'
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False

mail = Mail(app)

# Simulated functions to fetch users from Firebase and generate PDFs
def fetch_users_from_firebase():
    auth = firebase_admin.auth
    users = auth.list_users()
    for user in users.iterate_all():
        print(user.uid, user.email)
    return users

def generate_pdf_for_user(user):
    return "22-1-2_content.pdf"

def send_weekly_emails():
    with app.app_context():
        users = fetch_users_from_firebase()
        for user in users.iterate_all():
            pdf_file_path = generate_pdf_for_user(user)

            msg = Message('Weekly Report', sender='your_email@example.com', recipients=[user.email])
            msg.body = 'This is your weekly report.'

            html_body = render_template(
                'weekly_report.html',
                unsubscribe_url='https://example.com/unsubscribe?user_id=' + user.uid
            )
            msg.html = html_body

            with current_app.open_resource(pdf_file_path) as pdf:
                msg.attach("weekly_report.pdf", "application/pdf", pdf.read())
            mail.send(msg)
            print(user.email)
    return 'Weekly emails sent successfully!'

    

# scheduler = BackgroundScheduler()
# scheduler.add_job(send_weekly_emails, 'interval', weeks=1)  # Run job weekly
# scheduler.start()

# from apscheduler.triggers.interval import IntervalTrigger
# scheduler = BackgroundScheduler()
# scheduler.add_job(send_weekly_emails, IntervalTrigger(seconds=10))  # Run job every 10 seconds
# scheduler.start()

from apscheduler.triggers.cron import CronTrigger
scheduler = BackgroundScheduler()
scheduler.add_job(
    send_weekly_emails,
    trigger=CronTrigger(day_of_week='mon', hour=0, minute=0)  # Run every Monday at 00:00
)
scheduler.start()

# Route to manually trigger sending emails (for testing purposes)
@app.route('/send_emails_manually')
def send_emails_manually():
    send_weekly_emails()
    return 'Manually triggered emails sent!'



config = {
    "apiKey": "AIzaSyAbWBmQFxpQ7d3scN4zUbN-aMOw1ayxUYk",
    "authDomain": "departmentnewsletterandr-8a645.firebaseapp.com",
    "databaseURL": "",
    "projectId": "departmentnewsletterandr-8a645",
    "storageBucket": "departmentnewsletterandr-8a645.appspot.com",
    "messagingSenderId": "232023240265",
    "appId": "1:232023240265:web:bb7dbae79317dd90f65998"
}

firebase = pyrebase.initialize_app(config)
auth = firebase.auth()
# def determine_user_role(user_id):
#     # Fetch the user from the database using user_id and retrieve their role
#     user = user.query.get(user_id)  # Assuming a User model exists
#     if user:
#         return user.role  # Return the user's role
#     return None  # Return None or a default role if user not found

@app.route('/')
@app.route('/index', methods=['GET', 'POST'])
def index():
    if (request.method == 'POST'):
            email = request.form['name']
            password = request.form['password']
            try:
                user = auth.sign_in_with_email_and_password(email, password)
                
                # user_id = auth.get_account_info(user['idToken'])
                # session['usr'] = user_id
                # user_id = user['localId']
                # session['user_id'] = user_id
                
                session['email'] = email
                # # Now you have the user_id, you can store it in the session or use it further
                # session['user_id'] = user_id
                return render_template('index1.html', email=email )
            except Exception as e:
                print(str(e))
                unsuccessful = 'Please check your credentials'
                return render_template('index.html', umessage=unsuccessful)
    return render_template('index.html')

@app.route('/create_account', methods=['GET', 'POST'])
def create_account():
    if (request.method == 'POST'):
            email = request.form['name']
            password = request.form['password']
            auth.create_user_with_email_and_password(email, password)
            session['email'] = email
            return render_template('index.html')
    return render_template('create_account.html')

@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if (request.method == 'POST'):
            email = request.form['name']
            auth.send_password_reset_email(email)
            return render_template('index.html')
    return render_template('forgot_password.html')

@app.route('/subscribe_user', methods=['POST'])
def signup():
    if request.method == 'POST':
        email = request.form['email']
        password = '123456'
        # Create a user with a default password in Firebase Authentication
        try:
            user = auth.create_user_with_email_and_password(email, password)
            session['email'] = email
            # If successful, you can handle the result, maybe log or return a success message
            # return "You have subscribed successfully!"
            flash('You have subscribed successfully!', 'success')
        except Exception as e:
            # Handle any exceptions that might occur during user creation
            error_message = str(e)
            if 'EMAIL_EXISTS' in error_message:
                flash('This email is already in use. Please log in or use a different email.', 'error')
            else:
                flash(f'Error: {error_message}', 'error')
        return redirect(url_for('home'))
    else:
        return render_template('create_account.html')  # Render the signup form
    
@app.route('/logout')
def logout():
    session.pop('email', None)  # Remove the user's email from the session
    return redirect(url_for('index'))  # Redirect to the login or home page

    


@app.route('/home', methods=['GET', 'POST'])
def home():
    result = subprocess.run(['python', 'test.py'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if result.returncode == 0:
        output = result.stdout
    else:
        output = result.stderr
    
    return render_template('index1.html')





# Dictionary to store submitted content
content_data = {}
DATABASE = 'content.db'

page_to_route = {
    'Message from hod': 'HOD',
    'Faculty': 'faculty',
    'Events': 'events',
    'Placement Info': 'placement',
    'Student Acheivements': 'studentAcheivements'
}

@app.route('/<page>')
def display_page(page):
    # Use the dictionary to get the corresponding route name
    print(page)
    route_name = page_to_route.get(page, 'index')
    print("--------------------")
    print(route_name)
    # Use the route name to retrieve content based on the route
    content = get_content_by_page(route_name)

    # Render the template using the route name as the template name
    return render_template(f'{route_name}.html', content=content)

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def init_db():
    with app.app_context():
        db = get_db()
        cursor = db.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS content (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                contributor_name TEXT,
                semester_id TEXT,
                selected_page TEXT,
                content_title TEXT,
                content TEXT,
                file_name TEXT,
                date_added DATE
            )
        ''')
        db.commit()

def get_content_by_page(page):
    db = get_db()
    cursor = db.cursor()
    cursor.execute('''
        SELECT * FROM content WHERE selected_page = ? ORDER BY semester_id
        ''', (page,))
    content = cursor.fetchall()
    return content

# @app.route('/')
# def login():
#     return render_template('login.html')

# @app.route('/home')
# def index1():
#     result = subprocess.run(['python', 'test.py'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
#     if result.returncode == 0:
#         output = result.stdout
#     else:
#         output = result.stderr
#     return render_template('index.html')

@app.route('/download', methods=['POST'])
def download():
    pdf_choice = request.form.get('pdf_choice')
    try:
        return send_file(pdf_choice, as_attachment=True)
    except FileNotFoundError:
        return "Selected PDF not found"
    

@app.route('/HOD')
def hod():
    content = get_content_by_page('Message from hod')
    print("----------------")
    print(content)
    print("----------------")
    return render_template('HOD.html', content = content)


@app.route('/faculty')
def faculty():
    content = get_content_by_page('faculty')
    print("----------------")
    print(content)
    print("----------------")
    return render_template('faculty.html', content=content)

@app.route('/events')
def events():
    content = get_content_by_page('events')
    print("----------------")
    print(content)
    print("----------------")
    return render_template('events.html', content=content)

@app.route('/placement')
def placement():
    content = get_content_by_page('placement-info')
    print("----------------")
    print(content)
    print("----------------")
    return render_template('placement.html', content=content)

@app.route('/studentAcheivements')
def studentAcheivements():
    content = get_content_by_page('student-achievements')
    print("----------------")
    print(content)
    print("----------------")
    return render_template('studentAcheivements.html', content=content)

from datetime import datetime, timedelta

def get_current_week_content():
    current_date = datetime.today()
    # Calculate the start of the week (Monday)
    start_of_week = current_date - timedelta(days=current_date.weekday())
    # Calculate the end of the week (Sunday)
    end_of_week = start_of_week + timedelta(days=6)  # Sunday is 6 days ahead of Monday
    start_of_week_date = start_of_week.date()
    end_of_week_date = end_of_week.date()
    print(current_date)
    print('.........')
    print(start_of_week_date)
    print('.........')
    print(end_of_week_date)
    db = get_db()
    cursor = db.cursor()
    cursor.execute('''
        SELECT * FROM content 
        WHERE date(date_added) BETWEEN ? AND ?
    ''', (start_of_week_date, end_of_week_date))

    content = cursor.fetchall()
    return content


@app.route('/weekly_update')
def weekly_update():
    content = get_current_week_content()
    print("----------------")
    print(content)
    print("----------------")
    return render_template('weekly_update.html', content=content)

from datetime import datetime

@app.route('/submit_content', methods=['POST'])
def submit_content():

    # Get the email from the form
    user_email = request.form.get('user-email')

    # Set the user email in the session
    session['email'] = user_email

    contributor_name = request.form.get('contributor-name')
    semester_id = request.form.get('semester-id')
    selected_page = request.form.get('selected-page')
    content_title = request.form.get('content-title')
    content1 = request.form.get('content')
    content = content1.replace('\n', '<br>')
    # Handle the file upload
    uploaded_image = request.files['uploaded-image']
    file_name = uploaded_image.filename
    if uploaded_image:
        # Save the uploaded image to a directory
        uploaded_image.save('static/uploads/' + uploaded_image.filename)
    current_date = datetime.now().date()
    # Additional processing and database storage can be done here

    # Return a response or redirect as needed

    db = get_db()
    cursor = db.cursor()
    cursor.execute('''
        INSERT INTO content (contributor_name, semester_id, selected_page, content_title, content, file_name, date_added)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (contributor_name, semester_id, selected_page, content_title, content, file_name, current_date))
    db.commit()

    return render_template('index1.html', email=user_email)

if __name__ == '__main__':
    init_db()
    app.run(debug=True, host="0.0.0.0")
