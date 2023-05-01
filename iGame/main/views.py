import time
import Levenshtein
from flask import flash, render_template, redirect, request, url_for, jsonify, session
from sqlalchemy import and_
from sqlalchemy.exc import SQLAlchemyError

from functions import hash_pass, get_games, get_game_info, game_finder, \
    get_hi_list, get_list, get_genres, get_themes, get_similar, get_platforms, get_filters, \
    get_game_names
from . import main
from .forms import GameForm, LoginForm, RegistrationForm, RatingForm
from .. import db
from ..models import User, UserGames, UserPref, IGDBGame
from flask_login import login_user, logout_user, login_required, current_user
from more_itertools import collapse


@main.route('/add/<gameID>')
@login_required
def add(gameID):
    userGame = UserGames(current_user.id, gameID, True)
    try:
        db.session.add(userGame)
        db.session.commit()
        flash('Game added to bag!')
    except SQLAlchemyError as error:
        print(error)
    reconcilePref(current_user.id)
    session['bagCount'] = db.session.query(UserGames).filter(and_(UserGames.user_id == current_user.id, UserGames.pref_type == True)).count()
    return redirect(url_for('main.bag'))


@main.route('/delete/<gameID>')
@login_required
def delete(gameID):
    item = db.session.query(UserGames).filter(
        and_(UserGames.user_id == current_user.id, UserGames.game_id == gameID)).first()
    if item:
        try:
            db.session.delete(item)
            db.session.commit()
            flash('Game removed from bag!')
        except SQLAlchemyError as error:
            print(error)
    else:
        flash('Game not found.')
    reconcilePref(current_user.id)  # reconcile user pref each time bag changes
    session['bagCount'] = db.session.query(UserGames).filter(
        and_(UserGames.user_id == current_user.id, UserGames.pref_type == True)).count()
    return redirect(url_for('main.bag'))


