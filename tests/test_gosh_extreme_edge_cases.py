"""
Comprehensive edge case tests for gosh fuzzy matching and bookmark handling.
Tests extreme inputs, Unicode, emoji, malicious inputs, and boundary conditions.
"""

import sys
import unittest
from pathlib import Path
from difflib import SequenceMatcher

REPO_ROOT = Path(__file__).resolve().parents[1]
source = (REPO_ROOT / "gosh" / "gosh2.py").read_text(encoding="utf-8")
module_source = source.rsplit("\nmain()", 1)[0]
exec_globals = {"__file__": str(REPO_ROOT / "gosh" / "gosh2.py"), "__name__": "gosh2_test_module"}
exec(module_source, exec_globals)

fuzzy_score = exec_globals["fuzzy_score"]
find_best_match = exec_globals["find_best_match"]


class TestFuzzyScoreExtremeInputs(unittest.TestCase):
    """Test fuzzy_score with extreme, invalid, and edge case inputs."""

    def test_extremely_long_bookmark_name(self):
        """Test with bookmark name of 10000+ characters."""
        long_name = "saturno-" + "x" * 10000
        score = fuzzy_score(long_name, "saturno")
        self.assertGreater(score, 0)

    def test_extremely_long_query(self):
        """Test with query of 10000+ characters."""
        long_query = "a" * 10000
        score = fuzzy_score("repos", long_query)
        self.assertGreaterEqual(score, 0)

    def test_empty_name_empty_query(self):
        """Test with both name and query empty."""
        score = fuzzy_score("", "")
        self.assertGreaterEqual(score, 0)

    def test_empty_name_nonempty_query(self):
        """Test with empty name but non-empty query."""
        score = fuzzy_score("", "query")
        self.assertEqual(score, 0)

    def test_nonempty_name_empty_query(self):
        """Test with non-empty name but empty query."""
        score = fuzzy_score("name", "")
        self.assertGreaterEqual(score, 0)

    def test_unicode_emoji_in_name(self):
        """Test with emoji in bookmark name."""
        score = fuzzy_score("🚀rocket-project", "rocket")
        self.assertGreater(score, 0)

    def test_unicode_emoji_in_query(self):
        """Test with emoji in query."""
        score = fuzzy_score("rocket-project", "🚀rocket")
        self.assertGreaterEqual(score, 0)

    def test_unicode_emoji_exact_match(self):
        """Test exact match with emoji."""
        score = fuzzy_score("🎯target🎯", "🎯target🎯")
        self.assertEqual(score, 100000)

    def test_chinese_characters(self):
        """Test with Chinese characters."""
        score = fuzzy_score("项目-project", "项目")
        self.assertGreater(score, 0)

    def test_japanese_characters(self):
        """Test with Japanese characters."""
        score = fuzzy_score("プロジェクト-project", "プロジェクト")
        self.assertGreater(score, 0)

    def test_arabic_characters(self):
        """Test with Arabic characters."""
        score = fuzzy_score("مشروع-project", "مشروع")
        self.assertGreater(score, 0)

    def test_cyrillic_characters(self):
        """Test with Cyrillic characters."""
        score = fuzzy_score("проект-project", "проект")
        self.assertGreater(score, 0)

    def test_mixed_unicode_scripts(self):
        """Test with mixed Unicode scripts."""
        score = fuzzy_score("🚀проект-项目-プロジェクト", "проект")
        self.assertGreater(score, 0)

    def test_zero_width_characters(self):
        """Test with zero-width Unicode characters."""
        name_with_zwj = "pro‍ject"  # Zero-width joiner
        score = fuzzy_score(name_with_zwj, "project")
        self.assertGreaterEqual(score, 0)

    def test_combining_characters(self):
        """Test with Unicode combining characters."""
        name_with_combining = "café"  # é = e + combining accent
        score = fuzzy_score(name_with_combining, "cafe")
        self.assertGreaterEqual(score, 0)

    def test_right_to_left_marks(self):
        """Test with RTL direction marks."""
        name_with_rtl = "project‮"  # Right-to-left override
        score = fuzzy_score(name_with_rtl, "project")
        self.assertGreater(score, 0)

    def test_null_bytes_in_name(self):
        """Test with null bytes in name."""
        name_with_null = "pro\x00ject"
        score = fuzzy_score(name_with_null, "project")
        self.assertGreaterEqual(score, 0)

    def test_null_bytes_in_query(self):
        """Test with null bytes in query."""
        query_with_null = "pro\x00ject"
        score = fuzzy_score("project", query_with_null)
        self.assertGreaterEqual(score, 0)

    def test_newline_in_name(self):
        """Test with newline in name."""
        score = fuzzy_score("pro\nject", "project")
        self.assertGreaterEqual(score, 0)

    def test_newline_in_query(self):
        """Test with newline in query."""
        score = fuzzy_score("project", "pro\nject")
        self.assertGreaterEqual(score, 0)

    def test_tab_in_name(self):
        """Test with tab character in name."""
        score = fuzzy_score("pro\tject", "project")
        self.assertGreaterEqual(score, 0)

    def test_tab_in_query(self):
        """Test with tab character in query."""
        score = fuzzy_score("project", "pro\tject")
        self.assertGreaterEqual(score, 0)

    def test_carriage_return_in_name(self):
        """Test with carriage return in name."""
        score = fuzzy_score("pro\rject", "project")
        self.assertGreaterEqual(score, 0)

    def test_vertical_tab_in_query(self):
        """Test with vertical tab in query."""
        score = fuzzy_score("project", "pro\vject")
        self.assertGreaterEqual(score, 0)

    def test_form_feed_in_name(self):
        """Test with form feed character."""
        score = fuzzy_score("pro\fject", "project")
        self.assertGreaterEqual(score, 0)

    def test_all_whitespace_name(self):
        """Test with name containing only whitespace."""
        score = fuzzy_score("   \t\n\r  ", "query")
        self.assertGreaterEqual(score, 0)

    def test_all_whitespace_query(self):
        """Test with query containing only whitespace."""
        score = fuzzy_score("name", "   \t\n\r  ")
        self.assertGreaterEqual(score, 0)

    def test_control_characters_in_name(self):
        """Test with control characters in name."""
        name_with_control = "pro\x01\x02\x03ject"
        score = fuzzy_score(name_with_control, "project")
        self.assertGreaterEqual(score, 0)

    def test_control_characters_in_query(self):
        """Test with control characters in query."""
        query_with_control = "pro\x01\x02\x03ject"
        score = fuzzy_score("project", query_with_control)
        self.assertGreaterEqual(score, 0)

    def test_backspace_characters(self):
        """Test with backspace characters."""
        score = fuzzy_score("project\b\b\b", "project")
        self.assertGreater(score, 0)

    def test_escape_sequences(self):
        """Test with ANSI escape sequences."""
        name_with_escape = "\x1b[31mproject\x1b[0m"
        score = fuzzy_score(name_with_escape, "project")
        self.assertGreaterEqual(score, 0)

    def test_sql_injection_attempt_in_name(self):
        """Test with SQL injection patterns in name."""
        malicious_name = "project'; DROP TABLE bookmarks;--"
        score = fuzzy_score(malicious_name, "project")
        self.assertGreater(score, 0)

    def test_sql_injection_attempt_in_query(self):
        """Test with SQL injection patterns in query."""
        malicious_query = "'; DROP TABLE bookmarks;--"
        score = fuzzy_score("project", malicious_query)
        self.assertGreaterEqual(score, 0)

    def test_xss_attempt_in_name(self):
        """Test with XSS patterns in name."""
        xss_name = "<script>alert('xss')</script>"
        score = fuzzy_score(xss_name, "script")
        self.assertGreater(score, 0)

    def test_xss_attempt_in_query(self):
        """Test with XSS patterns in query."""
        xss_query = "<script>alert('xss')</script>"
        score = fuzzy_score("project", xss_query)
        self.assertGreaterEqual(score, 0)

    def test_path_traversal_in_name(self):
        """Test with path traversal patterns."""
        path_traversal = "../../etc/passwd"
        score = fuzzy_score(path_traversal, "etc")
        self.assertGreater(score, 0)

    def test_command_injection_in_query(self):
        """Test with command injection patterns."""
        cmd_injection = "project; rm -rf /"
        score = fuzzy_score("project", cmd_injection)
        self.assertGreaterEqual(score, 0)

    def test_format_string_attack(self):
        """Test with format string patterns."""
        format_string = "project%s%s%s%s"
        score = fuzzy_score(format_string, "project")
        self.assertGreater(score, 0)

    def test_ldap_injection(self):
        """Test with LDAP injection patterns."""
        ldap_injection = "project*)(uid=*))(|(uid=*"
        score = fuzzy_score(ldap_injection, "project")
        self.assertGreater(score, 0)

    def test_extremely_long_repeated_character(self):
        """Test with single character repeated 100000 times."""
        long_repeated = "a" * 100000
        score = fuzzy_score(long_repeated, "a" * 50000)
        # Score can be negative due to length penalty in implementation
        self.assertIsInstance(score, int)

    def test_unicode_normalization_different_forms(self):
        """Test with different Unicode normalization forms."""
        # é as single character vs composed
        name_nfc = "café"  # NFC form
        name_nfd = "café"  # NFD form
        score1 = fuzzy_score(name_nfc, "cafe")
        score2 = fuzzy_score(name_nfd, "cafe")
        self.assertGreaterEqual(score1, 0)
        self.assertGreaterEqual(score2, 0)

    def test_supplementary_unicode_planes(self):
        """Test with characters from supplementary Unicode planes."""
        # Mathematical Alphanumeric Symbols
        fancy_name = "𝓹𝓻𝓸𝓳𝓮𝓬𝓽"
        score = fuzzy_score(fancy_name, "project")
        self.assertGreaterEqual(score, 0)

    def test_mixed_case_extreme(self):
        """Test with extreme mixed case patterns."""
        mixed_case = "PrOjEcT-nAmE"
        score = fuzzy_score(mixed_case, "project-name")
        self.assertGreater(score, 0)

    def test_repeated_separators(self):
        """Test with many repeated separators."""
        many_dashes = "project-------name-------test"
        score = fuzzy_score(many_dashes, "projectnametest")
        self.assertGreater(score, 0)

    def test_only_punctuation_name(self):
        """Test with name containing only punctuation."""
        punctuation_only = "!@#$%^&*()"
        score = fuzzy_score(punctuation_only, "!")
        self.assertGreater(score, 0)

    def test_only_punctuation_query(self):
        """Test with query containing only punctuation."""
        score = fuzzy_score("project-name", "!@#$%")
        self.assertEqual(score, 0)

    def test_numeric_overflow_attempt(self):
        """Test with extremely large numbers."""
        huge_number = "project" + "9" * 1000
        score = fuzzy_score(huge_number, "project")
        self.assertGreater(score, 0)

    def test_surrogate_pairs(self):
        """Test with Unicode surrogate pairs."""
        # Emoji with skin tone modifier
        emoji_with_modifier = "👨🏽‍💻project"
        score = fuzzy_score(emoji_with_modifier, "project")
        self.assertGreater(score, 0)

    def test_bidirectional_text(self):
        """Test with bidirectional text (LTR and RTL)."""
        bidi_text = "project-مشروع-project"
        score = fuzzy_score(bidi_text, "project")
        self.assertGreater(score, 0)


