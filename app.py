from flask import Flask, flash, redirect, render_template, request, url_for
import requests
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import null
import flask_login

db = SQLAlchemy()
app = Flask(__name__)
app.app_context().push()
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///books.db"
app.config['SECRET_KEY'] = 'Final'
db.init_app(app)

class Book(db.Model):
        id = db.Column(db.Integer, primary_key=True, nullable=False)
        bookName = db.Column(db.String, unique=True, nullable=False)
        bookAuthor = db.Column(db.String)
        bookImg = db.Column(db.String)
        admin_id = db.Column(db.Integer, db.ForeignKey('user.id'))


class User(db.Model, flask_login.UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150))
    name = db.Column(db.String(150))
    book_connect = db.relationship('Book')

with app.app_context():
    db.create_all()

login_manager = flask_login.LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))

#INDEX PAGE
@app.route('/')
def home():
    return redirect((url_for('login')))

#LOGIN
@app.route('/login', methods = ['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('pass')

        user = User.query.filter_by(email=email).first()
        if user:
            if user.password == password:
                flask_login.login_user(user, remember=True)
                return render_template('profile.html')
            else:
                flash('Incorrect password. Please, try again!', category='error')
        else:
            flash('Email does not exist!', category='error')

    return render_template("login.html", user=flask_login.current_user)


#REGISTRATION
@app.route('/register', methods = ['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form.get('email')
        us_name = request.form.get('name')
        pass1 = request.form.get('pass1')
        pass2 = request.form.get('pass2')

        user = User.query.filter_by(email=email).first()
        if user is not None:
            flash('Email already exist!', category='error')
        elif len(email) < 4:
            flash('Email must me greater than 4 characters!', category='error')
        elif len(us_name) < 2:
            flash('Name must me greater than one character!', category='error')
        elif pass1 != pass2:
            flash('Sorry, passwords do not match!', category='error')
        elif len(pass1) < 5:
            flash('Password must be at least 5 characters!', category='error')
        else:
            
            new_user = User(name = us_name, email=email, password=pass1)
            
            db.session.add(new_user)
            db.session.commit()
            
            flash('Account successfully created!', category='success')
            return redirect(url_for('login'))
            
    return render_template('register.html')

@app.route('/profile')
def profile():
    return render_template('profile.html')

#INFRORMATION ABOUT bookS
@app.route('/result', methods = ['GET', 'POST'])
def result():
    if request.method == 'POST':
        
        #request of the book's name from form
        book = request.form.get('book')
        
        #searching for book's name in database
        book_in_db=Book.query.filter_by(bookName=book).first()
        
        #if book exist taking info from db
        if book_in_db != None:
            return render_template('result.html', Book_name=book_in_db.bookName, Book_Author=book_in_db.bookAuthor,
            Book_icon=book_in_db.bookImg)

        else:
            return render_template('error.html')
        
            

@app.route('/successAdd', methods=['GET', 'POST'])
@flask_login.login_required
def offer():
    if request.method == 'POST':
        bookName = request.form.get('offerBookName')
        bookAuthor = request.form.get('offerBookAuthor')
        bookImage = request.form.get('offerBookImg')


        if len(bookName) <1:
            flash('Too short name for a book!', category='error')
        elif len(bookAuthor) < 1:
            flash('Too short for a book Author!', category='error')
        
        else:
            new_offer = Book(bookName=bookName,
                             bookAuthor=bookAuthor, bookImg=bookImage, admin_id = flask_login.current_user.id)
            db.session.add(new_offer)
            db.session.commit()
            
            flash('book successfully added to database!', category='success')
            return render_template('successAdd.html')

    return render_template('profile.html', user = flask_login.current_user)


@app.route('/logout')
@flask_login.login_required
def logout():
    flask_login.logout_user()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)

