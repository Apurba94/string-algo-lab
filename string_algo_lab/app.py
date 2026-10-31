"""String Algorithm Lab desktop program."""
import tkinter as tk
from tkinter import messagebox, ttk

from . import appkit as ak
from . import strs as st
from .appkit import Entity, Field, entities

SCHEMA = entities(
    Entity("snippet", "String", "Saved strings", "name", [
        Field("name", "Name", required=True, list_col=True, width=26),
        Field("text", "Text", "long", required=True, list_col=True, width=44),
        Field("notes", "Notes", "long"),
    ]),
)
MAX_LEN = 5000


def sample(store):
    store.insert("snippet", name="Fibonacci word", text="abaababaabaababaababa", notes="Few distinct factors, rich in periods.")
    store.insert("snippet", name="Periodic", text="abcabcabcabc")
    store.insert("snippet", name="Palindrome heavy", text="abacabadabacaba", notes="A classic test for Manacher.")


def strip_text(s):
    return s.replace("\r", "").replace("\n", "")


def array_rows(s, columns):
    """Rows for an index table: index, character, then each named array."""
    out = []
    for i in range(len(s)):
        out.append([i, s[i]] + [(c[i] if i < len(c) else "") for _, c in columns])
    return out


class SharedText:
    def __init__(self, app):
        self.value = app.store.get_setting("text", "abacabadabacaba")


class Overview(ttk.Frame):
    title = "Overview"

    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        ttk.Label(self, text="Your string. Every screen uses it.", style="Muted.TLabel").pack(anchor="w")
        frame, self.text = ak.make_text(self, app.colors, height=4, mono=True)
        frame.pack(fill="x")
        row = ttk.Frame(self)
        row.pack(fill="x", pady=6)
        ttk.Button(row, text="Analyse", style="Accent.TButton", command=self.run).pack(side="left")
        self.alpha = tk.StringVar(value="ab")
        ttk.Button(row, text="Random", command=self.randomize).pack(side="left", padx=6)
        ak.labeled_entry(row, "Alphabet", self.alpha, 10).pack(side="left", padx=6)
        self.table = ak.Table(self, app, [("label", "Property", 28), ("value", "Value", 70)])
        self.table.pack(fill="both", expand=True)

    def get(self):
        return strip_text(ak.get_text(self.text))

    def randomize(self):
        ak.set_text(self.text, st.random_text(None, 24, self.alpha.get() or "ab"))
        self.run()

    def run(self):
        s = self.get()
        if len(s) > MAX_LEN:
            messagebox.showerror("Text", "Use at most %d characters on this screen." % MAX_LEN, parent=self)
            return
        self.app.store.set_setting("text", s)
        self.table.fill([[a, str(b)] for a, b in st.summary(s)])

    def refresh(self):
        if not self.get():
            ak.set_text(self.text, self.app.store.get_setting("text", "abacabadabacaba"))
        self.run()

    def commit(self):
        self.app.store.set_setting("text", self.get())
        return True


def current(app):
    v = app.view("Overview")
    if not v.get():
        v.refresh()
    return v.get()


class Arrays(ttk.Frame):
    title = "Arrays"

    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        ttk.Label(self, text="Index tables for the string on the Overview screen. pi: KMP prefix function.  z: Z function.  "
                             "d1, d2: Manacher odd and even radii.", style="Muted.TLabel").pack(anchor="w")
        self.table = ak.Table(self, app, [("i", "i", 6), ("c", "char", 6), ("pi", "pi", 8), ("z", "z", 8), ("d1", "d1", 8), ("d2", "d2", 8)])
        self.table.pack(fill="both", expand=True, pady=6)

    def refresh(self):
        s = current(self.app)[:MAX_LEN]
        d1, d2 = st.manacher(s)
        self.table.fill(array_rows(s, [("pi", st.prefix_function(s)), ("z", st.z_function(s)), ("d1", d1), ("d2", d2)]))


