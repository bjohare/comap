from fabric.api import local, run, task

@task
def test():
    local('python manage.py test')