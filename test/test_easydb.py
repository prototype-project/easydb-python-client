from unittest import TestCase
import json
from httmock import urlmatch, HTTMock
import easydb_client

SPACE_NAME = 'testSpace'
BUCKET_ELEMENT_ID = 'testId'
BUCKET_NAME = 'testBucket'


def with_mocked_api(api_mock):
    def decorator(test):
        def decorated_test(self):
            with HTTMock(api_mock):
                test(self)
        return decorated_test

    return decorator


@urlmatch(path='/api/v1/spaces', method='POST')
def create_space_api_mock(url, request):
    space_name = request.original.json['spaceName']
    return {
        'status_code': 201,
        'content': json.dumps({'spaceName': space_name})
    }


@urlmatch(path='/api/v1/spaces/{SPACE_NAME}'.format(SPACE_NAME=SPACE_NAME), method='GET')
def get_space_api_mock(url, request):
    return {
        'status_code': 200,
        'content': json.dumps({'spaceName': SPACE_NAME})
    }


@urlmatch(path='/api/v1/spaces/{SPACE_NAME}'.format(SPACE_NAME=SPACE_NAME), method='GET')
def space_exists_api_mock(url, request):
    return {
        'status_code': 200,
        'content': json.dumps({'spaceName': SPACE_NAME})
    }


@urlmatch(path='/api/v1/spaces/{SPACE_NAME}'.format(SPACE_NAME=SPACE_NAME), method='DELETE')
def remove_space_api_mock(url, request):
    return {
        'status_code': 200
    }


@urlmatch(path='/api/v1/spaces'.format(SPACE_NAME=SPACE_NAME), method='POST')
def try_to_create_space_with_non_unique_name_api_mock(url, request):
    return {
        'status_code': 400
    }


@urlmatch(path='/api/v1/spaces/{SPACE_NAME}'.format(SPACE_NAME=SPACE_NAME), method='DELETE')
def try_to_remove_nonexistent_space_api_mock(url, request):
    return {
        'status_code': 404
    }


@urlmatch(path='/api/v1/spaces/{SPACE_NAME}'.format(SPACE_NAME=SPACE_NAME), method='GET')
def try_to_get_nonexistent_space_api_mock(url, request):
    return {
        'status_code': 404
    }


class EasydbTest(TestCase):

    @with_mocked_api(create_space_api_mock)
    def test_should_create_new_space(self):
        # when
        space = easydb_client.create_space(SPACE_NAME)

        # then
        self.assertIsNotNone(space)

        # and
        self.assertEqual(space.name, SPACE_NAME)

    @with_mocked_api(get_space_api_mock)
    def test_should_get_space(self):
        # given space

        # when
        space = easydb_client.get_space(SPACE_NAME)

        # then
        self.assertIsNotNone(space)

    @with_mocked_api(space_exists_api_mock)
    def test_should_tell_if_space_exists(self):
        # given space

        # when
        exists = easydb_client.space_exists(SPACE_NAME)

        # then
        self.assertTrue(exists)

    @with_mocked_api(remove_space_api_mock)
    def test_should_remove_space(self):
        # when
        removed = easydb_client.remove_space(SPACE_NAME)

        # then
        self.assertIsNone(removed)

    @with_mocked_api(try_to_create_space_with_non_unique_name_api_mock)
    def test_should_throw_error_when_trying_to_create_space_with_non_unique_name(self):
        with self.assertRaises(easydb_client.SpaceAlreadyExists):  # then
            easydb_client.create_space(SPACE_NAME)  # when

    @with_mocked_api(try_to_remove_nonexistent_space_api_mock)
    def test_should_throw_error_when_trying_to_remove_nonexistent_space(self):
        with self.assertRaises(easydb_client.SpaceNotFound):  # then
            easydb_client.remove_space(SPACE_NAME)  # when

    @with_mocked_api(try_to_get_nonexistent_space_api_mock)
    def test_should_throw_error_when_trying_to_get_nonexistent_space(self):
        with self.assertRaises(easydb_client.SpaceNotFound):  # then
            easydb_client.get_space(SPACE_NAME)  # when


@urlmatch(path='/api/v1/{SPACE_NAME}/{BUCKET_NAME}'.format(SPACE_NAME=SPACE_NAME, BUCKET_NAME=BUCKET_NAME), method='POST')
def add_element_to_bucket_api_mock(url, request):
    return {
        'status_code': 201,
        'content': json.dumps({
            'id': BUCKET_ELEMENT_ID,
            'bucketName': BUCKET_NAME,
            'fields': [
                {
                    'name': 'firstName',
                    'value': 'John'
                }
            ]
        })
    }


