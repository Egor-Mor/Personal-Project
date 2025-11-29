from flask import Flask, render_template, url_for
from werkzeug.exceptions import HTTPException
from os import listdir

app = Flask(__name__)

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
    return render_template("login.html")

@app.route("/register", methods=["POST", "GET"])
def register():
    return render_template("register.html")

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
    app.run(host='192.168.1.23')