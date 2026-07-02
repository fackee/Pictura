# Animation Recipes

15 ready-to-use animation recipes. Each is a complete, self-contained JS code snippet
following the HTML template convention with `window.animationReady = true`.

## 1. Particle Explosion

```javascript
class Particle {
  constructor(x, y) {
    const angle = Math.random() * Math.PI * 2;
    const speed = 2 + Math.random() * 6;
    this.x = x; this.y = y;
    this.vx = Math.cos(angle) * speed;
    this.vy = Math.sin(angle) * speed;
    this.life = 1.0;
    this.decay = 0.01 + Math.random() * 0.02;
    this.size = 2 + Math.random() * 5;
    this.hue = Math.random() * 60 + 10;
  }
  update() {
    this.x += this.vx; this.y += this.vy;
    this.vy += 0.05; this.vx *= 0.99;
    this.life -= this.decay;
  }
  draw(ctx) {
    ctx.globalAlpha = this.life;
    ctx.fillStyle = `hsl(${this.hue}, 100%, 60%)`;
    ctx.beginPath();
    ctx.arc(this.x, this.y, Math.max(0.5, this.size * this.life), 0, Math.PI * 2);
    ctx.fill();
  }
  get isDead() { return this.life <= 0; }
}

const particles = [];
let exploded = false;
function animate() {
  ctx.fillStyle = 'rgba(0, 0, 0, 0.15)';
  ctx.fillRect(0, 0, W, H);
  if (!exploded) {
    for (let i = 0; i < 150; i++) particles.push(new Particle(W / 2, H / 2));
    exploded = true;
  }
  for (let i = particles.length - 1; i >= 0; i--) {
    particles[i].update(); particles[i].draw(ctx);
    if (particles[i].isDead) particles.splice(i, 1);
  }
  ctx.globalAlpha = 1;
  requestAnimationFrame(animate);
}
```

## 2. Floating Particles / Bokeh

```javascript
class Bokeh {
  constructor() {
    this.x = Math.random() * W;
    this.y = Math.random() * H;
    this.r = 10 + Math.random() * 50;
    this.alpha = 0.05 + Math.random() * 0.2;
    this.vx = (Math.random() - 0.5) * 0.5;
    this.vy = -0.2 - Math.random() * 0.5;
    this.hue = Math.random() * 360;
  }
  update() {
    this.x += this.vx; this.y += this.vy;
    if (this.y + this.r < 0) { this.y = H + this.r; this.x = Math.random() * W; }
    if (this.x < -this.r) this.x = W + this.r;
    if (this.x > W + this.r) this.x = -this.r;
  }
  draw(ctx) {
    const grad = ctx.createRadialGradient(this.x, this.y, 0, this.x, this.y, this.r);
    grad.addColorStop(0, `hsla(${this.hue}, 80%, 70%, ${this.alpha})`);
    grad.addColorStop(1, `hsla(${this.hue}, 80%, 70%, 0)`);
    ctx.fillStyle = grad;
    ctx.beginPath();
    ctx.arc(this.x, this.y, this.r, 0, Math.PI * 2);
    ctx.fill();
  }
}
const bokehs = Array.from({length: 30}, () => new Bokeh());
function animate() {
  ctx.fillStyle = '#0a0a2e';
  ctx.fillRect(0, 0, W, H);
  bokehs.forEach(b => { b.update(); b.draw(ctx); });
  requestAnimationFrame(animate);
}
```

## 3. Typewriter Text

```javascript
const text = "Hello, World!";
let charIndex = 0;
let lastTime = 0;
const charDelay = 100; // ms per character

ctx.font = 'bold 64px sans-serif';
ctx.fillStyle = '#ffffff';
ctx.textAlign = 'center';
ctx.textBaseline = 'middle';

function animate(timestamp) {
  if (!lastTime) lastTime = timestamp;
  if (timestamp - lastTime > charDelay && charIndex < text.length) {
    charIndex++;
    lastTime = timestamp;
  }
  ctx.fillStyle = '#000000';
  ctx.fillRect(0, 0, W, H);
  ctx.fillStyle = '#ffffff';
  ctx.font = 'bold 64px sans-serif';
  const displayText = text.substring(0, charIndex);
  ctx.fillText(displayText, W / 2, H / 2);
  // Cursor blink
  if (Math.floor(timestamp / 500) % 2 === 0) {
    const textW = ctx.measureText(displayText).width;
    ctx.fillRect(W / 2 + textW / 2 + 4, H / 2 - 30, 3, 60);
  }
  requestAnimationFrame(animate);
}
```

