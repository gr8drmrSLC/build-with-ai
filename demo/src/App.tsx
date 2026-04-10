import MethodologyPanel from './components/MethodologyPanel'
import OrchestratorPanel from './components/OrchestratorPanel'
import CaseStudyPanel from './components/CaseStudyPanel'
import './App.css'

export default function App() {
  return (
    <div className="app">
      <header className="app-header">
        <h1>build-with-ai</h1>
        <p className="tagline">
          A framework for AI-native project development — designed by a PM, built with agents
        </p>
        <a
          className="source-link"
          href="https://github.com/gr8drmrSLC/build-with-ai"
          target="_blank"
          rel="noreferrer"
        >
          View Source
        </a>
      </header>

      <main className="panels">
        <MethodologyPanel />
        <OrchestratorPanel />
        <CaseStudyPanel />
      </main>
    </div>
  )
}
