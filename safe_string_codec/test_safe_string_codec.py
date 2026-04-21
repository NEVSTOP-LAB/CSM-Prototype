import unittest

from safe_string_codec.safe_string_codec import from_safe_string, to_safe_string


class SafeStringCodecTests(unittest.TestCase):
    def test_empty_string(self):
        self.assertEqual(to_safe_string(""), "")
        self.assertEqual(from_safe_string(""), "")

    def test_ascii_unreserved_kept(self):
        original = "AbcXYZ019-_."
        safe = to_safe_string(original)
        self.assertEqual(safe, original)
        self.assertEqual(from_safe_string(safe), original)

    def test_special_characters_are_encoded(self):
        original = "a b/c?d=e&f#g"
        safe = to_safe_string(original)
        self.assertNotEqual(safe, original)
        self.assertEqual(from_safe_string(safe), original)

    def test_escape_character_is_always_encoded(self):
        original = "~"
        safe = to_safe_string(original)
        self.assertEqual(safe, "~7E")
        self.assertEqual(from_safe_string(safe), original)

    def test_unicode_chinese_and_emoji(self):
        original = "中文😀"
        safe = to_safe_string(original)
        self.assertEqual(from_safe_string(safe), original)

    def test_control_and_null_characters(self):
        original = "line1\nline2\t\x00end"
        safe = to_safe_string(original)
        self.assertEqual(from_safe_string(safe), original)

    def test_long_mixed_string(self):
        original = "A" * 1000 + "🚀" + "\x00" + "終"
        safe = to_safe_string(original)
        self.assertEqual(from_safe_string(safe), original)

    def test_lone_surrogate_preserved(self):
        original = "\ud800"
        safe = to_safe_string(original)
        restored = from_safe_string(safe)
        self.assertEqual(restored, original)

    def test_roundtrip_for_all_byte_values(self):
        original = bytes(range(256)).decode("latin1")
        safe = to_safe_string(original)
        restored = from_safe_string(safe)
        self.assertEqual(restored, original)

    def test_decode_rejects_incomplete_escape(self):
        with self.assertRaises(ValueError):
            from_safe_string("abc~")

    def test_decode_rejects_bad_hex(self):
        with self.assertRaises(ValueError):
            from_safe_string("abc~G1")

    def test_decode_rejects_unexpected_character(self):
        with self.assertRaises(ValueError):
            from_safe_string("abc def")

    def test_type_errors(self):
        with self.assertRaises(TypeError):
            to_safe_string(None)  # type: ignore[arg-type]
        with self.assertRaises(TypeError):
            from_safe_string(None)  # type: ignore[arg-type]


if __name__ == "__main__":
    unittest.main()
