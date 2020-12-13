import unittest

from bot.cogs.gsuite import GSuite

# TODO write dummy structures for these below:
# class DummyMessage:
# class DummyBot:
#      pass

class TestGSuiteCog(unittest.TestCase):
    def test_create_command_parse(self):
        self.assertEqual("foo".upper(), "FOO")

    def test_create_command_embed(self):
        self.assertTrue("FOO".isupper())
        self.assertFalse("Foo".isupper())

    def test_split(self):
        s = "hello world"
        self.assertEqual(s.split(), ["hello", "world"])
        # check that s.split fails when the separator is not a string
        with self.assertRaises(TypeError):
            s.split(2)


if __name__ == "__main__":
    unittest.main()
