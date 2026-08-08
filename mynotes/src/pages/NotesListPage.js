import React, { useState, useEffect } from 'react'
// import notes from '../assets/data.js'
import ListItem from '../components/ListItem.js'
import AddButton from '../components/AddButton.js'

const NotesListPage = () => {
    let [notes, setNote] = useState([])
    let [searchQuery, setSearchQuery] = useState('')
    let [searchResults, setSearchResults] = useState(null)
    let [searching, setSearching] = useState(false)
    let [searchError, setSearchError] = useState(null)

    useEffect(() => {
        getNotes()
    }, []) // fires once when the component is mounted

    let getNotes = async () => {
        let response = await fetch('/api/notes/')
        let data = await response.json()
        console.log(data)
        setNote(data)
    }

    // debounce: only search 400ms after the user stops typing
    useEffect(() => {
        if (!searchQuery.trim()) {
            setSearchResults(null)
            setSearchError(null)
            setSearching(false)
            return
        }
        setSearching(true)
        setSearchError(null)
        let timeoutId = setTimeout(async () => {
            try {
                let response = await fetch(`/api/notes/search/?q=${encodeURIComponent(searchQuery)}`)
                if (!response.ok) {
                    let err = await response.json().catch(() => ({}))
                    setSearchError(err.error || 'Search unavailable')
                    setSearchResults([])
                    return
                }
                let data = await response.json()
                setSearchResults(data)
            } catch (e) {
                setSearchError('Network error')
                setSearchResults([])
            } finally {
                setSearching(false)
            }
        }, 400)
        return () => clearTimeout(timeoutId)
    }, [searchQuery])

    let displayedNotes = searchResults !== null ? searchResults : notes

    return (
        <div className='notes'>
            <div className="notes-header">
                <h2 className="notes-title">
                    &#9782; Notes
                </h2>
                <p className="notes-count">{notes.length}</p>
            </div>
            <div className="search-bar">
                <input
                    type="text"
                    placeholder="Search notes by meaning..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                />
                {searching && <span className="search-status">Searching...</span>}
            </div>
            {searchError && <p className="search-error">{searchError}</p>}
            <div className='notes-list'>
                {displayedNotes.map((note,index) => {
                    return (
                        <div className='note-preview' key={index}>
                            <ListItem note={note}/>
                        </div>
                    )
                })}
                {searchResults !== null && !searching && !searchError && searchResults.length === 0 && (
                    <p className="search-empty">No notes matched "{searchQuery}"</p>
                )}
            </div>
            <AddButton/>
        </div>
    )
}

export default NotesListPage
