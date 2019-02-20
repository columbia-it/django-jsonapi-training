import os
from setuptools import find_packages, setup

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='jsonapi-demo-cli',
    version='0.2.0',
    packages=find_packages(),
    include_package_data=True,
    entry_points={"console_scripts": ["jsonapi-demo-cli=jsonapi_demo_cli:main"]},
    license='Apache 2.0',
    description='Companion CLI client to Django JSONAPI training demo',
    url='https://github.com/columbia-it/django-jsonapi-training/',
    author='Alan Crosswell',
    author_email='alan@columbia.edu',
    install_requires=[
        'pyperclip>=1.7.0',
        'oauthlib>=3.0.0',
        'requests>=2.21.0',
        'jsonapi-requests>=0.6.0',
    ]
)
