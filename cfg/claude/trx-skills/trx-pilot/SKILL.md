---
name: trx-pilot
description: Pilot rr-'s open TRX pull requests and work the current tracker milestone through one resident worker — 30-minute review rounds, merges under the lahm + aredfan approval rules, just-in-time rebases, stacked PRs, review-comment fixes, ticket status. Use when the user asks to pilot, babysit, shepherd or merge the TRX PRs, to "resume" the pilot, or to work through the milestone tickets.
---

# Skill: trx-pilot

Keep every open `rr-` PR on LostArtefacts/TRX moving to merge, and feed the
current milestone's tickets through one resident worker. Scripts live in
`scripts/` next to this file (`S=<this dir>/scripts`); scratch (worktrees,
round state) goes in `/tmp/claude-1000`.

## Rules

- **Merge** only with approvals from both `lahm86` (code) and `aredfan`
  (QA) on the current code. A pure rebase or refactor needs no new QA. A
  code change after lahm's approval needs lahm or the user to OK it; ask on
  the PR.
- **Stacked PRs** ("Stacked on #N" in the body) merge after their base.
  Never let a stacked commit undo a line its base wrote; if the base has no
  reviews yet, fold the change into the base instead.
- **Rebase just in time**: right before merging, or when a PR's build is
  stale and cannot build. Do not rebase every conflicting PR after each
  merge; changelog conflicts come back every time.
- **Push** only to `fork` (rr-/TRX), force-push with lease. GPG-signed
  commits, no trailers. Never push to origin.
- **Tickets** (trx-tracker): In Review while the PR is open, Done only after
  the merge. File every deferred item ("later") at once: assignee 1,
  milestone = current, with the findings in the description.
- **Work only current-milestone tickets.** New tickets the user names go to
  the front of the queue.
- **Never write under `test/`**, never copy or symlink game data.
- **Rounds** every 30 minutes and never before 08:00. After
  midnight, one background sleep until 08:00. Ending a turn is fine only
  while a background wait for the next round is armed.

## A round

1. Run `zsh $S/round.sh` and read the **whole** output — never `tail` it;
   review comments get lost that way. It prints new comments, reviews and
   inline notes since the last round, the double-approved PRs with
   approval times and stack base, and the non-mergeable PRs.
2. For each double-approved PR, check that both approvals post-date the
   last code change (not a pure rebase). Then merge in dependency order
   with the train (background):
   ```
   zsh $S/train.sh 7199:tr4/foo 7209:tr4/bar 7217:tr4/baz:7209 ...
   ```
   `pr:branch[:base_pr]`; a PR whose base failed is skipped. Each step is
   `rmerge.sh`: rebase onto develop with autosquash and union changelog,
   check changelog lines, fixups and signatures, push, wait for CI and
   MERGEABLE CLEAN, `gh pr merge --rebase`. It flags edited changelog lines
   as removals; check those by hand and merge manually.
3. Set merged PRs' tickets to Done.
4. Route review comments: nits and small fixes to the resident worker
   (fixup commits on the branch, autosquash, push with lease, then reply on
   the PR); questions and design calls to the user; QA findings that are
   out of scope become tickets.
5. Arm the next wait: `sleep 1800` in the background (after midnight: sleep
   until 08:00).

## Rebasing without merging

- `zsh $S/rbase.sh <pr> <branch> <oldbase> <newbase>` — move a branch.
- `bash $S/rbcat.sh <pr> <branch> [oldbase]` — onto develop, resolving TR4
  catalog conflicts (`keepboth.py` for objects.def, names.def, samples,
  generator aliases; `sortboth.py` for meson.build; regenerated catalog
  CSV/CATALOG.md folded into the commit that touches objects.def). Then
  build, test, push. Other conflicts stop it; resolve them by hand.
- `$S/attr` (`docs/CHANGELOG.md merge=union`) keeps both sides of changelog
  conflicts. It also re-adds lines a fixup removes, so never use it for a
  fixup that deletes a changelog line. It can also leave a PR's "Added"
  lines after develop's newer "Changed"/"Fixed" lines, which CI's changelog
  guard rejects; rebuild each commit's tree with `scripts/clorder.py`
  (stable sort Added, Changed, Fixed per [Unreleased] subsection) and
  `git commit-tree -S`, keeping author and message. `rbase.sh` and `rbcat.sh`
  run this as `scripts/clfix.sh <base>` after every rebase.
- When `rbcat.sh` reports "autosquash failed", the folded regenerated files
  (CATALOG.md and friends) collide with a later commit. Abort the rebase in
  its worktree and run `scripts/regen-each.sh origin/develop HEAD~1`: it
  rebuilds each commit with its own regenerated files and a clean `prek`,
  dropping the fold commit. Then build, test and push by hand.

## Tickets through the resident worker

- One worker for the whole session, ever: spawn it once (`worker` agent
  type), then give it each next ticket with `SendMessage`. Never spawn a
  second, never respawn per ticket. If its context gets very large, ask the
  user before replacing it.
- Brief per ticket: the ticket text, the retail reference (`../tr04` etc.),
  the worktree (`git worktree add /tmp/claude-1000/wt-<n> -b <branch>
  <base>`; stack on an open PR's `fork/<branch>` when it depends on it),
  commit rules (CLAUDE.md, one fix per commit, `Resolves TRX<n>`), checks
  (`prek -a`, `myjust test`, `lua-api-check` when the Lua API changes), and
  "no push, no PR; report a draft title and body with a Testing section".
- When it reports, review the result before publishing. Look for:
  duplicated mechanisms (grep for what TR1–3 already do before accepting a
  new API), changelog lines that repeat another PR's, and stacked commits
  that undo their base.
- Then push the branch to `fork`, open the PR with `gh pr create --assignee
  @me`, the template checklist ticked, "Stacked on #N" where stacked, and
  request `lahm86` and `aredfan`. Set the ticket In Review, remove the
  worktree, and file the worker's "not done" items as tickets.
- Cleanup: list the exact worktrees to remove; never delete one a worker
  is using.

## Handing over

When the user pauses, stop all sleepers and write the state to memory:
open PRs and what each waits on, stacks, the queue, the worker's agent id.
