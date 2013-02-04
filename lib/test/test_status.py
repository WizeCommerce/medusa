import unittest
from lib.utils.status import Status

class StatusTests(unittest.TestCase):
    def test_object_name(self):
        status1 = Status()
        status2 = Status()
        status1.__setattr__("work_dir", "mooooooo")
        status1.__setattr__("work_dir", "booooo")
        self.failUnlessEqual(status1.__getattr__("work_dir"), status2.__getattr__("work_dir"))

    def test_is_deployed(self):
        status = Status()
        name = "foobar"
        version = "1.0"
        status.add_artifact(name, version)
        self.assertTrue(status.is_deployed(name, version))

if __name__ == "__main__":
    # Run unit tests
    suite = unittest.TestLoader().loadTestsFromTestCase(StatusTests)
    unittest.TextTestRunner(verbosity=2).run(suite)
