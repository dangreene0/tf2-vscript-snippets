#!/usr/bin/env python3
from json import dump, load
from os import listdir, path

def main():

    try:
        with open("defs.txt", "r", encoding="utf-8") as defs_file:
            defs_data = defs_file.read().split('\n')
    except IOError:
        print("Unable to locate defs file")
        quit()

    functions = parse_defs(defs_data)
    sorted_keys = sorted(list(functions.keys()))# Good for comparing diffs
    function_registry = generate_snippet_format(sorted_keys, functions)

    addendum_json = update_registry_addendum()
    function_registry.update(addendum_json)

    with open("squirrel.json", "w", encoding="utf-8") as squirrel_json:
        dump(function_registry, squirrel_json, indent=2)

def update_registry_addendum() -> dict:
    '''
    ### Summary
    Returns a dict of all additional `.json` files from addendum folder. These additional files may include community suggestions or contributions. They are not generated from the 'defs.txt' file.
    ### Parameters
    `None`
    ### Returns
    1. dict
            - Dict of all the additional `.json` files in VSCode Snippet format.
    '''
    addendum_json = {}
    directory = "addendum"

    for file in listdir(directory):
        if (file.endswith('.json')):
            file_dir = path.join(directory, file)
            try:
                with open(file_dir, "r", encoding="utf-8") as additional_json:
                    current_json = load(additional_json)
                addendum_json.update(current_json)

            except IOError:
                print("Unable to locate additional file.")

    return addendum_json

def parse_defs(defs_data: str) -> dict:
    '''
    ### Summary
    Takes raw data from file and sorts it based on what line the entry was, in units of 4 lines.
    ### Parameters
    1. defs_data : str
            - The raw data from the `defs.txt` file.
    ### Returns
    1. functions : dict
            - All of the raw data parsed into a primitive dict that will be later reformated to the snippet formatting.
    '''
    functions = {}
    quad_defs_entry = 0
    most_recent_function = ""

    for line in defs_data:

        match ["function", "signature", "description", "space"][quad_defs_entry % 4]:
            case "function":
                most_recent_function = line
                functions[most_recent_function] = {
                    "function": line,
                    "signature": "",
                    "description": "",
                }
            case "signature":
                if functions[most_recent_function]["signature"] == "":
                    functions[most_recent_function]["signature"] = line
            case "description":
                if functions[most_recent_function]["description"] == "":
                    functions[most_recent_function]["description"] = line.replace(
                        "\\", "\\\\"
                    )
                    functions[most_recent_function]["description"] = functions[most_recent_function]["description"].replace('"', '\\"')

        quad_defs_entry += 1
    return functions

def generate_snippet_format(sorted_keys: list[str], functions: dict) -> dict:
    '''
    ### Summary
    Takes the sorted keys of the functions dict and formats where unset variables exist in the function body.
    ### Parameters
    1. sorted_keys : list[str]
            - A sorted list of the names of all of the functions.
    2. functions : dict
            - Primitive dictionary of all the functions that need to be formatted to include their unset variable syntax as added to the registry.
    ### Returns
    1. function_registry : dict
            - Formatted dict of all functions as VSCode snippets with unset variable syntax included.
    '''
    function_registry = {}
    for key in sorted_keys:
        prefix, body = "", ""
        base_signature = functions[key]["signature"]

        parentheses_index = base_signature.find("(")

        if parentheses_index >= 0:
            prefix = base_signature[0:parentheses_index].split(" ")[-1]
            # We need to parse params
            params = base_signature[parentheses_index + 1 : -1].split(", ")
            body = prefix + "("
            quad_defs_entry = 1
            if params[0] != "":
                for param in params:
                    body += "${" + str(quad_defs_entry) + ":" + param + "}"
                    if quad_defs_entry != len(params):
                        body += ", "
                    quad_defs_entry += 1
            body += ")$0"
        else:
            # This is a constant
            prefix, body = base_signature, base_signature + "$0"

        function_entry = {
            base_signature: {
                "prefix": prefix,
                "body": [
                    body
                ],
                "description" : functions[key]["description"]
            }
        }
        function_registry.update(function_entry)

    return  function_registry

if __name__ == "__main__":
    main()