import unittest

from safe_string_codec import (
    from_safe_string,
    make_string_arguments_safe,
    revert_arguments_safe_string,
    to_safe_string,
)


class SafeStringCodecTests(unittest.TestCase):
    def test_package_level_imports_are_available(self):
        self.assertEqual(to_safe_string.__name__, "to_safe_string")
        self.assertEqual(from_safe_string.__name__, "from_safe_string")
        self.assertEqual(make_string_arguments_safe.__name__, "make_string_arguments_safe")
        self.assertEqual(
            revert_arguments_safe_string.__name__, "revert_arguments_safe_string"
        )

    def test_empty_string(self):
        self.assertEqual(to_safe_string(""), "")
        self.assertEqual(from_safe_string(""), "")

    def test_make_string_arguments_safe_default_adds_type_prefix(self):
        safe = make_string_arguments_safe("A->B")
        self.assertTrue(safe.startswith("<SAFESTR>"))
        self.assertEqual(revert_arguments_safe_string(safe), "A->B")

    def test_make_string_arguments_safe_ignore_type(self):
        safe = make_string_arguments_safe("A->B", ignore_argument_type=True)
        self.assertEqual(safe, "A%2D%3EB")

    def test_revert_without_force_and_without_prefix_keeps_input(self):
        self.assertEqual(revert_arguments_safe_string("A%2D%3EB"), "A%2D%3EB")

    def test_revert_force_convert_without_prefix_decodes(self):
        self.assertEqual(
            revert_arguments_safe_string("A%2D%3EB", force_convert=True), "A->B"
        )

    def test_ascii_alphanumeric_and_space_kept(self):
        original = "AbcXYZ019_. hello"
        safe = to_safe_string(original)
        self.assertEqual(safe, original)
        self.assertEqual(from_safe_string(safe), original)

    def test_csm_keyword_characters_are_encoded(self):
        original = "->| -@ -& <-\r\n// >> >>> ;,"
        safe = to_safe_string(original)
        self.assertNotIn("->", safe)
        self.assertNotIn(">>", safe)
        self.assertNotEqual(safe, original)
        self.assertEqual(from_safe_string(safe), original)

    def test_percent_character_is_always_encoded(self):
        original = "%"
        safe = to_safe_string(original)
        self.assertEqual(safe, "%25")
        self.assertEqual(from_safe_string(safe), original)

    def test_unicode_chinese_and_emoji(self):
        original = "中文😀"
        safe = to_safe_string(original)
        self.assertEqual(from_safe_string(safe), original)

    def test_unicode_with_adjacent_keywords(self):
        original = "前缀->中文😀//后缀"
        safe = to_safe_string(original)
        self.assertNotIn("->", safe)
        self.assertNotIn("//", safe)
        self.assertEqual(from_safe_string(safe), original)

    def test_control_and_null_characters(self):
        original = "line1\nline2\t\x00end"
        safe = to_safe_string(original)
        self.assertEqual(from_safe_string(safe), original)

    def test_long_mixed_string(self):
        original = "A" * 1000 + "🚀" + "\x00" + "終"
        safe = to_safe_string(original)
        self.assertEqual(from_safe_string(safe), original)

    def test_roundtrip_for_all_ascii_values(self):
        original = "".join(chr(i) for i in range(128))
        safe = to_safe_string(original)
        restored = from_safe_string(safe)
        self.assertEqual(restored, original)

    def test_decode_rejects_incomplete_escape(self):
        with self.assertRaises(ValueError):
            from_safe_string("abc%")

    def test_decode_rejects_bad_hex(self):
        with self.assertRaises(ValueError):
            from_safe_string("abc%G1")

    def test_type_errors(self):
        with self.assertRaises(TypeError):
            to_safe_string(None)  # type: ignore[arg-type]
        with self.assertRaises(TypeError):
            from_safe_string(None)  # type: ignore[arg-type]
        with self.assertRaises(TypeError):
            make_string_arguments_safe("ok", ignore_argument_type=None)  # type: ignore[arg-type]
        with self.assertRaises(TypeError):
            revert_arguments_safe_string("ok", force_convert=None)  # type: ignore[arg-type]


if __name__ == "__main__":
    unittest.main()
