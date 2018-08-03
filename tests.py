# Set the path
import os, sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import unittest
import sqlalchemy
from flask_sqlalchemy import SQLAlchemy

from flask_blog import app,db

# models
from author.models import *
from blog.models import *

class UserTest(unittest.TestCase):
    def setUp(self):
        db_username = app.config['DB_USERNAME']
        db_password = app.config['DB_PASSWORD']
        db_host = app.config['DB_HOST']
        self.db_uri = "mysql+pymysql://%s:%s@%s/" % (db_username, db_password, db_host)
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['BLOG_DATABASE_NAME'] = 'test_blog'
        app.config['SQLALCHEMY_DATABASE_URI'] = self.db_uri + app.config['BLOG_DATABASE_NAME']
        engine = sqlalchemy.create_engine(self.db_uri)
        conn = engine.connect()
        conn.execute("commit")
        conn.execute("CREATE DATABASE " + app.config['BLOG_DATABASE_NAME'])
        db.create_all()
        conn.close()
        self.app = app.test_client()

    def tearDown(self):
        db.session.remove()
        engine = sqlalchemy.create_engine(self.db_uri)
        conn = engine.connect()
        conn.execute("commit")
        conn.execute("DROP DATABASE " + app.config['BLOG_DATABASE_NAME'])
        conn.close()

    def create_blog(self):
        return self.app.post('/setup', data=dict(
            name='My Test Blog',
            fullname='Alex Barnes',
            email='aeb@gmail.com',
            username='alex',
            password='test',
            confirm='test',
            ),
        follow_redirects=True)

    def login(self, username, password):
        return self.app.post('/login', data=dict(
            username=username,
            password=password
            ),
        follow_redirects=True)

    def create_post(self, title, body, category, new_category):
        # create a test post
        return self.app.post('/post', data=dict(
            title=title,
            body=body,
            category=category,
            new_category=new_category
            ),
        follow_redirects=True)
        
    def logout(self):
        return self.app.get('/logout', follow_redirects=True)

    def register_user(self, fullname, email, username, password, confirm):
        # register test user
        return self.app.post('/register', data=dict(
            fullname=fullname,
            email=email,
            username=username,
            password=password,
            confirm=confirm
            ),
        follow_redirects=True)

    def create_comment(self, slug):
        return self.app.post('/article/' + slug, data=dict(
            body='Test comment',
            ),
        follow_redirects=True)

    def remove_comment(self, comment_id):
        # remove test comment
        return self.app.post('/comment/' + str(comment_id), follow_redirects=True)

    def test_create_blog(self):
        rv = self.create_blog()
        assert 'Blog created' in str(rv.data)

    def test_login_logout(self):
        self.create_blog()
        rv = self.login('alex', 'test')
        assert 'User alex logged in' in str(rv.data)
        rv = self.logout()
        assert 'User logged out' in str(rv.data)
        rv = self.login('alex', 'wrong')
        assert 'Incorrect username and password' in str(rv.data)

    def test_create_post(self):
        self.create_blog()
        self.login('alex', 'test')
        rv = self.create_post('Test title', 'test body', None, 'test category')
        assert 'Post created' in str(rv.data)

    def test_register_user(self):
        # make sure a regular user can be created
        rv = self.register_user('Test McTester', 'test@example.com', 'test', 'test', 'test')
        assert 'User account created' in str(rv.data)

    def test_comment(self):
        self.create_blog()
        self.login('alex', 'test')
        self.create_post('Test title', 'test body', None, 'test category')
        rv = self.create_comment('Test-title')
        assert 'Comment posted' in str(rv.data)

        rv = self.remove_comment(1)
        assert 'Comment deleted' in str(rv.data)

    def test_admin(self):
        self.create_blog()
        self.register_user('Test McTester', 'test@example.com', 'test', 'test', 'test')
        rv = self.create_post('Test title', 'test body', None, 'test category')
        assert '403' in str(rv.data)

if __name__ == '__main__':
    unittest.main()
