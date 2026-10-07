---
name: pr-draft
description: Draft a pull request for the current branch into a PR_DRAFT-<branch>.md file at the repository root, watch the file in the background and apply every ">>" note the user saves into it, and push and hand over the PR when the user says "go". Use when asked to draft, revise or greenlight a PR description, or when the user says they left notes in a PR_DRAFT file.
---

# /pr-draft

The draft lives in `PR_DRAFT-<branch>.md` at the repository root, where
`<branch>` is the current branch with every `/` turned into `-`
(`fix/unicode-escapes` → `PR_DRAFT-fix-unicode-escapes.md`).
The user edits it directly and leaves notes on lines that start with `>>`.
A background watcher picks up each save, so the user never has to re-run the
skill. Nothing is pushed or opened until the user says "go".

## File format

```markdown
---
title: Decode surrogate pairs in `\u` escapes
base: octo-org/json-parser:main
head: octocat:fix/unicode-escapes
---

<PR body, exactly as it will be posted>
```

A note is any line whose first non-blank characters are `>>`. It applies to
the text right around it: the title if it sits in the front matter, otherwise
the paragraph, list or section it is next to. A note at the very top or bottom
applies to the whole draft.

## No file yet: write the draft

1. Find the base: the upstream remote's default branch (`origin/HEAD`), and
   the remote the branch is pushed to for `head`.
2. Read the commits in `base..HEAD` and their diff, so the description says
   what the code does, not what the commit subjects say.
3. Match the project's style before writing a word. Read
   `.github/PULL_REQUEST_TEMPLATE*` if present and the last ten or so merged
   PRs on the upstream repository (`gh pr list --state merged`, or the public
   GitHub API with curl when `gh` is missing), favouring PRs by the same
   author. Copy their title form, headings, checklist and how they reference
   tickets.
4. Follow the repository's own rules about commit and PR text (CLAUDE.md,
   AGENTS.md, CONTRIBUTING). If they forbid assistant footers or trailers,
   leave them out.
5. Only tick testing boxes for what was actually run. Leave manual checks
   unticked.
6. Add `PR_DRAFT-*.md` to `.git/info/exclude` if it is not already ignored,
   so the draft never gets committed.
7. Write the file, tell the user its path, then start the watch (below).

## File exists: apply the notes

1. Read the whole file. The user may have edited text directly as well;
   those edits stand and are never reverted.
2. Collect every `>>` note with its location. If there are none, say so and
   stop.
3. Re-evaluate each note against the draft, the diff and the commits, rather
   than pasting its words in. A note can ask for a rewrite, a cut, a fact
   check ("is this true?"), more detail, or a change of tone. When a note
   questions a claim, verify it in the code and fix the text either way.
4. When a note asks for something the draft cannot do on its own, such as a
   code change, a commit message change or a new test, do not touch the code.
   Leave the note in place, rewritten to start with `>> [needs action]`, and
   list it in your reply.
5. Apply every other note and delete its `>>` line. Keep the front matter
   and the rest of the file intact.
6. Reply with one line per note: what it asked and what changed.

Running `/pr-draft` with the file present applies any notes already in it,
then starts the watch if it is not running.

## Watch

Arm the Monitor tool with the watcher that ships next to this file:

```
Monitor(
  command: "<this skill's base directory>/watch.sh <absolute draft path>",
  description: "PR draft notes in <draft file name>",
  timeout_ms: 1800000,
)
```

It polls once a second and prints one line per settled save:

- `NOTES <n> <path>`: apply the notes as above. Saves without notes print
  nothing, so your own rewrites, which delete the notes, never trigger it.
- `GO <path>`: the user wrote a `>> go` line. Delete that line and go.
- `GONE <path>`: the draft was deleted. The watcher exits; stop watching.

When the monitor expires after 30 minutes, re-arm it while the draft still
exists and the PR has not been handed over. Keep a single watcher per draft:
stop the old one with TaskStop before arming a new one.

## Go

The user greenlights by saying "go" in chat or with a `>> go` line.

1. Re-read the file from disk, so the latest save is what ships. Refuse and
   list them while any other `>>` note is left.
2. Push the branch to the remote named in `head` so the PR shows the latest
   commits. Never force-push without asking.
3. With `gh` available, open the PR: `gh pr create --repo <base repo>
   --base <base branch> --head <head> --title <title> --body-file <body-only
   temp file>`, adding `--draft` only when the user asks for one, and report
   its URL.
4. Without `gh`, run `<this skill's base directory>/compare_url.py <draft>`
   and give the user its output: a compare URL that opens GitHub's new PR
   form with the title and body already filled in.
5. Stop the watcher. Leave the draft file for the user to delete.
