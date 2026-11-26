---
name: track
description: The user's private progress tracker for big multi-session work (ports, multi-PR modules, agent phase chains) — plain files in ~/work/priv/plans, changed only through the track MCP tools (track_set, track_note, track_add, ...). Use at the start of work in a repo that has a tracked project (the SessionStart hook prints it), whenever a tracked ticket changes state (agent report, PR opened or merged, decision, blocker), and before handing a ticket to a subagent. Not for bug fixes, one-offs or small PRs.
---

# Tracking big work with `track`

The user tracks **big** pieces of work only: anything that outlives one
session or one PR (a game port, a module spread over several PRs, an agent
chain, a feature with a header round). Bug fixes, one-offs, small PRs,
questions and CI fixes are **not** tracked; when one happens inside a tracked
ticket, it is one line in that ticket's note ("#44 fixed the stage test
leak"). Never create a project on your own, and never grow the plan beyond
what the rules below allow: suggest it ("this looks like several PRs, track
it?") and let the user decide.

Everything is private, plain text, and versioned: `~/work/priv/plans` is a
git repository, mirrored to the private GitHub repository `rr-/plans` (no
public tickets). `track` commits every change itself but never pushes;
pushing is the user's call. Never make that repository public or add
collaborators.

## Layout

`track` itself lives in `~/work/priv/track`: `bin/track` is the user's live
view (on PATH as `track`; terse text when piped), `bin/track-mcp` the MCP
server you change things through.

```
~/work/priv/plans/<project>/
  plan.md        ONE ticket table + the prose (why, decisions, process, "Now")
  notes.md       notes on the project as a whole
  notes/<id>.md  notes per ticket: dated entries, append-only
  repos          repository paths of the project, one per line
  review.md      only after an unattended replan, until the user clears it
```

The ticket table is the only source of status. Its columns, by header name:

| column | meaning |
|---|---|
| `id` | short slug, lowercase-dashes; the ticket's name everywhere |
| `parent` | the group it belongs to; empty for a top-level ticket |
| `item` | what it is, for humans; at most 100 characters, details go in a note |
| `size` | S, S–M, M, M–L, L, L–XL, XL — weights the progress bar |
| `status` | a word: `done` 🟢 · `wip` 🟡 · `todo` 🔴 · `hold` ⏸ · `none` ➖ out of scope · `proposed` 💡 |
| `origin` | `found` (added as found work) or `replan`; set once, never changed |

Extra columns (e.g. `decomp`) are allowed and kept. Plans are two levels:
groups hold leaves only. A group's status comes from its leaves, and its item
says what done means. Siblings keep their place in the table; `track_move`
reorders them and a new ticket goes after its last sibling. The bar is
completed leaf weight: done counts 1, wip, todo and hold count 0, weighted by
size; none and proposed are left out.

## Rules

- **Order:** work starts top to bottom. `track_next` names the one todo that
  may start; at most 3 leaves are wip at once. A blocked todo is set to hold
  with its reason, never walked past. Finished work is set done in any order.
- **Growth:** the plan grows only by the user's say.
  - `track_split` breaks up the work at hand (a wip leaf or the next todo)
    within one and a half times its size.
  - `track_add` under a running group adds found work, todo and marked
    found, within 10% of the group's planned weight; beyond that, or as a
    new group, it is proposed (💡).
  - Proposals are yours to reshape or drop freely until the user promotes
    them (`p` in the live view). When only proposals are left, stop and say
    so.
- **Replan:** when something significant means the plan no longer fits (a
  finding, a failed approach, a new requirement), `track_replan` adds and
  reshapes beyond those shares. Found work and proposals cover everything
  else. Use it only when the plan as it stands is wrong. See below.
- **Removal:** never drop or delete anything but your own proposals, and
  never add or remove projects, unless the user asked.

## Tools

All take an optional `project`; without it they use the project whose
`repos` file lists the session's folder.

```
track_projects                  every project, one bar each
track_list [active]             the ticket tree (🗒 = has notes); active: only wip leaves + last note line
track_show [id]                 a ticket's row, children and notes — read it before working on a ticket;
                                no id: the project's own notes
track_next                      the wip leaves and the one todo that may start
track_set id status             done wip todo hold none; hold and none need a reason
track_note text [id] [kind]     kind: note, handoff, decision, open; no id: a note on the project
track_add id size item [parent] found work or a proposal (see Rules)
track_split id pieces           the work at hand into [{id, size, item}]
track_update id changes         {item, size (shrinks only, but for a proposal), id, parent ("-" top level), extra column}
track_move id where [other]     top, bottom, before other, after other — among siblings
track_drop id                   a leaf and its notes — your own proposals, or when the user asked
track_new name [repos]          a project — only when the user asked
track_remove name               a whole project — only when the user asked
```

These ask the user to approve the exact change list (MCP elicitation) before
they change anything; a decline, or a client that cannot ask, changes
nothing:

```
track_delete ids                tickets with their notes, a group with all its leaves — when the user asked
track_bulk edits                {id: {column: value}} for many tickets in one commit, status and bigger sizes
                                included — when the user asked for a sweeping edit
track_replan reason [add] [edits]
                                after something significant (see Rules); add: [{id, size, item, parent?}]
                                as todo marked replan; edits: todo leaves' item, size, parent or status none,
                                groups' item; started and done work stays, nothing is removed
```

`track_replan` needs a reason: what happened and why the plan no longer
fits. It becomes a project decision note with every change, in one commit.
In an unattended run, which only the user turns on by starting the server
with `TRACK_UNATTENDED`, a replan applies without asking and flags the
project for review. Never set that variable yourself; a hook blocks it.

`track` on the command line only reads: `track --here` (what the
SessionStart hook prints), `track <project> --plain`, `track --json`. The
live view (`track` in a terminal) is the user's: `e`/`E` edit notes and the
plan in their editor, `p` promotes proposals, `d` then `y` deletes, `a`
clears an unattended replan's review flag.

Direct writes to `~/work/priv/plans` (Edit, Write, `sed -i`, `>`, git writes
there) are blocked by a hook. Reading with Read, cat, grep, `git log` or
`git config --get` is fine. Prose in `plan.md` (decisions, "Now", process) is
the user's to edit from the live view (`E`); when it must change, tell the
user what to change.

## When to write

- **Session start in a tracked repo:** the hook prints the wip tickets.
  Before working on one, `track_show` it and pick up from its last handoff
  instead of asking the user to re-explain.
- **After every step of a tracked ticket**, one `track_note`:
  - `handoff`: what happened and what is next — agent report summary, PR
    number, branch/worktree, checks run, the next concrete action. Write it so
    a fresh session (or a fork) can continue from it alone.
  - `decision`: what the user decided and why, in one or two lines.
  - `open`: an unresolved question, an unverified assumption, a deferred
    quirk, something a later ticket must remember.
  - `note`: anything else worth keeping.
  Notes about the project as a whole go to `track_note` without an id.
- **Status:** `track_set id wip` when work on it starts (headers drafted,
  agent sent), `done` when its last PR is merged, `hold` with the reason when
  it is blocked or the user defers it.
- **Subagents:** a brief may point the agent at `notes/<id>.md` (read-only
  for it). The agent does not write there; you summarise its report into a
  `handoff` note.

Notes are for the two of you: bullets, no prose, no pasted logs or diffs,
no restating the ticket. Link by reference (`#49`, `abc1234`,
`src/th07/player/chain.c:35`). One line per fact.
