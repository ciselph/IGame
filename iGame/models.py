from datetime import datetime
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.ext.mutable import Mutable, MutableList
from functions import hash_pass
from flask_login import UserMixin
from . import db, login_manager


class User(UserMixin, db.Model):
    __tablename__ = "user_details"
    id = db.Column(db.Integer, primary_key=True, unique=True)
    user_name = db.Column(db.String(50), nullable=False)
    full_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(150), nullable=False)
    birth_date = db.Column(db.DateTime(), nullable=False)
    zip_code = db.Column(db.Integer())
    phone_number = db.Column(db.String(20))
    user_password = db.Column(db.String(40), nullable=False)
    created_on = db.Column(db.DateTime(), default=datetime.now)

    def __init__(self, username: str, password: str, email: str, name, bday: datetime,
                 zipcode: int, phone: str):
        self.user_name = username
        self.user_password = password
        self.email = email
        self.full_name = name
        self.birth_date = bday
        self.zip_code = zipcode
        self.phone_number = phone

    @property
    def password(self):
        raise AttributeError('Not readable!')

    @password.setter
    def password(self, password):
        self.user_password = hash_pass(password)

    def verify_password(self, password):
        return self.user_password == hash_pass(password)

    games = db.relationship('UserGames', backref="user", order_by='UserGames.game_id')


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class IGDBGame(db.Model):
    __tablename__ = "igdb_games"
    game_id = db.Column(db.Integer(), primary_key=True)
    game_name = db.Column(db.String())

    def __init__(self, id_, name):
        self.game_id = id_
        self.game_name = name

    def __str__(self):
        return f'{self.game_name}'


# for the bag ('liked' games)
class UserGames(db.Model):
    """a table where USERID and GAMEID act as the primary key"""
    __tablename__ = "user_games"
    user_id = db.Column(db.Integer(), db.ForeignKey('user_details.id'), primary_key=True)
    game_id = db.Column(db.Integer(), primary_key=True)
    pref_type = db.Column(db.Boolean(), nullable=False)
    rating = db.Column(db.Integer())

    # can access user property from UserGameInstance.user to get associated user
    # establishes via backref a user_games property in User

    def __init__(self, user, game, pref):
        self.user_id = user
        self.game_id = game
        self.pref_type = pref

    def __repr__(self):
        return f'UserGame: User({self.user_id}, Game{self.game_id}, Pref{self.pref_type})'


class UserPref(db.Model):
    """
    to calculate and persist user preferences
    from set comparisons on genres, etc.
    on pref_type:bool
    """
    __tablename__ = 'user_pref'
    user_id = db.Column(db.Integer(), db.ForeignKey('user_details.id'), primary_key=True, nullable=False)
    higenres = db.Column(MutableList.as_mutable(ARRAY(db.Integer)), default=[])
    logenres = db.Column(MutableList.as_mutable(ARRAY(db.Integer)), default=[])
    nogenres = db.Column(MutableList.as_mutable(ARRAY(db.Integer)), default=[])
    hithemes = db.Column(MutableList.as_mutable(ARRAY(db.Integer)), default=[])
    lothemes = db.Column(MutableList.as_mutable(ARRAY(db.Integer)), default=[])
    nothemes = db.Column(MutableList.as_mutable(ARRAY(db.Integer)), default=[])

    def __init__(self, user_id):
        self.user_id = user_id

    def __repr__(self):
        return f'UserPref({self.user_id})'