import re
from abc import ABC, abstractmethod
from urllib import request

from .attributes import Attribute, AttributeList

from lxml import etree

from apl.models import Result


class Parser(ABC):

    _parsers = {}

    @classmethod
    @abstractmethod
    def from_string(cls, string, format='xml', parser=None):

        if parser is not None:
            return parser.from_string(string, format)

        # lookup the apl associated with the format
        parser = cls._parsers[format]
        if parser:
            return parser.from_string(string, format)
        else:
            raise ValueError(format, ' is not a recognized format.')

    @classmethod
    def from_url(cls, url, format='xml', parser=None):

        result_body = request.urlopen(url).read()

        return Parser.from_string(result_body, format, parser)

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
    def from_string(cls, string, format='xml', parser=None):
        root = cls._convert_root_to_etree(string)
        return cls(root)

    def __init__(self, root, namespaces=None):
        self.root = root
        self.namespaces = namespaces

    @staticmethod
    def _convert_root_to_etree(root):
        return etree.fromstring(root)

    def parse(self, obj_or_dict, root=None, namespaces=None):
        if root is None:
            root = self.root

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
        """
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
        """
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

    @staticmethod
    def _convert_root_to_etree(root):
        return etree.fromstring(root, parser=etree.HTMLParser())


Parser._parsers['xml'] = XmlParser
Parser._parsers['html'] = HtmlParser