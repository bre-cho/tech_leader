# OPTIONAL REACT CLASS PATCH

Nếu dev muốn chuẩn hơn, nên thêm class cho các button quan trọng:

```tsx
<button className="open-video-studio">Open Video Studio (5173)</button>
```

Button phụ:

```tsx
<button className="secondary">Test OpenRouter</button>
```

Button nguy hiểm:

```tsx
<button className="danger">Remove Account</button>
```

Form account:

```tsx
<div className="google-account-row">
  <input placeholder="Account label" />
  <input placeholder="Gemini API key" />
  <button>Add Account</button>
</div>

<div className="rotation-row">
  <button>Rotation: OFF</button>
  <button>Per Scene: OFF</button>
</div>
```

Nếu component nào đang vỡ layout vì input nằm chung hàng quá dài, bọc bằng:

```tsx
<div className="form">
  ...
</div>
```
