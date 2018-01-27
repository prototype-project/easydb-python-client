from distutils.core import setup

setup(
    name='easydb_client',
    packages=['easydb_client'],
    version='0.2.0',
    description='Client for easydb',
    author='Bartłomiej Bęczkowski',
    author_email='beczkowb@gmail.com',
    url='https://github.com/prototype-project/easydb-python-client',
    download_url='https://github.com/prototype-project/easydb-python-client/archive/0.2.0.tar.gz',
    keywords=['client', 'database'],
    classifiers=[],
    install_requires=[
          'requests',
          'httmock',
      ]
)