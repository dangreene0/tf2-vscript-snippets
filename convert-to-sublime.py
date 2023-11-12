#!/usr/bin/env python3

from json import load, dump

def main():
    try:
        with open("squirrel.json", "r", encoding="utf-8") as vsc_file:
            vsc_data = load(vsc_file)
    except IOError:
        print("Unable to local \".json\" file")
        quit()

    snippets = []

    for annotation in vsc_data:
        snippet = {
            "trigger": vsc_data[annotation]["prefix"],
            "annotation": annotation,
            "contents": vsc_data[annotation]["body"][0],
            "kind": "keyword",
            "details": vsc_data[annotation]["description"]
        }
        snippets.append(snippet)
        
    snippets_registry = {
        "scope": "source.nut",
        "completions": snippets
    }

    with open("tf2-snippets.sublime-completions", "w", encoding="utf-8") as sublime_json:
        dump(snippets_registry, sublime_json, indent=2)
    
if __name__ == "__main__":
    main()