## 4. Text Gradient Sweep

```javascript
const text = "ANIMATE";
const textY = H / 2;
ctx.font = `bold ${Math.min(W / 5, 180)}px sans-serif`;
ctx.textAlign = 'center';
ctx.textBaseline = 'middle';

function animate(timestamp) {
  const t = (timestamp % 3000) / 3000;
  ctx.fillStyle = '#111111';
  ctx.fillRect(0, 0, W, H);
  const textW = ctx.measureText(text).width;
  const gradX = textW * t;
  const grad = ctx.createLinearGradient(
    W / 2 - textW / 2 + gradX - textW * 0.3, 0,
    W / 2 - textW / 2 + gradX + textW * 0.3, 0
  );
  grad.addColorStop(0, '#666666');
  grad.addColorStop(0.5, '#ffffff');
  grad.addColorStop(1, '#666666');
  ctx.fillStyle = grad;
  ctx.fillText(text, W / 2, textY);
  requestAnimationFrame(animate);
}
```

## 5. Text Elastic Scale-In

```javascript
const text = "BOUNCE";
let startTime = null;
const duration = 1500;

function elasticOut(t) {
  if (t === 0 || t === 1) return t;
  return Math.pow(2, -10 * t) * Math.sin((t - 0.075) * (2 * Math.PI) / 0.3) + 1;
}

function animate(timestamp) {
  if (!startTime) startTime = timestamp;
  const progress = Math.min(1, (timestamp - startTime) / duration);
  const scale = elasticOut(progress);
  ctx.fillStyle = '#000000';
  ctx.fillRect(0, 0, W, H);
  ctx.save();
  ctx.translate(W / 2, H / 2);
  ctx.scale(scale, scale);
  ctx.font = `bold ${Math.min(W / 5, 160)}px sans-serif`;
  ctx.fillStyle = '#ffffff';
  ctx.textAlign = 'center';
  ctx.textBaseline = 'middle';
  ctx.fillText(text, 0, 0);
  ctx.restore();
  requestAnimationFrame(animate);
}
```

## 6. Progress Bar / Loading Bar

```javascript
let startTime = null;
const duration = 3000;
const barH = 20;
const barPadding = 60;
const barY = H / 2 - barH / 2;

function animate(timestamp) {
  if (!startTime) startTime = timestamp;
  const progress = Math.min(1, (timestamp - startTime) / duration);
  const eased = 1 - Math.pow(1 - progress, 3); // easeOutCubic
  ctx.fillStyle = '#1a1a2e';
  ctx.fillRect(0, 0, W, H);
  // Track
  ctx.fillStyle = '#2a2a4e';
  ctx.beginPath();
  ctx.roundRect(barPadding, barY, W - barPadding * 2, barH, barH / 2);
  ctx.fill();
  // Fill
  const fillW = Math.max(barH, (W - barPadding * 2) * eased);
  const grad = ctx.createLinearGradient(barPadding, 0, barPadding + fillW, 0);
  grad.addColorStop(0, '#6366f1');
  grad.addColorStop(1, '#ec4899');
  ctx.fillStyle = grad;
  ctx.beginPath();
  ctx.roundRect(barPadding, barY, fillW, barH, barH / 2);
  ctx.fill();
  // Percentage text
  ctx.fillStyle = '#ffffff';
  ctx.font = 'bold 24px sans-serif';
  ctx.textAlign = 'center';
  ctx.textBaseline = 'middle';
  ctx.fillText(`${Math.round(eased * 100)}%`, W / 2, barY + barH + 40);
  requestAnimationFrame(animate);
}
```

## 7. Countdown

```javascript
const total = 5; // seconds
let startTime = null;
ctx.font = `bold ${Math.min(W / 3, 300)}px sans-serif`;
ctx.textAlign = 'center';
ctx.textBaseline = 'middle';

function animate(timestamp) {
  if (!startTime) startTime = timestamp;
  const elapsed = (timestamp - startTime) / 1000;
  const remaining = Math.max(0, total - elapsed);
  const currentNum = Math.ceil(remaining);
  const frac = remaining - Math.floor(remaining);
  const scale = 1 + frac * 0.3; // pulse effect
  ctx.fillStyle = '#000000';
  ctx.fillRect(0, 0, W, H);
  if (remaining > 0) {
    ctx.save();
    ctx.translate(W / 2, H / 2);
    ctx.scale(scale, scale);
    ctx.fillStyle = '#ffffff';
    ctx.font = `bold ${Math.min(W / 3, 300)}px sans-serif`;
    ctx.fillText(currentNum.toString(), 0, 0);
    ctx.restore();
  } else {
    ctx.fillStyle = '#ffffff';
    ctx.font = `bold ${Math.min(W / 5, 120)}px sans-serif`;
    ctx.fillText("GO!", W / 2, H / 2);
  }
  requestAnimationFrame(animate);
}
```