class Suffixes(ttk.Frame):
    title = "Suffix array"

    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self.info = ttk.Label(self, text="", style="Muted.TLabel")
        self.info.pack(anchor="w")
        self.table = ak.Table(self, app, [("rank", "Rank", 7), ("sa", "Position", 9), ("lcp", "LCP with next", 13), ("suffix", "Suffix", 60)])
        self.table.pack(fill="both", expand=True, pady=6)

    def refresh(self):
        s = current(self.app)[:MAX_LEN]
        sa = st.suffix_array(s)
        lcp = st.lcp_array(s, sa)
        self.info.configure(text="%d distinct substrings. Longest repeated substring: %s" % (st.distinct_substrings(s) if s else 0, st.longest_repeated(s) or "(none)"))
        self.table.fill([[i, p, lcp[i] if i < len(lcp) else "", ak.short(s[p:], 70)] for i, p in enumerate(sa[:2000])])


class Matcher(ttk.Frame):
    title = "Pattern matching"

    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        nb = ttk.Notebook(self)
        nb.pack(fill="both", expand=True)
        one, many = ttk.Frame(nb, padding=8), ttk.Frame(nb, padding=8)
        nb.add(one, text="KMP: one pattern")
        nb.add(many, text="Aho-Corasick: many patterns")
        row = ttk.Frame(one)
        row.pack(fill="x")
        self.pat = tk.StringVar(value="aba")
        ak.labeled_entry(row, "Pattern", self.pat, 26).pack(side="left", padx=(0, 8))
        ttk.Button(row, text="Search", style="Accent.TButton", command=self.kmp).pack(side="left", anchor="s")
        self.result = ttk.Label(one, text="", style="Muted.TLabel")
        self.result.pack(anchor="w", pady=6)
        frame, self.view_text = ak.make_text(one, app.colors, height=5, mono=True)
        frame.pack(fill="x")
        self.view_text.tag_configure("hit", background=app.colors["sel"], foreground=app.colors["sel_ink"])
        ttk.Label(one, text="First comparisons (text index, pattern index, result)", style="Muted.TLabel").pack(anchor="w", pady=(6, 0))
        self.trace = ak.Table(one, app, [("i", "Text index", 11), ("k", "Pattern index", 13), ("ok", "Result", 12)])
        self.trace.pack(fill="both", expand=True)
        ttk.Label(many, text="One pattern per line", style="Muted.TLabel").pack(anchor="w")
        frame, self.pats = ak.make_text(many, app.colors, height=6, mono=True)
        frame.pack(fill="x")
        ak.set_text(self.pats, "a\naba\ncab\nbad")
        ttk.Button(many, text="Search all", style="Accent.TButton", command=self.aho).pack(anchor="w", pady=6)
        self.hits = ak.Table(many, app, [("pat", "Pattern", 22), ("n", "Matches", 10), ("first", "Positions", 60)])
        self.hits.pack(fill="both", expand=True)
        self.aho_info = ttk.Label(many, text="", style="Muted.TLabel")
        self.aho_info.pack(anchor="w")

    def kmp(self):
        s, p = current(self.app), self.pat.get()
        hits, trace = st.kmp_search(s, p)
        self.result.configure(text="%d match(es) at %s. Comparisons: %d (a naive search can need up to %d)" % (
            len(hits), hits[:30], len(trace), len(s) * max(1, len(p))))
        ak.set_text(self.view_text, s)
        for h in hits:
            self.view_text.tag_add("hit", "1.0+%dc" % h, "1.0+%dc" % (h + len(p)))
        self.trace.fill([[i, k, "match" if ok else "mismatch"] for i, k, ok in trace[:300]])

    def aho(self):
        pats = [p for p in ak.get_text(self.pats).splitlines() if p]
        s = current(self.app)
        a = st.AhoCorasick(pats)
        hits = a.search(s)
        rows = []
        for i, p in enumerate(pats):
            pos = sorted(x for x, idx in hits if idx == i)
            rows.append([p, len(pos), " ".join(map(str, pos[:40]))])
        self.hits.fill(rows)
        self.aho_info.configure(text="Trie with %d nodes, %d matches in total" % (a.nodes(), len(hits)))

    def refresh(self):
        self.kmp()
        self.aho()


