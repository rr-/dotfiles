import { describe, expect, test } from 'claude-code/testing'

const commit = (message: string): string =>
  `git commit -m "$(cat <<'EOF'\n${message}\nEOF\n)"`

describe('commit-style', () => {
  test('drops the commit attribution', async $ => {
    const { text } = await $.attribution.text({
      kind: 'commit',
      text: 'Co-Authored-By: Claude <noreply@anthropic.com>',
    })
    expect(text).toBe('')
  })

  test('lets a well-formed commit through', async ($, on) => {
    on('tool.call', () => ({ result: 'ok' }))
    const result = await $.tool.call({
      tool: 'Bash',
      command: commit(
        'cfg/tmux: give panes an explicit foreground\n\nSets the pane foreground so programs read the theme.',
      ),
    })
    expect(result.deny).toBeUndefined()
  })

  test('lets other commands through', async ($, on) => {
    on('tool.call', () => ({ result: 'ok' }))
    const result = await $.tool.call({ tool: 'Bash', command: 'git status' })
    expect(result.deny).toBeUndefined()
  })

  for (const [name, command] of [
    ['a trailer', commit('fix layout\n\nCo-Authored-By: Claude <x@y.z>')],
    ['a conventional prefix', commit('feat(ui): add dark mode')],
    ['a long subject', `git commit -m '${'x'.repeat(51)}'`],
    ['a missing blank line', commit('fix layout\nMoves things.')],
    ['a long body line', commit(`fix layout\n\n${'word '.repeat(20)}`)],
  ]) {
    test(`denies ${name}`, async $ => {
      const result = await $.tool.call({ tool: 'Bash', command })
      expect(result.deny).toBeDefined()
    })
  }
})
