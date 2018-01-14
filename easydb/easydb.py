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

    def remove_element(self, element_id):
        response = requests.delete(f'{EASYDB_URL}/api/v1/spaces/{self.space.name}/{self.bucket_name}/{element_id}')
        return response.status_code == 200

    def update(self, element_id, element):
        response = requests.put(f'{EASYDB_URL}/api/v1/spaces/{self.space.name}/{self.bucket_name}/{element_id}',
                                json={
                                    'fields': [{'name': field_name, 'value': field_value} for field_name, field_value in element.items()]
                                })
        body = response.json()
        return {
            'id': body['id'],
            'bucketName': body['bucketName'],
            'fields': {field['name']: field['value'] for field in body['fields']}
        }

    def all(self):
        response = requests.get(f'{EASYDB_URL}/api/v1/spaces/{self.space.name}/{self.bucket_name}')
        body = response.json()
        return [{
            'id': element['id'],
            'bucketName': element['bucketName'],
            'fields': {field['name']: field['value'] for field in element['fields']}
        } for element in body]

    def get(self, element_id):
        response = requests.get(f'{EASYDB_URL}/api/v1/spaces/{self.space.name}/{self.bucket_name}/{element_id}')
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