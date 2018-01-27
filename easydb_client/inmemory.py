from uuid import uuid1

from .easydb import SpaceAlreadyExists
from .easydb import SpaceNotFound
from .easydb import ElementNotFound
from .easydb import InvalidElementFormat

# in memory, NOT THREAD SAFE implementation of easydb client interface
# for testing and local development


class ElementsRepository:
    def __init__(self, bucket_name):
        self._bucket_name = bucket_name
        self._elements = {}

    def add(self, element):
        pk = str(uuid1())
        if not self._is_valid(element):
            raise InvalidElementFormat()
        element_to_store = self._map_to_internal_representation(element, pk)
        self._elements[pk] = element_to_store
        return element_to_store

    def remove(self, element_pk):
        if not self.exists(element_pk):
            raise ElementNotFound()
        del self._elements[element_pk]

    @property
    def all(self):
        return list(self._elements.values())

    def exists(self, element_pk):
        return element_pk in self._elements

    def update(self, element_pk, element):
        if not self._is_valid(element):
            raise InvalidElementFormat()
        if not self.exists(element_pk):
            raise ElementNotFound()
        self._elements[element_pk] = self._map_to_internal_representation(element, element_pk)
        return self._elements[element_pk]

    def get(self, element_pk):
        if not self.exists(element_pk):
            raise ElementNotFound()
        return self._elements[element_pk]

    def _map_to_internal_representation(self, element, pk):
        return {
            'fields': element,
            'id': pk,
            'bucketName': self._bucket_name
        }

    def _is_valid(self, element):
        return isinstance(element, dict) and \
            all(isinstance(k, str) and isinstance(v, str)
                for k, v in element.items())


class InMemoryBucket:
    def __init__(self, space, name):
        self.space = space
        self.name = name
        self._elements_repository = ElementsRepository(name)

    def add(self, element):
        return self._elements_repository.add(element)

    def remove(self, element_pk):
        self._elements_repository.remove(element_pk)

    def update(self, element_pk, element):
        return self._elements_repository.update(element_pk, element)

    def all(self):
        return self._elements_repository.all

    def get(self, element_pk):
        return self._elements_repository.get(element_pk)


class InMemorySpace:
    def __init__(self, name):
        self.name = name
        self._buckets = {}

    def get_bucket(self, bucket_name):
        if bucket_name not in self._buckets:
            self._buckets[bucket_name] = InMemoryBucket(self, bucket_name)
        return self._buckets[bucket_name]


class SpaceRepository:
    def __init__(self):
        self.spaces = {}

    def add(self, space_name):
        if space_name in self.spaces:
            raise SpaceAlreadyExists()

        self.spaces[space_name] = InMemorySpace(space_name)
        return self.spaces[space_name]

    def get(self, space_name):
        if not self.exists(space_name):
            raise SpaceNotFound()
        return self.spaces[space_name]

    def exists(self, space_name):
        return space_name in self.spaces

    def remove(self, space_name):
        if not self.exists(space_name):
            raise SpaceNotFound()
        del self.spaces[space_name]


space_repository = SpaceRepository()

# easydb client implementation
create_space = space_repository.add
get_space = space_repository.get
space_exists = space_repository.exists
remove_space = space_repository.remove