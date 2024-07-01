# Preparing for the classes

## Overview

The plan is to do this as a few 3 hours or so segments.
Content will be mostly me droning on about the stuff in
these notes with participants doing some live Postman, OAuth 2.0
testing using a deployed version of the demonstration app, followed
by Python/Django coding on their laptops.

Some of the material here may be too basic or the opposite
so it's hard to estimate how much time it will take. We may refer to
some stuff and then skip ahead. Anything not done in class should be
done as homework. We can always add on more sessions if we need to.

For CUIT staff, you can
always ask questions on Slack channel `#python-dev` 

## Expectations

- It is expected that students will bring laptops that have a functional
  Python development environment set up, including Python 3.10 or higher,
  [Postman](https://www.postman.com/downloads/), git, an editor or IDE,
  maybe Docker for some of the advanced examples. The examples are all MacOS-based, using the Unix
  Terminal CLI. Windows users will need to adjust as needed (see
  [SW Carpentry's shell lesson setup](https://swcarpentry.github.io/shell-novice/index.html) for
  Windows instructions).
- Optionally have [PyCharm](https://www.jetbrains.com/pycharm/download/) installed
  and licensed (not required; PyCharm CE works fine too). Some use
  [Microsoft Visual Studio Code](https://code.visualstudio.com/download).
  Or use a programmer's editor like Emacs, vi or atom. 
  However, PyCharm's/VSCode's ability to interactively debug is a lot more powerful than `$ python -m pdb ...`.
- git
  - CLI tools installed
  - access to gitlab/github
  - have successfully created one's own personal repo.
  - [SW Carpentry's Git lesson](http://swcarpentry.github.io/git-novice/) is a good resource to get
    started with git.
- Some familiarity with: JSON, HTTP, REST, XML, SOAP/WSDL, SQL,
  git, pycharm, Python object-oriented programming, Django, etc.
  I don't really care if you've heard of XML, SOAP or WSDL other than if you
  have heard of them, but not JSON or REST, they'll be a point of comparison.
  Similarly, knowledge of SQL can be cursory, basically understanding the
  concepts of tables and fields (columns).

## Development Environment Setup

Most all steps on macOS will be performed using the Unix shell. Open the "Terminal" application for this.

### Homebrew

Only macOS is supported by Homebrew. Windows users can skip this
section.

#### macOS
Homebrew is a package management system used to simplify software
installations on macOS.

Run the command listed at  <https://brew.sh/>

### Python

#### macOS

Once Homebrew is installed, it should be simple install python:
```
brew install python
```

More details are available
at: <http://docs.python-guide.org/en/latest/starting/install3/osx/>

You can create an alias in your \~/.bashrc or \~/.bash\_profile file to
set python3 as default:

**\~/.bashrc**

```bash
alias python='python3'
```

See more about running
["multiple versions of Python for use with tox on macOS"](#multiple-versions-of-python-for-use-with-tox-on-macos),
below, for more advanced Python tricks.

#### Windows

See <https://www.python.org/downloads/windows/>

This should install Python3 in `C:\\Program Files\\Python36`

### Git

#### macOS

The Git installation for macOS is easily done with Homebrew:

```
brew install git
```

If you would prefer to install this manually without homebrew,
see: <https://git-scm.com/book/en/v2/Getting-Started-Installing-Git>

#### Windows

1.  Download git from <https://git-scm.com/download/win>
2.  Click 'Run as administrator' on the .exe file in your Downloads
    directory.
3.  Set the installation directory to the following path: `C:\\Program Files\\Git`
4.  If there is an option to add git to your path, select it.
5.  Accept all defaults otherwise.

If git was not added to your path, add the above directory to your
system’s
[Environment Variables](https://superuser.com/questions/949560/how-do-i-set-system-environment-variables-in-windows-10)

You may also want to take a look at [Git for Windows](https://gitforwindows.org/).

### PyCharm of VSCode

PyCharm is an IDE for Python development (among other things). This instruction applies to
both macOS and Windows.

Download the professional or community edition from the following link and follow
the setup instructions: <https://www.jetbrains.com/pycharm/download/>

Alternatively, you can download [Microsoft Visual Studio Code](https://code.visualstudio.com/download).

### Postman

Postman is a powerful tool for testing HTTP. We'll be using it extensively to test our APIs.
If you don't already have it, you can get it at:
[https://www.postman.com/downloads/](https://www.postman.com/downloads/).

### Advanced Topic: Multiple Versions of Python for use with Tox on macOS

#### Why do I need multiple Python versions?
The problem: typical tox.ini files test against multiple version of Python as a means of making sure code written for
one version still works on others.So you need all those versions installed on macOS. 
For the purposes of this material, you can get by with the
system version as described [above](#python).

#### Installing pyenv

For MacOS install pyenv:

```
brew install pyenv
```

Add `eval "$(pyenv init -)"` to your bash profile (or similar for other shells):

```
cat >>~/.bash_profile
eval "$(pyenv init -)"
```

Don’t forget to do the eval once if you have an open shell window.

See https://pypi.org/project/pyenv-win/ for Windows.

#### Installing multiple Python versions with pyenv

Then choose versions of python you want. `pyvenv install -l` lists what’s available. There are many flavors and versions. We just care
about 3.{10,11,12} right now:

```
pyenv install -l | grep '^  3\.1[012]'
  3.10.0
  3.10-dev
  3.10.1
  ...
  3.10.13
  3.11.0
  3.11-dev
  3.11.1
  ...
  3.11.8
  3.12.0
  3.12-dev
  3.12.1
  3.12.2
```

#### Install those versions and make them “global”

```
pyenv install 3.10.13
pyenv install 3.11.8
pyenv install 3.12.2
pyenv global  3.12.2 3.11.8 3.10.13
```

#### Installation under Mojave and XCode 10
*This may not longer be a problem*

See [this issue](https://github.com/pyenv/pyenv/issues/1219)
where pyenv install complains about missing zlib. Here’s a workaround:

```
CFLAGS="-I$(brew --prefix readline)/include -I$(brew --prefix openssl)/include -I$(xcrun --show-sdk-path)/usr/include" \
LDFLAGS="-L$(brew --prefix readline)/lib -L$(brew --prefix openssl)/lib" \
PYTHON_CONFIGURE_OPTS=--enable-unicode=ucs2 \
pyenv install -v 3.12.2
```

#### Choosing which Python version to use

The preceding will make python3.10, python3.11 and python3.12 globally available. The first-listed version is the one that becomes “python”:
```
python --version
Python 3.12.2
```

`pyenv global` makes the versions global (for you only; it updates ~/.pyenv/version)

`pyenv local` makes the versions local to the CWD (it updates .python-version). Local settings override global.

See https://github.com/pyenv/pyenv/blob/master/COMMANDS.md for more.

#### Install the tox-pyenv plugin

This plugin makes tox magically find the versions required in the tox.ini file.

```
pip3 install tox tox-pyenv
```

For example, in a tox.ini that tests a matrix of multiple Python versions, it will make sure py34 uses python3.4, py35 uses python3.5 and so on.

Here’s a snippet from a Django add-on library that does a cross-product series of tests of three Python versions against django 2.0 and the django project’s current master branch:

```
[tox]
envlist =
        py34-django20,
        py35-django{20,master},
        py36-django{20,master},
        docs,
        flake8
…
[testenv]
commands = pytest --cov=oauth2_provider --cov-report= --cov-append {posargs}
setenv =
        DJANGO_SETTINGS_MODULE = tests.settings
        PYTHONPATH = {toxinidir}
        PYTHONWARNINGS = all
deps =
        django20: Django>=2.0,<2.1
        djangomaster: https://github.com/django/django/archive/master.tar.gz
        djangorestframework
        coverage
        pytest
        pytest-cov
        pytest-django
        pytest-xdist
```

If you’re running tox and you have all the interpreters installed already you can use `tox -e` to choose the one version to run tox with. Otherwise, tox will run with py34, py35 and then py36.
```
tox -e py36
```

#### Installing system python

You can still use homebrew to install the system python. Brew-installed system python is located in /usr/local/bin. macOS (High Sierra or older) also still installs py27 in /usr/bin.

```
$ brew install python
Updating Homebrew...
...
Python has been installed as
  /usr/local/bin/python3

Unversioned symlinks `python`, `python-config`, `pip` etc. pointing to
`python3`, `python3-config`, `pip3` etc., respectively, have been installed into
  /usr/local/opt/python/libexec/bin

If you need Homebrew's Python 2.7 run
  brew install python@2

Pip, setuptools, and wheel have been installed. To update them run
  pip3 install --upgrade pip setuptools wheel

You can install Python packages with
  pip3 install <package>
They will install into the site-package directory
  /usr/local/lib/python3.7/site-packages

See: https://docs.brew.sh/Homebrew-and-Python
```

You can also install a newer version of legacy Python 2.7:
```
brew install python@2
```

This might be a bit confusing since the pyenv shim is still first in your path (thanks to `eval "$(pyenv init -)"`):

```
$ python --version
Python 3.6.6
$ which python
/Users/ac45/.pyenv/shims/python
$ which python3.7
/usr/local/bin/python3.7
$ which python
/Users/ac45/.pyenv/shims/python
$ /usr/local/bin/python --version
Python 2.7.15
$ /usr/local/bin/python3 --version
Python 3.7.0
$ /usr/bin/python --version
Python 2.7.10
```
