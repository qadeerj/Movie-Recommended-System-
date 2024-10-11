from flask import Flask, render_template, redirect, url_for, request, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import pickle
import pandas as pd
import requests

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'  # Change this to a random secret key
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///movies.db'  # Database URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'  # Redirect to login page if unauthorized access

# User model
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

# User history model
class UserHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    movie_title = db.Column(db.String(200), nullable=False)

    user = db.relationship('User', backref='history')

# Movie recommendation model
class MovieRecommendation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    poster_url = db.Column(db.String(500), nullable=False)
    description = db.Column(db.String(500), nullable=True)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Create database tables
with app.app_context():
    db.create_all()

# Load the movies and similarity data
movies_dict = pickle.load(open('movie_dict.pkl', 'rb'))
movies = pd.DataFrame(movies_dict)
similarity = pickle.load(open('similarity.pkl', 'rb'))

# TMDb API details
API_KEY = '2e178fcb55efca6d115e24db67ed1af1'  # Replace with your TMDb API key

# Function to fetch movie details from TMDb API
def fetch_movie_details(movie_title):
    response = requests.get(f'https://api.themoviedb.org/3/search/movie?api_key={API_KEY}&query={movie_title}')
    data = response.json()
    if data['results']:
        return {
            'title': data['results'][0]['title'],
            'description': data['results'][0]['overview'],
            'poster_url': f"https://image.tmdb.org/t/p/w500/{data['results'][0]['poster_path']}"
        }
    return None

# Function to recommend movies
def recommend(movie):
    try:
        movie_index = movies[movies['title'] == movie].index[0]
    except IndexError:
        return []

    distances = similarity[movie_index]
    movies_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:81]  # Get top 80 movies

    recommended_movies = []
    for i in movies_list:
        movie_title = movies.iloc[i[0]].title
        movie_details = fetch_movie_details(movie_title)
        if movie_details:
            recommended_movies.append(movie_details)
    return recommended_movies

# Home route
@app.route('/')
def home():
    return render_template('home.html')

# Registration route
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        hashed_password = generate_password_hash(password)

        new_user = User(username=username, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        flash('Registration successful! You can now log in.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')

# Contact route
@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        message = request.form['message']
        
        # Here you can handle the message (e.g., send an email, save to database, etc.)
        flash('Your message has been sent!', 'success')
        return redirect(url_for('contact'))  # Redirect to the same page after submission

    return render_template('contact.html')

# Login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):
            login_user(user)
            flash('Login successful!', 'success')
            return redirect(url_for('recommend_movies'))  # Redirect to the recommend route
        else:
            flash('Login failed. Check your username and password.', 'danger')

    return render_template('login.html')

# Logout route
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('home'))

# About Us route
@app.route('/about')
def about():
    return render_template('about.html')

# Index route
@app.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    movies = MovieRecommendation.query.all()  # Fetch all movie recommendations
    recommendations = movies[:80]  # Limit to 80 movies

    page = request.args.get('page', 1, type=int)
    per_page = 40
    total_movies = len(recommendations)
    start = (page - 1) * per_page
    end = start + per_page

    paginated_recommendations = recommendations[start:end]
    has_next = end < total_movies

    return render_template('index.html', recommendations=paginated_recommendations,
                           page=page, has_next=has_next, user=current_user)

# Recommend route
@app.route('/recommend', methods=['POST', 'GET'])
@login_required
def recommend_movies():
    if request.method == 'POST':
        selected_movie_name = request.form.get('movie_name')
    else:
        selected_movie_name = request.args.get('movie_name')

    if not selected_movie_name:  # Handle case where no movie is selected
        return render_template('index.html', movies=movies['title'].values, page=1, error="Please select a movie.")

    # Get all recommendations
    recommendations = recommend(selected_movie_name)

    if not recommendations:  # Handle the case where no recommendations are found
        return render_template('index.html', movies=movies['title'].values, page=1, error="No recommendations found.")

    # Save to user history
    for recommendation in recommendations:
        new_history = UserHistory(user_id=current_user.id, movie_title=recommendation['title'])
        db.session.add(new_history)
    db.session.commit()

    # Paginate recommendations: Show 40 per page
    per_page = 40
    start_index = (request.args.get('page', 1, type=int) - 1) * per_page
    end_index = start_index + per_page
    recommendations_paginated = recommendations[start_index:end_index]
    
    # Check if there are more pages
    has_next = len(recommendations) > end_index

    return render_template(
        'index.html', 
        movies=movies['title'].values, 
        recommendations=recommendations_paginated, 
        page=request.args.get('page', 1, type=int), 
        has_next=has_next,
        selected_movie_name=selected_movie_name
    )

# History route
@app.route('/history')
@login_required
def history():
    # Fetch the user's movie history
    user_history = UserHistory.query.filter_by(user_id=current_user.id).all()
    return render_template('history.html', history=user_history, name=current_user.username)

if __name__ == "__main__":
    app.run(debug=True)
