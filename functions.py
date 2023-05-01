import requests.exceptions
from igdb.wrapper import IGDBWrapper
from more_itertools import collapse
import json
import hashlib

WRAPPER = IGDBWrapper("x80ohduafgkshvv7rnsf1r3c8nd5lz", "86ng7oxojsze0gzlaztz145menoaer")


def get_game_data(id_):
    try:
        rq = WRAPPER.api_request(
            'games',
            f'f name,age_ratings,genres.name,platforms.name,rating,similar_games,themes.name; where id = {id_};'
        )
        response = json.loads(rq)
        if len(response) == 1:
            return response[0]
    except requests.exceptions.HTTPError as err:
        print(f"{err}")
        return None


def get_game_id(string_):
    search1 = string_.strip()
    id_ = None
    try:
        rq = WRAPPER.api_request('games', f'search "{search1}"; fields name;')
        response = json.loads(rq)
    except requests.exceptions.HTTPError as err:
        print(f'{err}')
        response = []
    for each in response:
        if each['name'] == search1:
            id_ = each['id']
    return id_


def get_games(string_):
    search1 = string_.strip()
    gameList = []
    try:
        rq = WRAPPER.api_request('games', f'search "{search1}"; f name, platforms.name;')
        response = json.loads(rq)
    except requests.exceptions.HTTPError as err:
        print(f'{err}')
        response = None
    if response:
        for each in response:
            platformList = []
            platforms = each.get('platforms')
            if platforms:
                for platform in platforms:
                    platformList.append(platform.get('name'))
            else:
                platformList = ['None']
            listItem = {'id': each.get('id'), 'name': each.get('name'), 'platforms': platformList}
            gameList.append(listItem)
    return gameList


def get_game_info(id_):
    # cover, platforms, age rating, mode, genres, themes, rating, summary
    try:
        rq = WRAPPER.api_request(
            'games',
            f'f name, cover.url, summary,storyline,screenshots.url,age_ratings.synopsis,game_modes.name,genres.name,platforms.name,rating,themes.name; where id = {id_};'
        )
        response = json.loads(rq)
        if len(response) == 1:
            return response[0]
    except requests.exceptions.HTTPError as err:
        print(f"{err}")
        return None


def game_finder(selectPlatformCategory, selectPlatformFamily, selectThemes, selectGenres, selectModes):
    rqString = 'f name, cover.url, summary,storyline,screenshots.url,age_ratings.synopsis,game_modes.name,genres.name, platforms.category, platforms.platform_family, rating,themes.name; where rating != null'
    if len(selectPlatformCategory) > 1:
        selectPlatforms = tuple(selectPlatformCategory)
        rqString += f'& platforms.category = {selectPlatforms}'
    elif len(selectPlatformCategory) == 1:
        selectPlatforms = selectPlatformCategory[0]
        rqString += f'& platforms.category = ({selectPlatforms})'

    print(selectPlatformFamily)
    print(selectPlatformCategory)

    if len(selectPlatformFamily) > 1:
        selectPlatforms = tuple(selectPlatformFamily)
        rqString += f'& platforms.platform_family = {selectPlatforms}'
    elif len(selectPlatformFamily) == 1:
        selectPlatforms = selectPlatformFamily[0]
        rqString += f'& platforms.platform_family = ({selectPlatforms})'

    if len(selectThemes) > 1:
        selectThemes = tuple(selectThemes)
        rqString += f'& themes = {selectThemes}'
    elif len(selectThemes) == 1:
        selectThemes = selectThemes[0]
        rqString += f'& themes = ({selectThemes})'
    if len(selectGenres) > 1:
        selectGenres = tuple(selectGenres)
        rqString += f'& genres = {selectGenres}'
    elif len(selectGenres) == 1:
        selectGenres = selectGenres[0]
        rqString += f'& genres = ({selectGenres})'
    if len(selectModes) > 1:
        selectModes = tuple(selectModes)
        rqString += f'& game_modes = {selectModes}'
    elif len(selectModes) == 1:
        selectModes = selectModes[0]
        rqString += f'& game_modes = ({selectModes})'
    print(rqString)
    rq = WRAPPER.api_request('games', f'{rqString}; limit 50; sort rating desc;')
    load = json.loads(rq)
    gameList = []
    for each in load:
        infoDict = {'id': each.get('id'), 'name': each.get('name')}
        if each.get('platforms'):
            infoDict['platforms'] = [platform.get('name') for platform in each.get('platforms')]
        if each.get('cover'):
            infoDict['cover_url'] = each.get('cover').get('url')
        if each.get('game_modes'):
            infoDict['modes'] = [mode.get('name') for mode in each.get('game_modes')]
        if each.get('genres'):
            infoDict['genres'] = [genre.get('name') for genre in each.get('genres')]
        if each.get('themes'):
            infoDict['themes'] = [theme.get('name') for theme in each.get('themes')]
        infoDict['rating'] = each.get('rating')
        if each.get('screenshots'):
            infoDict['screenshot_url'] = [shot.get('url') for shot in each.get('screenshots')]
        infoDict['story'] = each.get('storyline')
        infoDict['sum'] = each.get('summary')
        gameList.append(infoDict)
    return gameList


