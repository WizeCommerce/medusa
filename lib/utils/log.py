__author__ = 'sfaci'
import logging
import os
import unittest
##Singlelton pattern recipe from:
# http://code.activestate.com/recipes/52558-the-singleton-pattern-implemented-with-python/


class Log:
    """ A python singleton """
    __instance__ = None

    class __impl:
        """ the purpose of this class is to keep track of which artifacts have already
         been deployed and what hasn't."""
        __deployed__ = {}

        def __init__(self, log_file, logger_name):
            self.logger = logging.getLogger(logger_name)
            hdlr = logging.FileHandler(os.path.join(os.getcwd(), log_file))
            formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
            hdlr.setFormatter(formatter)
            # console handling
            ch = logging.StreamHandler()
            ch.setLevel(logging.INFO)
            ch.setFormatter(formatter)

            self.logger.addHandler(hdlr)
            self.logger.addHandler(ch)
            self.logger.setLevel(logging.INFO)

        def log(self, message):
            self.logger.info(message)

        def get_logger(self):
            return self.logger

        def get_id(self):
            """
                Test method, return singleton id
            """
            return id(self)

    # storage for the instance reference
    __instance = None

    #def __init__(self):
    def __init__(self, log_file, logger_name):
        """ Create singleton instance """
        # Check whether we already have an instance
        if Log.__instance is None:
            # Create and remember instance
            Log.__instance = Log.__impl(log_file, logger_name)

        # Store instance reference as the only member in the handle
        self.__dict__['_Singleton__instance'] = Log.__instance

    def __getattr__(self, attr):
        """ Delegate access to implementation """
        return getattr(self.__instance, attr)

    def __setattr__(self, attr, value):
        """ Delegate access to implementation """
        return setattr(self.__instance, attr, value)
###---------------------------------------------------------------------------------------------
