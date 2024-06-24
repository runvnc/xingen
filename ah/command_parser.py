import json
from typing import List, Dict, Tuple, Any
from partial_json_parser import loads, ensure_json

def parse_streaming_commands(buffer: str) -> Tuple[List[Dict[str, Any]], str]:
    """
    Parse streaming commands from a buffer, identifying complete commands.
    
    Args:
    buffer (str): The current buffer of streamed data.
    
    Returns:
    Tuple[List[Dict[str, Any]], str]: A tuple containing a list of complete commands and the last partial command (if any).
    """
    complete_commands = []
    current_partial = None

    if not buffer.strip():
        return [], None
    
    try:
        # try to parse using normal json parser 
        complete_commands = json.loads(buffer)
        return complete_commands, None
    try:
        # Use partial_json_parser to parse the buffer
        parsed_data = loads(buffer)
        num_completed = len(parsed_data) - 1
        if num_completed > 0:
            if num_completed > 1:
                current_partial = parsed_data[-1]
            complete_commands = parsed_data[:num_completed]

    except Exception:
        # If parsing fails, return an empty list of commands and the entire buffer as remaining
        return [], None
    
    return complete_commands, current_partial

# Test cases
import unittest

class TestCommandParser(unittest.TestCase):
    
    def test_single_complete_command(self):
        buffer = '[{"say": {"text": "Hello", "done": true}}]'
        commands, remaining = parse_streaming_commands(buffer)
        self.assertEqual(len(commands), 1)
        self.assertEqual(commands[0], {"say": {"text": "Hello", "done": True}})
        self.assertEqual(remaining, '')
    
    def test_multiple_complete_commands(self):
        buffer = '[{"say": {"text": "Hello"}}, {"do_something": {"arg1": "value1"}}]'
        commands, remaining = parse_streaming_commands(buffer)
        self.assertEqual(len(commands), 2)
        self.assertEqual(commands[0], {"say": {"text": "Hello"}})
        self.assertEqual(commands[1], {"do_something": {"arg1": "value1"}})
        self.assertEqual(remaining, '')
    
    def test_partial_command(self):
        buffer = '[{"say": {"text": "Hello"}}, {"do_something": {"arg1": "valu'
        commands, remaining = parse_streaming_commands(buffer)
        self.assertEqual(len(commands), 1)
        self.assertEqual(commands[0], {"say": {"text": "Hello"}})
        self.assertEqual(remaining, ', {"do_something": {"arg1": "valu')
    
    def test_empty_buffer(self):
        buffer = ''
        commands, remaining = parse_streaming_commands(buffer)
        self.assertEqual(len(commands), 0)
        self.assertEqual(remaining, '')
    
    def test_invalid_json(self):
        buffer = '[{"say": {"text": "Hello"}, {"invalid": "command"}]'
        commands, remaining = parse_streaming_commands(buffer)
        self.assertEqual(len(commands), 0)
        self.assertEqual(remaining, buffer)
    
    def test_nested_objects(self):
        buffer = '[{"complex_command": {"nested": {"key": "value"}}}]'
        commands, remaining = parse_streaming_commands(buffer)
        self.assertEqual(len(commands), 1)
        self.assertEqual(commands[0], {"complex_command": {"nested": {"key": "value"}}})
        self.assertEqual(remaining, '')
    
    def test_partial_nested_objects(self):
        buffer = '[{"complex_command": {"nested": {"key": "val'
        commands, remaining = parse_streaming_commands(buffer)
        self.assertEqual(len(commands), 0)
        self.assertEqual(remaining, buffer)

    def test_partial_think_command(self):
        buffer = '{ "think": '
        commands, remaining = parse_streaming_commands(buffer)
        self.assertEqual(len(commands), 0)
        self.assertEqual(remaining, buffer)

    def test_partial_think_command_with_thoughts(self):
        buffer = '{ "think": { "thoughts": '
        commands, remaining = parse_streaming_commands(buffer)
        self.assertEqual(len(commands), 0)
        self.assertEqual(remaining, buffer)

    def test_partial_think_command_with_complete_thoughts(self):
        buffer = '{ "think": { "thoughts": "I am thinking" } }'
        commands, remaining = parse_streaming_commands(buffer)
        self.assertEqual(len(commands), 1)
        self.assertEqual(commands[0], {"think": {"thoughts": "I am thinking"}})
        self.assertEqual(remaining, '')

    def test_malformed_json(self):
        buffer = '{"key": "value"'
        commands, remaining = parse_streaming_commands(buffer)
        self.assertEqual(len(commands), 0)
        self.assertEqual(remaining, buffer)

if __name__ == '__main__':
    unittest.main()
