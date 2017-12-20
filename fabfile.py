import os

from fabric.api import *
from fabric.colors import green, red, yellow
from fabric.contrib.console import confirm
from fabric.decorators import with_settings


env.output_prefix = False

env.hosts = ['root@138.197.5.61']
env.password = 'MBSkd207T'

VIRTUALENV_PATH = 'source /home/ryan/.venvs/donkies/bin/activate'
PROJECT_PATH = os.path.join('/', 'home', 'ryan', 'dj', 'API')
PROJECT_PATH_DJANGO = os.path.join(PROJECT_PATH, 'donkies')


@with_settings(warn_only=True)
def pull():
    print(yellow('Start getting files from github'))

    with cd(PROJECT_PATH):
        if confirm('Stash?', default=False):
            run('git stash')
            run('git pull --rebase')
            run('git stash pop')
        else:
            run('git pull')

        print(green('Getting files from github completed'))


@with_settings(warn_only=True)
def install_requirements():
    print(green('Installing requirements...'))
    with prefix(VIRTUALENV_PATH), cd(PROJECT_PATH_DJANGO):
        run('pip install -r donkies/requirements/development.txt')
        run('pip install -r donkies/requirements/production.txt')


@with_settings(warn_only=True)
def shell():
    print(green('Starting shell...'))
    with prefix(VIRTUALENV_PATH), cd(PROJECT_PATH_DJANGO):
        run('python manage.py shell_plus')


@with_settings(warn_only=True)
def migrate():
    print(green('Starting shell...'))
    model = prompt('Model name (default: all): ')
    with prefix(VIRTUALENV_PATH), cd(PROJECT_PATH_DJANGO):
        if not model:
            run('python manage.py migrate')
        else:
            run('python manage.py migrate ' + model)


@with_settings(warn_only=True)
def restart_nginx():
    print(green('Restarting nginx...'))
    run('service nginx restart')


@with_settings(warn_only=True)
def restart_server():
    print(green('Restarting server...'))
    run('service supervisord restart')


@with_settings(warn_only=True)
def stop_server():
    print(green('Stoping server...'))
    run('service supervisord stop')


@with_settings(warn_only=True)
def start_server():
    print(green('Starting server...'))
    run('service supervisord start')


@with_settings(warn_only=True)
def deploy():

    print(green('Deploying to server'))

    execute(pull)

    if confirm('Install requirements?', default=False):
        execute(install_requirements)

    if confirm('Migrate something?', default=False):
        execute(migrate)

    if confirm('Restart server?', default=True):
        execute(restart_server)