## 8. Data Chart Animation (Bar Chart)

```javascript
const data = [
  {label: 'Mon', value: 65}, {label: 'Tue', value: 80},
  {label: 'Wed', value: 45}, {label: 'Thu', value: 90},
  {label: 'Fri', value: 70}, {label: 'Sat', value: 55},
  {label: 'Sun', value: 40}
];
const maxVal = Math.max(...data.map(d => d.value));
const chartLeft = 120, chartRight = W - 80;
const chartTop = 80, chartBottom = H - 100;
const barW = (chartRight - chartLeft) / data.length * 0.6;
const gap = (chartRight - chartLeft) / data.length;
let startTime = null;

function animate(timestamp) {
  if (!startTime) startTime = timestamp;
  const t = Math.min(1, (timestamp - startTime) / 1500);
  const eased = 1 - Math.pow(1 - t, 3);
  ctx.fillStyle = '#0f172a';
  ctx.fillRect(0, 0, W, H);
  // Grid lines
  ctx.strokeStyle = '#1e293b';
  ctx.lineWidth = 1;
  for (let i = 0; i <= 5; i++) {
    const y = chartTop + (chartBottom - chartTop) * (i / 5);
    ctx.beginPath(); ctx.moveTo(chartLeft, y); ctx.lineTo(chartRight, y); ctx.stroke();
  }
  // Bars
  data.forEach((d, i) => {
    const x = chartLeft + gap * i + (gap - barW) / 2;
    const barH = (d.value / maxVal) * (chartBottom - chartTop) * eased;
    const grad = ctx.createLinearGradient(0, chartBottom, 0, chartBottom - barH);
    grad.addColorStop(0, '#6366f1');
    grad.addColorStop(1, '#818cf8');
    ctx.fillStyle = grad;
    ctx.beginPath();
    ctx.roundRect(x, chartBottom - barH, barW, barH, [6, 6, 0, 0]);
    ctx.fill();
    // Label
    ctx.fillStyle = '#94a3b8';
    ctx.font = '20px sans-serif';
    ctx.textAlign = 'center';
    ctx.fillText(d.label, x + barW / 2, chartBottom + 30);
  });
  requestAnimationFrame(animate);
}
```

## 9. Ring Expansion

```javascript
class Ring {
  constructor(x, y, delay) {
    this.x = x; this.y = y; this.delay = delay;
    this.maxRadius = Math.min(W, H) * 0.4;
    this.life = 0; this.speed = 0.008;
  }
  update(timestamp) {
    if (timestamp < this.delay) return;
    this.life = Math.min(1, this.life + this.speed);
  }
  draw(ctx) {
    if (this.life <= 0) return;
    const r = this.maxRadius * this.life;
    const alpha = 1 - this.life;
    ctx.strokeStyle = `rgba(99, 102, 241, ${alpha})`;
    ctx.lineWidth = 3 * (1 - this.life) + 1;
    ctx.beginPath();
    ctx.arc(this.x, this.y, Math.max(1, r), 0, Math.PI * 2);
    ctx.stroke();
  }
}
const rings = [];
let lastRing = 0;
function animate(timestamp) {
  ctx.fillStyle = 'rgba(0, 0, 0, 0.1)';
  ctx.fillRect(0, 0, W, H);
  if (timestamp - lastRing > 500) {
    rings.push(new Ring(W / 2, H / 2, timestamp));
    lastRing = timestamp;
  }
  rings.forEach(r => { r.update(timestamp); r.draw(ctx); });
  for (let i = rings.length - 1; i >= 0; i--) {
    if (rings[i].life >= 1) rings.splice(i, 1);
  }
  requestAnimationFrame(animate);
}
```

## 10. Matrix Rain (Character Rain)

