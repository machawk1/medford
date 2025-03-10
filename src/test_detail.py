import unittest

from medford_detail import *

class TestDetailMethods(unittest.TestCase) :
    def setUp(self) :
        detail._clear_cache()

    def test_detail_simple(self) :
        example_line = "@Date 02/24"
        dr = detail.FromLine(example_line, -1, None)
        d = dr.detail
        self.assertListEqual(d.Major_Tokens, ["Date"])
        self.assertEqual(d.Minor_Token, "desc")
        self.assertEqual(d.Data, "02/24")

    def test_detail_ordinary(self) :
        example_line = "@Date-Note Samples Obtained"
        dr = detail.FromLine(example_line, -1, None)
        d = dr.detail
        self.assertListEqual(d.Major_Tokens, ["Date"])
        self.assertEqual(d.Minor_Token, "Note")
        self.assertEqual(d.Data, "Samples Obtained")
    
    def test_detail_2_level_recursive(self) :
        example_line = "@Freeform_Date-Note Samples Obtained"
        dr = detail.FromLine(example_line, -1, None)
        d = dr.detail
        self.assertListEqual(d.Major_Tokens, ["Freeform","Date"])
        self.assertEqual(d.Minor_Token, "Note")
        self.assertEqual(d.Data, "Samples Obtained")
    
    def test_recognizes_template(self) :
        example_line = "@Date-Note [...]"
        with self.assertRaises(ValueError) :
            detail.FromLine(example_line, -1, None)

    def test_detail_multiline(self) :
        example_line_1 = "@Date-Note asdf "
        example_line_2 = "More asdf"
        dr = detail.FromLine(example_line_1, -1, None)
        dr = detail.FromLine(example_line_2, -1, dr)
        self.assertEqual(dr.detail.Data, "asdf More asdf")

    # Tests for Macro functionality.
    def test_add_macro(self) :
        example_line = "`@macro_name macro body"
        dr = detail.FromLine(example_line, -1, None)
        self.assertListEqual(list(detail.macro_dictionary.keys()), ["macro_name"])

    def test_add_multiple_macros(self) :
        example_line = "`@macro_name macro body"
        example_line_2 = "`@macro_name_2 macro body"
        dr = detail.FromLine(example_line, -1, None)
        detail.FromLine(example_line_2, -1, dr)
        self.assertListEqual(list(detail.macro_dictionary.keys()), ["macro_name", "macro_name_2"])

    def test_add_same_macro_name(self) :
        example_line = "`@macro_name macro body"
        example_line_2 = "`@macro_name macro body"
        with self.assertRaises(ValueError) :
            dr = detail.FromLine(example_line, -1, None)
            detail.FromLine(example_line_2, -1, dr)
    
    def test_correctly_substitutes_macro(self) :
        example_line = "`@macro_name macro body"
        example_line_2 = "@major-minor text `@macro_name"
        dr = detail.FromLine(example_line, -1, None)
        dr = detail.FromLine(example_line_2, -1, dr)
        self.assertEqual(dr.detail.Data, "text macro body")

    def test_correctly_substitutes_macro_with_stuff_after(self) :
        example_line = "`@macro_name macro body"
        example_line_2 = "@major-minor text `@macro_name asdf asdf asdf"
        dr = detail.FromLine(example_line, -1, None)
        dr = detail.FromLine(example_line_2, -1, dr)
        self.assertEqual(dr.detail.Data, "text macro body asdf asdf asdf")

    def test_accepts_multiline_macro(self) :
        example_line = "`@macro_name macro_body"
        example_line_2 = "macro_body_2"
        dr = detail.FromLine(example_line, -1, None)
        dr = detail.FromLine(example_line_2, -1, dr)
        self.assertListEqual(list(detail.macro_dictionary.keys()), ["macro_name"])
        self.assertEqual(detail.macro_dictionary[dr], "macro_body macro_body_2")

    def test_substitutes_multiline_macro(self) :
        macro_body_1 = "macro_body"
        macro_body_2 = "macro_body_2"
        example_line = "`@macro_name " + macro_body_1
        example_line_2 = macro_body_2
        example_line_3 = "@major-minor `@macro_name"

        dr = detail.FromLine(example_line, -1, None)
        dr = detail.FromLine(example_line_2, -1, dr)
        dr = detail.FromLine(example_line_3, -1, dr)
        self.assertEqual(dr.detail.Data, macro_body_1 + " " + macro_body_2)

    # Tests for Comment functionality
    def test_ignores_inline_in_macro(self) :
        example_line = "`@macro_name macro_body # this is a comment"
        dr = detail.FromLine(example_line, -1, None)
        self.assertEqual(detail.macro_dictionary[dr], "macro_body")


if __name__ == '__main__':
    unittest.main()