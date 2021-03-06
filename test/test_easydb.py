from unittest import TestCase
import json
from httmock import urlmatch, HTTMock
from easydb_client.easydb import EASYDB_URL

SPACE_NAME = 'testSpace'
BUCKET_ELEMENT_ID = 'testId'
BUCKET_NAME = 'testBucket'


# Test for both easydb client and in memory version of easydb


def run_for_both_client_and_in_memory(
        in_memory_setup=lambda in_memory: None,
        in_memory_cleanup=lambda in_memory: None):
    def decorator(test_method):
        def test_for_both_client_and_in_memory(self, *args, **kwargs):
            import easydb_client
            import easydb_client.inmemory as inmemory
            test_method(self, easydb_client, *args, **kwargs)

            in_memory_setup(inmemory)
            test_method(self, inmemory, *args, **kwargs)
            in_memory_cleanup(inmemory)

        return test_for_both_client_and_in_memory

    return decorator


def with_mocked_api(api_mock):
    def decorator(test):
        def decorated_test(self):
            with HTTMock(api_mock):
                test(self)

        return decorated_test

    return decorator


@urlmatch(path='/api/v1/spaces', method='POST')
def create_space_api_mock(url, request):
    return {
        'status_code': 201,
        'content': json.dumps({'spaceName': SPACE_NAME})
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


@urlmatch(path='/api/v1/spaces/nonexistent'.format(SPACE_NAME=SPACE_NAME), method='GET')
def space_does_not_exist_api_mock(url, request):
    return {
        'status_code': 404
    }


@urlmatch(path='/api/v1/spaces/{SPACE_NAME}'.format(SPACE_NAME=SPACE_NAME), method='DELETE')
def remove_space_api_mock(url, request):
    return {
        'status_code': 200
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
    @run_for_both_client_and_in_memory(
        in_memory_cleanup=lambda in_memory: in_memory.remove_all_spaces()
    )
    def test_should_create_new_space(self, easydb_client):
        # when
        space = easydb_client.create_space()

        # then
        self.assertIsNotNone(space)

        # and
        self.assertTrue(space.name)

    @with_mocked_api(get_space_api_mock)
    @with_mocked_api(create_space_api_mock)
    @run_for_both_client_and_in_memory(
        in_memory_cleanup=lambda in_memory: in_memory.remove_all_spaces()
    )
    def test_should_get_space(self, easydb_client):
        # given
        created_space = easydb_client.create_space()

        # when
        space = easydb_client.get_space(created_space.name)

        # then
        self.assertIsNotNone(space)

        # and
        self.assertEqual(space.name, created_space.name)

    @with_mocked_api(space_exists_api_mock)
    @with_mocked_api(space_does_not_exist_api_mock)
    @with_mocked_api(create_space_api_mock)
    @run_for_both_client_and_in_memory(
        in_memory_cleanup=lambda in_memory: in_memory.remove_all_spaces()
    )
    def test_should_tell_if_space_exists(self, easydb_client):
        # given
        created_space = easydb_client.create_space()

        # when
        exists = easydb_client.space_exists(created_space.name)

        # then
        self.assertTrue(exists)

        # when
        exists = easydb_client.space_exists('nonexistent')

        # then
        self.assertFalse(exists)

    @with_mocked_api(remove_space_api_mock)
    @with_mocked_api(create_space_api_mock)
    @run_for_both_client_and_in_memory()
    def test_should_remove_space(self, easydb_client):
        # given
        created_space = easydb_client.create_space()

        # when
        removed = easydb_client.remove_space(created_space.name)

        # then
        self.assertIsNone(removed)

    @with_mocked_api(try_to_remove_nonexistent_space_api_mock)
    @run_for_both_client_and_in_memory()
    def test_should_throw_error_when_trying_to_remove_nonexistent_space(self, easydb_client):
        with self.assertRaises(easydb_client.SpaceNotFound):  # then
            easydb_client.remove_space(SPACE_NAME)  # when

    @with_mocked_api(try_to_get_nonexistent_space_api_mock)
    @run_for_both_client_and_in_memory()
    def test_should_throw_error_when_trying_to_get_nonexistent_space(self, easydb_client):
        with self.assertRaises(easydb_client.SpaceNotFound):  # then
            easydb_client.get_space(SPACE_NAME)  # when


@urlmatch(path='/api/v1/{SPACE_NAME}/{BUCKET_NAME}'
          .format(SPACE_NAME=SPACE_NAME, BUCKET_NAME=BUCKET_NAME), method='POST')
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
    if not url.query:
        return {
            'status_code': 200,
            'content': json.dumps({
                'next': f'{EASYDB_URL}/api/v1/{SPACE_NAME}/{BUCKET_NAME}?limit=1&offset=1',
                'results': [
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
                ]
            })
        }
    else:
        return {
            'status_code': 200,
            'content': json.dumps({
                'next': None,
                'results': [
                    {
                        'id': BUCKET_ELEMENT_ID,
                        'bucketName': BUCKET_NAME,
                        'fields': [
                            {
                                'name': 'firstName',
                                'value': 'Mark'
                            }
                        ]
                    }
                ]
            })
        }


@urlmatch(path='/api/v1/{SPACE_NAME}/{BUCKET_NAME}'.format(
    SPACE_NAME=SPACE_NAME, BUCKET_NAME=BUCKET_NAME), method='GET')
def get_filtered_bucket_elements_api_mock(url, request):
    return {
        'status_code': 200,
        'content': json.dumps({
            'next': None,
            'results': [
                {
                    'id': BUCKET_ELEMENT_ID,
                    'bucketName': BUCKET_NAME,
                    'fields': [
                        {
                            'name': 'firstName',
                            'value': 'Mark'
                        },
                        {
                            'name': 'lastName',
                            'value': 'Smith'
                        }
                    ]
                }
            ]
        })
    }


@urlmatch(path='/api/v1/{SPACE_NAME}/{BUCKET_NAME}'.format(
    SPACE_NAME=SPACE_NAME, BUCKET_NAME=BUCKET_NAME), method='GET')
def get_filtered_single_bucket_elements_api_mock(url, request):
    return {
        'status_code': 200,
        'content': json.dumps({
            'next': None,
            'results': [
                {
                    'id': BUCKET_ELEMENT_ID,
                    'bucketName': BUCKET_NAME,
                    'fields': [
                        {
                            'name': 'firstName',
                            'value': 'Mark'
                        },
                        {
                            'name': 'lastName',
                            'value': 'Robinson'
                        },
                        {
                            'name': 'alias',
                            'value': 'meh'
                        }
                    ]
                }
            ]
        })
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
    @with_mocked_api(create_space_api_mock)
    @run_for_both_client_and_in_memory(
        in_memory_cleanup=lambda in_memory: in_memory.remove_all_spaces()
    )
    def test_should_add_element_to_bucket(self, easydb_client):
        # given
        space = easydb_client.create_space()

        # and
        bucket = space.get_bucket(BUCKET_NAME)

        # when
        saved_element = bucket.add({'firstName': 'John'})

        # then
        self.assertEqual(saved_element['fields']['firstName'], 'John')

        # and
        self.assertIsInstance(saved_element['id'], str)

        # and
        self.assertEqual(saved_element['bucketName'], BUCKET_NAME)

    @with_mocked_api(add_element_to_bucket_api_mock)
    @with_mocked_api(create_space_api_mock)
    @with_mocked_api(remove_element_from_bucket_api_mock)
    @run_for_both_client_and_in_memory(
        in_memory_cleanup=lambda in_memory: in_memory.remove_all_spaces()
    )
    def test_should_remove_element_from_bucket(self, easydb_client):
        # given
        space = easydb_client.create_space()

        # and
        bucket = space.get_bucket(BUCKET_NAME)

        # and
        saved_element = bucket.add({'firstName': 'John'})

        # when then
        self.assertIsNone(bucket.remove(saved_element['id']))

    @with_mocked_api(add_element_to_bucket_api_mock)
    @with_mocked_api(create_space_api_mock)
    @with_mocked_api(update_element_from_bucket_api_mock)
    @run_for_both_client_and_in_memory(
        in_memory_cleanup=lambda in_memory: in_memory.remove_all_spaces()
    )
    def test_should_update_element_in_bucket(self, easydb_client):
        # given
        space = easydb_client.create_space()

        # and
        bucket = space.get_bucket(BUCKET_NAME)

        # and
        saved_element = bucket.add({'firstName': 'John'})

        # when
        updated_element = bucket.update(saved_element['id'], {'firstName': 'John'})

        # then
        self.assertEqual(updated_element['fields']['firstName'], 'John')

        # and
        self.assertEqual(updated_element['id'], saved_element['id'])

        # and
        self.assertEqual(updated_element['bucketName'], BUCKET_NAME)

    @with_mocked_api(add_element_to_bucket_api_mock)
    @with_mocked_api(create_space_api_mock)
    @with_mocked_api(get_all_bucket_elements_api_mock)
    @run_for_both_client_and_in_memory(
        in_memory_cleanup=lambda in_memory: in_memory.remove_all_spaces()
    )
    def test_should_get_all_elements_from_bucket(self, easydb_client):
        # given
        space = easydb_client.create_space()

        # and
        bucket = space.get_bucket(BUCKET_NAME)

        # and
        bucket.add({'firstName': 'John'})
        bucket.add({'firstName': 'Mark'})

        # when
        elements = list(bucket.all())

        # then
        self.assertEqual(len(elements), 2)

    @with_mocked_api(add_element_to_bucket_api_mock)
    @with_mocked_api(create_space_api_mock)
    @with_mocked_api(get_filtered_bucket_elements_api_mock)
    @run_for_both_client_and_in_memory(
        in_memory_cleanup=lambda in_memory: in_memory.remove_all_spaces()
    )
    def test_should_get_elements_filtered_by_multiple_fields_from_bucket(self, easydb_client):
        # given
        space = easydb_client.create_space()

        # and
        bucket = space.get_bucket(BUCKET_NAME)

        # and
        bucket.add({'firstName': 'John'})
        bucket.add({'firstName': 'Mark', 'lastName': 'Smith'})
        bucket.add({'firstName': 'Mark', 'lastName': 'Robinson'})

        # and
        first_name_eq_mark = easydb_client.query.where('firstName').eq('Mark')
        last_name_eq_smith = easydb_client.query.where('lastName').eq('Smith')

        # when
        elements = list(bucket.filter(first_name_eq_mark & last_name_eq_smith))

        # then
        self.assertEqual(len(elements), 1)

    @with_mocked_api(add_element_to_bucket_api_mock)
    @with_mocked_api(create_space_api_mock)
    @with_mocked_api(get_filtered_single_bucket_elements_api_mock)
    @run_for_both_client_and_in_memory(
        in_memory_cleanup=lambda in_memory: in_memory.remove_all_spaces()
    )
    def test_should_get_elements_filtered_by_single_field_from_bucket(self, easydb_client):
        # given
        space = easydb_client.create_space()

        # and
        bucket = space.get_bucket(BUCKET_NAME)

        # and
        bucket.add({'firstName': 'John'})
        bucket.add({'firstName': 'Mark', 'lastName': 'Smith'})
        bucket.add({'firstName': 'Mark', 'lastName': 'Robinson', 'alias': 'meh'})

        # when
        elements = list(bucket.filter(easydb_client.query.where('alias').eq('meh')))

        # then
        self.assertEqual(len(elements), 1)

    @with_mocked_api(add_element_to_bucket_api_mock)
    @with_mocked_api(create_space_api_mock)
    @run_for_both_client_and_in_memory(
        in_memory_cleanup=lambda in_memory: in_memory.remove_all_spaces()
    )
    def test_should_throw_error_when_passing_invalid_query_to_filter(self, easydb_client):
        # given
        space = easydb_client.create_space()

        # and
        bucket = space.get_bucket(BUCKET_NAME)

        # and
        bucket.add({'firstName': 'John'})

        # and
        first_name_eq_mark = easydb_client.query.where('firstName').eq('Mark')
        last_name_eq_smith = easydb_client.query.where('lastName').eq(None)

        with self.assertRaises(easydb_client.query.InvalidQuery):  # then
            list(bucket.filter(first_name_eq_mark & last_name_eq_smith))  # when

    @with_mocked_api(add_element_to_bucket_api_mock)
    @with_mocked_api(create_space_api_mock)
    @with_mocked_api(get_element_from_bucket_api_mock)
    @run_for_both_client_and_in_memory(
        in_memory_cleanup=lambda in_memory: in_memory.remove_all_spaces()
    )
    def test_should_get_element_from_bucket(self, easydb_client):
        # given
        space = easydb_client.create_space()

        # and
        bucket = space.get_bucket(BUCKET_NAME)

        # and
        saved_element = bucket.add({'firstName': 'John'})

        # when
        element = bucket.get(saved_element['id'])

        # then
        self.assertEqual(element, {
            'id': saved_element['id'],
            'bucketName': BUCKET_NAME,
            'fields': {
                'firstName': 'John'
            }
        })

    @with_mocked_api(create_space_api_mock)
    @with_mocked_api(try_to_update_nonexistent_element_api_mock)
    @run_for_both_client_and_in_memory(
        in_memory_cleanup=lambda in_memory: in_memory.remove_all_spaces()
    )
    def test_should_throw_error_when_trying_to_update_nonexistent_element(self, easydb_client):
        # given
        space = easydb_client.create_space()

        # and
        bucket = space.get_bucket(BUCKET_NAME)

        with self.assertRaises(easydb_client.ElementNotFound):  # then
            bucket.update(BUCKET_ELEMENT_ID, {'firstName': 'Johny'})  # when

    @with_mocked_api(create_space_api_mock)
    @with_mocked_api(try_to_get_nonexistent_element_api_mock)
    @run_for_both_client_and_in_memory(
        in_memory_cleanup=lambda in_memory: in_memory.remove_all_spaces()
    )
    def test_should_throw_error_when_trying_to_get_nonexistent_element(self, easydb_client):
        # given
        space = easydb_client.create_space()

        # and
        bucket = space.get_bucket(BUCKET_NAME)

        with self.assertRaises(easydb_client.ElementNotFound):  # then
            bucket.get(BUCKET_ELEMENT_ID)  # when

    @with_mocked_api(create_space_api_mock)
    @with_mocked_api(try_to_pass_invalid_element_to_update_api_mock)
    @run_for_both_client_and_in_memory(
        in_memory_cleanup=lambda in_memory: in_memory.remove_all_spaces()
    )
    def test_should_throw_error_when_passing_invalid_element_to_update(self, easydb_client):
        # given
        space = easydb_client.create_space()

        # and
        bucket = space.get_bucket(BUCKET_NAME)

        with self.assertRaises(easydb_client.InvalidElementFormat):  # then
            bucket.update(BUCKET_ELEMENT_ID, {'fieldWithInvalidValue': []})  # when

    @with_mocked_api(create_space_api_mock)
    @with_mocked_api(try_to_remove_nonexistent_element_api_mock)
    @run_for_both_client_and_in_memory(
        in_memory_cleanup=lambda in_memory: in_memory.remove_all_spaces
    )
    def test_should_throw_error_when_trying_to_remove_nonexistent_element(self, easydb_client):
        # given
        space = easydb_client.create_space()

        # and
        bucket = space.get_bucket(BUCKET_NAME)

        with self.assertRaises(easydb_client.ElementNotFound):  # then
            bucket.remove(BUCKET_ELEMENT_ID)  # when

    @with_mocked_api(create_space_api_mock)
    @with_mocked_api(try_to_pass_invalid_element_to_add_api_mock)
    @run_for_both_client_and_in_memory(
        in_memory_cleanup=lambda in_memory: in_memory.remove_all_spaces()
    )
    def test_should_throw_error_when_passing_invalid_element_to_add(self, easydb_client):
        # given
        space = easydb_client.create_space()

        # and
        bucket = space.get_bucket(BUCKET_NAME)

        with self.assertRaises(easydb_client.InvalidElementFormat):  # then
            bucket.add({'fieldWithInvalidValue': []})  # when
