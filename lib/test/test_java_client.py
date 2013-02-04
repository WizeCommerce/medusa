from lib.utils.config import *
import unittest
from lib.clients.java_client import JavaClient
from lib.utils.thrift import ThriftCompiler
from lib.utils.config import Config


class JavaClientTests(unittest.TestCase):
    def __get_client__(self):
        self.config = Config()
        compiler = None
        for item in self.config.get_thrift_option("compilers"):
            compiler = ThriftCompiler(item)
            break

        return JavaClient([], compiler)


    def test_check_version(self):
        client = self.__get_client__()
        client.check_shaded_version()
        self.config.set_local(False)
        expected = False
        check_value = client.check_version(groupId='com.wizecommerce.data', artifactId='tag-client',
                                         version='0.0.13')
        self.failUnlessEqual(check_value, expected)
        check_value = client.check_version(groupId='com.wizecommerce.data', artifactId='tag-client',
                                         version='X.Y.ZZ')
        expected = True
        self.failUnlessEqual(check_value, expected)

    def test_check_shaded_version(self):
        client = self.__get_client__()
        client.check_shaded_version()
        self.config.set_local(False)
        expected = False
        check_value_shaded = client.check_shaded_version(groupId='com.wizecommerce.data', artifactId='tag-client',
                                         version='0.0.13')
        self.failUnlessEqual(check_value_shaded, expected)
        check_value_shaded = client.check_shaded_version(groupId='com.wizecommerce.data', artifactId='tag-client',
                                         version='X.Y.ZZ')
        expected = True
        self.failUnlessEqual(check_value_shaded, expected)


if __name__ == "__main__":
    # Run unit tests
    suite = unittest.TestLoader().loadTestsFromTestCase(JavaClientTests)
    unittest.TextTestRunner(verbosity=2).run(suite)

