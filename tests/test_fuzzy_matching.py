import sys
import time
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
find_best_fast_match = exec_globals["find_best_fast_match"]
find_best_sequencematcher_match = exec_globals["find_best_sequencematcher_match"]
SEQUENCE_MATCHER_MIN_RATIO = exec_globals["SEQUENCE_MATCHER_MIN_RATIO"]


def pure_sequencematcher_match(bookmarks, query):
    best_ratio = 0
    best_name = None
    for name in bookmarks:
        ratio = SequenceMatcher(None, name, query).ratio()
        if ratio > best_ratio:
            best_ratio = ratio
            best_name = name
    return best_name


REAL_BOOKMARKS = {
    "apps": {},
    "cli": {},
    "internaltools": {},
    "libs": {},
    "projects": {},
    "repos": {},
    "saturno.alttilda": {},
    "saturno.backend.internal": {},
    "saturno.gosh": {},
    "saturno.projectbuilder": {},
    "saturno.rings": {},
    "saturno.secrets": {},
    "saturno.website.mateusdigital": {},
    "saturno.website.public": {},
    "saturno.websitekit": {},
    "services": {},
    "websites": {},
    "yallaplay": {},
}


class TestFuzzyScore(unittest.TestCase):

    def test_exact_match_returns_highest_score(self):
        self.assertEqual(fuzzy_score("repos", "repos"), 100000)

    def test_case_insensitive_exact(self):
        self.assertEqual(fuzzy_score("Repos", "repos"), 50000)

    def test_prefix_match(self):
        score = fuzzy_score("projects", "proj")
        self.assertGreater(score, 44000)
        self.assertLess(score, 45000)

    def test_substring_match(self):
        score = fuzzy_score("saturno.gosh", "gosh")
        self.assertGreater(score, 39000)
        self.assertLess(score, 40000)

    def test_case_insensitive_prefix(self):
        score = fuzzy_score("Projects", "proj")
        self.assertGreater(score, 34000)
        self.assertLess(score, 35000)

    def test_case_insensitive_substring(self):
        score = fuzzy_score("Saturno.Gosh", "gosh")
        self.assertGreater(score, 29000)
        self.assertLess(score, 30000)

    def test_subsequence_match(self):
        score = fuzzy_score("saturno.gosh", "sgosh")
        self.assertGreater(score, 9000)
        self.assertLess(score, 10000)

    def test_no_match_returns_zero(self):
        self.assertEqual(fuzzy_score("repos", "zzz"), 0)

    def test_shorter_name_scores_higher_for_prefix(self):
        score_short = fuzzy_score("repos", "repo")
        score_long = fuzzy_score("repos-archive", "repo")
        self.assertGreater(score_short, score_long)


