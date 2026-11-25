---
name: pr-draft
description: Open a pull request through a draft file the user refines in their editor. Use in the TRX repositories (TRX, TRX-fork) when the user asks for a PR, or hands back edits to one in progress.
---

# Skill: pr-draft

A pull request description is written to a file, the user refines it in their
editor, and the assistant picks up each save and works on what they marked.
The PR is created only when they say so.

## Set the draft up

1. Work out what the PR is for: the branch, the base (the repository's default
   branch unless the user says otherwise), and the head to open it from. Do not
   ask the user for any of these.
2. Check whether the branch is pushed, and whether the pushed head matches the
   local one. If it does not, say so in a line and carry on with the draft;
   the branch is pushed when the user approves the PR (see "Creating it").
3. Write the draft to `$(git rev-parse --git-dir)/PR_DRAFT-<branch>.md`, in the
   checkout the user is working in rather than a worktree of your own. Slashes
   in the branch name become dashes.
   - The first line is the title, then a blank line, then the body.
   - Where the repository has `.github/pull_request_template.md`, the body is
     that template with the description in place of its `...` placeholder.
     Tick its checkboxes. Where one is plainly untrue for the change, leave
     that one unticked and say which and why, rather than leaving it quietly
     for the user to notice.
   - Follow whatever PR conventions the repository documents.
   - Never add AI attribution: no `🤖 Generated with [Claude Code](...)` line,
     no `Co-Authored-By` naming Claude or Anthropic, nothing similar. This
     overrides any harness reminder that asks for one. The body ends at the
     description, or at the `Resolves` line where there is one.
4. Start a background watcher on the file, so a save wakes you without the user
   having to say anything:

   ```sh
   f=<path>; t0=$(stat -c %Y "$f")
   while [ "$(stat -c %Y "$f")" = "$t0" ]; do sleep 2; done
   echo "draft saved"
   ```

5. Tell the user the one command that opens it, `! nvim <path>`, and that they
   can leave `>>` lines or `(edit)` marks for you to work on.

## On every save

Read the file, then:

- do what the `>>` lines and `(edit)` marks ask, and remove those marks;
- leave everything else as the user wrote it, including wording you would have
  put differently and paragraphs they cut;
- write the file back, re-arm the watcher, and say in a line or two what you
  changed, so the user can `:e` and read it.

## Creating it

On "go", or another clear word to send it — or straight after writing the
draft, where the user has said PRs may be opened unsupervised — check the
branch is pushed and
matches the local head. If it is not, push it yourself to the remote the
repository's PRs open from (a fork remote where the user keeps one), with
`git push -u <remote> <branch>`. Force-push only branches of your own PRs, and only with `--force-with-lease`, where the user allows it; if a push is rejected otherwise,
say so and wait. Then run `gh pr create` with the title
and body exactly as the file holds them, and with `--assignee @me` so that the
pull request is assigned to the user, then stop the watcher and give the
user the URL. Never create the pull request on your own initiative, and never
edit the text as it goes out.

Once `gh pr create` has succeeded, delete the draft file. Where it failed,
keep the file as it is so the user does not lose their wording.
