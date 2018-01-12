import requests

EASYDB_URL = 'https://easy-db.herokuapp.com'


def create_space(unique_space_name):
    response = requests.post(
        f'{EASYDB_URL}/api/v1/spaces',
        json={'spaceName': unique_space_name}
    )
    return Space(response.json()['spaceName'])


def get_space(space_name):
    response = requests.get(f'{EASYDB_URL}/api/v1/spaces/{space_name}')
    if response.status_code == 200:
        return Space(response.json()['spaceName'])
    else:
        assert response.status_code == 404
        return None


def space_exists(space_name):
    return get_space(space_name) is not None


def remove_space(space_name):
    response = requests.delete(f'{EASYDB_URL}/api/v1/spaces/{space_name}')
    return response.status_code == 200


class Space:
    def __init__(self, name):
        self.name = name


class Bucket:
    pass