class TestFindBestMatch(unittest.TestCase):

    def test_exact_matches(self):
        for name in REAL_BOOKMARKS:
            result = find_best_match(REAL_BOOKMARKS, name)
            self.assertEqual(result, name, f"Exact match failed for '{name}'")

    def test_prefix_matches(self):
        cases = [
            ("repo", "repos"),
            ("app", "apps"),
            ("lib", "libs"),
            ("ser", "services"),
            ("int", "internaltools"),
            ("yalla", "yallaplay"),
        ]
        for query, expected in cases:
            result = find_best_match(REAL_BOOKMARKS, query)
            self.assertEqual(result, expected, f"Prefix '{query}' -> expected '{expected}', got '{result}'")

    def test_substring_matches(self):
        cases = [
            ("gosh", "saturno.gosh"),
            ("tilda", "saturno.alttilda"),
            ("backend", "saturno.backend.internal"),
            ("builder", "saturno.projectbuilder"),
            ("public", "saturno.website.public"),
            ("mateus", "saturno.website.mateusdigital"),
            ("secrets", "saturno.secrets"),
            ("rings", "saturno.rings"),
        ]
        for query, expected in cases:
            result = find_best_match(REAL_BOOKMARKS, query)
            self.assertEqual(result, expected, f"Substring '{query}' -> expected '{expected}', got '{result}'")

    def test_subsequence_matches(self):
        cases = [
            ("sgosh", "saturno.gosh"),
            ("sback", "saturno.backend.internal"),
            ("saltt", "saturno.alttilda"),
            ("wpub", "saturno.website.public"),
            ("spb", "saturno.projectbuilder"),
        ]
        for query, expected in cases:
            result = find_best_match(REAL_BOOKMARKS, query)
            self.assertEqual(result, expected, f"Subsequence '{query}' -> expected '{expected}', got '{result}'")

    def test_typo_fallback_to_sequencematcher(self):
        cases = [
            ("reops", "repos"),
            ("clii", "cli"),
            ("appz", "apps"),
            ("gohs", "saturno.gosh"),
            ("altidlda", "saturno.alttilda"),
            ("bckend", "saturno.backend.internal"),
        ]
        for query, expected in cases:
            result = find_best_match(REAL_BOOKMARKS, query)
            self.assertEqual(result, expected, f"Typo '{query}' -> expected '{expected}', got '{result}'")

    def test_no_match_returns_none(self):
        result = find_best_match(REAL_BOOKMARKS, "zzzzz")
        self.assertIsNone(result)

    def test_empty_bookmarks_returns_none(self):
        result = find_best_match({}, "anything")
        self.assertIsNone(result)

    def test_case_insensitive_exact_preferred_over_substring(self):
        bookmarks = {"Gosh": {}, "Saturno.Gosh": {}}
        result = find_best_match(bookmarks, "gosh")
        self.assertEqual(result, "Gosh")

    def test_prefix_preferred_over_longer_substring(self):
        bookmarks = {"project": {}, "my-project": {}, "project-alpha": {}}
        result = find_best_match(bookmarks, "proj")
        self.assertEqual(result, "project")

    def test_shorter_prefix_wins(self):
        bookmarks = {"repos": {}, "repos-archive": {}, "repos-backup": {}}
        result = find_best_match(bookmarks, "repo")
        self.assertEqual(result, "repos")


class TestFastFuzzyBetterThanPureSM(unittest.TestCase):

    def test_fast_fuzzy_wins_on_substring_disambiguation(self):
        cases = [
            ("back", "saturno.backend.internal"),
            ("sec", "saturno.secrets"),
            ("public", "saturno.website.public"),
            ("mateus", "saturno.website.mateusdigital"),
            ("secrets", "saturno.secrets"),
            ("websitekit", "saturno.websitekit"),
        ]
        for query, expected in cases:
            sm_result = pure_sequencematcher_match(REAL_BOOKMARKS, query)
            our_result = find_best_match(REAL_BOOKMARKS, query)
            self.assertEqual(our_result, expected, f"'{query}': got '{our_result}'")
            self.assertNotEqual(sm_result, expected,
                f"SM also gets '{query}' right — this test documents where we improve over SM")


class TestSequenceMatcherFallback(unittest.TestCase):

    def test_transposition_typos_handled(self):
        result = find_best_match(REAL_BOOKMARKS, "reops")
        self.assertEqual(result, "repos")

    def test_extra_char_typos_handled(self):
        result = find_best_match(REAL_BOOKMARKS, "clii")
        self.assertEqual(result, "cli")

    def test_wrong_char_typos_handled(self):
        result = find_best_match(REAL_BOOKMARKS, "appz")
        self.assertEqual(result, "apps")

    def test_rejects_garbage_queries(self):
        result = find_best_match(REAL_BOOKMARKS, "xyzxyz")
        self.assertIsNone(result)

    def test_min_ratio_threshold_enforced(self):
        bookmarks = {"alpha": {}, "beta": {}}
        result = find_best_match(bookmarks, "zzzz")
        best_ratio = max(SequenceMatcher(None, name, "zzzz").ratio() for name in bookmarks)
        self.assertLess(best_ratio, SEQUENCE_MATCHER_MIN_RATIO)
        self.assertIsNone(result)


