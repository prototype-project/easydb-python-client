from unittest import TestCase
import json
from httmock import urlmatch, HTTMock
import easydb

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


@urlmatch(path=f'/api/v1/spaces/{SPACE_NAME}', method='GET')
def get_space_api_mock(url, request):
    return {
        'status_code': 200,
        'content': json.dumps({'spaceName': SPACE_NAME})
    }


@urlmatch(path=f'/api/v1/spaces/{SPACE_NAME}', method='GET')
def space_exists_api_mock(url, request):
    return {
        'status_code': 200,
        'content': json.dumps({'spaceName': SPACE_NAME})
    }


@urlmatch(path=f'/api/v1/spaces/{SPACE_NAME}', method='DELETE')
def remove_space_api_mock(url, request):
    return {
        'status_code': 200
    }


class EasydbTest(TestCase):

    @with_mocked_api(create_space_api_mock)
    def test_should_create_new_space(self):
        # when
        space = easydb.create_space(SPACE_NAME)

        # then
        self.assertIsNotNone(space)

        # and
        self.assertEqual(space.name, SPACE_NAME)

    @with_mocked_api(get_space_api_mock)
    def test_should_get_space(self):
        # given space

        # when
        space = easydb.get_space(SPACE_NAME)

        # then
        self.assertIsNotNone(space)

    @with_mocked_api(space_exists_api_mock)
    def test_should_tell_if_space_exists(self):
        # given space

        # when
        exists = easydb.space_exists(SPACE_NAME)

        # then
        self.assertTrue(exists)

    @with_mocked_api(remove_space_api_mock)
    def test_should_remove_space(self):
        # when
        removed = easydb.remove_space(SPACE_NAME)

        # then
        self.assertTrue(removed)


@urlmatch(path=f'/api/v1/spaces/{SPACE_NAME}/{BUCKET_NAME}', method='POST')
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


@urlmatch(path=f'/api/v1/spaces/{SPACE_NAME}/{BUCKET_NAME}/{BUCKET_ELEMENT_ID}', method='DELETE')
def remove_element_from_bucket_api_mock(url, request):
    return {
        'status_code': 200
    }


@urlmatch(path=f'/api/v1/spaces/{SPACE_NAME}/{BUCKET_NAME}/{BUCKET_ELEMENT_ID}', method='PUT')
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


@urlmatch(path=f'/api/v1/spaces/{SPACE_NAME}/{BUCKET_NAME}', method='GET')
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


@urlmatch(path=f'/api/v1/spaces/{SPACE_NAME}/{BUCKET_NAME}/{BUCKET_ELEMENT_ID}', method='GET')
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


@urlmatch(path=f'/api/v1/spaces/{SPACE_NAME}/{BUCKET_NAME}/{BUCKET_ELEMENT_ID}', method='PUT')
def try_to_update_nonexistent_element_api_mock(url, request):
    return {
        'status_code': 404
    }


class BucketTest(TestCase):

    @with_mocked_api(add_element_to_bucket_api_mock)
    @with_mocked_api(get_space_api_mock)
    def test_should_add_element_to_bucket(self):
        # given
        space = easydb.get_space(SPACE_NAME)

        # and
        bucket = space.get_bucket(BUCKET_NAME)

        # when
        saved_element = bucket.add_element({'firstName': 'John'})

        # then
        self.assertEqual(saved_element['fields']['firstName'], 'John')

        # and
        self.assertEqual(saved_element['id'], BUCKET_ELEMENT_ID)

        # and
        self.assertEqual(saved_element['bucketName'], BUCKET_NAME)

    @with_mocked_api(get_space_api_mock)
    @with_mocked_api(remove_space_api_mock)
    def test_should_remove_element_from_bucket(self):
        # given
        bucket = easydb.get_space(SPACE_NAME).get_bucket(BUCKET_NAME)
        # and bucket element

        # when
        removed = bucket.remove_element(BUCKET_ELEMENT_ID)

        # then
        self.assertTrue(removed)

    @with_mocked_api(get_space_api_mock)
    @with_mocked_api(update_element_from_bucket_api_mock)
    def test_should_update_element_in_bucket(self):
        # given
        bucket = easydb.get_space(SPACE_NAME).get_bucket(BUCKET_NAME)

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
        bucket = easydb.get_space(SPACE_NAME).get_bucket(BUCKET_NAME)

        # when
        elements = bucket.all()

        # then
        self.assertEqual(len(elements), 1)

    @with_mocked_api(get_space_api_mock)
    @with_mocked_api(get_element_from_bucket_api_mock)
    def test_should_get_element_from_bucket(self):
        # given
        bucket = easydb.get_space(SPACE_NAME).get_bucket(BUCKET_NAME)

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
        bucket = easydb.get_space(SPACE_NAME).get_bucket(BUCKET_NAME)

        with self.assertRaises(easydb.ElementNotFound):  # then
            bucket.update('nonexistentId', {'firstName': 'Johny'})  # when
