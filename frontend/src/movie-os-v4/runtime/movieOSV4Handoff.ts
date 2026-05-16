import type { MovieOSV4Response } from '../../types/movie-os-v4'

export function readMovieOSV4Handoff(): MovieOSV4Response | null {
  const encoded = new URLSearchParams(window.location.search).get('movie_os_v4')
  if (!encoded) return null

  try {
    return JSON.parse(decodeURIComponent(encoded)) as MovieOSV4Response
  } catch {
    return null
  }
}
