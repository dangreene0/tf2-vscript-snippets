#!/usr/bin/env python3

import json, re

original = open("squirrel.json", "r")
unparsed = original.read()
original.close()

unparsed = re.sub("\n\t///// BEGIN TF2 VScript Snippets /////", "", unparsed)
unparsed = re.sub("\n\t///// END TF2 VScript Snippets /////", "", unparsed)

parsed = json.loads(unparsed)

i = 1
print("{\n\t\"scope\": \"source.nut\",\n\t\"completions\": [")
for annotation in parsed:
    trigger = parsed[annotation]["prefix"]
    contents = parsed[annotation]["body"][0]
    details = parsed[annotation]["description"]
    details = re.sub("\"", "\\\"", details)
    print("\t\t{")
    print(f"\t\t\t\"trigger\": \"{trigger}\",\n\t\t\t\"annotation\": \"{annotation}\",\n\t\t\t\"contents\": \"{contents}\",\n\t\t\t\"kind\": \"keyword\",\n\t\t\t\"details\": \"{details}\"")
    print("\t\t}", end="")
    if (i < len(parsed)):
        print(",")
    i += 1
print("\n\t]\n}", end="")
