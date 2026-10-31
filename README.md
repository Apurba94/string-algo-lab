# String Algorithm Lab

Type a string and see what the classic string algorithms compute on it, cell by cell.

* **Overview:** distinct substrings, palindrome counts, longest palindrome and repeated substring, period, borders,
  smallest rotation, Lyndon factorisation and run-length form.
* **Arrays:** the KMP prefix function, the Z function, and Manacher's odd and even radii, aligned with the characters.
* **Suffix array:** sorted suffixes with the LCP array (Kasai).
* **Pattern matching:** KMP with highlighted hits and a trace of comparisons, and Aho-Corasick for many patterns.
* **Hashing and compare:** double polynomial hashing of substrings, longest common substring through a joined suffix
  array, the Burrows-Wheeler transform and a Huffman size estimate.
* **Saved strings:** keep the test strings you care about.

Also inside the library: a suffix automaton, minimal rotation, and an inverse Burrows-Wheeler transform.

`--demo` opens a temporary database with sample strings.

## From source

```bash
python -m string_algo_lab
python -m unittest discover -s tests -t .
python build_exe.py
```

The tests compare every algorithm with a naive version on hundreds of random strings.

## Limits

Screens work on up to 5000 characters so that tables stay readable. Hash equality is probabilistic: two different
substrings could collide, though with two moduli this is very unlikely.

## License

MIT
