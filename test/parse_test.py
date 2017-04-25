import io
import unittest

from apl.attributes import Attribute, AttributeList
from apl.parse import Parser, XmlParser
from test.data.models import RevolutionsEpisode


class ParserClassTest(unittest.TestCase):
    """ Tests the Parser instantiation methods and the class Static methods. """

    def test_from_string_returns_XmlParser(self):
        """ Tests whether the from_string method with nothing but a string returns an XmlParser instance. """
        file = io.open('data/revolutions_feed.xml').read()
        actual = Parser.from_string(file)

        self.assertEqual(XmlParser, type(actual))

    def test_get_attr_obj(self):
        """ Tests whether get_attribute_list finds the Attributes from an object and returns a dict."""
        a1 = Attribute(['location'])
        a2 = Attribute(['second location'])

        class Example:
            attr1 = a1
            attr2 = a2

        expected = Parser._get_attribute_dict(Example)

        self.assertDictEqual(expected, {'attr1': a1, 'attr2': a2})

    def test_get_attr_dict(self):
        """ Tests whether get_attribute_list finds the Attributes from a dict. """
        a1 = Attribute(['location'])
        a2 = Attribute(['second location'])

        dict_ = {'attr1': a1, 'attr2': a2, 'attr3': 'not an attribute'}
        expected = {'attr1': a1, 'attr2': a2}

        self.assertDictEqual(expected, Parser._get_attribute_dict(dict_))

    def test_get_attr_dict_invalid_obj(self):
        """ Tests whether passing an object with no Attributes will raise a ValueError. """

        class Example:
            pass

        self.assertRaises(ValueError, Parser._get_attribute_dict, Example)

    def test_get_attr_dict_invalid_dic(self):
        """ Tests whether passing a dictionary with no Attribute will raise a ValueError."""
        dict_ = {}

        self.assertRaises(ValueError, Parser._get_attribute_dict, dict_)

    def test_convert_to_type(self):
        """ Tests the Parser._convert_to_type method with a string to int. """
        string_num = '210'

        self.assertEqual(Parser._convert_to_type(string_num, int), 210)

    def test_convert_to_type_invalid(self):
        """ Tests that an invalid String to int conversion will throw an ValueError. """
        invalid_string = 'asdasda'

        self.assertRaises(ValueError, Parser._convert_to_type, invalid_string, int)


class RevolutionsTest(unittest.TestCase):

    def setUp(self):
        import io
        file = io.open('data/revolutions_feed.xml').read()
        self.parser = Parser.from_string(file)

    def test_parse_attribute(self):
        attr = Attribute(['channel/title/text()'])
        root = self.parser.root

        self.assertEqual(self.parser.parse_attribute(attr, root=root), 'Revolutions')

    def test_parse_attribute_list(self):
        model = self.parser.parse_attribute_list(AttributeList('channel/item', RevolutionsEpisode),
                                                 'channel/item',
                                                 namespaces={'itunes': 'http://www.itunes.com/dtds/podcast-1.0.dtd'})
        expected = model[0].title

        self.assertEqual(expected, '6.05- The Barricades')

    def test_parse_attribute_method(self):

        def parse_method(string):
            return 'parse method string'

        attr = Attribute(['channel/title/text()'], parse_method=parse_method)

        expected = self.parser.parse_attribute(attr)

        self.assertEqual(expected, 'parse method string')


class HtmlTest(unittest.TestCase):

    class HtmlModel:
        title = Attribute(['body/h1/text()'])
        second_para = Attribute(['body/div/p/text()'])

    def setUp(self):
        import io
        file_text = io.open('data/html_file.html').read()
        self.parser = Parser.from_string(file_text, format='html')
        self.result = self.parser.parse(self.HtmlModel)

    def test_title(self):
        expected = 'Heading'
        actual = self.result.item('title')

        self.assertEqual(expected, actual)

    def test_second_p(self):
        expected = 'paragraph in div with id as \'second\''
        actual = self.result.item('second_para')

        self.assertEqual(expected, actual)
