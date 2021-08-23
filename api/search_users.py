from api.create_request import create_request
from pprint import pprint


def get_most_popular_photo(data):
    photos = [{'count': 0, 'url': '', 'id': ''}, {'count': 0, 'url': '', 'id': ''}, {'count': 0, 'url': '', 'id': ''}]
    print('photos')
    pprint(data)
    for i in range(3):
        for photo in data:
            count = photo['likes']['count'] + photo['comments']['count']
            if i == 0:
                if photos[i]['count'] < count:
                    photos[i]['count'] = count
                    photos[i]['url'] = photo['sizes'][-1]['url']
                    photos[i]['id'] = photo['id']
            if i == 1:
                if photos[i]['count'] < count and photos[0]['url'] != photo['sizes'][-1]['url']:
                    photos[i]['count'] = count
                    photos[i]['url'] = photo['sizes'][-1]['url']
                    photos[i]['id'] = photo['id']
            if i == 2:
                if photos[i]['count'] < count and photos[0]['url'] != photo['sizes'][-1]['url'] and photos[1]['url'] != \
                        photo['sizes'][-1]['url']:
                    photos[i]['count'] = count
                    photos[i]['url'] = photo['sizes'][-1]['url']
                    photos[i]['id'] = photo['id']
    return photos


def get_photo(id, token_user):
    params = {
        'owner_id': id,
        'extended': 1,
        'album_id': 'profile',
        'v': '5.77',
        'access_token': token_user,
    }
    result = create_request('photos.get', params)
    photos_data = result['response']['items']
    return get_most_popular_photo(photos_data)


def search_users(user, token_user, count):
    params = {
        'sort': 0,
        'city': user['city'],
        'age_from': int(user['age']) - 2,
        'age_to': int(user['age']) + 2,
        'status': user['status'],
        'sex': 1 if int(user['sex']) == 2 else 2,
        'access_token': token_user,
        'v': '5.131',
        'offset': count,
        'has_photo': 1,
    }
    pprint(params)
    result = create_request('users.search', params)
    pprint(result)
    user_id = result['response']['items'][0]['id']
    if is_private(user_id, token_user):
        return {
            'id': user_id,
            'photos': []
        }
    return {
        'id': user_id,
        'photos': get_photo(user_id, token_user)
    }


def is_private(id, token_user):
    params = {
        'user_ids': id,
        'v': '5.131',
        'access_token': token_user,
    }
    result = create_request('users.get', params)
    return result['response'][0]['is_closed']
