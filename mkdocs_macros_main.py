import configparser
import re


def define_env(env):
    """
    "Dynamic" mkdocs.yml using for mkdocs macros plugin:

    [`define_env`](https://mkdocs-macros-plugin.readthedocs.io/en/latest/python/#the-define_env-function>)

    Determines remote git repo URLs, etc. based on .git/config instead of hardcoding them.
    """
    # determine the repo_url from `git remote`
    config = configparser.ConfigParser()
    config.read('.git/config')
    url = None
    for sec in config.sections():
        if sec.startswith('remote'):
            url = config.get(sec, 'url')
            break
    if url:
        # remote url can be ssh or https style:
        # git@github.com:columbia-it/django-jsonapi-training.git
        # https://github.com/columbia-it/django-jsonapi-training
        url_re = re.match(r'https://(?P<host>[^/]*)/(?P<repo>.*)', url)
        if not url_re:
            url_re = re.match(r'[^@]*@(?P<host>[^:]*):(?P<repo>.*)\.git', url)

        if url_re:
            env.conf['repo_url'] = 'https://{host}/{repo}/'.format(host=url_re['host'], repo=url_re['repo'])

    # extra.view_uri and config.repo_name is conditioned based on the repo type
    if 'gitlab' in env.conf['repo_url']:
        env.variables['view_uri'] = env.conf['repo_url'] + 'tree/master'
        env.conf['repo_name'] = 'GitLab'
        print('GITLAB!')
    elif 'github' in env.conf['repo_url']:
        env.variables['view_uri'] = env.conf['repo_url'] + 'blob/master'
        env.conf['repo_name'] = 'GitHub'
    else:
        env.variables['view_uri'] = '..'
        env.conf['repo_name'] = '?'
