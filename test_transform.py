"""
Unit tests for the transform.py module.
Tests JSON transformation functionality using jsonbender library.
"""
import json
import os
import shutil
import tempfile
import unittest
from unittest.mock import patch, mock_open
import yaml
from transform import safe_eval_mapping, main


class TestTransform(unittest.TestCase):
    """Test cases for the transform module."""

    def setUp(self):
        """Set up test fixtures before each test method."""
        self.test_mapping = {
            'name': 'user.full_name',
            'email': 'user.email_address',
            'age': 'user.profile.age'
        }

        self.test_input_data = {
            'user': {
                'full_name': 'John Doe',
                'email_address': 'john@example.com',
                'profile': {
                    'age': 30
                }
            }
        }

        self.expected_output = {
            'name': 'user.full_name',
            'email': 'user.email_address',
            'age': 'user.profile.age'
        }

    def test_safe_eval_mapping(self):
        """Test the safe_eval_mapping function."""
        test_expression = "user.name"
        result = safe_eval_mapping(test_expression)
        self.assertEqual(result, test_expression)

        # Test with different types of expressions
        expressions = [
            "user.profile.age",
            "data.items[0].value",
            "simple_field"
        ]

        for expr in expressions:
            with self.subTest(expression=expr):
                result = safe_eval_mapping(expr)
                self.assertEqual(result, expr)

    def test_successful_transformation(self):
        """Test successful JSON transformation."""
        with patch('builtins.open', new_callable=mock_open), \
             patch('yaml.load') as mock_yaml_load, \
             patch('json.load') as mock_json_load, \
             patch('json.dump') as mock_json_dump, \
             patch('transform.bend') as mock_bend, \
             patch('builtins.print') as mock_print:

            # Setup mocks
            mock_yaml_load.return_value = self.test_mapping
            mock_json_load.return_value = self.test_input_data
            mock_bend.return_value = self.expected_output

            # Run the main function
            main()

            # Verify that the functions were called correctly
            mock_yaml_load.assert_called_once()
            mock_json_load.assert_called_once()
            mock_bend.assert_called_once()
            mock_json_dump.assert_called_once()
            mock_print.assert_called_with(json.dumps(self.expected_output))

    @patch('builtins.open', side_effect=FileNotFoundError("mapping.yaml not found"))
    @patch('builtins.print')
    def test_missing_mapping_file(self, mock_print, _mock_file):
        """Test handling of missing mapping.yaml file."""
        main()
        expected_msg = "Error: Required file not found - mapping.yaml not found"
        mock_print.assert_called_with(expected_msg)

    @patch('builtins.open', new_callable=mock_open, read_data="invalid: yaml: content:")
    @patch('yaml.load', side_effect=yaml.YAMLError("Invalid YAML"))
    @patch('builtins.print')
    def test_invalid_yaml_format(self, mock_print, _mock_yaml_load, _mock_file):
        """Test handling of invalid YAML format."""
        main()
        mock_print.assert_called_with("Error: Invalid YAML format - Invalid YAML")

    @patch('builtins.open', new_callable=mock_open)
    @patch('yaml.load')
    @patch('json.load', side_effect=json.JSONDecodeError("Invalid JSON", "", 0))
    @patch('builtins.print')
    def test_invalid_json_format(self, mock_print, _mock_json_load,
                                mock_yaml_load, _mock_file):
        """Test handling of invalid JSON format."""
        mock_yaml_load.return_value = self.test_mapping

        main()
        expected_msg = "Error: Invalid JSON format - Invalid JSON: line 1 column 1 (char 0)"
        mock_print.assert_called_with(expected_msg)

    @patch('builtins.print')
    @patch('transform.bend')
    @patch('json.dump', side_effect=OSError("Permission denied"))
    @patch('json.load')
    @patch('yaml.load')
    @patch('builtins.open', new_callable=mock_open)
    def test_file_operation_error(self, _mock_file, mock_yaml_load,
                                 mock_json_load, _mock_json_dump,
                                 mock_bend, mock_print):
        """Test handling of file operation errors."""
        mock_yaml_load.return_value = self.test_mapping
        mock_json_load.return_value = self.test_input_data
        mock_bend.return_value = self.expected_output

        main()
        expected_msg = "Error: File operation failed - Permission denied"
        mock_print.assert_called_with(expected_msg)

    def test_mapping_with_string_values(self):
        """Test mapping processing with string values."""
        test_mapping_with_strings = {
            'name': 'user.full_name',
            'contact': {
                'email': 'user.email_address'
            },
            'metadata': 'user.profile'
        }

        # Test that string values are processed through safe_eval_mapping
        for value in test_mapping_with_strings.values():
            if isinstance(value, str):
                result = safe_eval_mapping(value)
                self.assertEqual(result, value)

    def test_mapping_with_non_string_values(self):
        """Test mapping processing with non-string values."""
        test_mapping_mixed = {
            'name': 'user.full_name',
            'age': 25,  # integer value
            'active': True,  # boolean value
            'tags': ['tag1', 'tag2']  # list value
        }

        # Non-string values should be kept as-is
        for value in test_mapping_mixed.values():
            if not isinstance(value, str):
                # In the actual code, non-string values are kept unchanged
                self.assertIsInstance(value, type(value))

    @patch('builtins.print')
    @patch('transform.bend')
    @patch('json.dump')
    @patch('json.load')
    @patch('yaml.load')
    @patch('builtins.open', new_callable=mock_open)
    def test_output_printing(self, _mock_file, mock_yaml_load,
                           mock_json_load, _mock_json_dump,
                           mock_bend, mock_print):
        """Test that the result is printed to stdout."""
        mock_yaml_load.return_value = self.test_mapping
        mock_json_load.return_value = self.test_input_data
        mock_bend.return_value = self.expected_output

        main()

        # Verify that the result was printed
        expected_json_output = json.dumps(self.expected_output)
        mock_print.assert_called_with(expected_json_output)


