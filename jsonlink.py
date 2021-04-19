from jsondatahelper import KEY_SPLIT_CHAR, flatten, format_dict, unflatten

from globals import (
    ATTRIBUTES,
    FUNCTIONS,
    OBJECT_ATTRIBUTE,
    OBJECT_NAME,
    VARIABLE_NAMES,
    english,
    pythonic,
    is_instanciated,
    read_json_file,
    splunk,
    write_to_file,
)


def get_indexes(path, return_last_found=False):
    """
    'path' represents a single property in flattend dictionary
    input  : this->is->1->a->path 
    intermediate : ["this","is",1,"a","path"]
    output : [1]
    """
    # v: String representation of index in path

    found_indexes = [v for v in path.split(KEY_SPLIT_CHAR) if v.isdigit()]
    if found_indexes:
        if return_last_found:
            return found_indexes[-1]
    return found_indexes


class SubClass:
    def __init__(self, class_reference):
        self.properties = splunk(class_reference, attribute_filters=["__"])
        self.class_reference = class_reference
        self.name = self.properties[OBJECT_NAME].lower()
        self.attributes = self.properties[ATTRIBUTES]
        self.variables = self.properties[VARIABLE_NAMES]
        self.functions = self.properties[FUNCTIONS]

    def build_new(self):

        return self.class_reference()

    def has_attribute(self, attribute):
        return attribute in self.attributes

    def is_function(self, function_name):
        return function_name in self.functions


class KeywordAttributeLink:
    def __init__(self, attribute, class_name="", is_function=False):
        self.attribute = attribute
        self.class_name = class_name
        self.is_function = is_function


JSONLINK_ATTRIBUTE_FILTERS = ["update_from_dict", "is_function", "create_example"]


class JsonLink:
    def __init__(self, keywords_file_path="", sub_classes=[], attribute_filters=["__"]):
        self.__add_jsonlink_attribute_filters(attribute_filters)
        self.properties = splunk(self, attribute_filters=attribute_filters)
        self.name = self.properties[OBJECT_NAME]
        self.attributes = self.properties[ATTRIBUTES]
        self.functions = self.properties[FUNCTIONS]
        self.variables = self.properties[VARIABLE_NAMES]
        self.__build_keywords()
        self.__associate_sub_classes(sub_classes)
        self.__read_keywords_file(keywords_file_path)
        self.__associate_keywords_to_attributes()

    def __add_jsonlink_attribute_filters(self, attribute_filters):
        for attribute in JSONLINK_ATTRIBUTE_FILTERS:
            attribute_filters.append(attribute)
        return attribute_filters

    def __build_keywords(self):
        self.keywords = {}
        for attribute in self.properties[ATTRIBUTES]:
            self.keywords[english(attribute)] = []

    def __associate_sub_classes(self, sub_classes):
        self.sub_class_containers = {}
        self.sub_classes = {}
        if sub_classes:
            for class_reference in sub_classes:
                sub_class = SubClass(class_reference)
                self.sub_classes[sub_class.name] = sub_class
                self.sub_class_containers[sub_class.name] = []
                for sub_class_attribute in sub_class.attributes:
                    self.keywords[
                        english(sub_class.name + "_" + sub_class_attribute)
                    ] = []

    def __purge_sub_class_containters(self):
        for sub_class_name in self.sub_class_containers:
            self.sub_class_containers[sub_class_name] = []

    def __read_keywords_file(self, keywords_file_path):
        if not keywords_file_path:  # Set Default Keywords file for given class object
            keywords_file_path = self.properties[OBJECT_NAME] + "_keywords" + ".json"

        found_keywords_file_contents = read_json_file(keywords_file_path)

        if not found_keywords_file_contents:  # If file not found, create new
            write_to_file(keywords_file_path, self.keywords)

        elif not len(self.keywords.keys()) == len(found_keywords_file_contents.keys()):
            for key in self.keywords.keys():
                try:
                    found_keywords_file_contents[key]
                except KeyError:
                    found_keywords_file_contents[key] = []

            write_to_file(keywords_file_path, found_keywords_file_contents)
            self.keywords = found_keywords_file_contents
        else:
            self.keywords = found_keywords_file_contents

    def is_function(self, function_name):
        return function_name in self.properties[FUNCTIONS]

    def __associate_keywords_to_attributes(self):
        """
        Associates Keyword File in local directory to functions
        in this class.
        """

        self.attribute_keyword_links = {}
        for default_keyword, keyword_aliases in self.keywords.items():
            default_keyword = pythonic(default_keyword)
            attribute_link = None
            if default_keyword in self.attributes:
                attribute_link = KeywordAttributeLink(
                    default_keyword, self.name, self.is_function(default_keyword)
                )
            else:
                attribute_link = self.__find_sub_class_attribute(default_keyword)

            if attribute_link:
                self.attribute_keyword_links[default_keyword] = attribute_link
                for alias in keyword_aliases:
                    self.attribute_keyword_links[pythonic(alias)] = attribute_link

    def __find_sub_class_attribute(self, keyword):
        split_keyword = keyword.split("_")
        class_name = split_keyword[0].lower()
        attribute_name = pythonic(" ".join(split_keyword[1 : len(split_keyword)]))
        try:
            if self.sub_classes[class_name].has_attribute(attribute_name):
                KeywordAttributeLink(
                    attribute_name,
                    class_name,
                    self.sub_classes[class_name].is_function(attribute_name),
                )

        except KeyError:
            return None  # Is not sub-class keyword

    def __process_attribute(
        self, property_name, property_value, sub_class_container_index=-1
    ):
        property_name = pythonic(property_name)
        try:
            attribute_link = self.attribute_keyword_links[property_name]
            perform_action_on_this = None
            if attribute_link.class_name == self.name:
                perform_action_on_this = self

            elif sub_class_container_index >= 0:  # Is sub class object
                sub_class_object = self.__get_sub_class_item(
                    attribute_link.class_name, sub_class_container_index
                )
                if not sub_class_object:
                    sub_class_object = self.sub_classes[
                        attribute_link.class_name
                    ].build_new()
                    self.sub_class_containers[attribute_link.class_name].append(
                        sub_class_object
                    )

                perform_action_on_this = sub_class_object

            self.__perform_attribute_action(
                instanciated_object=perform_action_on_this,
                attribute_link=attribute_link,
                property_value=property_value,
            )

        except KeyError:
            return False  # Attribute not found
        return True  # Attribute found

    def __get_sub_class_item(self, sub_class_name, sub_class_container_index):
        try:
            return self.sub_class_containers[sub_class_name][sub_class_container_index]
        except IndexError:  # Item Does Not Exist
            return None

    def __perform_attribute_action(
        self, instanciated_object, attribute_link, property_value
    ):
        if attribute_link.is_function:
            getattr(instanciated_object, attribute_link.attribute)(property_value)
        else:
            setattr(instanciated_object, attribute_link.attribute, property_value)

    def update_from_dict(self, dictionary):
        self.__purge_sub_class_containters()
        for property_path, property_value in flatten(dictionary).items():
            split_path = property_path.split(KEY_SPLIT_CHAR)
            root_property = split_path[0]
            if not self.__process_attribute(root_property, dictionary[root_property]):
                leaf_property = pythonic(split_path[-1])
                index = get_indexes(property_path, return_last_found=True)
                self.__process_attribute(leaf_property, property_value, index)
        return self

    def create_example(self):
        pass

    def __repr__(self):
        return f"""
            Object Name : {self.name}\n
            Attributes  : {self.attributes}\n
            Variables   : {self.variables}\n
            Functions   : {self.functions}\n
            Keywords    : {self.keywords}\n
        """

