import unittest
from attributes import Attribute


class AttributeTest(unittest.TestCase):

    def test_invalid_parse_method(self):
        attr = Attribute('location')

        self.assertRaises(ValueError, attr.parse_method, 'not a function')
