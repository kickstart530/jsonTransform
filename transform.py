import json
from jsonbender import bend, K, S

# Create a mapping between source and destination JSON files
MAPPING = {
    'fullName': (S('customer', 'first_name') +
                 K(' ') +
                 S('customer', 'last_name')),
    'city': S('address', 'city'),
}


# Load the Input.json
sourceFile = open('input.json')
source = json.load(sourceFile)
sourceFile.close()

result = bend(MAPPING, source)

# Create a output.json with JSONBender Output
outputFile = open('output.json','w');

json_object = json.dumps(result)

outputFile.write(json_object)

print(json_object)

outputFile.close()