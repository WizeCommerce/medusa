"""
 Licensed under the Apache License, Version 2.0 (the "License");
 you may not use this file except in compliance with the License.
 You may obtain a copy of the License at

     http://www.apache.org/licenses/LICENSE-2.0

 Unless required by applicable law or agreed to in writing, software
 distributed under the License is distributed on an "AS IS" BASIS,
 WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 See the License for the specific language governing permissions and
 limitations under the License.
"""
__author__ = 'sfaci'
import logging
import os
##Singlelton (The borg) pattern recipe from:
# http://code.activestate.com/recipes/66531/


class Log:
    """ A python singleton """
    __shared_state = {}

    def __init__(self, log_file, logger_name):
        self.__dict__ = self.__shared_state

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
