# Client library for Easydb
## Installation
`pip install easydb_client`

## Managing spaces
```python
import easydb_client as easydb

# CREATE SPACE
space = easydb.create_space()
print('Your space unique id: ', space.name)

# GET SPACE
space = easydb.get_space(space.name)

# CHECK IF SPACE EXISTS
space_exists = easydb.space_exists(space.name)
print('Space exists: ', space_exists)

# REMOVE SPACE
easydb.remove_space(space.name)
print('Space exists: ', easydb.space_exists(space.name))
```

## Using space
```python
import easydb_client as easydb

space = easydb.create_space()

# GET BUCKET
bucket = space.get_bucket('users')
```

## Using bucket
```python
import easydb_client as easydb

space = easydb.create_space()

users_bucket = space.get_bucket('users')

# ADD ELEMENT TO BUCKET
smith = users_bucket.add({'firstName': 'John', 'lastName': 'Smith'})
neo = users_bucket.add({'firstName': 'Thomas', 'lastName': 'Anderson', 'alias': 'Neo'})
print(smith)
print(neo)

# GET ALL ELEMENTS
all_users = users_bucket.all()
print(all_users)

# GET SINGLE ELEMENT
smith = users_bucket.get(smith['id'])
print(smith)

# REMOVE ELEMENT
users_bucket.remove(smith['id'])

# UPDATE ELEMENT
updated_neo = users_bucket.update(neo['id'], {'name': 'Neo'})
print(updated_neo)
```

## Testing
`easydb_client.inmemory` contains in-memory implementation that you can use for automated testing/local development. In-memory implementation is NOT thread safe.