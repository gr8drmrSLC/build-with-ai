import './MethodologyPanel.css'

const STEPS = [
  {
    number: '01',
    title: 'Frame the problem before writing a line',
    body: 'A project brief captures the goal, the constraints, and what success looks like. Written before any code, it becomes the handoff document between the high-context design conversation and the fresh executor context that builds. This document is what you\'re reading the output of right now.',
    principle: 'Ambiguity at the start compounds into rework at the end.',
  },
  {
    number: '02',
    title: 'Protect the repo before anything enters it',
    body: 'The .gitignore is the first commit — before README, before source, before anything. Secrets in git history require history rewriting. Once a key is pushed, rotation alone is insufficient. Prevention costs nothing; recovery costs hours and breaks collaborator clones.',
    principle: 'Security is a sequencing decision, not a feature.',
  },
  {
    number: '03',
    title: 'Design the system, then record why',
    body: 'Architecture Decision Records (ADRs) capture what was decided, what was rejected, and why. Not for documentation\'s sake, but for the next session, the next collaborator, or the next Claude context window that needs to understand the project without relitigating every choice.',
    principle: 'Decisions not recorded get made again, worse.',
  },
  {
    number: '04',
    title: 'Delegate execution, not judgment',
    body: 'The orchestrator (this conversation) stays lean: architecture, decisions, narrative, task ledger only. Everything executable gets delegated to a subagent born with exactly what it needs. Context compaction is real, and the orchestrator/subagent pattern routes around it.',
    principle: 'A subagent that closes carries nothing forward. That is the point.',
  },
  {
    number: '05',
    title: 'Change working code with a safety protocol',
    body: 'Eight steps: state what works, find the smallest change, map the blast radius, make the change, verify it works, verify nothing else broke, commit with a why-not-what message, update the status doc. AI agents are fast and confident — the protocol makes that safe.',
    principle: 'The most common failure is a good suggestion that silently breaks something adjacent.',
  },
  {
    number: '06',
    title: 'Keep memory in files, not conversation',
    body: 'PROJECT_STATUS.md, DECISIONS.md, and PROJECT_NARRATIVE.md survive context compaction. The conversation does not. Every session ends with these files updated. The next session starts by reading them. This repo is self-bootstrapping — a fresh session pointed at it can orient without verbal context.',
    principle: 'External memory is the only memory that compounds.',
  },
]

export default function MethodologyPanel() {
  return (
    <section className="panel methodology-panel" aria-label="The Framework">
      <p className="panel-label">The Framework</p>
      <p className="methodology-intro">
        Six practices that prevent the architecture failures behind most AI project breakdowns.
        Not invented here, but synthesized from ADRs, FinOps, OWASP, and the Well-Architected Framework
        and translated into PM/strategist language.
      </p>
      <ol className="steps-list">
        {STEPS.map(step => (
          <li key={step.number} className="step">
            <div className="step-header">
              <span className="step-number">{step.number}</span>
              <h3 className="step-title">{step.title}</h3>
            </div>
            <p className="step-body">{step.body}</p>
            <p className="step-principle">{step.principle}</p>
          </li>
        ))}
      </ol>
    </section>
  )
}
