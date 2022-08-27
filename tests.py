'''
Test decoding scripts against expected output
'''
import unittest
from pathlib import Path
from keyboard_decode import decode_keypresses


root = Path('.')
border_length = 40
error_message = '''{top_rule}
Expected
{mid_rule}
{{expected}}
{top_rule}
Decoded
{mid_rule}
{{decoded}}
'''.format(top_rule='~' * border_length, mid_rule='-' * border_length)


class KeyboardTest(unittest.TestCase):
    def setUp(self):
        self.longMessage = False

    def test_raw_output(self):
        for ctf in (root / 'samples' / 'keyboard').iterdir():
            with self.subTest(ctf.name):
                with open(ctf / 'usbdata.txt') as f, open(ctf / 'output-raw.txt') as g:
                    expected = g.read()
                    decoded = decode_keypresses(f.read())
                    self.assertEqual(expected, decoded, f'Decoded keypresses do not match expected output\n{error_message.format(expected=expected, decoded=decoded)}')
    
    def test_simulated_output(self):
        for ctf in (root / 'samples' / 'keyboard').iterdir():
            with self.subTest(ctf.name):
                with open(ctf / 'usbdata.txt') as f, open(ctf / 'output-simulated.txt') as g:
                    self.assertEqual(decode_keypresses(f.read(), simulate=True), g.read())


if __name__ == '__main__':
    unittest.main()
