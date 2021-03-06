class Attribute(object):
    """
    Represents a value that needs to be parsed from a document.

    :param xpath_locations: location of the desired value within the document. Type list
    :param name: name to save the value as in the generated model
    :param default: default value if it could not be parsed.
    :param expected_type: the value's expected type. Default is string
    :param parse_method: optional method used to parse the value. Must take a single string.
    """

    def __init__(self, xpath_locations, name=None, default=None, expected_type=str, parse_method=None):

        self._parse_method = None
        self._locations = None

        self.locations = xpath_locations
        self.name = name
        self.default_value = default
        self.expected_type = expected_type
        self.parse_method = parse_method

    @property
    def locations(self):
        return self._locations

    @locations.setter
    def locations(self, loc):
        if not isinstance(loc, list):
            raise ValueError('locations must be a list.')
        self._locations = loc

    @property
    def parse_method(self):
        return self._parse_method

    @parse_method.setter
    def parse_method(self, method):
        """ Must either be a callable or None. """
        if not callable(method) and method is not None:
            raise ValueError(method, ' is not callable.')
        self._parse_method = method

    def __str__(self):
        if self.name:
            return self.name
        else:
            return str(self.locations)


class AttributeList(Attribute):
    """
    Represents a list of values that need to be parsed from a document. This is a subclass of Attribute with two
    additional values:

    :param root_location: location of the root node to search for the data specified by the model.
    """

    def __init__(self, root_location, model, name=None, default=None, expected_type=str, parse_method=None):
        super(AttributeList, self).__init__(xpath_locations=[], name=name, default=default,
                                            expected_type=expected_type, parse_method=parse_method)

        self.model = model
        self.root_location = root_location