@urlmatch(path='/api/v1/{SPACE_NAME}/{BUCKET_NAME}/{BUCKET_ELEMENT_ID}'.format(
    SPACE_NAME=SPACE_NAME, BUCKET_NAME=BUCKET_NAME, BUCKET_ELEMENT_ID=BUCKET_ELEMENT_ID), method='DELETE')
def remove_element_from_bucket_api_mock(url, request):
    return {
        'status_code': 200
    }


@urlmatch(path='/api/v1/{SPACE_NAME}/{BUCKET_NAME}/{BUCKET_ELEMENT_ID}'.format(
    SPACE_NAME=SPACE_NAME, BUCKET_NAME=BUCKET_NAME, BUCKET_ELEMENT_ID=BUCKET_ELEMENT_ID), method='PUT')
def update_element_from_bucket_api_mock(url, request):
    return {
        'status_code': 200,
        'content': json.dumps({
            'id': BUCKET_ELEMENT_ID,
            'bucketName': BUCKET_NAME,
            'fields': [
                {
                    'name': 'firstName',
                    'value': 'John'
                }
            ]
        })
    }


@urlmatch(path='/api/v1/{SPACE_NAME}/{BUCKET_NAME}'.format(
    SPACE_NAME=SPACE_NAME, BUCKET_NAME=BUCKET_NAME), method='GET')
def get_all_bucket_elements_api_mock(url, request):
    return {
        'status_code': 200,
        'content': json.dumps([
            {
                'id': BUCKET_ELEMENT_ID,
                'bucketName': BUCKET_NAME,
                'fields': [
                    {
                        'name': 'firstName',
                        'value': 'John'
                    }
                ]
            }
        ])
    }


@urlmatch(path='/api/v1/{SPACE_NAME}/{BUCKET_NAME}/{BUCKET_ELEMENT_ID}'.format(
    SPACE_NAME=SPACE_NAME, BUCKET_NAME=BUCKET_NAME, BUCKET_ELEMENT_ID=BUCKET_ELEMENT_ID), method='GET')
def get_element_from_bucket_api_mock(url, request):
    return {
        'status_code': 200,
        'content': json.dumps({
            'id': BUCKET_ELEMENT_ID,
            'bucketName': BUCKET_NAME,
            'fields': [
                {
                    'name': 'firstName',
                    'value': 'John'
                }
            ]
        })
    }


@urlmatch(path='/api/v1/{SPACE_NAME}/{BUCKET_NAME}/{BUCKET_ELEMENT_ID}'.format(
    SPACE_NAME=SPACE_NAME, BUCKET_NAME=BUCKET_NAME, BUCKET_ELEMENT_ID=BUCKET_ELEMENT_ID), method='PUT')
def try_to_update_nonexistent_element_api_mock(url, request):
    return {
        'status_code': 404
    }


@urlmatch(path='/api/v1/{SPACE_NAME}/{BUCKET_NAME}/{BUCKET_ELEMENT_ID}'.format(
    SPACE_NAME=SPACE_NAME, BUCKET_NAME=BUCKET_NAME, BUCKET_ELEMENT_ID=BUCKET_ELEMENT_ID), method='GET')
def try_to_get_nonexistent_element_api_mock(url, request):
    return {
        'status_code': 404
    }


@urlmatch(path='/api/v1/{SPACE_NAME}/{BUCKET_NAME}/{BUCKET_ELEMENT_ID}'.format(
    SPACE_NAME=SPACE_NAME, BUCKET_NAME=BUCKET_NAME, BUCKET_ELEMENT_ID=BUCKET_ELEMENT_ID), method='PUT')
def try_to_pass_invalid_element_to_update_api_mock(url, request):
    return {
        'status_code': 400
    }


@urlmatch(path='/api/v1/{SPACE_NAME}/{BUCKET_NAME}/{BUCKET_ELEMENT_ID}'.format(
    SPACE_NAME=SPACE_NAME, BUCKET_NAME=BUCKET_NAME, BUCKET_ELEMENT_ID=BUCKET_ELEMENT_ID), method='DELETE')
def try_to_remove_nonexistent_element_api_mock(url, request):
    return {
        'status_code': 404
    }


@urlmatch(path='/api/v1/{SPACE_NAME}/{BUCKET_NAME}'.format(
    SPACE_NAME=SPACE_NAME, BUCKET_NAME=BUCKET_NAME), method='POST')
def try_to_pass_invalid_element_to_add_api_mock(url, request):
    return {
        'status_code': 400
    }


