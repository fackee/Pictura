# Nano Banana Image Generation Guide

## Model Overview

Nano Banana models are advanced image generation and editing models with real-world knowledge and deep reasoning. Two variants are available:

| Model | ID | Max Input Tokens | Extra Aspect Ratios | Extra Resolution |
|-------|----|-----------------|---------------------|-------------------|
| Nano Banana 2 | `gemini-3.1-flash-image` | 131,072 | 1:4, 4:1, 1:8, 8:1 | 512px (0.5K) |
| Nano Banana Pro | `gemini-3-pro-image` | 65,536 | — | — |

**Shared specs:** Max 32,768 output tokens. Resolutions: 1K, 2K, 4K. Aspect ratios: 1:1, 3:2, 2:3, 3:4, 4:3, 4:5, 5:4, 9:16, 16:9, 21:9. Up to 14 reference images per prompt. Knowledge cutoff: January 2025. All outputs include C2PA Content Credentials and SynthID watermark.

---

## Prompting Best Practices

- **Be specific**: Provide concrete details on subject, lighting, and composition.
- **Use positive framing**: Describe what you want, not what you don't (e.g., "empty street" instead of "no cars").
- **Control the camera**: Use photographic/cinematic terms like "low angle", "aerial view".
- **Iterate**: Refine with follow-up prompts.
- **Start with a strong verb** that tells the model the primary operation to perform.

---

## Five Prompting Frameworks

### 1. Image Generation

**Text-to-image (no references):**

Formula: `[Subject] + [Action] + [Location/context] + [Composition] + [Style]`

Example: A striking fashion model wearing a tailored brown dress, sleek boots, and holding a structured handbag. Posing with a confident, statuesque stance, slightly turned. A seamless, deep cherry red studio backdrop. Medium-full shot, center-framed. Fashion magazine editorial, shot on medium-format analog film, pronounced grain, high saturation, cinematic lighting.

**Multimodal generation (with references):**

Formula: `[Reference images] + [Relationship instruction] + [New scenario]`

Example: Using the attached napkin sketch as the structure and the attached fabric sample as the texture, transform this into a high-fidelity 3D armchair render. Place it in a sun-drenched, minimalist living room.

---

### 2. Image Editing

**Conversational editing (no new references):** Define a "mask" through text to edit a specific part while leaving the rest untouched. Be explicit about what to keep the same.

Example: "Remove the man from the photo"

**Composition and style transfer (with new references):**

- **Adding elements**: Upload a base image and an object image, tell the model to combine them.
- **Style transfer**: Upload a photo and ask the model to recreate it in a different artistic style (e.g., Van Gogh).

---

### 3. Real-Time Web Search Generation

Instead of describing a fictional scene, instruct the model to retrieve real-world data and visualize it.

Formula: `[Source/Search request] + [Analytical task] + [Visual translation]`

Example: Search for current weather and date in San Francisco. Use this data to modify the scene (e.g., if raining, make it look grey and rainy). Visualize this in a miniature city-in-a-cup concept embedded within a realistic, modern smartphone UI.

---

### 4. Text Rendering & Localization

Nano Banana excels at rendering sharp, legible text and supports 10+ languages.

Rules for best results:

- **Use quotes**: Enclose target text in quotes (e.g., "Happy Birthday").
- **Specify font**: Describe the style (e.g., "bold white sans-serif" or "Century Gothic 12px").
- **Text-first hack**: First converse with the model to generate text concepts, then ask for an image with that text.
- **Translate/localize**: Write the prompt in one language and specify the target language for text output.

Example: A high-end beauty product shot with a minimalist nude-colored jar on a warm studio background. Next to the product, render three lines: "GLOW" in Brush Script, "10% OFF" in Impact font, "Your First Order" in Century Gothic. Then translate into Korean and Arabic.

---

### 5. Prompting Like a Creative Director

#### Design your lighting

- Studio setups: "three-point softbox setup" for even product lighting.
- Dramatic effects: "Chiaroscuro lighting with harsh, high contrast" or "Golden hour backlighting creating long shadows".

#### Choose your camera, lens, and focus

- **Camera body**: GoPro for immersive distortion, Fujifilm for authentic color, disposable camera for raw nostalgic flash.
- **Lens**: "low-angle shot, shallow depth of field (f/1.8)", "wide-angle lens" for vast scale, "macro lens" for detail.

#### Define color grading and film stock

- Nostalgic/gritty: "as if on 1980s color film, slightly grainy".
- Modern moody: "Cinematic color grading with muted teal tones".

#### Emphasize materiality and texture

- Don't just say "suit jacket" — say "navy blue tweed".
- Don't just say "armor" — describe "ornate elven plate armor, etched with silver leaf patterns".
