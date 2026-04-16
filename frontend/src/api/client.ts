// repomind/frontend/src/api/client.ts

export interface Chunk {
  file_path: string
  language: string
  content: string
  start_line: number
  end_line: number
  chunk_type: string
  score: number
}

export interface IngestResponse {
  files_processed: number
  chunks_indexed: number
}

export async function ingestRepo(path: string): Promise<IngestResponse> {
  const resp = await fetch('/ingest', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ path }),
  })
  if (!resp.ok) {
    const err = await resp.json()
    throw new Error(err.detail || 'Ingest failed')
  }
  return resp.json()
}

export function queryStream(
  question: string,
  onSources: (chunks: Chunk[]) => void,
  onToken: (token: string) => void,
  onDone: () => void,
  onError: (err: Error) => void,
): () => void {
  const controller = new AbortController()

  fetch('/query', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ question }),
    signal: controller.signal,
  }).then(async (resp) => {
    if (!resp.ok) throw new Error('Query failed')
    const reader = resp.body!.getReader()
    const decoder = new TextDecoder()
    let buffer = ''

    while (true) {
      const { done, value } = await reader.read()
      if (done) break
      buffer += decoder.decode(value, { stream: true })
      const lines = buffer.split('\n')
      buffer = lines.pop() || ''

      for (const line of lines) {
        if (line.startsWith('event: sources')) continue
        if (line.startsWith('event: token')) continue
        if (line.startsWith('event: done')) { onDone(); return }
        if (line.startsWith('data: ')) {
          const data = line.slice(6)
          try {
            const parsed = JSON.parse(data)
            if (Array.isArray(parsed)) {
              onSources(parsed as Chunk[])
            } else {
              onToken(data)
            }
          } catch {
            onToken(data)
          }
        }
      }
    }
    onDone()
  }).catch((err) => {
    if (err.name !== 'AbortError') onError(err)
  })

  return () => controller.abort()
}