```javascript
const fontSize = 16;
const columns = Math.floor(W / fontSize);
const drops = new Array(columns).fill(1);
const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789@#$%^&*';

function animate() {
  ctx.fillStyle = 'rgba(0, 0, 0, 0.05)';
  ctx.fillRect(0, 0, W, H);
  ctx.fillStyle = '#0f0';
  ctx.font = `${fontSize}px monospace`;
  for (let i = 0; i < drops.length; i++) {
    const char = chars[Math.floor(Math.random() * chars.length)];
    ctx.fillStyle = drops[i] * fontSize < fontSize * 2 ? '#fff' : `hsl(120, 100%, ${40 + Math.random() * 30}%)`;
    ctx.fillText(char, i * fontSize, drops[i] * fontSize);
    if (drops[i] * fontSize > H && Math.random() > 0.975) drops[i] = 0;
    drops[i]++;
  }
  requestAnimationFrame(animate);
}
```

## 11. Wave Background

```javascript
const waves = [
  {amplitude: 40, frequency: 0.01, speed: 0.02, color: 'rgba(99, 102, 241, 0.3)', yOffset: 0},
  {amplitude: 30, frequency: 0.015, speed: -0.015, color: 'rgba(139, 92, 246, 0.3)', yOffset: 30},
  {amplitude: 25, frequency: 0.02, speed: 0.025, color: 'rgba(168, 85, 247, 0.3)', yOffset: 60},
];
let t = 0;

function animate() {
  ctx.fillStyle = '#0f172a';
  ctx.fillRect(0, 0, W, H);
  waves.forEach(wave => {
    ctx.beginPath();
    ctx.moveTo(0, H);
    for (let x = 0; x <= W; x++) {
      const y = H / 2 + wave.yOffset + Math.sin(x * wave.frequency + t * wave.speed * 60) * wave.amplitude;
      ctx.lineTo(x, y);
    }
    ctx.lineTo(W, H);
    ctx.closePath();
    ctx.fillStyle = wave.color;
    ctx.fill();
  });
  t++;
  requestAnimationFrame(animate);
}
```

## 12. Gradient Background Rotation

```javascript
function animate(timestamp) {
  const angle = (timestamp / 5000) * Math.PI * 2;
  const cx = W / 2, cy = H / 2, r = Math.max(W, H);
  const x1 = cx + Math.cos(angle) * r;
  const y1 = cy + Math.sin(angle) * r;
  const x2 = cx + Math.cos(angle + Math.PI) * r;
  const y2 = cy + Math.sin(angle + Math.PI) * r;
  const grad = ctx.createLinearGradient(x1, y1, x2, y2);
  grad.addColorStop(0, '#6366f1');
  grad.addColorStop(0.5, '#ec4899');
  grad.addColorStop(1, '#f59e0b');
  ctx.fillStyle = grad;
  ctx.fillRect(0, 0, W, H);
  requestAnimationFrame(animate);
}
```

## 13. Star Twinkle

```javascript
class Star {
  constructor() {
    this.x = Math.random() * W;
    this.y = Math.random() * H;
    this.baseSize = 0.5 + Math.random() * 2;
    this.phase = Math.random() * Math.PI * 2;
    this.speed = 1 + Math.random() * 3;
    this.brightness = 0.5 + Math.random() * 0.5;
  }
  draw(ctx, t) {
    const twinkle = 0.5 + 0.5 * Math.sin(t * this.speed + this.phase);
    const size = this.baseSize * (0.5 + twinkle * 0.5);
    const alpha = this.brightness * twinkle;
    ctx.fillStyle = `rgba(255, 255, 255, ${alpha})`;
    ctx.beginPath();
    ctx.arc(this.x, this.y, Math.max(0.5, size), 0, Math.PI * 2);
    ctx.fill();
    // Cross sparkle for larger stars
    if (this.baseSize > 1.5 && twinkle > 0.7) {
      ctx.strokeStyle = `rgba(255, 255, 255, ${alpha * 0.5})`;
      ctx.lineWidth = 0.5;
      ctx.beginPath();
      ctx.moveTo(this.x - size * 3, this.y);
      ctx.lineTo(this.x + size * 3, this.y);
      ctx.moveTo(this.x, this.y - size * 3);
      ctx.lineTo(this.x, this.y + size * 3);
      ctx.stroke();
    }
  }
}
const stars = Array.from({length: 200}, () => new Star());
function animate(timestamp) {
  const t = timestamp / 1000;
  ctx.fillStyle = '#0a0a2e';
  ctx.fillRect(0, 0, W, H);
  stars.forEach(s => s.draw(ctx, t));
  requestAnimationFrame(animate);
}
```

