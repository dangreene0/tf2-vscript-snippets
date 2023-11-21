#!/usr/bin/env python3
from json import dump, load
from os import listdir, path
from urllib.request import urlretrieve

def main():

    try:
        with open("data/defs.txt", "r", encoding="utf-8") as defs_file:
            defs_data = defs_file.read().split('\n')
    except IOError:
        print("Unable to locate defs file")
        quit()

    functions = parse_defs(defs_data)
    sorted_keys = sorted(list(functions.keys()))# Good for comparing diffs
    function_registry = generate_snippet_format(sorted_keys, functions)

    get_ents()

    addendum_json = update_registry_addendum()

    function_registry.update(addendum_json)
    ## TODO sort the keys again

    with open("squirrel.json", "w", encoding="utf-8") as squirrel_json:
        dump(function_registry, squirrel_json, indent=2)

def generate_netprop_snippets(netprops: list[dict]) -> dict:
    netprops_registry = {}

    for netprop in netprops:
        ent_name = netprop["ent"]
        netprop_entry = {
            f"ent.{ent_name}": {
                "prefix": ent_name ,
                "body": [
                    f"NetProps.GetPropInt(ent, \"{ent_name}\")"
                ],
                "description" : ""
            }
        }
        netprops_registry.update(netprop_entry)
    return netprops_registry

def parse_netprops() -> tuple[list[str], dict]:

    netprops_registry = []
    try:
        with open("data/netprops.txt", "r", encoding="utf-8") as ent_file:
                netprops_data = ent_file.read().split('\n')
    except IOError:
        print("Unable to locate defs file")
        quit()

    for line in netprops_data:

        supported_types = ["integer", "float", "vector", "string"] # shrug emoji
        ent = ""
        type = ""
        existing_ents = []

        line = line.split()
        for word in line:
            if word.startswith("m_") or word.startswith("move"):
                if word[-1] != ")":
                    ent = word
            if ent in existing_ents:
                continue
            if "(type" == word and ent != "":
                type_index = line.index(word) + 1
                type = line[type_index][:-1]

            if ent != "" and type != "":
                netprop = {
                    "ent": ent,
                    "type": type
                }
                existing_ents.append(ent)
                netprops_registry.append(netprop)

    return existing_ents, netprops_registry

def parse_datamaps(existing_ents: list[str]) -> dict:
    '''
    I don't know what types these are supposed to be. So they're integers by default.
    '''
    try:
        with open("data/datamaps.txt", "r", encoding="utf-8") as ent_file:
                datamaps_data = ent_file.read().split('\n')
    except IOError:
        print("Unable to locate defs file")
        quit()

    datamaps_registry = []

    for line in datamaps_data:
        line = line.split()
        for word in line:
            if word.startswith("m_"):
                if word not in existing_ents:
                    datamap = {
                        "ent": word,
                        "type": "integer"
                    }
                    existing_ents.append(word)
                    datamaps_registry.append(datamap)

    return datamaps_registry

def get_ents() -> dict:
    netprops_url = "https://invalidvertex.com/tf2dump/netprops.txt"
    datamaps_url = "https://invalidvertex.com/tf2dump/datamaps.txt"

    netprops_snippets = []
    urlretrieve(netprops_url, "data/netprops.txt")
    urlretrieve(datamaps_url, "data/datamaps.txt")

    netprops_ents, netprops_registry = parse_netprops()
    netprops_registry.extend(parse_datamaps(netprops_ents))

    netprops_snippets = generate_netprop_snippets(netprops_registry)

    with open("addendum/netprops.json", "w", encoding="utf-8") as netprops_json:
            dump(netprops_snippets, netprops_json, indent=2)

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