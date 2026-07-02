# Canvas 2D API Reference

Quick reference for Canvas 2D API patterns used in animation creation.

## Setup

```javascript
const canvas = document.getElementById('canvas');
const ctx = canvas.getContext('2d');
canvas.width = WIDTH;  // e.g. 1920
canvas.height = HEIGHT; // e.g. 1080
```

## Drawing Primitives

### Rectangles

```javascript
ctx.fillRect(x, y, width, height);       // Filled rectangle
ctx.strokeRect(x, y, width, height);     // Outlined rectangle
ctx.clearRect(x, y, width, height);      // Clear to transparent
```

### Circles / Arcs

```javascript
ctx.beginPath();
ctx.arc(centerX, centerY, radius, startAngle, endAngle, counterclockwise);
ctx.fill();   // or ctx.stroke()

// Full circle
ctx.arc(x, y, r, 0, Math.PI * 2);

// Semicircle
ctx.arc(x, y, r, 0, Math.PI);
```

### Lines

```javascript
ctx.beginPath();
ctx.moveTo(x1, y1);
ctx.lineTo(x2, y2);
ctx.stroke();

// Dashed line
ctx.setLineDash([dashLen, gapLen]);
ctx.setLineDash([]); // reset to solid
```

### Rounded Rectangles

```javascript
ctx.beginPath();
ctx.roundRect(x, y, w, h, [topLeft, topRight, bottomRight, bottomLeft]);
ctx.fill();
```

### Polygons

```javascript
function drawPolygon(ctx, cx, cy, radius, sides, rotation = 0) {
  ctx.beginPath();
  for (let i = 0; i <= sides; i++) {
    const angle = (i / sides) * Math.PI * 2 + rotation;
    const x = cx + Math.cos(angle) * radius;
    const y = cy + Math.sin(angle) * radius;
    if (i === 0) ctx.moveTo(x, y);
    else ctx.lineTo(x, y);
  }
  ctx.closePath();
}
```

## Paths

```javascript
ctx.beginPath();           // Start new path
ctx.moveTo(x, y);         // Move pen
ctx.lineTo(x, y);          // Line to point
ctx.quadraticCurveTo(cpx, cpy, x, y);  // Quadratic bezier
ctx.bezierCurveTo(cp1x, cp1y, cp2x, cp2y, x, y); // Cubic bezier
ctx.arcTo(x1, y1, x2, y2, radius);     // Arc tangent
ctx.closePath();           // Close path back to start
ctx.fill();                // Fill the path
ctx.stroke();              // Stroke the path
```

## Styles

```javascript
// Fill & stroke
ctx.fillStyle = '#ff0000';
ctx.fillStyle = 'rgba(255, 0, 0, 0.5)';
ctx.fillStyle = 'hsl(0, 100%, 50%)';
ctx.strokeStyle = '#000000';
ctx.lineWidth = 2;
ctx.lineCap = 'round';    // 'butt' | 'round' | 'square'
ctx.lineJoin = 'round';    // 'miter' | 'round' | 'bevel'

// Shadows
ctx.shadowColor = 'rgba(0, 0, 0, 0.5)';
ctx.shadowBlur = 10;
ctx.shadowOffsetX = 2;
ctx.shadowOffsetY = 2;
```

## Gradients

### Linear Gradient

```javascript
const grad = ctx.createLinearGradient(x0, y0, x1, y1);
grad.addColorStop(0, '#ff0000');     // Start color
grad.addColorStop(0.5, '#00ff00');  // Mid color
grad.addColorStop(1, '#0000ff');     // End color
ctx.fillStyle = grad;
```

### Radial Gradient

```javascript
const grad = ctx.createRadialGradient(cx, cy, r0, cx, cy, r1);
grad.addColorStop(0, 'rgba(255, 255, 255, 1)');
grad.addColorStop(1, 'rgba(255, 255, 255, 0)');
ctx.fillStyle = grad;
```

### Conic Gradient

```javascript
const grad = ctx.createConicGradient(startAngle, cx, cy);
grad.addColorStop(0, '#ff0000');
grad.addColorStop(0.33, '#00ff00');
grad.addColorStop(0.66, '#0000ff');
grad.addColorStop(1, '#ff0000');
ctx.fillStyle = grad;
```

## Transforms

```javascript
ctx.save();                        // Save current transform state
ctx.translate(dx, dy);             // Move origin
ctx.rotate(angle);                 // Rotate (radians, clockwise)
ctx.scale(sx, sy);                 // Scale
ctx.transform(a, b, c, d, e, f);  // Apply matrix
ctx.setTransform(a, b, c, d, e, f); // Set absolute matrix
ctx.restore();                     // Restore saved state

// Common pattern: draw centered
ctx.save();
ctx.translate(centerX, centerY);
ctx.rotate(angle);
ctx.fillRect(-w / 2, -h / 2, w, h);
ctx.restore();
```

