from . import easydb as client
from .easydb import SpaceAlreadyExists
from .easydb import SpaceNotFound

# in memory, non-thread safe implementation of easydb client interface


class SpaceRepository:
    def __init__(self):
        self.spaces = {}

    def add(self, space_name):
        if space_name in self.spaces:
            raise SpaceAlreadyExists()

        self.spaces[space_name] = client.Space(space_name)
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