class TestFindBestMatchExtremeEdgeCases(unittest.TestCase):
    """Test find_best_match with extreme and edge case inputs."""

    def test_empty_bookmarks_dict(self):
        """Test with empty bookmarks dictionary."""
        result = find_best_match({}, "query")
        self.assertIsNone(result)

    def test_single_bookmark_exact_match(self):
        """Test with single bookmark, exact match."""
        bookmarks = {"project": {}}
        result = find_best_match(bookmarks, "project")
        self.assertEqual(result, "project")

    def test_single_bookmark_no_match(self):
        """Test with single bookmark, no match."""
        bookmarks = {"project": {}}
        result = find_best_match(bookmarks, "zzzzz")
        self.assertIsNone(result)

    def test_bookmarks_with_emoji_names(self):
        """Test with bookmarks containing emoji."""
        bookmarks = {
            "🚀rocket": {},
            "⭐star": {},
            "🎯target": {},
            "🔥fire": {},
            "💻code": {}
        }
        result = find_best_match(bookmarks, "rocket")
        self.assertEqual(result, "🚀rocket")

    def test_bookmarks_with_all_emoji_names(self):
        """Test with bookmarks that are only emoji."""
        bookmarks = {
            "🚀": {},
            "⭐": {},
            "🎯": {}
        }
        result = find_best_match(bookmarks, "🚀")
        self.assertEqual(result, "🚀")

    def test_bookmarks_with_unicode_names(self):
        """Test with bookmarks containing various Unicode scripts."""
        bookmarks = {
            "项目-chinese": {},
            "プロジェクト-japanese": {},
            "проект-russian": {},
            "مشروع-arabic": {},
            "projeto-portuguese": {}
        }
        result = find_best_match(bookmarks, "chinese")
        self.assertEqual(result, "项目-chinese")

    def test_bookmarks_with_very_similar_names(self):
        """Test with bookmarks that differ by one character."""
        bookmarks = {
            "project": {},
            "projects": {},
            "project1": {},
            "project2": {},
            "project-": {},
            "_project": {}
        }
        result = find_best_match(bookmarks, "project")
        self.assertEqual(result, "project")

    def test_bookmarks_with_identical_lowercase_names(self):
        """Test with bookmarks that are identical when lowercased."""
        bookmarks = {
            "Project": {},
            "PROJECT": {},
            "project": {},
            "pRoJeCt": {}
        }
        result = find_best_match(bookmarks, "project")
        self.assertEqual(result, "project")

    def test_extremely_large_bookmark_set(self):
        """Test with 10000 bookmarks."""
        bookmarks = {f"project-{i}": {} for i in range(10000)}
        bookmarks["target-project"] = {}
        result = find_best_match(bookmarks, "target")
        self.assertEqual(result, "target-project")

    def test_query_with_only_whitespace(self):
        """Test with query containing only whitespace."""
        bookmarks = {"project": {}, "repos": {}}
        result = find_best_match(bookmarks, "   \t\n  ")
        self.assertIsNone(result)

    def test_query_with_leading_trailing_whitespace(self):
        """Test with query having leading/trailing whitespace."""
        bookmarks = {"project": {}, "repos": {}}
        result = find_best_match(bookmarks, "  project  ")
        # Depends on implementation - may or may not strip
        self.assertIn(result, ["project", None])

    def test_bookmarks_with_null_bytes(self):
        """Test with bookmarks containing null bytes."""
        bookmarks = {"pro\x00ject": {}, "repos": {}}
        result = find_best_match(bookmarks, "project")
        self.assertIsInstance(result, (str, type(None)))

    def test_bookmarks_with_newlines(self):
        """Test with bookmarks containing newlines."""
        bookmarks = {"pro\nject": {}, "repos": {}}
        result = find_best_match(bookmarks, "project")
        self.assertIsInstance(result, (str, type(None)))

    def test_query_with_sql_injection(self):
        """Test with SQL injection in query."""
        bookmarks = {"project": {}, "repos": {}}
        malicious_query = "project'; DROP TABLE bookmarks;--"
        result = find_best_match(bookmarks, malicious_query)
        # Should safely return a result or None
        self.assertIsInstance(result, (str, type(None)))

    def test_query_with_xss_attempt(self):
        """Test with XSS attempt in query."""
        bookmarks = {"project": {}, "script": {}}
        xss_query = "<script>alert('xss')</script>"
        result = find_best_match(bookmarks, xss_query)
        self.assertIsInstance(result, (str, type(None)))

    def test_query_with_path_traversal(self):
        """Test with path traversal in query."""
        bookmarks = {"etc": {}, "passwd": {}, "project": {}}
        result = find_best_match(bookmarks, "../../etc/passwd")
        self.assertIsInstance(result, (str, type(None)))

    def test_query_with_unicode_confusables(self):
        """Test with Unicode confusable characters."""
        bookmarks = {"project": {}}
        # Using Cyrillic 'о' instead of Latin 'o'
        confusable_query = "prоject"  # Has Cyrillic о
        result = find_best_match(bookmarks, confusable_query)
        self.assertIsInstance(result, (str, type(None)))

    def test_bookmarks_with_homoglyphs(self):
        """Test with bookmarks containing homoglyphs."""
        bookmarks = {
            "project": {},      # Latin
            "prоject": {},      # With Cyrillic о
            "рroject": {}       # With Cyrillic р
        }
        result = find_best_match(bookmarks, "project")
        self.assertEqual(result, "project")

    def test_query_with_zero_width_characters(self):
        """Test with zero-width characters in query."""
        bookmarks = {"project": {}, "repos": {}}
        query_with_zwj = "pro‍ject"
        result = find_best_match(bookmarks, query_with_zwj)
        self.assertIsInstance(result, (str, type(None)))

    def test_bookmarks_with_combining_characters(self):
        """Test with bookmarks having combining characters."""
        bookmarks = {
            "café": {},
            "naïve": {},
            "résumé": {}
        }
        result = find_best_match(bookmarks, "cafe")
        self.assertIsInstance(result, (str, type(None)))

    def test_query_with_rtl_override(self):
        """Test with RTL override character in query."""
        bookmarks = {"project": {}, "repos": {}}
        query_with_rtl = "project‮"
        result = find_best_match(bookmarks, query_with_rtl)
        self.assertIsInstance(result, (str, type(None)))

    def test_bookmarks_with_control_characters(self):
        """Test with control characters in bookmark names."""
        bookmarks = {
            "pro\x01ject": {},
            "re\x02pos": {},
            "code\x03": {}
        }
        result = find_best_match(bookmarks, "project")
        self.assertIsInstance(result, (str, type(None)))

    def test_query_with_ansi_escape_sequences(self):
        """Test with ANSI escape sequences in query."""
        bookmarks = {"project": {}, "repos": {}}
        ansi_query = "\x1b[31mproject\x1b[0m"
        result = find_best_match(bookmarks, ansi_query)
        self.assertIsInstance(result, (str, type(None)))

    def test_bookmarks_all_single_character(self):
        """Test with single-character bookmark names."""
        bookmarks = {"a": {}, "b": {}, "c": {}, "d": {}, "e": {}}
        result = find_best_match(bookmarks, "a")
        self.assertEqual(result, "a")

    def test_query_single_character_many_matches(self):
        """Test single char query matching many bookmarks."""
        bookmarks = {
            "project": {},
            "python": {},
            "perl": {},
            "php": {},
            "pascal": {}
        }
        result = find_best_match(bookmarks, "p")
        self.assertIn(result, ["python", "perl", "php", "pascal", "project"])

    def test_bookmarks_with_numbers_only(self):
        """Test with bookmarks containing only numbers."""
        bookmarks = {
            "12345": {},
            "67890": {},
            "11111": {}
        }
        result = find_best_match(bookmarks, "123")
        self.assertEqual(result, "12345")

    def test_query_with_floating_point_number(self):
        """Test with floating point number as query."""
        bookmarks = {"3.14159": {}, "2.71828": {}}
        result = find_best_match(bookmarks, "3.14")
        self.assertEqual(result, "3.14159")

    def test_bookmarks_with_scientific_notation(self):
        """Test with scientific notation in bookmarks."""
        bookmarks = {"1e10": {}, "2.5e-3": {}, "project": {}}
        result = find_best_match(bookmarks, "1e")
        self.assertEqual(result, "1e10")

    def test_bookmarks_with_hexadecimal(self):
        """Test with hexadecimal strings."""
        bookmarks = {"0x1234": {}, "0xABCD": {}, "0xDEADBEEF": {}}
        result = find_best_match(bookmarks, "0xDE")
        self.assertEqual(result, "0xDEADBEEF")

    def test_bookmarks_with_url_encoded_characters(self):
        """Test with URL-encoded characters."""
        bookmarks = {
            "project%20name": {},
            "repos%2Fcode": {},
            "file%3Apath": {}
        }
        result = find_best_match(bookmarks, "project")
        self.assertEqual(result, "project%20name")

    def test_bookmarks_with_html_entities(self):
        """Test with HTML entities."""
        bookmarks = {
            "project&amp;name": {},
            "repos&lt;code&gt;": {},
            "file&quot;path": {}
        }
        result = find_best_match(bookmarks, "project")
        self.assertEqual(result, "project&amp;name")

    def test_query_with_regex_metacharacters(self):
        """Test with regex metacharacters in query."""
        bookmarks = {"project": {}, "repos": {}}
        regex_query = "proj.*ect$"
        result = find_best_match(bookmarks, regex_query)
        self.assertIsInstance(result, (str, type(None)))

    def test_bookmarks_with_glob_patterns(self):
        """Test with glob-like patterns in names."""
        bookmarks = {
            "project*": {},
            "repos?": {},
            "code[123]": {}
        }
        result = find_best_match(bookmarks, "project")
        self.assertEqual(result, "project*")

    def test_extremely_long_prefix_match(self):
        """Test with very long common prefix."""
        long_prefix = "a" * 5000
        bookmarks = {
            long_prefix + "-first": {},
            long_prefix + "-second": {},
            "short": {}
        }
        result = find_best_match(bookmarks, long_prefix)
        self.assertIn(result, [long_prefix + "-first", long_prefix + "-second"])

    def test_bookmarks_with_backslashes(self):
        """Test with Windows-style paths."""
        bookmarks = {
            "C:\\Users\\Project": {},
            "D:\\repos\\code": {},
            "/usr/local/bin": {}
        }
        result = find_best_match(bookmarks, "Project")
        self.assertEqual(result, "C:\\Users\\Project")

    def test_bookmarks_with_forward_slashes(self):
        """Test with Unix-style paths."""
        bookmarks = {
            "/home/user/project": {},
            "/var/log/system": {},
            "/usr/bin/code": {}
        }
        result = find_best_match(bookmarks, "project")
        self.assertEqual(result, "/home/user/project")

    def test_case_sensitivity_edge_cases(self):
        """Test various case sensitivity scenarios."""
        bookmarks = {
            "PROJECT": {},
            "Project": {},
            "project": {},
            "pRoJeCt": {},
            "PrOjEcT": {}
        }
        result = find_best_match(bookmarks, "PROJECT")
        self.assertEqual(result, "PROJECT")

    def test_accented_character_variations(self):
        """Test with various accented character forms."""
        bookmarks = {
            "café": {},
            "cafe": {},
            "cafè": {},
            "cafê": {},
            "cafë": {}
        }
        result = find_best_match(bookmarks, "cafe")
        self.assertEqual(result, "cafe")

    def test_ligature_characters(self):
        """Test with ligature characters."""
        bookmarks = {
            "ﬁle": {},  # fi ligature
            "ﬂag": {},  # fl ligature
            "file": {},
            "flag": {}
        }
        result = find_best_match(bookmarks, "file")
        self.assertEqual(result, "file")


