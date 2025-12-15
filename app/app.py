from flask import Flask, render_template, url_for, request, redirect, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.exceptions import HTTPException
import os
import tempfile
import hashlib
from models import db, User, Comment

_base_dir = os.path.dirname(os.path.abspath(__file__))
_writable_instance = os.environ.get("FLASK_INSTANCE_PATH") or os.environ.get("TMPDIR") or tempfile.gettempdir()
os.makedirs(_writable_instance, exist_ok=True)

_static_folder = os.path.join(_base_dir, 'static')
_template_folder = os.path.join(_base_dir, 'templates')

app = Flask(__name__,
            instance_path=_writable_instance,
            static_folder=_static_folder,
            template_folder=_template_folder)

secret_env = os.environ.get('SECRET_KEY')
db_env = os.environ.get('DATABASE_URL')
if secret_env:
    app.config['SECRET_KEY'] = secret_env
elif db_env:
    app.config['SECRET_KEY'] = hashlib.sha256(db_env.encode()).hexdigest()
else:
    app.config['SECRET_KEY'] = 'dev-static-key-change-in-production'

if db_env:
    db_url = db_env
    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)
else:
    db_path = os.path.join(_writable_instance, 'app.db')
    db_url = f'sqlite:///{db_path}'

app.config['SQLALCHEMY_DATABASE_URI'] = db_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SESSION_COOKIE_SAMESITE'] = 'Strict'
app.config['SESSION_COOKIE_HTTPONLY'] = True
if os.environ.get('FLASK_ENV') == 'production' or os.environ.get('VERCEL') == '1':
    app.config['SESSION_COOKIE_SECURE'] = True

db.init_app(app)
try:
    with app.app_context():
        db.create_all()
except Exception as e:
    print("Warning: failed to create DB tables on import:", e)

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
        avg = self.get_average_rating()
        game_url = url_for("game", game_id=self.game_id)
        image_url = url_for("static", filename=f"img/{self.game_id}.png")
        return f'''<div class="d-inline col-md-4 col-sm-6 col-xs-12 my-2">
            <div class="card shadow m-3" >
                <img class="card-img-top" src="{image_url}" alt="{self.game_name}" style="height: 300px; object-fit: cover;">
                <div class="card-body">
                    <h3 class="card-title">{self.game_name}</h3>
                    <p class="card-text">{self.description}</p>
                    <h4 class="card-subtitle">{avg:.1f}/5 ⭐</h4>
                    <a class="btn btn-primary btn-sm my-2" href="{game_url}" type="button">Go to game</a>
                </div>
            </div>
        </div>'''

    def get_average_rating(self):
        try:
            comments = Comment.query.with_entities(Comment.rating).filter_by(game_id=self.game_id).all()
            if not comments:
                return float(self.rating)
            total = sum((c[0] or 0) for c in comments)
            return round(total / len(comments), 1)
        except Exception:
            return float(self.rating)

game_of_life = GameCard(
    'game_of_life',
    "Conway's game of life",
    "A zero-player cellular automaton where complex, self-organizing patterns emerge from simple rules governing cell birth, survival, and death on a grid.",
    4.6
)
platformer = GameCard(
    'platformer',
    "Star adventure",
    "A classic action game genre focused on precise movement, running, and jumping across suspended platforms to navigate challenging environments and overcome obstacles.",
    4.9
)
pong = GameCard(
    'pong',
    "Pong",
    "The original two-dimensional sports video game that simulates table tennis, where players use paddles to hit a ball back and forth to score points against an opponent.",
    3.7)
snake = GameCard(
    'snake',
    "Snake",
    "An action game where the player maneuvers a growing line to collect food, with the core challenge being to avoid collisions with the boundaries or the snake's own ever-lengthening body.",
    4.2)
tetris = GameCard(
    'tetris',
    "Tetris",
    "A timeless puzzle game requiring players to rotate and position falling geometric shapes (tetrominoes) to form complete horizontal lines and prevent the stack from reaching the top.",
    4.7
)
typing_test = GameCard(
    'typing_test',
    "Type speed testing",
    "An application designed to measure and improve keyboarding skills by tracking a user's speed (Words Per Minute) and accuracy while transcribing provided text.",
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
    rendered = ''
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
        if User.query.filter_by(username=username).first():
            flash('Username already exists', 'error')
            return render_template("register.html")
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
    comment_amount = request.args.get('com-am', 5, type=int)
    game_obj = None
    for g in games:
        if g.game_id == game_id:
            game_obj = g
            break
    if not game_obj:
        return 'Game not found'
    total_comments_count = Comment.query.filter_by(game_id=game_id).count()
    db_comments = Comment.query.filter_by(game_id=game_id).order_by(Comment.created_at.desc()).limit(comment_amount).all()
    avg_rating = game_obj.get_average_rating()
    user_comment = None
    if current_user.is_authenticated:
        user_comment = Comment.query.filter_by(game_id=game_id, user_id=current_user.id).first()
    return render_template("game.html",
                           game=game_obj,
                           comments=db_comments,
                           total_comments_count=total_comments_count,
                           rating=avg_rating,
                           user_comment=user_comment)

@app.route("/games/<game_id>/comment", methods=["POST"])
@login_required
def add_comment(game_id):
    game_obj = None
    for g in games:
        if g.game_id == game_id:
            game_obj = g
            break
    if not game_obj:
        flash('Game not found', 'error')
        return redirect(url_for('index'))
    content = request.form.get('content', '').strip()
    rating = request.form.get('rating', type=int)
    if not content:
        flash('Comment cannot be empty', 'error')
        return redirect(url_for('game', game_id=game_id))
    if not rating or rating < 1 or rating > 5:
        flash('Please select a rating (1-5 stars)', 'error')
        return redirect(url_for('game', game_id=game_id))
    existing_comment = Comment.query.filter_by(game_id=game_id, user_id=current_user.id).first()
    if existing_comment:
        existing_comment.content = content
        existing_comment.rating = rating
        db.session.commit()
        flash('Comment updated!', 'success')
    else:
        comment = Comment(
            content=content,
            rating=rating,
            game_id=game_id,
            user_id=current_user.id
        )
        db.session.add(comment)
        db.session.commit()
        flash('Comment added!', 'success')
    return redirect(url_for('game', game_id=game_id))

@app.route('/static/Games/<path:filename>')
def serve_game_static(filename):
    from flask import send_from_directory
    import os
    games_dir = os.path.join(app.static_folder, 'Games')
    file_path = os.path.join(games_dir, filename)
    if os.path.exists(file_path) and os.path.isfile(file_path):
        response = send_from_directory(games_dir, filename)
        if filename.endswith('.apk'):
            response.headers['Content-Type'] = 'application/zip'
            response.headers['Access-Control-Allow-Origin'] = '*'
            response.headers['Access-Control-Allow-Methods'] = 'GET, OPTIONS, HEAD'
            response.headers['Access-Control-Allow-Headers'] = '*'
            response.headers['Accept-Ranges'] = 'bytes'
        return response
    else:
        return 'File not found', 404

@app.errorhandler(HTTPException)
def error(e):
    return f'Error code is: {e}'

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0')