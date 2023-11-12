#!/usr/bin/env python3
from json import dump, load

def main():
    # TODO add logic for OnGameEvent so that the end result is "OnGameEvent_${1:name}(${2:table params})$0"
    # Change data management to dicts and json
    try:
        with open("defs.txt", "r", encoding="utf-8") as defs_file:
            defs_data = defs_file.readlines()
    except IOError:
        print("Unable to locate defs file")
        quit()

    functions = parse_defs(defs_data)
    sorted_keys = sorted(list(functions.keys()))# Good for comparing diffs
    function_registry = generate_snippet_format(sorted_keys, functions)

    with open("squirrel.json", "w") as json_test:
        dump(function_registry, json_test, indent=2)

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
        text = line[0:-1] # necessary because ".readlines() injects newlines"

        match ["function", "signature", "description", "space"][quad_defs_entry % 4]:
            case "function":
                most_recent_function = text
                functions[most_recent_function] = {
                    "function": text,
                    "signature": "",
                    "description": "",
                }
            case "signature":
                if functions[most_recent_function]["signature"] == "":
                    functions[most_recent_function]["signature"] = text
            case "description":
                if functions[most_recent_function]["description"] == "":
                    functions[most_recent_function]["description"] = text.replace(
                        "\\", "\\\\"
                    )
                    functions[most_recent_function]["description"] = functions[
                        most_recent_function
                    ]["description"].replace('"', '\\"')

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
        paren_index = base_signature.find("(")
        if paren_index >= 0:
            prefix = base_signature[0:paren_index].split(" ")[-1]
            # We need to parse params
            params = base_signature[paren_index + 1 : -1].split(", ")
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