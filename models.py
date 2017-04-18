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

    def item(self, key):
        """
        Returns the value associated with the key from the item_dict. If not found it will return None.
        """
        try:
            return self.item_dict[key]
        except KeyError:
            return None

    def __getattr__(self, item):
        return self.item_dict[item]
