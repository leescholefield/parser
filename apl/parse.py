import re
from abc import ABC, abstractmethod
from urllib import request

from .attributes import Attribute, AttributeList

from lxml import etree


class Parser(ABC):
    """ Abstract class for a Parser. """

    _parsers = {}

    @classmethod
    @abstractmethod
    def from_string(cls, string, format='xml', parser=None, namespaces=None):

        if parser is not None:
            return parser.from_string(string, format)
        if not isinstance(namespaces, dict) and namespaces is not None:
            raise ValueError('If namespaces is provided it must be a dictionary.')

        # lookup the Parser implementation associated with the format
        parser = cls._parsers[format]
        if parser:
            return parser.from_string(string, format)
        else:
            raise ValueError(format, ' is not a recognized format.')

    @classmethod
    def from_url(cls, url, format='xml', parser=None, namespaces=None):
        """
        Uses urllib to make a Http request, and then converts the response body to an etree Element.

        :param url: either a string url or a request.Request instance.
        :param format: expected format of the response body. Defaults to xml.
        :param parser: Parser implementation to use.
        :param namespaces: xml namespace dict used by lxml.
        """

        result_body = request.urlopen(url).read()

        return Parser.from_string(result_body, format, parser, namespaces)

    @abstractmethod
    def parse(self, obj_or_dict, root=None, namespaces=None):
        """
        Main public method for parsing a collection of Attributes.
        """
        pass

    @abstractmethod
    def parse_attribute(self, attribute, root=None, namespaces=None):
        """
        Parses an attributes.Attribute. Searches the root for the locations within the attribute and then returns
        a value, or None if no value could be found.
        """
        pass

    @abstractmethod
    def parse_attribute_list(self, attribute, root_path, root=None, namespaces=None):
        pass

    @abstractmethod
    def _get_value_from_loc(self, locations, root=None):
        """
        Implementation method for parse_attribute(). Loops through the locations and searches the root node for a value.
        """
        pass

    @staticmethod
    def _get_attribute_dict(obj_or_dict):
        """
        Looks in an objects __dict__ and creates a new dictionary containing all of the attributes.Attribute instances.
        """
        if isinstance(obj_or_dict, dict):
            dict_ = obj_or_dict
        else:
            dict_ = obj_or_dict.__dict__

        attr_dict = {key: val for (key, val) in dict_.items() if isinstance(val, Attribute)}

        # raise exception if no attributes were found
        if not attr_dict:
            raise ValueError(obj_or_dict, ' contains no Attributes.')

        return attr_dict

    @classmethod
    def _sanitize_string(cls, string):
        return re.sub('<[^<]+?>', '', string)

    @classmethod
    def _convert_to_type(cls, val, convert_type):
        """Raises TypeError if could not convert. """
        return convert_type(val)


class XmlParser(Parser):

    @classmethod
    def from_string(cls, string, format='xml', parser=None, namespaces=None):
        root = cls._convert_root_to_etree(string)
        return cls(root, namespaces)

    def __init__(self, root, namespaces=None):
        self.root = root
        self.namespaces = namespaces

    @staticmethod
    def _convert_root_to_etree(root):
        return etree.fromstring(root)

    def parse(self, obj_or_dict, root=None, namespaces=None):
        if root is None:
            root = self.root
        if namespaces is None:
            namespaces = self.namespaces

        result_obj = Result()

        attr_dict = self._get_attribute_dict(obj_or_dict)
        for name, val in attr_dict.items():
            if isinstance(val, AttributeList):
                attr = self.parse_attribute_list(val, root_path=val.root_location, root=root, namespaces=namespaces)
            else:
                attr = self.parse_attribute(val, root, namespaces)

            # add attr to the result object
            if attr:
                result_obj.add_value(name, attr)

        return result_obj

    def parse_attribute(self, attribute, root=None, namespaces=None):
        """
        Parses an Attribute instance.

        :param attribute: attributes.Attribute instance.
        :param root: root node to search. If none, self.root will be used instead.
        :param namespaces: dictionary containing xml namespaces.

        :returns: the first none-null value found after performing the xpath search. It will sanitize the string,
        and then attempt to convert it to the type found in attribute.expected_type (default is str). If no value is
        by the xpath search it will return attribute.default_value.

        :raises: ValueError if attribute is not an instance of Attribute, or if the found value cannot be converted
        to the expected type.
        """
        if not isinstance(attribute, Attribute):
            raise ValueError(attribute, ' is not an instance of Attribute.')

        if root is None:
            root = self.root
        if namespaces is None:
            namespaces = self.namespaces

        attr = self._get_value_from_loc(attribute.locations, root, namespaces=namespaces)
        if attr:
            if attribute.parse_method:
                return attribute.parse_method(attr)
            else:
                return self._convert_to_type(attr, attribute.expected_type)

        # if no value could be found return the default
        return attribute.default_value

    def parse_attribute_list(self, attribute, root_path, root=None, namespaces=None):
        """
        Parses an AttributeList instance.

        :param attribute: AttributeList instance.
        :param root_path: xpath location of each Element to be parser. This will perform an xpath search on the root
        node and then pass each Element obtained to the parse() method as the root.
        :param root: root node. If none it will use self.root.
        :param namespaces: dictionary containing xml namespaces.

        :returns result_list: list of Result objects returned by the parse() method. Or an empty list if none could be
        found.
        """
        if not isinstance(attribute, AttributeList):
            return ValueError(attribute, ' is not an instance of AttributeList.')

        if root is None:
            root = self.root
        if namespaces is None:
            namespaces = self.namespaces

        result_list = []

        node_list = root.xpath(root_path, namespaces=namespaces)
        for val in node_list:
            result = self.parse(attribute.model, root=val, namespaces=namespaces)
            result_list.append(result)

        return result_list

    def _get_value_from_loc(self, locations, root=None, namespaces=None):
        """
        Loops through locations and performs an xpath search on the root. Sanitizes and returns the first non-null
        value.
        """
        if root is None:
            root = self.root
        if namespaces is None:
            namespaces = self.namespaces

        for val in locations:
            attr = root.xpath(val, namespaces=namespaces)
            if attr:
                return self._sanitize_string(attr[0])

        return None


class HtmlParser(XmlParser):
    """ Identical to XmlParser except the _convert_root_to_etree() method now passes an etree.HTMLParser instance. """

    @staticmethod
    def _convert_root_to_etree(root):
        return etree.fromstring(root, parser=etree.HTMLParser())


Parser._parsers['xml'] = XmlParser
Parser._parsers['html'] = HtmlParser


class Result:

    def __init__(self):
        self.item_dict = {}

    def add_value(self, name, value):
        """
        Adds the given value to the item_dict.
        """
        self.item_dict[name] = value

    def items(self):
        """
        Convenience method for looping over the item_dict.
        """
        return self.item_dict.items()

    def item(self, key, default=None):
        """
        Returns the value associated with the key from the item_dict. If not found it will return None.
        """
        try:
            return self.item_dict[key]
        except KeyError:
            return default

    def __getattr__(self, item):
        return self.item_dict[item]
