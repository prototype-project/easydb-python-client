from distutils.core import setup

setup(
    name='easydb_client',
    packages=['easydb_client'],
    version='0.1.2',
    description='Client for easydb',
    author='Bartłomiej Bęczkowski',
    author_email='beczkowb@gmail.com',
    url='https://github.com/prototype-project/easydb-python-client',
    download_url='https://github.com/prototype-project/easydb-python-client/archive/0.1.2.tar.gz',
    keywords=['client', 'database'],
    classifiers=[],
    install_requires=[
          'requests',
          'httmock',
      ]
)