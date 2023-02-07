import json
import yaml
from jsonbender import bend, K, S

# Create a mapping between source and destination JSON files
with open("mapping.yaml","r") as file:
    MAPPINGFILE = yaml.load(file,Loader=yaml.FullLoader)

MAPPING = dict()
for key, value in MAPPINGFILE.items():
    m = { key: eval(value)}
    MAPPING.update(m)

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