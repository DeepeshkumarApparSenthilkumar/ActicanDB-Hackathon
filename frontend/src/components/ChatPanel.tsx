// repomind/frontend/src/components/ChatPanel.tsx
import { useState, useRef, useEffect } from 'react'
import { queryStream, Chunk } from '../api/client'

interface Message {
  role: 'user' | 'assistant'
  content: string
}

interface Props {
  onSources: (chunks: Chunk[]) => void
}

export function ChatPanel({ onSources }: Props) {
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState('')
  const [streaming, setStreaming] = useState(false)
  const cancelRef = useRef<(() => void) | null>(null)
  const bottomRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  function handleSend() {
    if (!input.trim() || streaming) return
    const question = input.trim()
    setInput('')
    setMessages(prev => [...prev, { role: 'user', content: question }])
    setStreaming(true)

    let assistantContent = ''
    setMessages(prev => [...prev, { role: 'assistant', content: '' }])

    const cancel = queryStream(
      question,
      (chunks) => onSources(chunks),
      (token) => {
        assistantContent += token
        setMessages(prev => {
          const next = [...prev]
          next[next.length - 1] = { role: 'assistant', content: assistantContent }
          return next
        })
      },
      () => setStreaming(false),
      (err) => {
        setMessages(prev => {
          const next = [...prev]
          next[next.length - 1] = { role: 'assistant', content: `Error: ${err.message}` }
          return next
        })
        setStreaming(false)
      }
    )
    cancelRef.current = cancel
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100%', background: '#0f172a' }}>
      <div style={{ flex: 1, overflowY: 'auto', padding: '1rem' }}>
        {messages.length === 0 && (
          <p style={{ color: '#64748b', textAlign: 'center', marginTop: '4rem', fontFamily: 'monospace' }}>
            Index a repo, then ask anything about it.
          </p>
        )}
        {messages.map((msg, i) => (
          <div key={i} style={{
            marginBottom: '1rem',
            display: 'flex',
            flexDirection: 'column',
            alignItems: msg.role === 'user' ? 'flex-end' : 'flex-start'
          }}>
            <div style={{
              maxWidth: '80%', padding: '0.75rem 1rem',
              background: msg.role === 'user' ? '#1e40af' : '#1e293b',
              borderRadius: 8, color: '#e2e8f0',
              fontFamily: msg.role === 'assistant' ? 'monospace' : 'inherit',
              fontSize: '0.875rem', lineHeight: 1.6,
              whiteSpace: 'pre-wrap'
            }}>
              {msg.content || (streaming && i === messages.length - 1 ? '▌' : '')}
            </div>
          </div>
        ))}
        <div ref={bottomRef} />
      </div>
      <div style={{ padding: '1rem', borderTop: '1px solid #1e293b', display: 'flex', gap: '0.5rem' }}>
        <input
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyDown={e => e.key === 'Enter' && !e.shiftKey && handleSend()}
          placeholder="Ask anything about the codebase..."
          disabled={streaming}
          style={{
            flex: 1, padding: '0.75rem', background: '#1e293b',
            border: '1px solid #334155', borderRadius: 4,
            color: '#e2e8f0', fontSize: '0.875rem'
          }}
        />
        <button
          onClick={handleSend}
          disabled={streaming || !input.trim()}
          style={{
            padding: '0.75rem 1.25rem', background: streaming ? '#475569' : '#3b82f6',
            border: 'none', borderRadius: 4, color: '#fff',
            cursor: streaming ? 'not-allowed' : 'pointer'
          }}
        >
          {streaming ? '...' : 'Ask'}
        </button>
      </div>
    </div>
  )
}
