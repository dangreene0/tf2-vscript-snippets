#!/usr/bin/env python3
from json import dump, load

def main():
    # TODO add logic for OnGameEvent so that the end result is "OnGameEvent_${1:name}(${2:table params})$0"
    # Change data management to dicts and json
    with open("defs.txt", "r", encoding="utf-8") as defs_file:
        defs_data = defs_file.readlines()

    functions = {}
    i = 0
    most_recent_function = ""

    for line in defs_data:
        text = line[0:-1]

        match ["function", "signature", "description", "space"][i % 4]:
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

        i += 1

    sorted_keys = sorted(list(functions.keys()))
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
            i = 1
            if params[0] != "":
                for param in params:
                    body += "${" + str(i) + ":" + param + "}"
                    if i != len(params):
                        body += ", "
                    i += 1
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

    with open("squirrel_.json", "w") as json_test:
        dump(function_registry, json_test, indent=2)

if __name__ == "__main__":
    main()