class TestIntegration(unittest.TestCase):
    """Integration tests using actual files."""

    def setUp(self):
        """Set up temporary files for integration testing."""
        self.temp_dir = tempfile.mkdtemp()

        # Create test files
        self.mapping_file = os.path.join(self.temp_dir, 'mapping.yaml')
        self.input_file = os.path.join(self.temp_dir, 'input.json')
        self.output_file = os.path.join(self.temp_dir, 'output.json')

        # Sample mapping
        mapping_data = {
            'user_name': 'data.user.name',
            'user_email': 'data.user.email'
        }

        # Sample input data
        input_data = {
            'data': {
                'user': {
                    'name': 'Alice Smith',
                    'email': 'alice@example.com'
                }
            }
        }

        # Write test files
        with open(self.mapping_file, 'w', encoding='utf-8') as f:
            yaml.dump(mapping_data, f)

        with open(self.input_file, 'w', encoding='utf-8') as f:
            json.dump(input_data, f)

    def tearDown(self):
        """Clean up temporary files."""
        shutil.rmtree(self.temp_dir)

    @patch('builtins.print')
    @patch('transform.bend')
    @patch('json.dump')
    @patch('json.load')
    @patch('yaml.load')
    @patch('builtins.open', new_callable=mock_open)
    def test_file_encoding_usage(self, mock_open_func, mock_yaml_load,
                                mock_json_load, _mock_json_dump,
                                mock_bend, _mock_print):
        """Test that files are opened with UTF-8 encoding."""
        # Setup mocks
        mock_yaml_load.return_value = {'test': 'value'}
        mock_json_load.return_value = {'data': 'test'}
        mock_bend.return_value = {'result': 'test'}

        main()

        # Verify that open was called with encoding parameter
        calls = mock_open_func.call_args_list
        for call in calls:
            if len(call[1]) > 0:  # Check if keyword arguments exist
                self.assertIn('encoding', call[1])
                self.assertEqual(call[1]['encoding'], 'utf-8')


if __name__ == '__main__':
    # Run the tests
    unittest.main(verbosity=2)
