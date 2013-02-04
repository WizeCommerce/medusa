import unittest
from lib.utils.thrift import Thrift, ThriftCompiler


class ThriftTests(unittest.TestCase):

    def setUp(self):
        self.helper = Thrift(None)

    def test_extract_string(self):
        raw = \
            """
namespace java com.wizecommerce.service.common

const string VERSION = "0.0.6"

# Type Definitions
typedef i32 Integer

        """
        expected = "0.0.6"

        result = self.helper.__extract_string__("VERSION", raw, "0.0.0")
        self.failUnlessEqual(result, expected)


    def test_thrift_compiler(self):
        init = {}
        init['name'] = 'testThrift'
        init['bin'] = '/dev/null'
        init['options'] = 'testoptions'
        init['supported_languages'] = ['java', 'ruby', 'python']
        t = ThriftCompiler(init)
        self.failUnless('testThrift' == t.name)
        self.failUnless('/dev/null' == t.bin)
        self.failUnless('testoptions' == t.options)
        self.failUnless(len(t.languages) == 3)
        self.failUnless(t.is_language_supported('ruby'))
        self.failUnless(not t.is_language_supported('erlang') )

    def test_object_name(self):
        th = Thrift(None)
        src = "/home/user/foobar/blah/wizecommerce.bizobj.sellerprogramrecord.thrift"
        result = th.get_object_name(src)
        expected = "sellerprogramrecord-bizobj"
        self.failUnlessEqual(expected, result)

    def test_complex_object_name(self):
        th = Thrift(None)
        src = "/home/user/foobar/blah/wizecommerce.bizobj.search.foobar.sellerprogramrecord.thrift"
        result = th.get_object_name(src)
        expected = "search-foobar-sellerprogramrecord-bizobj"
        self.failUnlessEqual(expected, result)

    def test_special_case_object_name(self):
        th = Thrift(None)
        src = "/home/user/foobar/blah/wizecommerce.services.sellerprogramrecord.thrift"
        result = th.get_object_name(src)
        expected = "sellerprogramrecord-client"
        self.failUnlessEqual(expected, result)


if __name__ == "__main__":
    # Run unit tests
    suite = unittest.TestLoader().loadTestsFromTestCase(ThriftTests)
    unittest.TextTestRunner(verbosity=2).run(suite)