@main.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        flash('Seems like you are registered and logged in. Log out to register a new account.')
        return redirect(url_for('main.home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        username = form.username.data
        password_hash = hash_pass(form.password.data)
        email = form.email.data
        name = form.name.data
        bday = form.bday.data
        zipcode = form.zipcode.data
        phone = form.phone.data

        try:
            newUser = User(username, password_hash, email, name, bday, zipcode, phone)
        except:
            return render_template('404.html'), 404
        try:
            db.session.add(newUser)
            db.session.commit()
            flash("Registered!")
            return redirect(url_for('main.index'))
        except Exception as e:
            print(e)
            return render_template('500.html'), 500

    return render_template('register.html', form=form)


@main.route('/', methods=['GET', 'POST'])  # LOGIN
def index():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = LoginForm()
    if form.validate_on_submit():
        """
        checks validators= in 'forms.py' in username,password vars in
        # initializing LoginForm(), then calling form in the template 'login.html'
        """
        user = db.session.query(User) \
            .filter(User.user_name == form.username.data) \
            .first()
        if user is not None and user.verify_password(form.password.data):
            """
            the user query returns a Python object of the .first() user
            it finds in the db
            """
            login_user(user, form.remember.data)
            bagItems = db.session.query(UserGames).filter(and_(UserGames.user_id == current_user.id),
                                                          UserGames.pref_type == True).count()
            session['bagCount'] = bagItems
            return redirect(url_for('main.home'))
        flash('Invalid username or password.')
    return render_template('index.html', title="Welcome to iGame!", form=form)


@main.route('/home')
@login_required
def home():
    """
    in return, explain why the return of that game
    if filter bar does not live in home, home should link to filter bar
    """
    top5 = []
    user_bag = db.session.query(UserGames).filter(UserGames.user_id == current_user.id).all()
    if len(user_bag) < 5:
        flash("We need more information about your game preferences.")
        return redirect(url_for('main.gameForm'))
    pref = db.session.query(UserPref).filter(UserPref.user_id == current_user.id).first()
    if pref is None:
        reconcilePref(current_user.id)
    pref = db.session.query(UserPref).filter(UserPref.user_id == current_user.id).first()

    likes = [game_.game_id for game_ in user_bag if game_.pref_type]

    similar_games = list(get_similar(likes) - set(likes))

    user_games = [game_.game_id for game_ in user_bag]
    user_platforms = list(get_platforms(user_games))
    loGen = pref.logenres
    loThm = pref.lothemes
    noThemes = pref.nothemes
    noGenres = pref.nogenres

    hiRecs, similar = get_hi_list(user_platforms, pref.higenres, noGenres, pref.hithemes, noThemes,
                                  similar_games)

    if len(similar) >= 1 and len(hiRecs) < 5:
        loRecs, similar = get_hi_list(user_platforms, loGen, noGenres, loThm, noThemes, similar)
    else:
        loRecs = []
    sumRecs = hiRecs + loRecs
    if len(similar) >= 1 and len(sumRecs) < 5:
        noRecs = get_list(user_platforms, noThemes, noGenres, similar)
    else:
        noRecs = []

    sumRecs = hiRecs + loRecs + noRecs
    top5 = sumRecs[:5]
    return render_template('home.html', title="iGame - Dashboard", top5=top5, sumRecs=sumRecs)


@main.route('/shuffle', methods=['GET'])
@login_required
def gamePicker():
    """
    code to shuffle results, with filters on / filters off
    """
    user = current_user
    top5 = None
    return render_template('home.html', title="iGame - Dashboard", top5=top5, user=user)


@main.route('/gameForm/<name>')
@login_required
def search(name):
    search1 = name.strip()
    games = get_games(search1)
    if games:
        return jsonify({'games': games})
    else:  # find the longest matching substring
        searchNames = list(collapse(db.session.query(IGDBGame.game_name).order_by(IGDBGame.game_name).all()))
        lowest = len(search1)
        search2 = ""
        for each in searchNames:
            distance = Levenshtein.distance(each, search1)
            if distance == 0:
                search2 = each
                break
            elif distance < lowest:
                lowest = distance
                search2 = each
        games = get_games(search2)
        return jsonify({'games': games})


@main.route('/gameForm', methods=['GET', 'POST'])
@login_required
def gameForm():
    """
    to collect 5 games: 3 likes, 2 dislikes
    and if not in db, add the game to db

    subscreen
    """
    form = GameForm()
    userGames = db.session.query(UserGames.game_id).filter(UserGames.user_id == current_user.id).all()
    if len(userGames) >= 5:
        return redirect(url_for('main.home'))
    if form.validate_on_submit():
        likes = (form.game1sel.data,
                 form.game2sel.data,
                 form.game3sel.data)
        dislikes = (form.game4sel.data,
                    form.game5sel.data)
        for gameID in likes:
            userGame = UserGames(current_user.id, gameID, True)
            db.session.add(userGame)
            db.session.commit()
        for gameID in dislikes:
            userGame = UserGames(current_user.id, gameID, False)
            db.session.add(userGame)
            db.session.commit()
        reconcilePref(current_user.id)
        return redirect(url_for('main.home'))
    return render_template('gameform.html', form=form, title="iGame - Game Preferences")


@main.route('/rate/<gameID>', methods=['GET', 'POST'])
@login_required
def rate(gameID):
    form = RatingForm()
    if form.validate_on_submit():
        userGame = db.session.query(UserGames).filter(
            and_(UserGames.user_id == current_user.id, UserGames.game_id == gameID)).first()
        userGame.rating = form.gameRating.data  # form.rating.data
        try:
            db.session.commit()
            flash('Rating saved.')
        except:
            flash('Rating not saved')
    return redirect(url_for('main.bag'))


@main.route('/bag')
@login_required
def bag():
    form = RatingForm()
    bagItems = db.session.query(UserGames).filter(and_(UserGames.user_id == current_user.id),
                                                  UserGames.pref_type == True).all()
    print(bagItems)
    if not bagItems:
        return render_template('bag.html',games=[],form=form)
    ids_ = [bagItem.game_id for bagItem in bagItems]
    bagNames = get_game_names(ids_)  # param is list of game IDs
    for each in bagNames:
        for item in bagItems:
            if item.game_id == each.get('id'):
                item.game_name = each.get('name')
                break
    sortedBag = sorted(bagItems, key=lambda g: str(g.game_name))
    return render_template('bag.html', games=sortedBag, form=form)


@main.route('/gameFinder/<id_>')
@login_required
def game(id_):
    # cover, platforms, genres, themes, rating
    platforms, modes, genres, themes, screenshot_url = [], [], [], [], []
    info_dict = get_game_info(id_)
    name = info_dict.get('name')
    if info_dict.get('platforms'):
        platforms = [platform.get('name') for platform in info_dict.get('platforms')]
    if info_dict.get('cover'):
        cover_url = info_dict.get('cover').get('url')
    if info_dict.get('game_modes'):
        modes = [mode.get('name') for mode in info_dict.get('game_modes')]
    if info_dict.get('genres'):
        genres = [genre.get('name') for genre in info_dict.get('genres')]
    if info_dict.get('themes'):
        themes = [theme.get('name') for theme in info_dict.get('themes')]
    rating = info_dict.get('rating')
    if info_dict.get('screenshots'):
        screenshot_url = [shot.get('url') for shot in info_dict.get('screenshots')]
    story = info_dict.get('storyline')
    sum = info_dict.get('summary')
    infoDict = {'name': name, 'platforms': platforms, 'cover_url': cover_url, 'modes': modes,
                'genres': genres, 'themes': themes, 'rating': rating, 'screenshot_url': screenshot_url, 'story': story,
                'sum': sum}
    return jsonify({'gameInfo': infoDict})


# @main.route('/gameFinder', methods=['GET', 'POST'])
# @login_required
# def gameFinder():
#     platform, genre, mode, theme = get_filters()
#     games = []
#     platformChoices = [(choice.get('id'), choice.get('name')) for choice in platform]
#     game_modeChoices = [(choice.get('id'), choice.get('name')) for choice in mode]
#     themesChoices = [(choice.get('id'), choice.get('name')) for choice in theme]
#     genresChoices = [(choice.get('id'), choice.get('name')) for choice in genre]
#     if request.method == 'POST':
#         selectPlatforms = request.form.getlist('platform')
#         selectThemes = request.form.getlist('theme')
#         selectGenres = request.form.getlist('genre')
#         selectModes = request.form.getlist('mode')
#         selectPlatforms = [eval(int_) for int_ in selectPlatforms]
#         selectThemes = [eval(int_) for int_ in selectThemes]
#         selectGenres = [eval(int_) for int_ in selectGenres]
#         selectModes = [eval(int_) for int_ in selectModes]
#         gameList = game_finder(selectPlatforms, selectThemes, selectGenres, selectModes)
#         games = gameList[:5]
#     return render_template('gamefinder.html', platforms=platformChoices, themes=themesChoices, genres=genresChoices,
#                            modes=game_modeChoices, games=games)


@main.route('/gameFinder', methods=['GET', 'POST'])
@login_required
def gameFinder():
    if session.get('theme') is None:
        session['platformCat'], session['platformFam'], session['genre'], session['mode'], session['theme'] = get_filters()
    games = []
    platformCategoriesChoices = [(choice.get('id'), choice.get('name')) for choice in session['platformCat']]
    platformFamilyChoices = [(choice.get('id'), choice.get('name')) for choice in session['platformFam']]
    game_modeChoices = [(choice.get('id'), choice.get('name')) for choice in session['mode']]
    themesChoices = [(choice.get('id'), choice.get('name')) for choice in session['theme']]
    genresChoices = [(choice.get('id'), choice.get('name')) for choice in session['genre']]
    if request.method == 'POST':
        selectPlatformCat = request.form.getlist('platformCat')
        selectPlatformFam = request.form.getlist('platformFam')
        selectThemes = request.form.getlist('theme')
        selectGenres = request.form.getlist('genre')
        selectModes = request.form.getlist('mode')
        selectPlatformCat = [eval(int_) for int_ in selectPlatformCat]
        selectPlatformFam = [eval(int_) for int_ in selectPlatformFam]
        selectThemes = [eval(int_) for int_ in selectThemes]
        selectGenres = [eval(int_) for int_ in selectGenres]
        selectModes = [eval(int_) for int_ in selectModes]
        gameList = game_finder(selectPlatformCat, selectPlatformFam, selectThemes, selectGenres, selectModes)
        games = gameList[:5]
    return render_template('gamefinder.html',
                           platformCategories=platformCategoriesChoices,
                           platformFamilies=platformFamilyChoices,
                           themes=themesChoices,
                           genres=genresChoices,
                           modes=game_modeChoices,
                           games=games)


@main.route('/docs')
def docs():
    return '<h1>Docs/Manual/FAQ</h1>'


@main.route('/user')
@login_required
def user():
    return '<h1>User Details</h1>'


@main.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect((url_for('main.index')))


"""
VIEW FUNCTIONS: not sure how to modularize these
"""


def reconcilePref(id_):
    pref = db.session.query(UserPref).filter(UserPref.user_id == id_).first()
    user_likes = list(collapse(
        db.session.query(UserGames.game_id).filter(and_(UserGames.user_id == id_, UserGames.pref_type == True)).all()))
    user_dislikes = list(collapse(
        db.session.query(UserGames.game_id).filter(and_(UserGames.user_id == id_, UserGames.pref_type == False)).all()))
    genres = get_genres(user_likes)
    genresX = get_genres(user_dislikes)
    themes = get_themes(user_likes)
    themesX = get_themes(user_dislikes)

    if not pref:
        pref = UserPref(id_)
        db.session.add(pref)
        db.session.commit()

    pref = db.session.query(UserPref).filter(UserPref.user_id == id_).first()
    pref.higenres = list(genres - genresX)
    pref.logenres = list(genres & genresX)
    pref.nogenres = list(genresX - genres)
    pref.hithemes = list(themes - themesX)
    pref.lothemes = list(themes & themesX)
    pref.nothemes = list(themesX - themes)
    db.session.commit()
    pref = db.session.query(UserPref).filter(UserPref.user_id == id_).first()
    return pref
