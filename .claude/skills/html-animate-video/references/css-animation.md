# CSS Animation Reference

Quick reference for CSS-based animations. Use CSS for simple text effects, transforms,
and transitions. For complex particle systems or programmatic effects, use Canvas/JS.

## Transitions

```css
.element {
  transition: property duration timing-function delay;
  /* Multiple properties */
  transition: opacity 0.3s ease, transform 0.5s ease-out 0.1s;
  /* All animatable properties */
  transition: all 0.3s ease;
}

/* Trigger by adding class */
.element.active {
  opacity: 1;
  transform: scale(1);
}
```

### Animatable Properties

Common animatable CSS properties:
- `opacity`, `transform`, `background-color`, `color`
- `width`, `height`, `top`, `left`, `right`, `bottom`
- `margin`, `padding`, `border-width`, `border-radius`
- `font-size`, `font-weight`, `letter-spacing`, `line-height`
- `box-shadow`, `text-shadow`, `filter`
- `clip-path`

## @keyframes

```css
@keyframes fadeIn {
  from { opacity: 0; }
  to   { opacity: 1; }
}

@keyframes slideUp {
  from { transform: translateY(100px); opacity: 0; }
  to   { transform: translateY(0); opacity: 1; }
}

@keyframes pulse {
  0%, 100% { transform: scale(1); }
  50%      { transform: scale(1.05); }
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* Multi-step */
@keyframes bounce {
  0%   { transform: translateY(0); }
  30%  { transform: translateY(-30px); }
  50%  { transform: translateY(0); }
  70%  { transform: translateY(-15px); }
  100% { transform: translateY(0); }
}
```

### Applying Keyframes

```css
.element {
  animation: name duration timing-function delay iteration-count direction fill-mode;
  /* Example */
  animation: fadeIn 1s ease-out 0.5s 1 normal forwards;
  /* Shorthand breakdown */
  animation-name: fadeIn;
  animation-duration: 1s;
  animation-timing-function: ease-out;
  animation-delay: 0.5s;
  animation-iteration-count: 1;
  animation-direction: normal;
  animation-fill-mode: forwards;
}
```

### animation-fill-mode

| Value | Description |
|-------|-------------|
| `none` | Default, element reverts after animation |
| `forwards` | Retain end state after animation |
| `backwards` | Apply start state during delay |
| `both` | Both forwards and backwards |

### animation-direction

| Value | Description |
|-------|-------------|
| `normal` | Forward each cycle |
| `reverse` | Backward each cycle |
| `alternate` | Forward then backward |
| `alternate-reverse` | Backward then forward |

## Easing Functions

### Named Easings

| Name | Feel |
|------|------|
| `ease` | Default, fast start, slow end |
| `ease-in` | Slow start, fast end |
| `ease-out` | Fast start, slow end (most natural) |
| `ease-in-out` | Slow start and end |
| `linear` | Constant speed |

### cubic-bezier Presets

```css
/* Ease Out Quad */
transition-timing-function: cubic-bezier(0.25, 0.46, 0.45, 0.94);

/* Ease Out Cubic */
transition-timing-function: cubic-bezier(0.33, 1, 0.68, 1);

/* Ease Out Quart */
transition-timing-function: cubic-bezier(0.25, 1, 0.5, 1);

/* Ease Out Expo */
transition-timing-function: cubic-bezier(0.16, 1, 0.3, 1);

/* Ease In Back (overshoot) */
transition-timing-function: cubic-bezier(0.36, 0, 0.66, -0.56);

/* Ease Out Back */
transition-timing-function: cubic-bezier(0.34, 1.56, 0.64, 1);

/* Ease Out Elastic (approximation) */
transition-timing-function: cubic-bezier(0.68, -0.6, 0.32, 1.6);
```

## Transform

```css
/* Combine transforms in order: scale → rotate → translate */
transform: scale(1.2) rotate(45deg) translateX(100px);

/* Individual transforms */
transform: translateX(50px);
transform: translateY(-20px);
transform: translate(50px, -20px);
transform: rotate(45deg);
transform: rotateX(45deg);  /* 3D */
transform: rotateY(45deg);  /* 3D */
transform: scale(1.5);
transform: scaleX(2);
transform: skew(10deg, 5deg);

/* Transform origin */
transform-origin: center center;  /* default */
transform-origin: top left;
transform-origin: 50% 100%;      /* bottom center */
```

## Text Animation Recipes

### Typewriter Effect

```css
@keyframes typewriter {
  from { width: 0; }
  to   { width: 100%; }
}

@keyframes blink {
  50% { border-color: transparent; }
}

.typewriter-text {
  overflow: hidden;
  white-space: nowrap;
  border-right: 2px solid #fff;
  animation:
    typewriter 2s steps(20) forwards,
    blink 0.5s step-end infinite;
}
```

### Text Gradient Animation

```css
@keyframes gradientShift {
  0%   { background-position: 0% 50%; }
  100% { background-position: 100% 50%; }
}

.gradient-text {
  background: linear-gradient(90deg, #6366f1, #ec4899, #f59e0b, #6366f1);
  background-size: 300% 100%;
  -webkit-background-clip: text;
  background-clip: text;
  -webkit-text-fill-color: transparent;
  animation: gradientShift 3s linear infinite;
}
```

### Letter Stagger

```css
@keyframes letterIn {
  from { opacity: 0; transform: translateY(20px); }
  to   { opacity: 1; transform: translateY(0); }
}

.stagger-text span {
  display: inline-block;
  opacity: 0;
  animation: letterIn 0.5s ease-out forwards;
}

/* Apply via nth-child or inline style */
.stagger-text span:nth-child(1) { animation-delay: 0.0s; }
.stagger-text span:nth-child(2) { animation-delay: 0.05s; }
.stagger-text span:nth-child(3) { animation-delay: 0.1s; }
/* ... etc */
```

### Text Scale In

```css
@keyframes scaleIn {
  from { transform: scale(0); opacity: 0; }
  to   { transform: scale(1); opacity: 1; }
}

.scale-in {
  animation: scaleIn 0.6s cubic-bezier(0.34, 1.56, 0.64, 1) forwards;
}
```

## Filter Animations

```css
@keyframes blurIn {
  from { filter: blur(20px); opacity: 0; }
  to   { filter: blur(0); opacity: 1; }
}

@keyframes glow {
  0%, 100% { filter: brightness(1) drop-shadow(0 0 5px #6366f1); }
  50%      { filter: brightness(1.3) drop-shadow(0 0 20px #6366f1); }
}
```

## Video Capture Notes

When using CSS animations for video capture:

1. **No external fonts** — use system fonts (`sans-serif`, `monospace`) to avoid flash of unstyled text
2. **animation-fill-mode: forwards** — ensure final frame holds correctly
3. **Prefer @keyframes over transitions** — more control over timing and intermediate states
4. **Avoid `animation: infinite`** for one-shot captures — set iteration-count matching your duration
5. **Force GPU layers** — `will-change: transform, opacity` for smoother capture
6. **CSS animations may not be frame-accurate** — for precise frame control, use Canvas/JS instead
7. **Background colors** — always set explicit `background-color` on body and elements; MP4 does not support transparency, so a solid background is required
8. **`window.animationReady`** — set after DOM is ready and first paint is complete:
   ```javascript
   window.addEventListener('load', () => {
     requestAnimationFrame(() => { window.animationReady = true; });
   });
   ```