## Compositing Modes

```javascript
ctx.globalCompositeOperation = mode;
```

| Mode | Description | Use Case |
|------|-------------|----------|
| `source-over` | Default, draw on top | Normal drawing |
| `lighter` | Additive blend (colors add) | Glows, particles, light effects |
| `screen` | Brighten | Soft glow, overlays |
| `overlay` | Contrast boost | Dramatic lighting |
| `multiply` | Darken | Shadows |
| `destination-out` | Erase existing pixels | Cutout, reveal effects |
| `destination-in` | Keep only overlap | Masking |
| `source-atop` | Draw only on existing pixels | Layered effects |

### Glow Effect Pattern

```javascript
// Additive glow
ctx.globalCompositeOperation = 'lighter';
ctx.globalAlpha = 0.3;
// Draw glowing element
ctx.globalCompositeOperation = 'source-over';
ctx.globalAlpha = 1.0;
```

## Text

```javascript
ctx.font = 'bold 48px sans-serif';
ctx.textAlign = 'center';    // 'left' | 'center' | 'right'
ctx.textBaseline = 'middle';  // 'top' | 'middle' | 'alphabetic' | 'bottom'
ctx.fillStyle = '#ffffff';
ctx.fillText('Hello', x, y);
ctx.strokeStyle = '#000000';
ctx.strokeText('Hello', x, y);

// Measure text
const metrics = ctx.measureText('Hello');
const textWidth = metrics.width;
```

## ImageData (Pixel Manipulation)

```javascript
// Read pixels
const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);
const data = imageData.data; // Uint8ClampedArray [R,G,B,A, R,G,B,A, ...]

// Modify pixels
for (let i = 0; i < data.length; i += 4) {
  data[i]     = Math.min(255, data[i] * 1.2);     // R boost
  data[i + 1] = Math.min(255, data[i + 1] * 1.2); // G boost
  data[i + 2] = Math.min(255, data[i + 2] * 1.2); // B boost
  // data[i + 3] is alpha
}

// Write pixels back
ctx.putImageData(imageData, 0, 0);
```

## Clipping

```javascript
ctx.save();
ctx.beginPath();
// Define clip shape
ctx.arc(cx, cy, radius, 0, Math.PI * 2);
ctx.clip();
// Draw only within clip region
ctx.fillRect(0, 0, canvas.width, canvas.height);
ctx.restore(); // Removes clip
```

## Particle System Pattern

```javascript
class Particle {
  constructor(x, y) {
    this.x = x;
    this.y = y;
    this.vx = (Math.random() - 0.5) * 4;
    this.vy = (Math.random() - 0.5) * 4;
    this.life = 1.0;
    this.decay = 0.005 + Math.random() * 0.01;
    this.size = 2 + Math.random() * 4;
    this.color = `hsl(${Math.random() * 60 + 10}, 100%, 60%)`;
  }

  update() {
    this.x += this.vx;
    this.y += this.vy;
    this.vy += 0.02; // gravity
    this.life -= this.decay;
  }

  draw(ctx) {
    ctx.globalAlpha = this.life;
    ctx.fillStyle = this.color;
    ctx.beginPath();
    ctx.arc(this.x, this.y, this.size * this.life, 0, Math.PI * 2);
    ctx.fill();
  }

  get isDead() { return this.life <= 0; }
}

// Usage in animation loop
const particles = [];

function animate() {
  ctx.clearRect(0, 0, canvas.width, canvas.height);

  // Emit new particles
  if (particles.length < 200) {
    particles.push(new Particle(canvas.width / 2, canvas.height / 2));
  }

  // Update and draw
  for (let i = particles.length - 1; i >= 0; i--) {
    particles[i].update();
    particles[i].draw(ctx);
    if (particles[i].isDead) particles.splice(i, 1);
  }

  ctx.globalAlpha = 1.0;
  requestAnimationFrame(animate);
}
```

## Trail / Motion Blur Pattern

```javascript
// Instead of clearRect, draw semi-transparent overlay
ctx.fillStyle = 'rgba(0, 0, 0, 0.1)'; // Adjust alpha for trail length
ctx.fillRect(0, 0, canvas.width, canvas.height);

// Then draw current frame elements on top
```

## Common Utilities

```javascript
// Random in range
function rand(min, max) { return Math.random() * (max - min) + min; }

// Lerp
function lerp(a, b, t) { return a + (b - a) * t; }

// Distance
function dist(x1, y1, x2, y2) { return Math.hypot(x2 - x1, y2 - y1); }

// Map value from one range to another
function mapValue(val, inMin, inMax, outMin, outMax) {
  return outMin + (val - inMin) / (inMax - inMin) * (outMax - outMin);
}

// Clamp
function clamp(val, min, max) { return Math.min(max, Math.max(min, val)); }
```
