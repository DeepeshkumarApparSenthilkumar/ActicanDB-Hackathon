// repomind/frontend/src/components/IngestPanel.tsx
import { useState } from 'react'
import { ingestRepo, IngestResponse } from '../api/client'

interface Props {
  onIngested: () => void
}

export function IngestPanel({ onIngested }: Props) {
  const [path, setPath] = useState('')
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState<IngestResponse | null>(null)
  const [error, setError] = useState('')

  async function handleIngest() {
    if (!path.trim()) return
    setLoading(true)
    setError('')
    setResult(null)
    try {
      const res = await ingestRepo(path.trim())
      setResult(res)
      onIngested()
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : 'Unknown error')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div style={{ padding: '1rem', borderBottom: '1px solid #333' }}>
      <h2 style={{ marginTop: 0, color: '#e2e8f0', fontSize: '1rem' }}>Ingest Repository</h2>
      <div style={{ display: 'flex', gap: '0.5rem' }}>
        <input
          value={path}
          onChange={e => setPath(e.target.value)}
          onKeyDown={e => e.key === 'Enter' && handleIngest()}
          placeholder="/path/to/repo"
          disabled={loading}
          style={{
            flex: 1, padding: '0.5rem', background: '#1e293b',
            border: '1px solid #475569', borderRadius: 4,
            color: '#e2e8f0', fontFamily: 'monospace', fontSize: '0.875rem'
          }}
        />
        <button
          onClick={handleIngest}
          disabled={loading || !path.trim()}
          style={{
            padding: '0.5rem 1rem', background: loading ? '#475569' : '#3b82f6',
            border: 'none', borderRadius: 4, color: '#fff',
            cursor: loading ? 'not-allowed' : 'pointer', fontSize: '0.875rem'
          }}
        >
          {loading ? 'Indexing...' : 'Index'}
        </button>
      </div>
      {error && <p style={{ color: '#f87171', margin: '0.5rem 0 0', fontSize: '0.8rem' }}>{error}</p>}
      {result && (
        <p style={{ color: '#4ade80', margin: '0.5rem 0 0', fontSize: '0.8rem' }}>
          Indexed {result.chunks_indexed} chunks from {result.files_processed} files
        </p>
      )}
    </div>
  )
}
