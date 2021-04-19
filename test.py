from jsonlink import JsonLink


class JsonLinkTest(JsonLink):
    def __init__(self):
        self.test_var_1 = "1"
        self.test_var_2 = "2"
        super(JsonLinkTest, self).__init__(sub_classes=[SubClassOne, SubClassTwo])

    def this_is_a_function(self, properties):
        self.nest_test_var = "This is a nested value hidden in a function!"
        print(properties)


class SubClassOne:
    def __init__(self):
        self.classone_var_one = "class 1 var 1"
        self.classone_var_two = [1, 2, 3, 4, 5, 6, 7, 8]

    def sub_class_func_one(self, properties):
        self.test_nested_sub_var = {"Nested": "dictionary"}
        # print("Sub Class Function Hit!", properties)


class SubClassTwo:
    def __init__(self):
        self.classtwo_var_one = "class 2 var 1"
        self.classtwo_var_two = [8, 7, 6, 5, 4, 3, 2, 1]

    def sub_class_2_func_1(self, properties):
        print(properties)


json_link_test = JsonLinkTest().update_from_dict(
    {
        "test_var_1": "This is a test",
        "test_var_2": "This is also a test",
        "this_is_a_function": "This will be printed out",
        "sub_class_ones": [
            {
                "Subclassone Classone Var One": "sub one value",
                "Subclassone classone var two": "var 2 value",
                "Subclassone_sub_class_func_one": ("a1", "b2", "c3"),
            }
        ],
        "sub_class_twos": [{"SubClassTwo classtwo_var_one":"ahhhh"}],
    }
)


print(json_link_test.get_state())
