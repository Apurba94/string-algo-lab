import os
import random
import shutil
import tempfile
import tkinter as tk
import unittest
from unittest import mock

from string_algo_lab import app as A
from string_algo_lab import appkit as ak
from string_algo_lab import strs as st


def words(n=250, seed=1):
    rng = random.Random(seed)
    for _ in range(n):
        yield "".join(rng.choice("abc"[:rng.randint(1, 3)]) for _ in range(rng.randint(0, 30)))


def all_subs(s):
    return {s[i:j] for i in range(len(s)) for j in range(i + 1, len(s) + 1)}


class TestArrays(unittest.TestCase):
    def test_prefix_and_z(self):
        for s in words():
            pi, z = st.prefix_function(s), st.z_function(s)
            for i in range(len(s)):
                self.assertEqual(pi[i], max((k for k in range(i + 1) if s[:k] == s[i - k + 1:i + 1]), default=0))
                if i:
                    k = 0
                    while i + k < len(s) and s[k] == s[i + k]:
                        k += 1
                    self.assertEqual(z[i], k)

    def test_kmp(self):
        for s in words():
            for p in ("a", "ab", "aba", "bb", "abcabc"):
                naive = [i for i in range(len(s) - len(p) + 1) if s[i:i + len(p)] == p]
                self.assertEqual(st.kmp_search(s, p)[0], naive)
        self.assertEqual(st.kmp_search("abc", ""), ([], []))
        self.assertLessEqual(len(st.kmp_search("a" * 1000, "a" * 500 + "b")[1]), 3000)     # linear, unlike naive search

    def test_manacher(self):
        for s in words():
            d1, d2 = st.manacher(s)
            for i in range(len(s)):
                k = 0
                while i - k >= 0 and i + k < len(s) and s[i - k] == s[i + k]:
                    k += 1
                self.assertEqual(d1[i], k)
                k = 0
                while i - k - 1 >= 0 and i + k < len(s) and s[i - k - 1] == s[i + k]:
                    k += 1
                self.assertEqual(d2[i], k)
            count = sum(1 for i in range(len(s)) for j in range(i + 1, len(s) + 1) if s[i:j] == s[i:j][::-1])
            self.assertEqual(st.count_palindromes(s), count)
            lp = st.longest_palindrome(s)
            self.assertEqual(lp, lp[::-1])
            self.assertIn(lp, s + " " if not lp else s)
            self.assertEqual(len(lp), max((j - i for i in range(len(s)) for j in range(i + 1, len(s) + 1) if s[i:j] == s[i:j][::-1]), default=0))


class TestSuffixStructures(unittest.TestCase):
    def test_suffix_array_lcp(self):
        for s in words():
            sa = st.suffix_array(s)
            self.assertEqual(sa, sorted(range(len(s)), key=lambda i: s[i:]))
            lcp = st.lcp_array(s, sa)
            for i, v in enumerate(lcp):
                a, b = s[sa[i]:], s[sa[i + 1]:]
                k = 0
                while k < min(len(a), len(b)) and a[k] == b[k]:
                    k += 1
                self.assertEqual(v, k)

    def test_substring_counts(self):
        for s in words(120):
            subs = all_subs(s)
            self.assertEqual(st.distinct_substrings(s) if s else 0, len(subs))
            self.assertEqual(st.SuffixAutomaton(s).distinct(), len(subs))
            rep = st.longest_repeated(s)
            want = max((len(x) for x in subs if sum(1 for i in range(len(s)) if s.startswith(x, i)) >= 2), default=0)
            self.assertEqual(len(rep), want)

    def test_automaton_contains(self):
        for s in words(60):
            a = st.SuffixAutomaton(s)
            subs = all_subs(s)
            for w in ("a", "ab", "abc", "ba", "cc", "aaa"):
                self.assertEqual(a.contains(w), w in subs)

    def test_common_substring(self):
        rng = random.Random(2)
        for _ in range(120):
            a = st.random_text(rng.random(), rng.randint(1, 12), "abc")
            b = st.random_text(rng.random(), rng.randint(1, 12), "abc")
            common = all_subs(a) & all_subs(b)
            r = st.longest_common_substring(a, b)
            self.assertEqual(len(r), max(map(len, common), default=0))
            if r:
                self.assertIn(r, common)
        self.assertEqual(st.longest_common_substring("abc", "xyz"), "")


