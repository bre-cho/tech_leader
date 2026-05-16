import type { MovieDirectorResponse } from '../../types/movie-os-v3'

export function readMovieHandoff(): MovieDirectorResponse | null {
  const encoded = new URLSearchParams(window.location.search).get('movie_handoff')
  if (!encoded) return null

  try {
    return JSON.parse(decodeURIComponent(encoded)) as MovieDirectorResponse
  } catch {
    return null
  }
}
