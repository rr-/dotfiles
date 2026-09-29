---
description: Edit the prose in named files, or across a commit range
---
Edit prose so it follows the conventions at the end of this file. The target is
whatever the extra instructions name: paths or globs, a commit range, or
nothing, in which case it is the range.

Work file by file. Never enumerate the whole target before editing, and never
finish having edited nothing: each file is resolved before the next one starts,
so stopping early still leaves real progress behind.

1. Apply the conventions at the end of this file.

2. Resolve the target, and print what you resolved and how.

   Where the extra instructions name paths or globs, that is the target. Expand
   the globs, and take every file they match, tracked or not: a file that is in
   no commit is still in scope, and so is one outside the repository. Where a
   glob matches nothing, say which one and stop. Skip to step 4, where every
   line of each file is in scope rather than the changed ones.

   Otherwise the target is a commit range:
   - Use the range named in the extra instructions below, if there is one.
   - Otherwise find the base branch: `git symbolic-ref --short
     refs/remotes/origin/HEAD`, or `git remote show origin` and read its "HEAD
     branch:" line. Use `<base>...HEAD`.
   - With no remote, use whichever of `main` or `master` exists as the base.
   - Confirm the range resolves — `git rev-parse <range>` — before using it.

3. For a commit range, list the changed files: `git diff --name-only
   <range>`. Print the count. Every file in that list is in scope — no
   sampling, no top-N.

   An empty list means HEAD is the base branch with nothing unpushed on it. Fall
   back to the uncommitted work, `git status --porcelain`, and say that is what
   you are editing. Still empty: say there is nothing to edit and stop.

4. For each file in the target, in order, do all of the following before moving
   to the next file:

   a. For a commit range, collect the changed lines: `git diff -U0 <range> --
      <file>`. For a named file, the whole file is in scope.

   b. Find the prose-bearing constructs in scope. Grep the file for these
      rather than eyeballing it, then, for a commit range, keep the hits whose
      line numbers the diff touched:
      - comments: `//`, `#`, `--`, `;`, `/* */`, `<!-- -->`, docstrings, doc
        comments
      - string literals: `"…"`, `'…'`, `` `…` ``, `"""…"""`, `'''…'''`, `[[…]]`
      - markup prose: Markdown body text, headings, list items, alt text,
        frontmatter descriptions
      - user-facing text: CLI help, usage strings, error and log messages

   c. Edit each construct, or leave it alone when it already follows the
      conventions.

   d. Print one line per construct: `path:line`, edited or kept, and the reason
      in a few words. Then print the running file count, as `12/40`.

5. When a file defeats you — unreadable, generated, or a construct you cannot
   judge — say so on its line and carry on to the next file. A file you skipped
   is a line of output, not a reason to abandon the rest.

6. Finish with the totals: files visited, constructs edited, constructs kept,
   and every file or construct left unresolved, named.

# Conventions

Every word that ships with the code reads the way a reference manual is
written: plain words, short sentences, one idea each, no flourishes. To
shorten a passage, cut whole clauses and sentences rather than compressing the
words that stay.

## Comments

Comments are an antipattern by default. Keep one only where it documents a
public API, or where the code is genuinely tricky, and then in plain words a
newcomer would follow. The reader can read code, so one that restates it,
summarises a block, or explains ordinary control flow, ordering or cleanup
goes. A comment describes the code as it stands, never the change that produced
it, and never an invented actor such as "a reader that ...".

Open with a verb saying what the thing does. Put the main clause first and the
reason after it, so no sentence has to be read twice, and use the standard
technical word where one exists: fatal, return, report failure, error flag,
position. Name the place something belongs rather than saying "here", and keep
two contrasted statements in the same shape. Length is not the problem: a long
sentence that runs in a straight line beats the same text cut into stubs.

## Docstrings and documentation

Say what the thing does and what states it leaves behind. Stay high level: the
code carries the mechanism. Use the voice the surrounding document already
uses, and the vocabulary its readers use.

## Commit bodies and pull requests

The first sentence says what changed, so a reader who stops there knows what
landed. Give the old behaviour only where the reader needs it, as one "Before
this, ..." sentence that says what it cost. Do not argue for the design or
answer objections nobody raised. A bug fix opens with "Fixes a bug where" and
names the symptom a user saw, not the function.

## User-facing strings and error messages

Name the symptom the user saw, in their vocabulary, and stop: no internals, no
blame, no apology. Where the user can do something about it, say that in one
further sentence.

Extra instructions: $ARGUMENTS