def hash_pass(password: str = "password"):
    hashPass = password
    # *adds salt*
    salt = "igame"  # probably needs to exist as environment variable at some point
    hashPass += salt
    hashed = hashlib.md5(hashPass.encode())
    return hashed.hexdigest()


def get_game_names(ids_):
    rqString = 'f name;'
    if len(ids_) > 1:
        selectGames = tuple(ids_)
        rqString += f'where id = {selectGames}'
    elif len(ids_) == 1:
        selectGames = ids_[0]
        rqString += f'where id = ({selectGames})'
    else:
        return None
    rq = WRAPPER.api_request('games', f'{rqString};')
    resp = json.loads(rq)
    return resp


def get_list(platforms, noThemes, noGenres, games):
    rqString = 'f name, cover.url, summary,storyline,screenshots.url,age_ratings.synopsis,game_modes.name,genres.name, platforms.name,rating,themes.name;'
    if len(games) > 1:
        selectGames = tuple(games)
        rqString += f'where id = {selectGames} '
    elif len(games) == 1:
        selectGames = games[0]
        rqString += f'where id = {selectGames} '
    if len(platforms) > 1:
        selectPlatforms = tuple(platforms)
        rqString += f'& platforms.category = {selectPlatforms}'
    elif len(platforms) == 1:
        selectPlatforms = platforms[0]
        rqString += f'& platforms.category = ({selectPlatforms})'
    if len(noThemes) > 1:
        selectThemes = tuple(noThemes)
        rqString += f'& themes.id != {selectThemes}'
    elif len(noThemes) == 1:
        selectThemes = noThemes[0]
        rqString += f'& themes.id != ({selectThemes})'
    if len(noGenres) > 1:
        selectGenres = tuple(noGenres)
        rqString += f'& genres.id != {selectGenres}'
    elif len(noGenres) == 1:
        selectGenres = noGenres[0]
        rqString += f'& genres.id != ({selectGenres})'
    rq = WRAPPER.api_request('games', f'{rqString} & rating != null; sort rating desc;')
    load = json.loads(rq)
    gameList = []
    for each in load:
        infoDict = {'id': each.get('id'), 'name': each.get('name')}
        if each.get('platforms'):
            infoDict['platforms'] = [platform.get('name') for platform in each.get('platforms')]
        infoDict['cover_url'] = each.get('cover').get('url')
        if each.get('game_modes'):
            infoDict['modes'] = [mode.get('name') for mode in each.get('game_modes')]
        if each.get('genres'):
            infoDict['genres'] = [genre.get('name') for genre in each.get('genres')]
        if each.get('themes'):
            infoDict['themes'] = [theme.get('name') for theme in each.get('themes')]
        infoDict['rating'] = each.get('rating')
        if each.get('screenshots'):
            infoDict['screenshot_url'] = [shot.get('url') for shot in each.get('screenshots')]
        infoDict['story'] = each.get('storyline')
        infoDict['sum'] = each.get('summary')
        gameList.append(infoDict)
    return gameList


