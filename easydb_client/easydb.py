import requests
from . import query as Q

EASYDB_URL = 'https://easy-db.herokuapp.com'


class ElementNotFound(ValueError):
    pass


class InvalidElementFormat(ValueError):
    pass


class ServerError(RuntimeError):
    pass


class SpaceNotFound(ValueError):
    pass


class Bucket:
    def __init__(self, space, bucket_name):
        self.space = space
        self.bucket_name = bucket_name

    def add(self, element):
        response = requests.post(
            '{EASYDB_URL}/api/v1/{space_name}/{bucket_name}'.format(
                EASYDB_URL=EASYDB_URL, space_name=self.space.name, bucket_name=self.bucket_name),
            json={
                'fields': [{'name': field_name, 'value': field_value} for field_name, field_value in element.items()]
            })
        if response.status_code == 201:
            body = response.json()
            return {
                'id': body['id'],
                'bucketName': body['bucketName'],
                'fields': {field['name']: field['value'] for field in body['fields']}
            }
        elif response.status_code == 400:
            raise InvalidElementFormat()
        else:
            assert response.status_code == 500
            raise ServerError()

    def remove(self, element_id):
        response = requests.delete('{EASYDB_URL}/api/v1/{space_name}/{bucket_name}/{element_id}'.format(
            EASYDB_URL=EASYDB_URL, space_name=self.space.name, bucket_name=self.bucket_name, element_id=element_id))
        if response.status_code == 404:
            raise ElementNotFound()
        elif response.status_code == 500:
            raise ServerError()
        else:
            assert response.status_code == 200

    def update(self, element_id, element):
        response = requests.put('{EASYDB_URL}/api/v1/{space_name}/{bucket_name}/{element_id}'.format(
            EASYDB_URL=EASYDB_URL, space_name=self.space.name, bucket_name=self.bucket_name, element_id=element_id),
                                json={
                                    'fields': [{'name': field_name, 'value': field_value} for field_name, field_value in element.items()]
                                })
        if response.status_code == 200:
            return {
                'id': element_id,
                'bucketName': self.bucket_name,
                'fields': element
            }
        elif response.status_code == 404:
            raise ElementNotFound()
        elif response.status_code == 400:
            raise InvalidElementFormat()
        else:
            assert response.status_code == 500
            raise ServerError()

    def filter(self, q):
        q_string = self._produce_query_string_from_query(q._validate())
        yield from self._fetch(f'{self._build_url()}?{q_string}')

    def _produce_query_string_from_query(self, q):
        if isinstance(q, Q.WhereCriteria):
            return f'{q.field_name}={q.expected_value}'
        elif isinstance(q, Q.AndCriteria):
            left_result = self._produce_query_string_from_query(q.left)
            right_result = self._produce_query_string_from_query(q.right)
            return f'{left_result}&{right_result}'

    def all(self):
        url = self._build_url()
        yield from self._fetch(url)

    def _fetch(self, url):
        next_url, part = self._fetch_part(url)
        yield from part

        while next_url:
            next_url, part = self._fetch_part(next_url)
            yield from part

    def _fetch_part(self, url):
        response = requests.get(url)
        assert response.status_code == 200
        body = response.json()
        return body['next'], ({
            'id': element['id'],
            'bucketName': element['bucketName'],
            'fields': {field['name']: field['value'] for field in element['fields']}
        } for element in body['results'])

    def _build_url(self):
        result = '{EASYDB_URL}/api/v1/{space_name}/{bucket_name}'.format(
            EASYDB_URL=EASYDB_URL, space_name=self.space.name, bucket_name=self.bucket_name)
        return result

    def get(self, element_id):
        response = requests.get('{EASYDB_URL}/api/v1/{space_name}/{bucket_name}/{element_id}'.format(
            EASYDB_URL=EASYDB_URL, space_name=self.space.name, bucket_name=self.bucket_name, element_id=element_id))
        if response.status_code == 200:
            body = response.json()
            return {
                'id': body['id'],
                'bucketName': body['bucketName'],
                'fields': {field['name']: field['value'] for field in body['fields']}
            }
        elif response.status_code == 404:
            raise ElementNotFound()
        else:
            raise ServerError()


class Space:
    def __init__(self, name):
        self.name = name

    def get_bucket(self, bucket_name):
        return Bucket(self, bucket_name)


def create_space():
    response = requests.post('{EASYDB_URL}/api/v1/spaces'.format(EASYDB_URL=EASYDB_URL))
    assert response.status_code == 201
    return Space(response.json()['spaceName'])


def get_space(space_name):
    response = requests.get('{EASYDB_URL}/api/v1/spaces/{space_name}'.format(EASYDB_URL=EASYDB_URL, space_name=space_name))
    if response.status_code == 200:
        return Space(response.json()['spaceName'])
    else:
        assert response.status_code == 404
        raise SpaceNotFound()


def space_exists(space_name):
    try:
        get_space(space_name)
        return True
    except SpaceNotFound:
        return False


def remove_space(space_name):
    response = requests.delete('{EASYDB_URL}/api/v1/spaces/{space_name}'.format(EASYDB_URL=EASYDB_URL, space_name=space_name))
    if response.status_code == 404:
        raise SpaceNotFound()
    elif response.status_code == 500:
        raise ServerError()
    else:
        assert response.status_code == 200