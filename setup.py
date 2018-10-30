import os
from setuptools import find_packages, setup

with open(os.path.join(os.path.dirname(__file__), 'README.md')) as readme:
    README = readme.read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='myapp',
    version='0.1.0',
    packages=find_packages(),
    include_package_data=True,
    zip_safe = False,
    license='none',
    description='django-training app',
    long_description=README,
    url='https://gitlab.cc.columbia.edu/ac45/django-training',
    download_url='https://gitlab.cc.columbia.edu/ac45/django-training/repository/master/archive.tar.gz',
    author='Alan Crosswell',
    author_email='alan@columbia.edu',
    # TODO: this duplicates requirements.txt
    install_requires=[
        'Django>=2.1.0<2.2',
        'django-admin',
    ]
)
