"""String algorithms. Each returns the same array a contestant would compute, plus a trace where that teaches something."""
import random
from collections import deque


def prefix_function(s):
    p = [0] * len(s)
    k = 0
    for i in range(1, len(s)):
        while k and s[i] != s[k]:
            k = p[k - 1]
        if s[i] == s[k]:
            k += 1
        p[i] = k
    return p


def kmp_search(text, pat):
    """Start positions of pat in text, and a trace of (text index, pattern index, matched?)."""
    if not pat:
        return [], []
    p = prefix_function(pat)
    out, trace, k = [], [], 0
    for i, c in enumerate(text):
        while k and c != pat[k]:
            trace.append((i, k, False))
            k = p[k - 1]
        if c == pat[k]:
            trace.append((i, k, True))
            k += 1
        else:
            trace.append((i, k, False))
        if k == len(pat):
            out.append(i - k + 1)
            k = p[k - 1]
    return out, trace


def z_function(s):
    n = len(s)
    z = [0] * n
    l = r = 0
    for i in range(1, n):
        if i < r:
            z[i] = min(r - i, z[i - l])
        while i + z[i] < n and s[z[i]] == s[i + z[i]]:
            z[i] += 1
        if i + z[i] > r:
            l, r = i, i + z[i]
    if n:
        z[0] = n
    return z


def manacher(s):
    """(odd radii, even radii): d1[i] counts palindromes centred at i, d2[i] those centred between i-1 and i."""
    n = len(s)
    d1, d2 = [0] * n, [0] * n
    l, r = 0, -1
    for i in range(n):
        k = 1 if i > r else min(d1[l + r - i], r - i + 1)
        while i - k >= 0 and i + k < n and s[i - k] == s[i + k]:
            k += 1
        d1[i] = k
        if i + k - 1 > r:
            l, r = i - k + 1, i + k - 1
    l, r = 0, -1
    for i in range(n):
        k = 0 if i > r else min(d2[l + r - i + 1], r - i + 1)
        while i - k - 1 >= 0 and i + k < n and s[i - k - 1] == s[i + k]:
            k += 1
        d2[i] = k
        if i + k - 1 > r:
            l, r = i - k, i + k - 1
    return d1, d2


def longest_palindrome(s):
    if not s:
        return ""
    d1, d2 = manacher(s)
    best, start = 0, 0
    for i in range(len(s)):
        if 2 * d1[i] - 1 > best:
            best, start = 2 * d1[i] - 1, i - d1[i] + 1
        if 2 * d2[i] > best:
            best, start = 2 * d2[i], i - d2[i]
    return s[start:start + best]


def count_palindromes(s):
    d1, d2 = manacher(s)
    return sum(d1) + sum(d2)


def suffix_array(s):
    """Prefix doubling with counting sort, O(n log n)."""
    n = len(s)
    if n == 0:
        return []
    order = sorted(range(n), key=lambda i: s[i])
    rank = [0] * n
    for i in range(1, n):
        rank[order[i]] = rank[order[i - 1]] + (s[order[i]] != s[order[i - 1]])
    k = 1
    while k < n and rank[order[-1]] < n - 1:
        key = lambda i: (rank[i], rank[i + k] if i + k < n else -1)
        order.sort(key=key)
        new = [0] * n
        for i in range(1, n):
            new[order[i]] = new[order[i - 1]] + (key(order[i]) != key(order[i - 1]))
        rank = new
        k *= 2
    return order


def lcp_array(s, sa):
    """Kasai: lcp[i] is the common prefix of the suffixes at sa[i] and sa[i+1]."""
    n = len(s)
    rank = [0] * n
    for i, x in enumerate(sa):
        rank[x] = i
    lcp = [0] * max(0, n - 1)
    h = 0
    for i in range(n):
        if rank[i] == n - 1:
            h = 0
            continue
        j = sa[rank[i] + 1]
        while i + h < n and j + h < n and s[i + h] == s[j + h]:
            h += 1
        lcp[rank[i]] = h
        if h:
            h -= 1
    return lcp


def distinct_substrings(s):
    n = len(s)
    return n * (n + 1) // 2 - sum(lcp_array(s, suffix_array(s)))


def longest_repeated(s):
    sa = suffix_array(s)
    lcp = lcp_array(s, sa)
    if not lcp or max(lcp) == 0:
        return ""
    i = lcp.index(max(lcp))
    return s[sa[i]:sa[i] + lcp[i]]


def longest_common_substring(a, b):
    joined = a + "\0" + b
    sa = suffix_array(joined)
    lcp = lcp_array(joined, sa)
    best, at = 0, 0
    split = len(a)
    for i, v in enumerate(lcp):
        if (sa[i] < split) != (sa[i + 1] < split) and v > best:
            best, at = v, sa[i]
    return joined[at:at + best].replace("\0", "")


class AhoCorasick:
    def __init__(self, patterns):
        self.go, self.fail, self.out = [{}], [0], [[]]
        self.patterns = patterns
        for idx, p in enumerate(patterns):
            node = 0
            for c in p:
                if c not in self.go[node]:
                    self.go[node][c] = len(self.go)
                    self.go.append({})
                    self.fail.append(0)
                    self.out.append([])
                node = self.go[node][c]
            if p:
                self.out[node].append(idx)
        q = deque(self.go[0].values())
        while q:
            u = q.popleft()
            for c, v in self.go[u].items():
                f = self.fail[u]
                while f and c not in self.go[f]:
                    f = self.fail[f]
                self.fail[v] = self.go[f].get(c, 0) if self.go[f].get(c, 0) != v else 0
                self.out[v] = self.out[v] + self.out[self.fail[v]]
                q.append(v)

    def search(self, text):
        """[(start position, pattern index)]"""
        node, hits = 0, []
        for i, c in enumerate(text):
            while node and c not in self.go[node]:
                node = self.fail[node]
            node = self.go[node].get(c, 0)
            for idx in self.out[node]:
                hits.append((i - len(self.patterns[idx]) + 1, idx))
        return hits

    def nodes(self):
        return len(self.go)


