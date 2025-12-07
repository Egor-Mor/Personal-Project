from flask import Flask, render_template, url_for, request, redirect, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.exceptions import HTTPException
from os import listdir, environ
from models import db, User, Comment

app = Flask(__name__)
app.config['SECRET_KEY'] = environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please log in to access this page.'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class GameCard:
    def __init__(self, game_id, game_name, description, rating=0.0):
        self.game_id = game_id
        self.game_name = game_name
        self.rating = rating
        self.ratings = 0
        self.description = description

    def return_HTML(self):
        # Generate the URL using Flask's url_for in application context
        with app.app_context():
            game_url = url_for("game", game_id=self.game_id)
        return f'''<div class="d-inline col-md-4 col-sm-6 col-xs-12 my-2">
            <div class="card shadow m-3" >
                <div class="card-body">
                    <h3 class="card-title">{self.game_name}</h3>
                    <p class="card-text">{self.description}</p>
                    <h4 class="card-subtitle">{self.rating:.1f}/5</h4>
                    <a class="btn btn-primary btn-sm my-2" href="{game_url}" type="button">Go to game</a>
                </div>
            </div>
        </div>'''

    def recalculate_rating(self, rating):
        self.rating = (self.rating * self.ratings + rating)/(self.ratings+1)
        self.ratings += 1

game_of_life = GameCard(
    'game_of_life',
    "Conway's game of life",
    "Basic game of life with back and white squares.",
    4.6
)
platformer = GameCard(
    'platformer',
    "Star adventure",
    "Collect 3 stars to complete the level, only some can finish the third!",
    4.9
)
pong = GameCard(
    'pong',
    "Pong",
    "Nostalgic game for 2 players.",
    3.7)
snake = GameCard(
    'snake',
    "Snake",
    "Snake arcade: collect apples, and don`t bump into anything.",
    4.2)
tetris = GameCard(
    'tetris',
    "Tetris",
    "Game, where you learn to pack your luggage.",
    4.7
)
typing_test = GameCard(
    'typing_test',
    "Type speed testing",
    "How fast can you actually type?",
    3.5
)

games = [
    game_of_life,
    platformer,
    pong,
    snake,
    tetris,
    typing_test
]

def render_cards():
    rendered=''''''
    for card in games:
        rendered += card.return_HTML() + '\n'
    return rendered


@app.route("/")
@app.route("/games")
def index():
    return render_template("index.html", rendered_cards=render_cards())

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            login_user(user)
            flash('Login successful!', 'success')
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('index'))
        else:
            flash('Invalid username or password', 'error')
    
    return render_template("login.html")

@app.route("/register", methods=["POST", "GET"])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # Validation
        if User.query.filter_by(username=username).first():
            flash('Username already exists', 'error')
            return render_template("register.html")
        
        # Create new user
        user = User(username=username)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))
    
    return render_template("register.html")

@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash('You have been logged out', 'info')
    return redirect(url_for('index'))

@app.route("/games/<game_id>")
def game(game_id):
    for game in games:
        if game.game_id == game_id:
            return render_template("game.html",
                                   game_name=game.game_id,
                                   game_display_name=game.game_name,
                                   rating=game.rating,
                                   description=game.description)
    return 'Game not found'
@app.errorhandler(HTTPException)
def error(e):
    return f'Error code is: {e}'

if __name__ == "__main__":
    with app.app_context():
        db.create_all()  # Create tables if they don't exist
    app.run(host='0.0.0.0')