class BucketTest(TestCase):

    @with_mocked_api(add_element_to_bucket_api_mock)
    @with_mocked_api(get_space_api_mock)
    def test_should_add_element_to_bucket(self):
        # given
        space = easydb_client.get_space(SPACE_NAME)

        # and
        bucket = space.get_bucket(BUCKET_NAME)

        # when
        saved_element = bucket.add({'firstName': 'John'})

        # then
        self.assertEqual(saved_element['fields']['firstName'], 'John')

        # and
        self.assertEqual(saved_element['id'], BUCKET_ELEMENT_ID)

        # and
        self.assertEqual(saved_element['bucketName'], BUCKET_NAME)

    @with_mocked_api(get_space_api_mock)
    @with_mocked_api(remove_element_from_bucket_api_mock)
    def test_should_remove_element_from_bucket(self):
        # given
        bucket = easydb_client.get_space(SPACE_NAME).get_bucket(BUCKET_NAME)
        # and bucket element

        # when then
        bucket.remove(BUCKET_ELEMENT_ID)

    @with_mocked_api(get_space_api_mock)
    @with_mocked_api(update_element_from_bucket_api_mock)
    def test_should_update_element_in_bucket(self):
        # given
        bucket = easydb_client.get_space(SPACE_NAME).get_bucket(BUCKET_NAME)

        # and bucket element

        # when
        updated_element = bucket.update(BUCKET_ELEMENT_ID, {'firstName': 'John'})

        # then
        self.assertEqual(updated_element['fields']['firstName'], 'John')

        # and
        self.assertEqual(updated_element['id'], BUCKET_ELEMENT_ID)

        # and
        self.assertEqual(updated_element['bucketName'], BUCKET_NAME)

    @with_mocked_api(get_space_api_mock)
    @with_mocked_api(get_all_bucket_elements_api_mock)
    def test_should_get_all_elements_from_bucket(self):
        # given
        bucket = easydb_client.get_space(SPACE_NAME).get_bucket(BUCKET_NAME)

        # when
        elements = bucket.all()

        # then
        self.assertEqual(len(elements), 1)

    @with_mocked_api(get_space_api_mock)
    @with_mocked_api(get_element_from_bucket_api_mock)
    def test_should_get_element_from_bucket(self):
        # given
        bucket = easydb_client.get_space(SPACE_NAME).get_bucket(BUCKET_NAME)

        # when
        element = bucket.get(BUCKET_ELEMENT_ID)

        # then
        self.assertEqual(element, {
            'id': BUCKET_ELEMENT_ID,
            'bucketName': BUCKET_NAME,
            'fields': {
                'firstName': 'John'
            }
        })

    @with_mocked_api(get_space_api_mock)
    @with_mocked_api(try_to_update_nonexistent_element_api_mock)
    def test_should_throw_error_when_trying_to_update_nonexistent_element(self):
        # given
        bucket = easydb_client.get_space(SPACE_NAME).get_bucket(BUCKET_NAME)

        with self.assertRaises(easydb_client.ElementNotFound):  # then
            bucket.update(BUCKET_ELEMENT_ID, {'firstName': 'Johny'})  # when

    @with_mocked_api(get_space_api_mock)
    @with_mocked_api(try_to_get_nonexistent_element_api_mock)
    def test_should_throw_error_when_trying_to_get_nonexistent_element(self):
        # given
        bucket = easydb_client.get_space(SPACE_NAME).get_bucket(BUCKET_NAME)

        with self.assertRaises(easydb_client.ElementNotFound):  # then
            bucket.get(BUCKET_ELEMENT_ID)  # when

    @with_mocked_api(get_space_api_mock)
    @with_mocked_api(try_to_pass_invalid_element_to_update_api_mock)
    def test_should_throw_error_when_passing_invalid_element_to_update(self):
        # given
        bucket = easydb_client.get_space(SPACE_NAME).get_bucket(BUCKET_NAME)

        with self.assertRaises(easydb_client.InvalidElementFormat):  # then
            bucket.update(BUCKET_ELEMENT_ID, {'fieldWithInvalidValue': []})  # when

    @with_mocked_api(get_space_api_mock)
    @with_mocked_api(try_to_remove_nonexistent_element_api_mock)
    def test_should_throw_error_when_trying_to_remove_nonexistent_element(self):
        # given
        bucket = easydb_client.get_space(SPACE_NAME).get_bucket(BUCKET_NAME)

        with self.assertRaises(easydb_client.ElementNotFound):  # then
            bucket.remove(BUCKET_ELEMENT_ID)  # when

    @with_mocked_api(get_space_api_mock)
    @with_mocked_api(try_to_pass_invalid_element_to_add_api_mock)
    def test_should_throw_error_when_passing_invalid_element_to_add(self):
        # given
        bucket = easydb_client.get_space(SPACE_NAME).get_bucket(BUCKET_NAME)

        with self.assertRaises(easydb_client.InvalidElementFormat):  # then
            bucket.add({'fieldWithInvalidValue': []})  # when