class SuffixAutomaton:
    def __init__(self, s):
        self.next, self.link, self.len = [{}], [-1], [0]
        last = 0
        for c in s:
            cur = len(self.next)
            self.next.append({})
            self.len.append(self.len[last] + 1)
            self.link.append(0)
            p = last
            while p != -1 and c not in self.next[p]:
                self.next[p][c] = cur
                p = self.link[p]
            if p != -1:
                q = self.next[p][c]
                if self.len[p] + 1 == self.len[q]:
                    self.link[cur] = q
                else:
                    clone = len(self.next)
                    self.next.append(dict(self.next[q]))
                    self.len.append(self.len[p] + 1)
                    self.link.append(self.link[q])
                    while p != -1 and self.next[p].get(c) == q:
                        self.next[p][c] = clone
                        p = self.link[p]
                    self.link[q] = self.link[cur] = clone
            last = cur

    def distinct(self):
        return sum(self.len[i] - self.len[self.link[i]] for i in range(1, len(self.len)))

    def contains(self, w):
        v = 0
        for c in w:
            if c not in self.next[v]:
                return False
            v = self.next[v][c]
        return True


class Hasher:
    """Double polynomial hash with substring queries."""
    MODS = (1000000007, 998244353)

    def __init__(self, s, bases=(131, 137)):
        self.s, self.bases = s, bases
        self.h, self.p = [], []
        for m, b in zip(self.MODS, bases):
            h, p = [0], [1]
            for c in s:
                h.append((h[-1] * b + ord(c)) % m)
                p.append(p[-1] * b % m)
            self.h.append(h)
            self.p.append(p)

    def get(self, l, r):
        """Hash of s[l:r]."""
        return tuple((self.h[k][r] - self.h[k][l] * self.p[k][r - l]) % self.MODS[k] for k in range(2))


def minimal_rotation(s):
    """Start index of the lexicographically smallest rotation (Booth-style two pointers)."""
    n = len(s)
    i, j, k = 0, 1, 0
    while i < n and j < n and k < n:
        a, b = s[(i + k) % n], s[(j + k) % n]
        if a == b:
            k += 1
            continue
        if a > b:
            i += k + 1
        else:
            j += k + 1
        if i == j:
            j += 1
        k = 0
    return min(i, j) if n else 0


def smallest_period(s):
    if not s:
        return 0
    return len(s) - prefix_function(s)[-1]


def is_periodic(s):
    p = smallest_period(s)
    return p < len(s) and len(s) % p == 0


def borders(s):
    """All proper border lengths, longest first."""
    p = prefix_function(s)
    k = p[-1] if p else 0
    out = []
    while k:
        out.append(k)
        k = p[k - 1]
    return out


def lyndon_factorization(s):
    """Duval: the unique non-increasing factorisation into Lyndon words."""
    n, i, out = len(s), 0, []
    while i < n:
        j, k = i + 1, i
        while j < n and s[k] <= s[j]:
            k = i if s[k] < s[j] else k + 1
            j += 1
        while i <= k:
            out.append(s[i:i + j - k])
            i += j - k
    return out


def run_length(s):
    out, i = [], 0
    while i < len(s):
        j = i
        while j < len(s) and s[j] == s[i]:
            j += 1
        out.append((s[i], j - i))
        i = j
    return out


def bwt(s, end="$"):
    if end in s:
        raise ValueError("the text must not contain %s" % end)
    t = s + end
    return "".join(t[i - 1] for i in suffix_array(t))


def unbwt(b, end="$"):
    order = sorted(range(len(b)), key=lambda i: (b[i], i))
    i = b.index(end)
    out = []
    for _ in range(len(b)):
        i = order[i]
        out.append(b[i])
    return "".join(out).rstrip(end)


def huffman_lengths(s):
    import heapq
    from collections import Counter
    counts = Counter(s)
    if len(counts) == 1:
        return {next(iter(counts)): 1}
    heap = [(n, i, [c]) for i, (c, n) in enumerate(sorted(counts.items()))]
    heapq.heapify(heap)
    depth = {c: 0 for c in counts}
    tie = len(heap)
    while len(heap) > 1:
        a, b = heapq.heappop(heap), heapq.heappop(heap)
        for c in a[2] + b[2]:
            depth[c] += 1
        tie += 1
        heapq.heappush(heap, (a[0] + b[0], tie, a[2] + b[2]))
    return depth


def random_text(seed=None, n=24, alphabet="ab"):
    rng = random.Random(seed)
    return "".join(rng.choice(alphabet) for _ in range(n))


def summary(s):
    """(label, value) rows for the overview."""
    period = smallest_period(s)
    return [("Length", len(s)), ("Distinct letters", len(set(s))), ("Distinct substrings", distinct_substrings(s) if s else 0),
            ("Palindromic substrings", count_palindromes(s)), ("Longest palindrome", longest_palindrome(s)),
            ("Longest repeated substring", longest_repeated(s) or "(none)"), ("Smallest period", period),
            ("Periodic", "yes, %d copies" % (len(s) // period) if s and is_periodic(s) else "no"),
            ("Borders", ", ".join(map(str, borders(s))) or "(none)"),
            ("Smallest rotation", (s[minimal_rotation(s):] + s[:minimal_rotation(s)]) if s else ""),
            ("Lyndon factorisation", " | ".join(lyndon_factorization(s))),
            ("Run-length", " ".join("%s%d" % r for r in run_length(s)[:30]))]
