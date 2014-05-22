__author__ = 'sfaci'

##Singlelton pattern recipe from:
# http://code.activestate.com/recipes/52558-the-singleton-pattern-implemented-with-python/

class Status:
    """ A python singleton """
    __instance__ = None

    class __impl:
        """ the purpose of this class is to keep track of which artifacts have already
         been deployed and what hasn't.

         ie. try to only build an artifact once.

         """
        __deployed__ = {}

        @staticmethod
        def __build_key__(artifact, version, lang="java"):
            return artifact + "-" + version + "-" + lang

        def is_deployed(self, artifact, version, lang="java"):
            """
                expected format of "artifact" is artifact-version
            """
            return self.__deployed__.has_key(self.__build_key__(artifact, version, lang))

        def add_artifact(self, artifact, version, lang="java"):
            id = artifact + "-" + version + "-" + lang
            self.__deployed__[id] = id

        def get_id(self):
            """
                Test method, return singleton id
            """
            return id(self)

    # storage for the instance reference
    __instance = None

    def __init__(self):
        """ Create singleton instance """
        # Check whether we already have an instance
        if Status.__instance is None:
            # Create and remember instance
            Status.__instance = Status.__impl()

        # Store instance reference as the only member in the handle
        self.__dict__['_Singleton__instance'] = Status.__instance

    def __getattr__(self, attr):
        """ Delegate access to implementation """
        return getattr(self.__instance, attr)

    def __setattr__(self, attr, value):
        """ Delegate access to implementation """
        return setattr(self.__instance, attr, value)
###---------------------------------------------------------------------------------------------

