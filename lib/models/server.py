__author__ = 'sfaci'


class Server(object):
    """
        This class will serve as a wrapping class since we seem to be passing around host,pass,remote,local around
        a lot.  It wraps around the typical data.
    """

    def __init__(self, **kwargs):
        self.dictionary = kwargs.copy()

    @property
    def host(self):
        return self.dictionary.get("host")

    @host.setter
    def host(self, value):
        self.dictionary['host'] = value

    @property
    def user(self):
        return self.dictionary.get("user")

    @user.setter
    def user(self, value):
        self.dictionary['user'] = value

    @property
    def password(self):
        return self.dictionary.get("password")

    @password.setter
    def password(self, value):
        self.dictionary['password'] = value


    @property
    def remote_path(self):
        return self.dictionary.get("remote_path")

    @remote_path.setter
    def remote_path(self, value):
        self.dictionary['remote_path'] = value

    @property
    def local_path(self):
        return self.dictionary.get("local_path")

    @local_path.setter
    def local_path(self, value):
        self.dictionary['local_path'] = value

