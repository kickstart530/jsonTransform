import json
import yaml
from jsonbender import bend, K, S

try:
    with open("mapping.yaml", "r") as file:
        MAPPINGFILE = yaml.load(file, Loader=yaml.FullLoader)

    MAPPING = {}
    for key, value in MAPPINGFILE.items():
        if isinstance(value, str):
            MAPPING[key] = eval(value)
        else:
            MAPPING[key] = value

    with open('input.json', 'r') as sourceFile:
        source = json.load(sourceFile)

    result = bend(MAPPING, source)

    with open('output.json', 'w') as outputFile:
        json.dump(result, outputFile)

    print(json.dumps(result))

except FileNotFoundError as e:
    print(f"Error: Required file not found - {e}")
except yaml.YAMLError as e:
    print(f"Error: Invalid YAML format - {e}")
except json.JSONDecodeError as e:
    print(f"Error: Invalid JSON format - {e}")
except Exception as e:
    print(f"Error: {e}")
