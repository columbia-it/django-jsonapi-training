import os
import re

from setuptools import find_packages, setup

def get_version():
    """
    Return package version as listed in `__version__` in `init.py`.
    """
    init_py = open(os.path.join('myapp', '__init__.py')).read()
    return re.search("^__version__ = ['\"]([^'\"]+)['\"]",
                     init_py, re.MULTILINE).group(1)

version=get_version()

def parse_requirements(filename):
    """Read requirements file and include recursive requirements."""
    lines = []
    with open(filename, 'r') as f:
        for line in f:
            line = line.strip()
            if line.startswith('-r '):
                # Recursively read included requirements files
                included_file = line.split(' ')[1]
                if os.path.exists(included_file):
                    lines.extend(parse_requirements(included_file))
            elif line and not line.startswith('#'):
                lines.append(line)
    return lines

# Parse the requirements.txt file
requirements = parse_requirements('requirements.txt')
print(f"requirements: {requirements}")

with open(os.path.join(os.path.dirname(__file__), 'README.md'), encoding="utf-8") as readme:
    README = readme.read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='myapp',
    version=version,
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
    install_requires=requirements,
)
