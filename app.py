# from flask import Flask, render_template, request, redirect
# import sqlite3
# from flask_sqlalchemy import SQLAlchemy

# app = Flask(__name__)


  
  
# connect = sqlite3.connect('database.db')
# connect.execute(
#     'CREATE TABLE IF NOT EXISTS PARTICIPANTS (name TEXT, \
#     email TEXT, city TEXT, country TEXT, phone TEXT)')
  
  
# @app.route('/join', methods=['GET', 'POST'])
# def join():
#     if request.method == 'POST':
#         name = request.form['name']
#         email = request.form['email']
#         city = request.form['city']
#         country = request.form['country']
#         phone = request.form['phone']
  
#         with sqlite3.connect("database.db") as users:
#             cursor = users.cursor()
#             cursor.execute("INSERT INTO PARTICIPANTS \
#             (name,email,city,country,phone) VALUES (?,?,?,?,?)",
#                            (name, email, city, country, phone))
#             users.commit()
#         return render_template("index.html")
#     else:
#         return render_template('join.html')
  
  
# @app.route('/participants')
# def participants():
#     connect = sqlite3.connect('database.db')
#     cursor = connect.cursor()
#     cursor.execute('SELECT * FROM PARTICIPANTS')
  
#     data = cursor.fetchall()
#     return render_template("participants.html", data=data)

# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///your_database.db'
# db = SQLAlchemy(app)

# class Page(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     title = db.Column(db.String(100))
#     content = db.Column(db.Text)

# @app.route('/create_page', methods=['GET', 'POST'])
# def create_page():
#     if request.method == 'POST':
#         title = request.form['title']
#         content = request.form['content']
#         page = Page(title=title, content=content)
#         db.session.add(page)
#         db.session.commit()
#         return redirect(url_for('index'))

#     return render_template('create_page.html')

# @app.route('/')
# def index():
#     pages = Page.query.all()
#     return render_template('index.html', pages=pages)


# if __name__ == "__main__":
#   db.create_all()
#   app.run()

from flask import Flask, render_template, request, redirect, url_for, g
import sqlite3

app = Flask(__name__)

# Dictionary to store submitted content
content_data = {}
DATABASE = 'content.db'

page_to_route = {
    'Message from hod': 'HOD',
    'Faculty': 'faculty',
    'Events': 'events',
    'Placement Info': 'placement',
    'Student Acheivements': '/studentAcheivements'
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
                content TEXT
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


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/HOD')
def hod():
    content = get_content_by_page('Message from HOD')
    print("----------------")
    print(content)
    print("----------------")
    return render_template('HOD.html', comtent = content)

@app.route('/faculty')
def faculty():
    content = get_content_by_page('Faculty')
    return render_template('faculty.html', content=content)

@app.route('/events')
def events():
    content = get_content_by_page('Events')
    return render_template('events.html', content=content)

@app.route('/placement')
def placement():
    content = get_content_by_page('Placement Info')
    return render_template('placement.html', content=content)

@app.route('/studentAcheivements')
def studentAcheivements():
    content = get_content_by_page('Student Acheivements')
    return render_template('studentAcheivements.html', content=content)

@app.route('/submit_content', methods=['POST'])
def submit_content():
    contributor_name = request.form.get('contributor-name')
    semester_id = request.form.get('semester-id')
    selected_page = request.form.get('selected-page')
    content_title = request.form.get('content-title')
    content = request.form.get('content')

    db = get_db()
    cursor = db.cursor()
    cursor.execute('''
        INSERT INTO content (contributor_name, semester_id, selected_page, content_title, content)
        VALUES (?, ?, ?, ?, ?)
    ''', (contributor_name, semester_id, selected_page, content_title, content))
    db.commit()

    return 'Content submitted successfully.'



if __name__ == '__main__':
    init_db()
    app.run(debug=True, host="0.0.0.0")