class Hashing(ttk.Frame):
    title = "Hashing and compare"

    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        p = ak.panel(self, "Compare two substrings with a double polynomial hash")
        p.pack(fill="x")
        row = ttk.Frame(p, style="Panel.TFrame")
        row.pack(anchor="w")
        self.vals = [tk.StringVar(value=v) for v in ("0", "3", "4", "7")]
        for label, v in zip(("First start", "First end", "Second start", "Second end"), self.vals):
            ak.labeled_entry(row, label, v, 10, "PanelMuted.TLabel").pack(side="left", padx=(0, 8))
        ttk.Button(row, text="Compare", style="Accent.TButton", command=self.compare).pack(side="left", anchor="s")
        self.res = ttk.Label(p, text="", style="Panel.TLabel", font=(ak.MONO, 10), justify="left")
        self.res.pack(anchor="w", pady=6)
        q = ak.panel(self, "Two strings")
        q.pack(fill="x", pady=8)
        self.a, self.b = tk.StringVar(value="dynamicprogramming"), tk.StringVar(value="programmingcontest")
        ak.labeled_entry(q, "A", self.a, 50, "PanelMuted.TLabel").pack(anchor="w")
        ak.labeled_entry(q, "B", self.b, 50, "PanelMuted.TLabel").pack(anchor="w", pady=4)
        ttk.Button(q, text="Longest common substring", command=self.common).pack(anchor="w")
        self.lcs = ttk.Label(q, text="", style="Panel.TLabel")
        self.lcs.pack(anchor="w", pady=4)
        r = ak.panel(self, "Transforms")
        r.pack(fill="both", expand=True)
        self.tr = ttk.Label(r, text="", style="Panel.TLabel", wraplength=int(800 * app.scale), justify="left")
        self.tr.pack(anchor="w")

    def compare(self, quiet=False):
        s = current(self.app)
        problem = None
        try:
            a, b, c, d = [int(v.get()) for v in self.vals]
            if not (0 <= a <= b <= len(s) and 0 <= c <= d <= len(s)):
                problem = "Positions must fit the string of length %d." % len(s)
        except ValueError:
            problem = "Positions must be whole numbers."
        if problem:
            if quiet:                                 # opening the screen must never raise a dialog
                self.res.configure(text=problem)
            else:
                messagebox.showerror("Compare", problem, parent=self)
            return
        h = st.Hasher(s)
        x, y = h.get(a, b), h.get(c, d)
        self.res.configure(text="%r  %s\n%r  %s\n%s" % (ak.short(s[a:b], 30), x, ak.short(s[c:d], 30), y, "Equal" if x == y else "Different"))

    def common(self):
        self.lcs.configure(text="Longest common substring: %s" % (st.longest_common_substring(self.a.get(), self.b.get()) or "(none)"))

    def refresh(self):
        s = current(self.app)
        self.compare(quiet=True)
        self.common()
        lengths = st.huffman_lengths(s) if s else {}
        from collections import Counter
        bits = sum(lengths[c] * n for c, n in Counter(s).items())
        self.tr.configure(text="Burrows-Wheeler transform: %s\nHuffman coding: %d bits, against %d bits at 8 bits per character" % (
            ak.short(st.bwt(s), 90) if "$" not in s else "(the text contains $)", bits, 8 * len(s)))


class Saved(ttk.Frame):
    title = "Saved strings"

    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self.view = ak.EntityView(self, app, "snippet", buttons=[("Use this string", self.use)])
        self.view.pack(fill="both", expand=True)
        self.refresh, self.commit = self.view.refresh, self.view.commit

    def use(self):
        if self.view.current:
            s = self.app.store.get("snippet", self.view.current)["text"]
            self.app.view("Overview")
            ak.set_text(self.app.views["Overview"].text, strip_text(s))
            self.app.navigate("Overview")


class APP(ak.BaseApp):
    APP_NAME, ACCENT = "String Algorithm Lab", "#a16207"
    SCHEMA, SAMPLE = SCHEMA, staticmethod(sample)
    VIEWS = [Overview, Arrays, Suffixes, Matcher, Hashing, Saved, ak.DataView]


def main(argv=None):
    return ak.main(APP, argv)
