const SUBJECT_MAX = 50
const BODY_MAX = 72

const CONVENTIONAL =
  /^(feat|fix|docs|style|refactor|perf|tests?|build|ci|chore|revert)(\([^)]*\))?!?:/i
const TRAILER = /^co-authored-by:/im
const GIT_COMMIT = /\bgit\b(\s+-\S+(\s+[^-\s]\S*)?)*\s+commit\b/
const HEREDOC = /<<-?\s*(['"]?)(\w+)\1[^\n]*\n([\s\S]*?)\n\s*\2\b/
const MESSAGE_FLAG =
  /(?:^|\s)(?:-m|--message)(?:=|\s+)("((?:[^"\\]|\\.)*)"|'([^']*)')/g

export const RULES = `\
When writing a git commit message:
- The subject is "scope: summary in imperative mood", e.g. \
"cfg/tmux: give panes an explicit foreground". Use a scope when the \
repository's history uses them; never a conventional commits type such as \
"feat:", "fix:" or "chore(x):".
- The subject is at most ${SUBJECT_MAX} characters, with no trailing period.
- If a body is needed, leave a blank line after the subject, then write the \
body in third person ("Moves the search box so it no longer..."), wrapped \
at ${BODY_MAX} characters.
- Never add a Co-Authored-By trailer or any other attribution lines.`

const unescapeDouble = (text: string): string =>
  text.replace(/\\([\\"$`])/g, '$1')

/** The message a `git commit` command passes inline, or null if none. */
export const extractMessage = (command: string): string | null => {
  if (!GIT_COMMIT.test(command)) {
    return null
  }
  const heredoc = HEREDOC.exec(command)
  if (heredoc) {
    return heredoc[3]
  }
  const parts = [...command.matchAll(MESSAGE_FLAG)].map(m =>
    m[2] !== undefined ? unescapeDouble(m[2]) : m[3],
  )
  return parts.length > 0 ? parts.join('\n\n') : null
}

/** Why the message breaks the house style, one line per problem. */
export const findProblems = (message: string): string[] => {
  const lines = message.trim().split('\n')
  const subject = lines[0].trim()
  const problems: string[] = []

  if (TRAILER.test(message)) {
    problems.push('remove the Co-Authored-By trailer')
  }
  if (CONVENTIONAL.test(subject)) {
    problems.push(
      'do not use conventional commits; write "scope: imperative summary"',
    )
  }
  if (subject.length > SUBJECT_MAX) {
    problems.push(
      `shorten the subject to ${SUBJECT_MAX} characters (it has ${subject.length})`,
    )
  }
  if (lines.length > 1 && lines[1].trim() !== '') {
    problems.push('leave a blank line between the subject and the body')
  }
  const longLines = lines
    .slice(1)
    .filter(line => line.length > BODY_MAX && /\s/.test(line.trim()))
  if (longLines.length > 0) {
    problems.push(
      `wrap the body at ${BODY_MAX} characters (${longLines.length} line(s) are longer)`,
    )
  }
  return problems
}
