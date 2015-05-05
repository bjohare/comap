from fabric.api import local

def test():
    local('python manage.py test')