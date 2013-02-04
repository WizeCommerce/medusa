import unittest
from lib.models.server import Server

__author__ = 'sfaci'



class TestServer(unittest.TestCase):
    server = ""
    def setUp(self):
       raw = {'host': 'localhost', 'user': 'tux', 'password': '123', 'local_path': '/tmp', 'remote_path': 'foobar'}
       self.server = Server(**raw)

    def testHost(self):
        self.setUp()
        self.failUnlessEqual(self.server.host, 'localhost')

    def testUser(self):
        self.setUp()
        self.failUnlessEqual(self.server.user, 'tux')

    def testPassword(self):
        self.setUp()
        self.failUnlessEqual(self.server.password, '123')

    def testLocalPath(self):
        self.setUp()
        self.failUnlessEqual(self.server.local_path, '/tmp')

    def testRemotePath(self):
        self.setUp()
        self.failUnlessEqual(self.server.remote_path, 'foobar')