def get_hi_list(plats, hiGen, noGen, hiThm, noThm, games):
    rqString = 'f name, cover.url, summary,storyline,screenshots.url,age_ratings.synopsis,game_modes.name,genres.name, platforms.name,rating,themes.name;'
    if len(games) > 1:
        selectGames = tuple(games)
        rqString += f'where id = {selectGames} '
    elif len(games) == 1:
        selectGames = games[0]
        rqString += f'where id = {selectGames} '
    if len(plats) > 1:
        selectPlatforms = tuple(plats)
        rqString += f'& platforms.id = {selectPlatforms}'
    elif len(plats) == 1:
        selectPlatforms = plats[0]
        rqString += f'& platforms.id = ({selectPlatforms})'
    if len(hiThm) > 1:
        hiThm = tuple(hiThm)
        rqString += f'& themes.id = {hiThm}'
    elif len(hiThm) == 1:
        hiThm = hiThm[0]
        rqString += f'& themes.id = ({hiThm})'
    if len(noThm) > 1:
        noThm = tuple(noThm)
        rqString += f'& themes.id != {noThm}'
    elif len(noThm) == 1:
        noThm = noThm[0]
        rqString += f'& themes.id != ({noThm})'
    if len(hiGen) > 1:
        hiGen = tuple(hiGen)
        rqString += f'& genres.id = {hiGen}'
    elif len(hiGen) == 1:
        hiGen = hiGen[0]
        rqString += f'& genres.id = ({hiGen})'
    if len(noGen) > 1:
        noGen = tuple(noGen)
        rqString += f'& genres.id != {noGen}'
    elif len(noGen) == 1:
        noGen = noGen[0]
        rqString += f'& genres.id != ({noGen})'
    rq = WRAPPER.api_request('games', f'{rqString} & rating != null; sort rating desc;')
    load = json.loads(rq)
    similar = games
    gameList = []
    for each in load:
        infoDict = {'id': each.get('id'), 'name': each.get('name')}
        if each.get('platforms'):
            infoDict['platforms'] = [platform.get('name') for platform in each.get('platforms')]
        infoDict['cover_url'] = each.get('cover').get('url')
        if each.get('game_modes'):
            infoDict['modes'] = [mode.get('name') for mode in each.get('game_modes')]
        if each.get('genres'):
            infoDict['genres'] = [genre.get('name') for genre in each.get('genres')]
        if each.get('themes'):
            infoDict['themes'] = [theme.get('name') for theme in each.get('themes')]
        infoDict['rating'] = each.get('rating')
        if each.get('screenshots'):
            infoDict['screenshot_url'] = [shot.get('url') for shot in each.get('screenshots')]
        infoDict['story'] = each.get('storyline')
        infoDict['sum'] = each.get('summary')
        similar.remove(infoDict['id'])
        gameList.append(infoDict)
    return gameList, similar


def get_genres(games):
    rqString = 'f genres;'
    if len(games) > 1:
        selectGames = tuple(games)
        rqString += f'where id = {selectGames}'
    elif len(games) == 1:
        selectGames = games[0]
        rqString += f'where id = {selectGames}'
    rq = WRAPPER.api_request('games', f'{rqString};')
    response = json.loads(rq)
    if response:
        genres = set(collapse([each.get('genres') for each in response if each.get('genres') is not None]))
        return genres
    else:
        return None


def get_themes(games):
    rqString = 'f themes;'
    if len(games) > 1:
        selectGames = tuple(games)
        rqString += f'where id = {selectGames}'
    elif len(games) == 1:
        selectGames = games[0]
        rqString += f'where id = {selectGames}'
    rq = WRAPPER.api_request('games', f'{rqString};')
    response = json.loads(rq)
    if response:
        themes = set(collapse([each.get('themes') for each in response if each.get('themes') is not None]))
        return themes
    else:
        return None


def get_similar(games):
    rqString = 'f similar_games;'
    if len(games) > 1:
        selectGames = tuple(games)
        rqString += f'where id = {selectGames}'
    elif len(games) == 1:
        selectGames = games[0]
        rqString += f'where id = {selectGames}'
    rq = WRAPPER.api_request('games', f'{rqString};')
    response = json.loads(rq)
    if response:
        similar = set(collapse([each.get('similar_games') for each in response if each.get('similar_games') is not None]))
        return similar
    else:
        return None


def get_platforms(games):
    rqString = 'f platforms;'
    if len(games) > 1:
        selectGames = tuple(games)
        rqString += f'where id = {selectGames}'
    elif len(games) == 1:
        selectGames = games[0]
        rqString += f'where id = {selectGames}'
    rq = WRAPPER.api_request('games', f'{rqString};')
    response = json.loads(rq)
    if response:
        platforms = set(collapse([each.get('platforms') for each in response if each.get('platforms') is not None]))
        return platforms
    else:
        return None


def get_filters():
    # platforms = []
    # rq = WRAPPER.api_request('platforms', 'f name; limit 500; sort id asc;')
    # response = json.loads(rq)
    # if response:
    #     platforms = response

    platformCategories = [{'id': 1, 'name': 'console'}, {'id': 2, 'name': 'arcade'}, {'id': 3, 'name': 'platform'}, {'id': 4, 'name': 'operating system'}, {'id': 5, 'name': 'portable console'}, {'id': 6, 'name': 'computer'}]

    platformFamilies = [{'id': 1, 'name': 'Playstation'}, {'id': 2, 'name': 'Xbox'}, {'id': 3, 'name': 'Sega'}, {'id': 4, 'name': 'Linux'}, {'id': 5, 'name': 'Nintendo'}]


    modes = []
    rq = WRAPPER.api_request('game_modes', 'f name; limit 500; sort id asc;')
    response = json.loads(rq)
    if response:
        modes = response
    genres = []
    rq = WRAPPER.api_request('genres', 'f name; limit 500; sort name asc;')
    response = json.loads(rq)
    if response:
        genres = response
    themes = []
    rq = WRAPPER.api_request('themes', 'f name; limit 500; sort name asc;')
    response = json.loads(rq)
    if response:
        themes = response
    return platformCategories, platformFamilies, genres, modes, themes
