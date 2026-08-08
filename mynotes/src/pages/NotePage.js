import React, { useEffect, useState } from 'react'
import { useParams,useNavigate,Link } from 'react-router-dom'
// import notes from '../assets/data.js'
import { ReactComponent as ArrowLeft } from '../assets/arrow-left.svg'

const NotePage = () => {
  let { id }  = useParams();
  let navigate = useNavigate()
  let [note, setNote] = useState({})

  let [summary, setSummary] = useState(null)
  let [summarizing, setSummarizing] = useState(false)
  let [summarizeError, setSummarizeError] = useState(null)

  let [suggestion, setSuggestion] = useState(null)
  let [improving, setImproving] = useState(false)
  let [improveError, setImproveError] = useState(null)

  let [regenerating, setRegenerating] = useState(false)
  let [regenerateError, setRegenerateError] = useState(null)

  useEffect(() => {
    let getNote = async () => {
      if (id === 'new') return
      let response = await fetch(`/api/notes/${id}`)
      let data = await response.json()
      console.log(data)
      setNote(data)
    }
    getNote()
  }, [id])

  let createNote = async () => {
    await fetch(`/api/notes/create/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({...note, 'updated': new Date()})
    })
  }

  let updateNote = async () => {
    await fetch(`/api/notes/${id}/update/`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({...note, 'updated': new Date()})
    })
  }

  let deleteNote = async () => {
    await fetch(`/api/notes/${id}/delete/`, {
      method: 'DELETE'
    })
    navigate('/')
  }

  let handleSubmit = () => {
    if (id !== 'new' && !note.body) {
      deleteNote()
    } else if (id !== 'new') {
      updateNote()
    } else if (id ==='new' && note !== null) {
      createNote()
    }
    navigate('/')
  }

  let handleSummarize = async () => {
    setSummarizing(true)
    setSummarizeError(null)
    setSummary(null)
    try {
      let response = await fetch(`/api/notes/${id}/summarize/`, { method: 'POST' })
      let data = await response.json()
      if (!response.ok) {
        setSummarizeError(data.error || 'Summarization unavailable')
        return
      }
      setSummary(data.summary)
    } catch (e) {
      setSummarizeError('Network error')
    } finally {
      setSummarizing(false)
    }
  }

  let handleImprove = async () => {
    setImproving(true)
    setImproveError(null)
    setSuggestion(null)
    try {
      let response = await fetch(`/api/notes/${id}/improve/`, { method: 'POST' })
      let data = await response.json()
      if (!response.ok) {
        setImproveError(data.error || 'Improve writing unavailable')
        return
      }
      setSuggestion(data.suggestion)
    } catch (e) {
      setImproveError('Network error')
    } finally {
      setImproving(false)
    }
  }

  let acceptSuggestion = () => {
    setNote({...note, body: suggestion})
    setSuggestion(null)
  }

  let discardSuggestion = () => {
    setSuggestion(null)
  }

  let handleRegenerateTags = async () => {
    setRegenerating(true)
    setRegenerateError(null)
    try {
      let response = await fetch(`/api/notes/${id}/regenerate-tags/`, { method: 'POST' })
      let data = await response.json()
      if (!response.ok) {
        setRegenerateError(data.error || 'AI title/tag generation unavailable')
        return
      }
      setNote({...note, title: data.title, tags: data.tags})
    } catch (e) {
      setRegenerateError('Network error')
    } finally {
      setRegenerating(false)
    }
  }

  return (
    <div className='note'>
      <div className="note-header">
        <h3>
          <Link to='/'>
            <ArrowLeft onClick={handleSubmit} />
          </Link>
        </h3>
        {id !== 'new' ? (
          <button onClick={deleteNote}>Delete</button>
        ):(
          <button onClick={handleSubmit}>Save</button>
        )}
      </div>

      <div className="note-body">
        {id !== 'new' && (
          <input
            className="note-title-input"
            type="text"
            placeholder="Title"
            value={note.title || ''}
            onChange={(e) => setNote({...note, title: e.target.value})}
          />
        )}
        {id !== 'new' && note.tags && note.tags.length > 0 && (
          <div className="note-tags">
            {note.tags.map((tag, i) => <span className="tag-chip" key={i}>{tag}</span>)}
          </div>
        )}

        {id !== 'new' && (
          <div className="ai-actions">
            <button onClick={handleSummarize} disabled={summarizing}>
              {summarizing ? 'Summarizing...' : 'Summarize'}
            </button>
            <button onClick={handleImprove} disabled={improving}>
              {improving ? 'Improving...' : 'Improve writing'}
            </button>
            <button onClick={handleRegenerateTags} disabled={regenerating}>
              {regenerating ? 'Regenerating...' : 'Regenerate title & tags'}
            </button>
          </div>
        )}

        {summarizeError && <p className="ai-error">{summarizeError}</p>}
        {summary && (
          <div className="ai-panel">
            <p className="ai-panel-label">Summary</p>
            <p>{summary}</p>
            <button className="ai-panel-dismiss" onClick={() => setSummary(null)}>Dismiss</button>
          </div>
        )}

        {improveError && <p className="ai-error">{improveError}</p>}
        {suggestion && (
          <div className="ai-panel">
            <p className="ai-panel-label">Suggested rewrite</p>
            <p className="ai-suggestion-text">{suggestion}</p>
            <div className="ai-panel-buttons">
              <button onClick={acceptSuggestion}>Accept</button>
              <button onClick={discardSuggestion}>Discard</button>
            </div>
          </div>
        )}

        {regenerateError && <p className="ai-error">{regenerateError}</p>}

        <textarea onChange={(e) => {setNote({...note, 'body':e.target.value})}} value={note.body || ''}>
        </textarea>
      </div>
    </div>
  )
}

export default NotePage
