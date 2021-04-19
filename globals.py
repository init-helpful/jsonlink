import json

PYTHON_DEPENDENCIES = "Python Dependencies"
TASK_DESCRIPTION = "Task Description"
GLOBAL_VALUES = "Global Values"
GLOBAL_HOOKS = "Global Hooks"
STEP_GROUPINGS = "Step Groupings"
STEPS = "Steps"
STEP_NAME = "Step Name"
STEP_DESCRIPTION = "Step Description"
STEP_HOOKS = "Step Hooks"
STEP_DATA = "Step Data"
STEP_DEPENDENT_ON = "Step Dependent On"

DEFAULT_KEYWORD_FILE_NAME = "keywords"
DEFAULT_KEYWORD_FILE_PATH = DEFAULT_KEYWORD_FILE_NAME + ".json"


DEFAULT_KEYWORDS = {
    PYTHON_DEPENDENCIES: [],
    TASK_DESCRIPTION: [],
    GLOBAL_VALUES: [],
    GLOBAL_HOOKS: [],
    STEP_GROUPINGS: [],
    STEPS: [],
    STEP_NAME: [],
    STEP_DESCRIPTION: [],
    STEP_HOOKS: [],
    STEP_DATA: [],
    STEP_DEPENDENT_ON: [],
}
OBJECT_NAME = "name"
OBJECT_ATTRIBUTE = "attribute"
ATTRIBUTES = "attributes"
FUNCTIONS = "functions"
VARIABLE_NAMES = "variable Names"
VARIABLE_VALUES = "variable Values"


def write_to_file(file_path, data):
    with open(file_path, "w+", encoding="utf-8") as f:
        json.dump(
            data, f, ensure_ascii=True, indent=4,
        )


def convert_bytes(loaded_json):
    for key, val in loaded_json.items():
        if isinstance(val, dict):
            loaded_json[key] = convert_bytes(val)
        elif isinstance(val, list):
            for index, item in enumerate(val):
                if isinstance(item, dict):
                    loaded_json[key][index] = convert_bytes(item)
                elif isinstance(item, str) and item.startswith("b'"):
                    loaded_json[key][index] = bytes.fromhex(item.split("b'")[1])
        elif isinstance(val, str) and val.startswith("b'"):
            loaded_json[key] = bytes.fromhex(val.split("b'")[1])

    return loaded_json


def read_json_file(file_path):
    try:
        with open(file_path, "r+") as file_contents:
            return convert_bytes(json.load(file_contents))
    except FileNotFoundError:
        return None


def get_attributes(object_reference, filters=["__"]):
    functions = dir(object_reference)
    filtered_functions = dir(object_reference)
    for function_name in functions:
        for filter in filters:
            if filter in function_name:
                filtered_functions.remove(function_name)
    return filtered_functions


# def get_attributes(object):
#     return [prop for prop in dir(object) if "__" not in prop]


def get_variables(object):
    variables = object.__dict__
    return list(variables.keys()), list(variables.values())


def is_instanciated(object):
    return "." in str(type(object))


def splunk(object, attribute_filters=["__"], *args, **kwargs):
    if not is_instanciated(object):  # If not instanciated
        object = object()

    object_name = type(object).__name__
    object_attributes = get_attributes(object, attribute_filters)
    object_variable_names, object_variable_values = get_variables(object)
    object_functions = list(
        set(object_attributes).difference(set(object_variable_names))
    )
    object_functions.sort()

    return {
        OBJECT_NAME: object_name,
        ATTRIBUTES: object_attributes,
        FUNCTIONS: object_functions,
        VARIABLE_NAMES: object_variable_names,
        VARIABLE_VALUES: object_variable_values,
    }


def pythonic(string):
    return string.replace(" ", "_").lower()


def english(string):
    s = ""
    for word in string.split("_"):
        s = s + word.capitalize() + " "
    return s.rstrip()