class TestOthers(unittest.TestCase):
    def test_aho_corasick(self):
        rng = random.Random(3)
        for _ in range(120):
            text = st.random_text(rng.random(), 40, "abc")
            pats = list({st.random_text(rng.random(), rng.randint(1, 4), "abc") for _ in range(6)})
            ac = st.AhoCorasick(pats)
            want = sorted((i, k) for k, p in enumerate(pats) for i in range(len(text) - len(p) + 1) if text.startswith(p, i))
            self.assertEqual(sorted(ac.search(text)), want)

    def test_hash_equal_substrings(self):
        s = st.random_text(1, 300, "ab")
        h = st.Hasher(s)
        rng = random.Random(4)
        for _ in range(3000):
            l1, n = rng.randrange(0, 290), rng.randint(1, 8)
            l2 = rng.randrange(0, 290)
            self.assertEqual(h.get(l1, l1 + n) == h.get(l2, l2 + n), s[l1:l1 + n] == s[l2:l2 + n])

    def test_rotation_and_periods(self):
        for s in words(150):
            if s:
                i = st.minimal_rotation(s)
                self.assertEqual(s[i:] + s[:i], min(s[k:] + s[:k] for k in range(len(s))))
                p = st.smallest_period(s)
                self.assertEqual(p, next(k for k in range(1, len(s) + 1) if all(s[i] == s[i + k] for i in range(len(s) - k))))
        self.assertEqual(st.smallest_period("abcabcab"), 3)
        self.assertTrue(st.is_periodic("abab"))
        self.assertFalse(st.is_periodic("ababa"))
        self.assertEqual(st.borders("abacaba"), [3, 1])

    def test_lyndon(self):
        def is_lyndon(w):
            return all(w < w[i:] + w[:i] for i in range(1, len(w)))
        for s in words(150):
            f = st.lyndon_factorization(s)
            self.assertEqual("".join(f), s)
            self.assertTrue(all(is_lyndon(w) for w in f))
            self.assertTrue(all(a >= b for a, b in zip(f, f[1:])))

    def test_bwt_roundtrip(self):
        for s in words(150):
            self.assertEqual(st.unbwt(st.bwt(s)), s)
        with self.assertRaises(ValueError):
            st.bwt("a$b")

    def test_huffman_is_prefix_feasible(self):
        for s in words(120):
            if s:
                lengths = st.huffman_lengths(s)
                self.assertLessEqual(sum(2.0 ** -l for l in lengths.values()), 1.0 + 1e-9)     # Kraft inequality

    def test_run_length_and_summary(self):
        self.assertEqual(st.run_length("aabccc"), [("a", 2), ("b", 1), ("c", 3)])
        self.assertTrue(dict(st.summary("abab")))
        self.assertEqual(dict(st.summary(""))["Length"], 0)


class TestGui(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.mkdtemp()
        self.store = ak.Store(A.SCHEMA, os.path.join(self.dir, "t.sqlite3"), A.APP.APP_NAME)
        A.sample(self.store)
        try:
            self.app = A.APP(self.store)
        except tk.TclError as exc:
            self.skipTest(str(exc))
        self.errors = []
        self.app.report_callback_exception = lambda e, v, t: self.errors.append(repr(v))
        self.app.update()

    def tearDown(self):
        self.store.close()
        self.app.destroy()
        shutil.rmtree(self.dir, ignore_errors=True)
        self.assertEqual(self.errors, [])

    def test_every_screen_in_both_themes(self):
        for theme in ("Dark", "Light"):
            self.app.set_theme(theme)
            for t in self.app.titles():
                self.app.navigate(t)
                self.app.update()

    def test_text_flows_everywhere(self):
        v = self.app.views["Overview"]
        ak.set_text(v.text, "banana")
        v.run()
        self.assertEqual(self.store.get_setting("text"), "banana")
        self.app.navigate("Suffix array")
        t = self.app.views["Suffix array"].table.tree
        self.assertEqual([t.item(i, "values")[1] for i in t.get_children()], ["5", "3", "1", "0", "4", "2"])
        self.app.navigate("Arrays")
        self.assertEqual(len(self.app.views["Arrays"].table.tree.get_children()), 6)
        self.app.navigate("Pattern matching")
        m = self.app.views["Pattern matching"]
        m.pat.set("ana")
        m.kmp()
        self.assertIn("2 match(es)", m.result.cget("text"))
        self.assertTrue(m.view_text.tag_ranges("hit"))
        m.aho()
        self.assertIn("Trie", m.aho_info.cget("text"))

    def test_limits_and_empty(self):
        v = self.app.views["Overview"]
        ak.set_text(v.text, "a" * (A.MAX_LEN + 1))
        with mock.patch("tkinter.messagebox.showerror") as err:
            v.run()
        self.assertTrue(err.called)
        ak.set_text(v.text, "a")
        v.run()
        for t in self.app.titles():
            self.app.navigate(t)
            self.app.update()

    def test_compare_and_saved(self):
        self.app.navigate("Hashing and compare")
        h = self.app.views["Hashing and compare"]
        h.vals[1].set("99999")
        with mock.patch("tkinter.messagebox.showerror") as err:
            h.compare()
        self.assertTrue(err.called)
        h.vals[1].set("3")
        h.common()
        self.assertIn("programming", h.lcs.cget("text"))
        self.app.navigate("Saved strings")
        s = self.app.views["Saved strings"]
        s.view.select(self.store.list("snippet")[1]["id"])
        s.use()
        self.assertEqual(self.app.views["Overview"].get(), "abcabcabcabc")


if __name__ == "__main__":
    unittest.main()
