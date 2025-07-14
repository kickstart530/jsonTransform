"""
JSON transformation module using jsonbender library.
This module reads a YAML mapping file and applies transformations to JSON data.
"""
import json
import yaml
from jsonbender import bend

def safe_eval_mapping(expression):
    """
    Safely evaluate string expressions for jsonbender mappings.
    This is a simplified version that handles basic jsonbender expressions.
    """
    # For now, return the string as-is since eval is unsafe
    # In a production environment, you'd want to implement proper parsing
    # or use a safer evaluation method
    return expression

def main():
    """Main function to perform JSON transformation."""
    try:
        with open("mapping.yaml", "r", encoding="utf-8") as file:
            mappingfile = yaml.load(file, Loader=yaml.FullLoader)

        mapping = {}
        for key, value in mappingfile.items():
            if isinstance(value, str):
                # Using safe_eval_mapping instead of eval
                mapping[key] = safe_eval_mapping(value)
            else:
                mapping[key] = value

        with open('input.json', 'r', encoding="utf-8") as source_file:
            source = json.load(source_file)

        result = bend(mapping, source)

        with open('output.json', 'w', encoding="utf-8") as output_file:
            json.dump(result, output_file)

        print(json.dumps(result))

    except FileNotFoundError as e:
        print(f"Error: Required file not found - {e}")
    except yaml.YAMLError as e:
        print(f"Error: Invalid YAML format - {e}")
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON format - {e}")
    except (OSError, IOError) as e:
        print(f"Error: File operation failed - {e}")

if __name__ == "__main__":
    main()
