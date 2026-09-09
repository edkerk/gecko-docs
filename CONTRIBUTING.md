# Contributing to gecko-docs

## Documentation prose style

Many readers are not native English speakers. Prose must be direct and
literal, not just factually correct.

1. No em dashes, anywhere: not in prose, headings, table cells, or generated
   strings. Use the punctuation the sentence actually calls for: a comma
   where the clause continues, a semicolon where it is independent, a colon
   where what follows defines or enumerates what precedes it, parentheses
   for a matched pair around an aside.
2. Apply these five checks to every sentence while writing it, not as a
   later sweep:
   - Can the subject perform the verb? A file, function, or table can
     return, raise, contain, default to. It cannot want, know, prefer, or
     do anything "quietly," "conveniently," or "simply." A manner adverb on
     an inanimate subject is the most common violation.
   - Does the sentence state a behavior and its condition, or does it tell
     the reader what's "worth" doing? No "worth using," "the usual way,"
     "best practice." State the fact; leave the judgment to the reader.
   - Is the sentence about the software, or about the document? Cut "this
     page is about," "as mentioned above," "the point of this example."
   - Does a word minimize something? "just," "simply," "merely," "only,"
     "of course." If removing it doesn't change the claim, remove it.
   - Would a non-native English reader parse this correctly on first read?
     No idioms, figures of speech, or headline-style fragments that drop
     the subject or verb for effect (example of what to avoid: "same
     verdicts, very different cost" as a heading). Rewrite as a complete,
     literal sentence. This is not the same as dumbing content down: keep
     the technical precision, drop only the cleverness.
3. No AI/Claude/Anthropic attribution anywhere in the repository: not in
   commit messages, PR text, code comments, or the docs themselves.

One exception worth stating explicitly: established, consistently-used
technical shorthand (a real domain term, a standard abbreviation) is not
the same as a one-off clever phrase, and doesn't need to be purged just
because it isn't perfectly literal. Reserve the rewrite effort for genuine
idiom and headline compression, especially on pages newcomers read first.
