from unittest import TestCase
from easydb_client.inmemory import create_space


class InMemoryEasydb(TestCase):
    def test_should_create_new_space(self):
        # when
        space = create_space()