import type { Register } from 'claude-code'
import { RULES, extractMessage, findProblems } from './message'

export const register: Register = on => {
  on('attribution.text', { kind: 'commit' }, () => ({ text: '' }))

  on('prompt.compose', async ($, e, next) => {
    const { sections } = await next(e)
    return {
      sections: [
        ...sections,
        { id: `${$.plugin.name}:rules`, text: RULES, scope: 'session' },
      ],
    }
  })

  on('tool.call', { tool: 'Bash' }, ($, e, next) => {
    const message = extractMessage(e.command)
    const problems = message === null ? [] : findProblems(message)
    return problems.length > 0
      ? {
          deny: `${$.plugin.name}: fix the commit message:\n- ${problems.join('\n- ')}`,
        }
      : next(e)
  }).catch(($, e, next) => next(e))
}
