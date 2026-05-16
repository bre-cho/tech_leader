import React from 'react'
import ReactDOM from 'react-dom/client'
import MovieStudioV3 from '../../pages/MovieStudioV3'
import '../../styles/movie-os-v3.css'

export function mountMovieStudioV3IfNeeded(rootElement: HTMLElement) {
  const params = new URLSearchParams(window.location.search)

  if (!params.has('movie_handoff')) {
    return false
  }

  ReactDOM.createRoot(rootElement).render(
    <React.StrictMode>
      <MovieStudioV3 />
    </React.StrictMode>
  )

  return true
}
