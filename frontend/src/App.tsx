// repomind/frontend/src/App.tsx
import { useState } from 'react'
import { IngestPanel } from './components/IngestPanel'
import { ChatPanel } from './components/ChatPanel'
import { SourceViewer } from './components/SourceViewer'
import { Chunk } from './api/client'

export default function App() {
  const [sources, setSources] = useState<Chunk[]>([])
  const [ingested, setIngested] = useState(false)

  return (
    <div style={{
      display: 'flex', flexDirection: 'column', height: '100vh',
      background: '#0f172a', color: '#e2e8f0', fontFamily: 'system-ui, sans-serif'
    }}>
      <header style={{
        padding: '0.75rem 1.5rem', borderBottom: '1px solid #1e293b',
        display: 'flex', alignItems: 'center', gap: '1rem'
      }}>
        <span style={{ fontFamily: 'monospace', fontWeight: 700, fontSize: '1.1rem', color: '#60a5fa' }}>
          RepoMind
        </span>
        <span style={{ color: '#64748b', fontSize: '0.8rem' }}>
          local codebase Q&A · powered by Actian VectorAI DB
        </span>
      </header>

      <div style={{ flex: 1, display: 'flex', overflow: 'hidden' }}>
        <div style={{ width: 320, borderRight: '1px solid #1e293b', display: 'flex', flexDirection: 'column' }}>
          <IngestPanel onIngested={() => setIngested(true)} />
          {ingested && (
            <div style={{ padding: '0.5rem 1rem', color: '#4ade80', fontSize: '0.75rem', fontFamily: 'monospace' }}>
              ● Repo indexed. Ready.
            </div>
          )}
        </div>

        <div style={{ flex: 1, display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
          <ChatPanel onSources={setSources} />
        </div>

        <div style={{ width: 400, borderLeft: '1px solid #1e293b', overflow: 'hidden', display: 'flex', flexDirection: 'column' }}>
          <div style={{ padding: '0.5rem 0.75rem', borderBottom: '1px solid #1e293b', fontSize: '0.75rem', color: '#64748b' }}>
            SOURCE EXCERPTS
          </div>
          <SourceViewer chunks={sources} />
        </div>
      </div>
    </div>
  )
}
