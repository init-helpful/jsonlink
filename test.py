from jsonlink import JsonLink


class JsonLinkTest(JsonLink):
    def __init__(self):
        self.test_object1 = "two"
        self.test_object_two = "1"
        super(JsonLinkTest, self).__init__()

    def this_is_a_function(self):
        print("This is a function")


json_link_test = JsonLinkTest().update_from_dict(
    {
        "test_object1": "This is a test",
        "Test oBjeCT TwO": "This is also a test",
        "this_is_a_function": "Test",
    }
)


print(json_link_test)
