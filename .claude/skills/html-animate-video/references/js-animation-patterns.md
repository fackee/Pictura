# JS Animation Patterns

Core patterns and utilities for writing JavaScript-based animations.

## requestAnimationFrame Loop

```javascript
let startTime = null;

function animate(timestamp) {
  if (!startTime) startTime = timestamp;
  const elapsed = timestamp - startTime; // ms
  const t = elapsed / 1000; // seconds

  // Clear and draw
  ctx.clearRect(0, 0, W, H);
  // ... drawing code ...

  requestAnimationFrame(animate);
}

requestAnimationFrame(animate);
```

### With Stop Condition

```javascript
const DURATION = 3000; // 3 seconds
let startTime = null;

function animate(timestamp) {
  if (!startTime) startTime = timestamp;
  const elapsed = timestamp - startTime;

  if (elapsed > DURATION) {
    // Draw final frame
    drawFrame(1.0);
    return; // Stop
  }

  const progress = elapsed / DURATION;
  drawFrame(progress);
  requestAnimationFrame(animate);
}
```

### Trail Effect (No Full Clear)

```javascript
function animate(timestamp) {
  // Semi-transparent overlay creates trail
  ctx.fillStyle = 'rgba(0, 0, 0, 0.05)';
  ctx.fillRect(0, 0, W, H);

  // Draw current elements
  // ...

  requestAnimationFrame(animate);
}
```

## Easing Functions

All easing functions take `t` in [0, 1] and return a value in [0, 1].

### Standard Easing

```javascript
// Ease In Quad
function easeInQuad(t) { return t * t; }

// Ease Out Quad
function easeOutQuad(t) { return 1 - (1 - t) * (1 - t); }

// Ease In Out Quad
function easeInOutQuad(t) { return t < 0.5 ? 2 * t * t : 1 - Math.pow(-2 * t + 2, 2) / 2; }

// Ease In Cubic
function easeInCubic(t) { return t * t * t; }

// Ease Out Cubic (most commonly used)
function easeOutCubic(t) { return 1 - Math.pow(1 - t, 3); }

// Ease In Out Cubic
function easeInOutCubic(t) { return t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2; }
```

### Elastic Easing

```javascript
// Elastic Ease Out (bouncy ending)
function easeOutElastic(t) {
  if (t === 0 || t === 1) return t;
  return Math.pow(2, -10 * t) * Math.sin((t * 10 - 0.75) * (2 * Math.PI) / 3) + 1;
}

// Elastic Ease In
function easeInElastic(t) {
  if (t === 0 || t === 1) return t;
  return -Math.pow(2, 10 * t - 10) * Math.sin((t * 10 - 10.75) * (2 * Math.PI) / 3);
}
```

### Bounce Easing

```javascript
// Bounce Ease Out (ball drop)
function easeOutBounce(t) {
  const n1 = 7.5625;
  const d1 = 2.75;
  if (t < 1 / d1) return n1 * t * t;
  if (t < 2 / d1) return n1 * (t -= 1.5 / d1) * t + 0.75;
  if (t < 2.5 / d1) return n1 * (t -= 2.25 / d1) * t + 0.9375;
  return n1 * (t -= 2.625 / d1) * t + 0.984375;
}

// Bounce Ease In
function easeInBounce(t) { return 1 - easeOutBounce(1 - t); }
```

### Back Easing (Overshoot)

```javascript
// Back Ease Out
function easeOutBack(t) {
  const c1 = 1.70158;
  const c3 = c1 + 1;
  return 1 + c3 * Math.pow(t - 1, 3) + c1 * Math.pow(t - 1, 2);
}

// Back Ease In
function easeInBack(t) {
  const c1 = 1.70158;
  const c3 = c1 + 1;
  return c3 * t * t * t - c1 * t * t;
}
```

### Spring Easing (Physics-based)

```javascript
function spring(t, damping = 0.5, frequency = 10) {
  return 1 - Math.exp(-damping * t * 10) * Math.cos(frequency * t);
}
// Usage: spring(progress, 0.3, 12) for bouncier spring
```

## Time Control

### Normalize Time

```javascript
const DURATION = 3000;
let startTime = null;

function animate(timestamp) {
  if (!startTime) startTime = timestamp;
  const rawProgress = (timestamp - startTime) / DURATION;
  const loopProgress = rawProgress % 1; // Loop forever
  // or
  const clampedProgress = Math.min(1, rawProgress); // One-shot
}
```

### Staggered Delays

```javascript
const items = [...]; // array of elements
const STAGGER = 100; // ms between each item start

items.forEach((item, i) => {
  item.startTime = startTime + i * STAGGER;
});

// In animate():
items.forEach(item => {
  const itemProgress = Math.max(0, Math.min(1,
    (timestamp - item.startTime) / ITEM_DURATION
  ));
  if (itemProgress > 0) {
    drawItem(item, easeOutCubic(itemProgress));
  }
});
```

### Loop with Pause

```javascript
const CYCLE = 4000; // total cycle ms
const ANIM = 2000;  // animation ms
const PAUSE = 2000;  // pause ms

function animate(timestamp) {
  const cycleTime = timestamp % CYCLE;
  const progress = cycleTime < ANIM
    ? cycleTime / ANIM
    : 1.0; // Hold at end during pause
}
```

