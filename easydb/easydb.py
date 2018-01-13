import requests

EASYDB_URL = 'https://easy-db.herokuapp.com'


class Bucket:
    def __init__(self, space, bucket_name):
        self.space = space
        self.bucket_name = bucket_name

    def add_element(self, element):
        response = requests.post(f'{EASYDB_URL}/api/v1/spaces/{self.space.name}/{self.bucket_name}', json=element)
        body = response.json()
        return {
            'id': body['id'],
            'bucketName': body['bucketName'],
            'fields': {field['name']: field['value'] for field in body['fields']}
        }


class Space:
    def __init__(self, name):
        self.name = name

    def get_bucket(self, bucket_name):
        return Bucket(self, bucket_name)


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