class TestBookmarkNameEdgeCases(unittest.TestCase):
    """Test edge cases specific to bookmark naming conventions."""

    def test_bookmark_with_multiple_dots(self):
        """Test bookmark with multiple dots (domain-like)."""
        bookmarks = {"com.example.project.main": {}}
        result = find_best_match(bookmarks, "project")
        self.assertEqual(result, "com.example.project.main")

    def test_bookmark_with_version_numbers(self):
        """Test bookmark with version numbers."""
        bookmarks = {
            "project-v1.0.0": {},
            "project-v2.5.3": {},
            "project-v10.0.0": {}
        }
        result = find_best_match(bookmarks, "project")
        self.assertEqual(result, "project-v1.0.0")

    def test_bookmark_with_dates(self):
        """Test bookmark with date stamps."""
        bookmarks = {
            "project-2024-01-15": {},
            "project-2024-12-31": {},
            "repos-2025-06-01": {}
        }
        result = find_best_match(bookmarks, "2024")
        self.assertIn(result, ["project-2024-01-15", "project-2024-12-31"])

    def test_bookmark_with_timestamps(self):
        """Test bookmark with full timestamps."""
        bookmarks = {
            "backup-20240115-143000": {},
            "backup-20240116-090000": {}
        }
        result = find_best_match(bookmarks, "20240115")
        self.assertEqual(result, "backup-20240115-143000")

    def test_bookmark_with_git_branches(self):
        """Test bookmark with git branch-like names."""
        bookmarks = {
            "feature/new-ui": {},
            "bugfix/crash-issue": {},
            "hotfix/security-patch": {}
        }
        result = find_best_match(bookmarks, "feature")
        self.assertEqual(result, "feature/new-ui")

    def test_bookmark_with_namespaces(self):
        """Test bookmark with namespace-like structure."""
        bookmarks = {
            "@company/project-name": {},
            "@team/another-project": {},
            "@org/tool": {}
        }
        result = find_best_match(bookmarks, "company")
        self.assertEqual(result, "@company/project-name")


if __name__ == "__main__":
    unittest.main(verbosity=2)