## State Machine

```javascript
const states = {
  ENTERING: 'entering',
  ACTIVE: 'active',
  EXITING: 'exiting',
  DONE: 'done',
};

let state = states.ENTERING;
let stateStartTime = null;
const ENTER_DURATION = 800;
const EXIT_DURATION = 500;

function animate(timestamp) {
  if (!stateStartTime) stateStartTime = timestamp;
  const stateElapsed = timestamp - stateStartTime;

  switch (state) {
    case states.ENTERING:
      drawEntering(Math.min(1, stateElapsed / ENTER_DURATION));
      if (stateElapsed >= ENTER_DURATION) {
        state = states.ACTIVE;
        stateStartTime = timestamp;
      }
      break;
    case states.ACTIVE:
      drawActive(timestamp);
      // Transition to exit when needed
      if (shouldExit) {
        state = states.EXITING;
        stateStartTime = timestamp;
      }
      break;
    case states.EXITING:
      drawExiting(Math.min(1, stateElapsed / EXIT_DURATION));
      if (stateElapsed >= EXIT_DURATION) {
        state = states.DONE;
        return; // Stop animation
      }
      break;
  }
  requestAnimationFrame(animate);
}
```

## Color Interpolation

### RGB Lerp

```javascript
function lerpColor(c1, c2, t) {
  // c1, c2 are [r, g, b] arrays (0-255)
  return [
    Math.round(c1[0] + (c2[0] - c1[0]) * t),
    Math.round(c1[1] + (c2[1] - c1[1]) * t),
    Math.round(c1[2] + (c2[2] - c1[2]) * t),
  ];
}

// Usage
const startColor = [99, 102, 241];  // #6366f1
const endColor = [236, 72, 153];    // #ec4899
const mid = lerpColor(startColor, endColor, 0.5);
ctx.fillStyle = `rgb(${mid[0]}, ${mid[1]}, ${mid[2]})`;
```

### HSL Lerp (better for vibrant transitions)

```javascript
function lerpHSL(h1, s1, l1, h2, s2, l2, t) {
  // Shortest path hue interpolation
  let dh = h2 - h1;
  if (dh > 180) dh -= 360;
  if (dh < -180) dh += 360;
  const h = ((h1 + dh * t) % 360 + 360) % 360;
  const s = s1 + (s2 - s1) * t;
  const l = l1 + (l2 - l1) * t;
  return `hsl(${h}, ${s}%, ${l}%)`;
}
```

### Hex ↔ RGB Conversion

```javascript
function hexToRgb(hex) {
  hex = hex.replace('#', '');
  return [
    parseInt(hex.substring(0, 2), 16),
    parseInt(hex.substring(2, 4), 16),
    parseInt(hex.substring(4, 6), 16),
  ];
}

function rgbToHex(r, g, b) {
  return '#' + [r, g, b].map(v => v.toString(16).padStart(2, '0')).join('');
}
```

## Math Utilities

```javascript
// Linear interpolation
function lerp(a, b, t) { return a + (b - a) * t; }

// Clamp value to range
function clamp(val, min, max) { return Math.min(max, Math.max(min, val)); }

// Map value from one range to another
function mapRange(val, inMin, inMax, outMin, outMax) {
  return outMin + (val - inMin) / (inMax - inMin) * (outMax - outMin);
}

// Random float in range
function rand(min, max) { return Math.random() * (max - min) + min; }

// Random integer in range (inclusive)
function randInt(min, max) { return Math.floor(Math.random() * (max - min + 1)) + min; }

// Distance between two points
function dist(x1, y1, x2, y2) { return Math.hypot(x2 - x1, y2 - y1); }

// Angle from point 1 to point 2
function angle(x1, y1, x2, y2) { return Math.atan2(y2 - y1, x2 - x1); }

// Normalize angle to [0, 2π)
function normalizeAngle(a) { return ((a % (Math.PI * 2)) + Math.PI * 2) % (Math.PI * 2); }

// Smooth step
function smoothstep(edge0, edge1, x) {
  const t = clamp((x - edge0) / (edge1 - edge0), 0, 1);
  return t * t * (3 - 2 * t);
}

// Noise-like pseudo-random (simple hash)
function hash(x, y) {
  let h = x * 374761393 + y * 668265263;
  h = (h ^ (h >> 13)) * 1274126177;
  return ((h ^ (h >> 16)) & 0x7fffffff) / 0x7fffffff;
}
```

## Timing Helpers

### Delayed Execution

```javascript
function afterDelay(delay, callback) {
  let start = null;
  return function(timestamp) {
    if (!start) start = timestamp;
    if (timestamp - start >= delay) {
      callback();
      return true;
    }
    return false;
  };
}
```

### Repeating Timer

```javascript
class Timer {
  constructor(interval, callback) {
    this.interval = interval;
    this.callback = callback;
    this.accumulator = 0;
  }
  update(dt) {
    this.accumulator += dt;
    while (this.accumulator >= this.interval) {
      this.callback();
      this.accumulator -= this.interval;
    }
  }
}
```
