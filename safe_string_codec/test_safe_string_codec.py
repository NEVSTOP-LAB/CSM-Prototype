import unittest

from safe_string_codec import make_string_arguments_safe, revert_arguments_safe_string


class SafeStringCodecTests(unittest.TestCase):
    def test_package_level_imports_are_available(self):
        self.assertEqual(make_string_arguments_safe.__name__, "make_string_arguments_safe")
        self.assertEqual(
            revert_arguments_safe_string.__name__, "revert_arguments_safe_string"
        )

    def test_empty_string(self):
        self.assertEqual(make_string_arguments_safe("", ignore_argument_type=True), "")
        self.assertEqual(revert_arguments_safe_string("", force_convert=True), "")

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
        safe = make_string_arguments_safe(original, ignore_argument_type=True)
        self.assertEqual(safe, original)
        self.assertEqual(revert_arguments_safe_string(safe, force_convert=True), original)

    def test_csm_keyword_characters_are_encoded(self):
        original = "->| -@ -& <-\r\n// >> >>> ;,"
        safe = make_string_arguments_safe(original, ignore_argument_type=True)
        self.assertNotIn("->", safe)
        self.assertNotIn(">>", safe)
        self.assertNotEqual(safe, original)
        self.assertEqual(revert_arguments_safe_string(safe, force_convert=True), original)

    def test_percent_character_is_always_encoded(self):
        original = "%"
        safe = make_string_arguments_safe(original, ignore_argument_type=True)
        self.assertEqual(safe, "%25")
        self.assertEqual(revert_arguments_safe_string(safe, force_convert=True), original)

    def test_unicode_chinese_and_emoji(self):
        original = "中文😀"
        safe = make_string_arguments_safe(original, ignore_argument_type=True)
        self.assertEqual(revert_arguments_safe_string(safe, force_convert=True), original)

    def test_unicode_with_adjacent_keywords(self):
        original = "前缀->中文😀//后缀"
        safe = make_string_arguments_safe(original, ignore_argument_type=True)
        self.assertNotIn("->", safe)
        self.assertNotIn("//", safe)
        self.assertEqual(revert_arguments_safe_string(safe, force_convert=True), original)

    def test_control_and_null_characters(self):
        original = "line1\nline2\t\x00end"
        safe = make_string_arguments_safe(original, ignore_argument_type=True)
        self.assertEqual(revert_arguments_safe_string(safe, force_convert=True), original)

    def test_long_mixed_string(self):
        original = "A" * 1000 + "🚀" + "\x00" + "終"
        safe = make_string_arguments_safe(original, ignore_argument_type=True)
        self.assertEqual(revert_arguments_safe_string(safe, force_convert=True), original)

    def test_roundtrip_for_all_ascii_values(self):
        original = "".join(chr(i) for i in range(128))
        safe = make_string_arguments_safe(original, ignore_argument_type=True)
        restored = revert_arguments_safe_string(safe, force_convert=True)
        self.assertEqual(restored, original)

    def test_decode_rejects_incomplete_escape(self):
        with self.assertRaises(ValueError):
            revert_arguments_safe_string("abc%", force_convert=True)

    def test_decode_rejects_bad_hex(self):
        with self.assertRaises(ValueError):
            revert_arguments_safe_string("abc%G1", force_convert=True)

    def test_type_errors(self):
        with self.assertRaises(TypeError):
            make_string_arguments_safe(None)  # type: ignore[arg-type]
        with self.assertRaises(TypeError):
            revert_arguments_safe_string(None)  # type: ignore[arg-type]
        with self.assertRaises(TypeError):
            make_string_arguments_safe("ok", ignore_argument_type=None)  # type: ignore[arg-type]
        with self.assertRaises(TypeError):
            revert_arguments_safe_string("ok", force_convert=None)  # type: ignore[arg-type]


if __name__ == "__main__":
    unittest.main()