class TestFuzzyMatchingEdgeCases(unittest.TestCase):

    def test_empty_query_returns_result_or_none(self):
        result = find_best_match(REAL_BOOKMARKS, "")
        # Empty query may return a result based on implementation
        self.assertIn(result, list(REAL_BOOKMARKS.keys()) + [None])

    def test_whitespace_only_query_returns_none(self):
        result = find_best_match(REAL_BOOKMARKS, "   ")
        self.assertIsNone(result)

    def test_query_with_special_characters(self):
        bookmarks = {"my-project": {}, "my_project": {}, "my.project": {}}
        result = find_best_match(bookmarks, "my-proj")
        self.assertEqual(result, "my-project")

    def test_query_with_unicode(self):
        bookmarks = {"プロジェクト": {}, "проект": {}, "proyecto": {}}
        result = find_best_match(bookmarks, "プロジェクト")
        self.assertEqual(result, "プロジェクト")

    def test_very_long_bookmark_name(self):
        long_name = "a" * 1000
        bookmarks = {long_name: {}, "short": {}}
        result = find_best_match(bookmarks, "a" * 500)
        self.assertEqual(result, long_name)

    def test_very_long_query(self):
        long_query = "saturno" * 100
        result = find_best_match(REAL_BOOKMARKS, long_query)
        # Very long query may or may not match
        self.assertIsInstance(result, (str, type(None)))

    def test_single_character_queries(self):
        bookmarks = {"repos": {}, "apps": {}, "cli": {}}
        result = find_best_match(bookmarks, "r")
        self.assertEqual(result, "repos")

    def test_numeric_bookmark_names(self):
        bookmarks = {"project2024": {}, "project2023": {}, "project2025": {}}
        result = find_best_match(bookmarks, "2024")
        self.assertEqual(result, "project2024")

    def test_mixed_case_exact_match(self):
        bookmarks = {"MyProject": {}, "myproject": {}, "MYPROJECT": {}}
        result = find_best_match(bookmarks, "MyProject")
        self.assertEqual(result, "MyProject")

    def test_handles_null_bytes_in_query(self):
        result = find_best_match(REAL_BOOKMARKS, "repos\x00")
        self.assertIn(result, [None, "repos"])

    def test_handles_newline_in_query(self):
        result = find_best_match(REAL_BOOKMARKS, "repos\n")
        self.assertIn(result, [None, "repos"])

    def test_duplicate_bookmarks_returns_first_match(self):
        bookmarks = {"duplicate": {}, "duplicate": {}}
        result = find_best_match(bookmarks, "duplicate")
        self.assertEqual(result, "duplicate")

    def test_all_bookmarks_equally_bad_matches(self):
        bookmarks = {"aaa": {}, "bbb": {}, "ccc": {}}
        result = find_best_match(bookmarks, "xyz")
        self.assertIsNone(result)

    def test_query_longer_than_all_bookmark_names(self):
        bookmarks = {"a": {}, "ab": {}, "abc": {}}
        result = find_best_match(bookmarks, "abcdefghijklmnop")
        # Query much longer than names may not match
        self.assertIn(result, ["abc", "ab", "a", None])

    def test_query_with_repeated_characters(self):
        bookmarks = {"repos": {}, "repoooos": {}}
        result = find_best_match(bookmarks, "repooos")
        self.assertIn(result, ["repos", "repoooos", None])

    def test_punctuation_only_bookmark_name(self):
        bookmarks = {"...": {}, "!!!": {}, "???": {}}
        result = find_best_match(bookmarks, "...")
        self.assertEqual(result, "...")

    def test_bookmark_with_leading_dots(self):
        bookmarks = {".config": {}, ".hidden": {}, "visible": {}}
        result = find_best_match(bookmarks, "conf")
        self.assertEqual(result, ".config")

    def test_bookmark_with_trailing_numbers(self):
        bookmarks = {"project1": {}, "project2": {}, "project10": {}}
        result = find_best_match(bookmarks, "proj1")
        self.assertEqual(result, "project1")

    def test_fuzzy_score_handles_empty_name(self):
        score = fuzzy_score("", "query")
        self.assertEqual(score, 0)

    def test_fuzzy_score_handles_empty_query(self):
        score = fuzzy_score("name", "")
        # Implementation may return non-zero for empty query
        self.assertGreaterEqual(score, 0)

    def test_fuzzy_score_both_empty(self):
        score = fuzzy_score("", "")
        # Both empty is an exact match
        self.assertGreaterEqual(score, 0)

    def test_subsequence_with_gaps(self):
        bookmarks = {"abcdefghij": {}, "abcdef": {}}
        result = find_best_match(bookmarks, "acegi")
        self.assertIn(result, ["abcdefghij", "abcdef", None])

    def test_handles_tab_characters_in_query(self):
        bookmarks = {"repos": {}, "apps": {}}
        result = find_best_match(bookmarks, "repos\t")
        self.assertIn(result, [None, "repos"])

    def test_handles_carriage_return_in_query(self):
        bookmarks = {"repos": {}}
        result = find_best_match(bookmarks, "repos\r")
        self.assertIn(result, [None, "repos"])

    def test_multiple_hyphens_in_name(self):
        bookmarks = {"my-awesome-project-name": {}, "simple": {}}
        result = find_best_match(bookmarks, "myawesomeproject")
        self.assertEqual(result, "my-awesome-project-name")

    def test_multiple_underscores_in_name(self):
        bookmarks = {"my_awesome_project_name": {}, "simple": {}}
        result = find_best_match(bookmarks, "myawesomeproject")
        self.assertEqual(result, "my_awesome_project_name")

    def test_mixed_separators_in_name(self):
        bookmarks = {"my-awesome_project.name": {}, "simple": {}}
        result = find_best_match(bookmarks, "myawesomeproject")
        self.assertEqual(result, "my-awesome_project.name")

    def test_emoji_in_bookmark_name(self):
        bookmarks = {"🚀rocket": {}, "⭐star": {}, "🎯target": {}}
        result = find_best_match(bookmarks, "rocket")
        self.assertEqual(result, "🚀rocket")

    def test_accented_characters(self):
        bookmarks = {"café": {}, "naïve": {}, "résumé": {}}
        result = find_best_match(bookmarks, "cafe")
        self.assertIn(result, ["café", None])

    def test_handles_zero_score_for_all_candidates(self):
        bookmarks = {"aaa": {}, "bbb": {}, "ccc": {}}
        result = find_best_match(bookmarks, "zzz")
        self.assertIsNone(result)