## 14. Geometric Pattern Fill

```javascript
const cellSize = 40;
let t = 0;

function drawShape(ctx, cx, cy, size, type, color) {
  ctx.fillStyle = color;
  ctx.strokeStyle = color;
  ctx.lineWidth = 1.5;
  ctx.beginPath();
  if (type === 0) { // Circle
    ctx.arc(cx, cy, size / 2, 0, Math.PI * 2);
    ctx.fill();
  } else if (type === 1) { // Square
    ctx.fillRect(cx - size / 2, cy - size / 2, size, size);
  } else if (type === 2) { // Diamond
    ctx.moveTo(cx, cy - size / 2);
    ctx.lineTo(cx + size / 2, cy);
    ctx.lineTo(cx, cy + size / 2);
    ctx.lineTo(cx - size / 2, cy);
    ctx.closePath(); ctx.fill();
  } else { // Triangle
    ctx.moveTo(cx, cy - size / 2);
    ctx.lineTo(cx + size / 2, cy + size / 2);
    ctx.lineTo(cx - size / 2, cy + size / 2);
    ctx.closePath(); ctx.fill();
  }
}

function animate(timestamp) {
  const t = timestamp / 1000;
  ctx.fillStyle = '#0f172a';
  ctx.fillRect(0, 0, W, H);
  const cols = Math.ceil(W / cellSize) + 1;
  const rows = Math.ceil(H / cellSize) + 1;
  for (let r = 0; r < rows; r++) {
    for (let c = 0; c < cols; c++) {
      const cx = c * cellSize + cellSize / 2;
      const cy = r * cellSize + cellSize / 2;
      const dist = Math.hypot(cx - W / 2, cy - H / 2);
      const wave = Math.sin(dist * 0.01 - t * 2) * 0.5 + 0.5;
      const size = cellSize * 0.3 * wave + 2;
      const hue = (dist * 0.3 + t * 50) % 360;
      const type = (r + c) % 4;
      drawShape(ctx, cx, cy, size, type, `hsla(${hue}, 70%, 60%, ${0.3 + wave * 0.7})`);
    }
  }
  requestAnimationFrame(animate);
}
```

## 15. Logo / Icon Bounce-In

```javascript
let startTime = null;
const duration = 1200;

function bounceOut(t) {
  if (t < 1 / 2.75) return 7.5625 * t * t;
  if (t < 2 / 2.75) return 7.5625 * (t -= 1.5 / 2.75) * t + 0.75;
  if (t < 2.5 / 2.75) return 7.5625 * (t -= 2.25 / 2.75) * t + 0.9375;
  return 7.5625 * (t -= 2.625 / 2.75) * t + 0.984375;
}

function drawLogo(ctx, cx, cy, size) {
  // Simple placeholder: a rounded square with inner circle
  ctx.fillStyle = '#6366f1';
  ctx.beginPath();
  ctx.roundRect(cx - size, cy - size, size * 2, size * 2, size * 0.3);
  ctx.fill();
  ctx.fillStyle = '#ffffff';
  ctx.beginPath();
  ctx.arc(cx, cy, size * 0.55, 0, Math.PI * 2);
  ctx.fill();
  ctx.fillStyle = '#6366f1';
  ctx.beginPath();
  ctx.arc(cx, cy, size * 0.3, 0, Math.PI * 2);
  ctx.fill();
}

function animate(timestamp) {
  if (!startTime) startTime = timestamp;
  const progress = Math.min(1, (timestamp - startTime) / duration);
  const scale = bounceOut(progress);
  ctx.fillStyle = '#0f172a';
  ctx.fillRect(0, 0, W, H);
  // Shadow
  ctx.save();
  ctx.globalAlpha = 0.2 * scale;
  ctx.translate(W / 2 + 4, H / 2 + 4);
  ctx.scale(scale, scale);
  drawLogo(ctx, 0, 0, 60);
  ctx.restore();
  // Logo
  ctx.save();
  ctx.globalAlpha = scale;
  ctx.translate(W / 2, H / 2);
  ctx.scale(scale, scale);
  drawLogo(ctx, 0, 0, 60);
  ctx.restore();
  requestAnimationFrame(animate);
}
```
