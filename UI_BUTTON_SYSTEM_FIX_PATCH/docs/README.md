# UI_BUTTON_SYSTEM_FIX_PATCH

## Mục tiêu

Sửa CSS cho toàn bộ button/input/select/textarea trong các trang:

- Brand Studio
- Upscale
- Beauty Commerce
- Beauty Commerce V28
- Beauty Intelligence
- Beauty Avatar
- Storyboard V30 / V31
- HiDream Commercial
- Color Intelligence
- AI Engine Settings
- Pipeline OS
- Movie Director / Creative OS

## Vấn đề hiện tại

Nhiều trang vẫn đang dùng style mặc định của browser:

- button nền trắng, chữ đen
- input/select quá sát nhau
- textarea nhỏ, bị vỡ layout
- button không đồng bộ với sidebar/card
- form nằm ngang bị dính chữ
- thiếu hover/focus/disabled state
- thiếu responsive wrapping

## Cách áp dụng nhanh

Copy file:

```text
frontend-next/app/ui-button-system.css
```

vào project Next.js.

Sau đó import trong:

```text
app/globals.css
```

thêm dòng:

```css
@import "./ui-button-system.css";
```

Hoặc nếu project dùng CSS global ở root:

```css
@import "@/app/ui-button-system.css";
```

## Nếu muốn áp dụng cho Vite

Copy:

```text
frontend-vite/src/styles/ui-button-system.css
```

vào Vite frontend, rồi import trong:

```tsx
import './styles/ui-button-system.css'
```

## Ghi chú

Patch này dùng selector global an toàn:

```css
button:not(.unstyled)
input
select
textarea
```

Nếu có button nào không muốn áp dụng style này, thêm class:

```tsx
className="unstyled"
```
