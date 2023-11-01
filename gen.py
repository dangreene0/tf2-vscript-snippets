#!/usr/bin/env python3

defs = open("defs.txt", "r", 1, "utf-8")
lines = defs.readlines()
functions = {}
i = 0
mostRecentFunction = ""
for line in lines:
    text = line[0:-1]

    match ["function", "signature", "description", "space"][i % 4]:
        case "function":
            mostRecentFunction = text
            functions[mostRecentFunction] = {"function": text, "signature": "", "description": ""}
        case "signature":
            if (functions[mostRecentFunction]["signature"] == ""):
                functions[mostRecentFunction]["signature"] = text
        case "description":
            if (functions[mostRecentFunction]["description"] == ""):
                functions[mostRecentFunction]["description"] = text.replace("\\", "\\\\")
                functions[mostRecentFunction]["description"] = functions[mostRecentFunction]["description"].replace("\"", "\\\"")

    i += 1
defs.close()

outputString = "{\n\t///// BEGIN TF2 VScript Snippets /////\n"
sortedKeys = sorted(list(functions.keys()))
for key in sortedKeys:

    prefix, body = "", ""
    baseSignature = functions[key]["signature"]
    parenIndex = baseSignature.find("(")
    if (parenIndex >= 0):
        prefix = baseSignature[0:parenIndex].split(" ")[-1]
        # We need to parse params
        params = baseSignature[parenIndex+1:-1].split(", ")
        body = prefix + "("
        i = 1
        if (params[0] != ""):
            for param in params:
                body += "${" + str(i) + ":" + param + "}"
                if (i != len(params)):
                    body += ", "
                i += 1
        body += ")$0"
    else:
        # This is a constant
        prefix, body = baseSignature, baseSignature + "$0"

    outputString += ("\t\"" + baseSignature + "\": {\n\t\t\"prefix\": \"" + prefix + "\",\n\t\t\"body\": [\n\t\t\t\"" + body + "\"\n\t\t],\n\t\t\"description\": \"" + functions[key]["description"] + "\"\n\t},\n")
outputString = outputString[:len(outputString)-2] + "\n\t///// END TF2 VScript Snippets /////\n}"
print(outputString, end="")

outputFile = open("squirrel.json", "w")
outputFile.write(outputString)