from fabric.api import local, run, task

@task
def test():
    local('python manage.py test')

def run_server():
    local('python manage.py runserver 0.0.0.0:8080')

