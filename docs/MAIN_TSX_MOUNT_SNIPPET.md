# frontend/src/main.tsx mount snippet

Thêm vào `frontend/src/main.tsx`:

```tsx
import FashionMovieStudio from './pages/FashionMovieStudio'

const rootElement = document.getElementById('root')!
const root = ReactDOM.createRoot(rootElement)
const params = new URLSearchParams(window.location.search)

if (params.has('fashion_handoff')) {
  root.render(
    <React.StrictMode>
      <FashionMovieStudio />
    </React.StrictMode>
  )
} else {
  root.render(
    <React.StrictMode>
      <DesignStudio />
    </React.StrictMode>
  )
}
```

Nếu repo đã có nhánh `movie_handoff` hoặc `creative_handoff`, thêm `fashion_handoff` vào trước nhánh mặc định.
