from fabric.api import local

def test():
    local('python manage.py test')

def run_server():
    local('python manage.py runserver 0.0.0.0:8080')

