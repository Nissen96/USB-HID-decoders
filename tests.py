'''
Test decoding scripts against expected output
'''
import unittest
from pathlib import Path
from keyboard_decode import decode_keypresses, format_raw_keypresses, simulate_keypresses


root = Path('.')
border_length = 40
error_message = '''{top_rule}
Expected
{mid_rule}
{{expected}}
{top_rule}
Decoded
{mid_rule}
{{output}}
'''.format(top_rule='~' * border_length, mid_rule='-' * border_length)


class KeyboardTest(unittest.TestCase):
    def setUp(self):
        self.longMessage = False

    def test_raw_output(self):
        for ctf in (root / 'samples' / 'keyboard').iterdir():
            with self.subTest(ctf.name):
                with open(ctf / 'usbdata.txt') as f, open(ctf / 'output-raw.txt') as g:
                    expected = g.read()
                    keypresses = decode_keypresses(f.read())
                    output = format_raw_keypresses(keypresses)
                    self.assertEqual(expected, output, f'Decoded keypresses do not match expected output\n{error_message.format(expected=expected, output=output)}')

    def test_simulated_txt_output(self):
        for ctf in (root / 'samples' / 'keyboard').iterdir():
            with self.subTest(ctf.name):
                with open(ctf / 'usbdata.txt') as f, open(ctf / 'output-sim-txt.txt') as g:
                    expected = g.read()
                    keypresses = decode_keypresses(f.read())
                    output = simulate_keypresses(keypresses, text_mode=True)
                    self.assertEqual(expected, output, f'Decoded keypresses do not match expected output\n{error_message.format(expected=expected, output=output)}')

    def test_simulated_cmd_output(self):
        for ctf in (root / 'samples' / 'keyboard').iterdir():
            with self.subTest(ctf.name):
                with open(ctf / 'usbdata.txt') as f, open(ctf / 'output-sim-cmd.txt') as g:
                    expected = g.read()
                    keypresses = decode_keypresses(f.read())
                    output = simulate_keypresses(keypresses, text_mode=False)
                    self.assertEqual(expected, output, f'Decoded keypresses do not match expected output\n{error_message.format(expected=expected, output=output)}')


if __name__ == '__main__':
    unittest.main()