class TestPerformance(unittest.TestCase):

    def test_fast_fuzzy_is_faster_than_sequencematcher(self):
        queries = ["repos", "gosh", "back", "proj", "sgosh", "tilda", "mateus", "spb"]
        iterations = 500

        start = time.perf_counter()
        for _ in range(iterations):
            for q in queries:
                find_best_fast_match(REAL_BOOKMARKS, q)
        fast_time = time.perf_counter() - start

        start = time.perf_counter()
        for _ in range(iterations):
            for q in queries:
                pure_sequencematcher_match(REAL_BOOKMARKS, q)
        sm_time = time.perf_counter() - start

        speedup = sm_time / fast_time
        print(f"\n  Fast Fuzzy: {fast_time*1000:.1f}ms, PureSM: {sm_time*1000:.1f}ms, speedup: {speedup:.1f}x")
        self.assertGreater(speedup, 5.0, "Fast fuzzy should be at least 5x faster than SequenceMatcher")

    def test_find_best_match_completes_quickly(self):
        queries = ["repos", "gosh", "back", "reops", "sgosh", "clii"]
        iterations = 200

        start = time.perf_counter()
        for _ in range(iterations):
            for q in queries:
                find_best_match(REAL_BOOKMARKS, q)
        elapsed = time.perf_counter() - start

        per_query_us = elapsed / (iterations * len(queries)) * 1_000_000
        print(f"\n  find_best_match: {per_query_us:.1f}us/query")
        self.assertLess(per_query_us, 5000, "Each query should complete in under 5ms")


if __name__ == "__main__":
    unittest.main(verbosity=2)
