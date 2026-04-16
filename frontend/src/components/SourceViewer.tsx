// repomind/frontend/src/components/SourceViewer.tsx
import { Chunk } from '../api/client'
import SyntaxHighlighter from 'react-syntax-highlighter'
import { atomOneDark } from 'react-syntax-highlighter/dist/esm/styles/hljs'

interface Props {
  chunks: Chunk[]
}

const LANG_MAP: Record<string, string> = {
  python: 'python', typescript: 'typescript', javascript: 'javascript',
  go: 'go', rust: 'rust', java: 'java', cpp: 'cpp', c: 'c', markdown: 'markdown',
}

export function SourceViewer({ chunks }: Props) {
  if (chunks.length === 0) {
    return (
      <div style={{ padding: '1rem', color: '#64748b', fontFamily: 'monospace', fontSize: '0.8rem' }}>
        Source excerpts will appear here after a query.
      </div>
    )
  }

  return (
    <div style={{ overflowY: 'auto', height: '100%' }}>
      {chunks.map((chunk, i) => (
        <div key={i} style={{ borderBottom: '1px solid #1e293b', padding: '0.75rem' }}>
          <div style={{
            fontSize: '0.75rem', color: '#94a3b8', fontFamily: 'monospace',
            marginBottom: '0.25rem', display: 'flex', justifyContent: 'space-between'
          }}>
            <span>{chunk.file_path}</span>
            <span>lines {chunk.start_line}–{chunk.end_line} · score {chunk.score.toFixed(2)}</span>
          </div>
          <SyntaxHighlighter
            language={LANG_MAP[chunk.language] || 'text'}
            style={atomOneDark}
            customStyle={{ margin: 0, borderRadius: 4, fontSize: '0.8rem' }}
            showLineNumbers
            startingLineNumber={chunk.start_line}
          >
            {chunk.content}
          </SyntaxHighlighter>
        </div>
      ))}
    </div>
  )
}
