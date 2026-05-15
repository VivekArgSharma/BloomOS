# Design Thesis: Organic Grounded UI System
**Codename: "Root & Ink"**

---

## The Core Idea

This design language is built on a single tension: **bold editorial type on warm earth matter**.

Everything lives inside deep forest-green panels. Cream inputs breathe against the green. Typography is loud, slab-serif, and unapologetically large. The overall feel is: *a natural goods company that went to design school in New York* — confident, earthy, modern, not twee.

This is NOT a "minimal green startup" look. It avoids gradients, glassmorphism, and soft shadows. Every decision is grounded (literally and conceptually).

---

## Design Tokens

```css
:root {
  /* Core Palette */
  --color-forest:      #2D6A4F;  /* dominant panel/bg color */
  --color-forest-dark: #1E4D38;  /* hover states, borders, dividers */
  --color-forest-deep: #163D2C;  /* darkest, used sparingly for depth */
  --color-cream:       #F5EFE6;  /* input bg, text-on-green, logo fill */
  --color-cream-dark:  #EBE0D0;  /* input border, subtle dividers */
  --color-accent:      #4CAF82;  /* CTA buttons only — a lighter spring green */
  --color-page-bg:     #FAF5EF;  /* off-white warm page background */

  /* Typography */
  --font-display: 'Playfair Display', 'Libre Baskerville', Georgia, serif;
    /* For all headings: slab or transitional serif, heavy weight */
  --font-body:    'DM Sans', 'Outfit', sans-serif;
    /* For labels, body copy: clean geometric sans, not Inter */

  /* Type Scale */
  --text-hero:   clamp(3rem, 8vw, 7rem);   /* brand wordmark, page-filling type */
  --text-h1:     clamp(2rem, 4vw, 3.5rem); /* section headings, ALL CAPS */
  --text-h2:     clamp(1.25rem, 2vw, 1.75rem);
  --text-body:   1rem;
  --text-label:  0.8125rem;                /* form labels, uppercase tracking */

  /* Spacing */
  --space-xs:  0.5rem;
  --space-sm:  1rem;
  --space-md:  1.5rem;
  --space-lg:  2.5rem;
  --space-xl:  4rem;
  --space-2xl: 7rem;

  /* Radius */
  --radius-input:  6px;   /* slightly rounded, not fully rounded */
  --radius-button: 6px;
  --radius-card:   14px;  /* panels/section containers */

  /* Shadows */
  --shadow-panel: 0 8px 40px rgba(30, 77, 56, 0.18);
  --shadow-input:  inset 0 1px 3px rgba(30, 77, 56, 0.08);
}
```

---

## Component Rules

### 1. The Panel (Core Container)
Every major section of every page lives inside a **forest-green rounded panel** placed on the warm cream page background. Think of each page section as a card that breathes.

```css
.panel {
  background: var(--color-forest);
  border-radius: var(--radius-card);
  padding: var(--space-xl) var(--space-lg);
  color: var(--color-cream);
  box-shadow: var(--shadow-panel);
}

/* Panels never go full-bleed on wide screens — they have horizontal margin */
.panel-wrapper {
  max-width: 1100px;
  margin: var(--space-lg) auto;
  padding: 0 var(--space-sm);
}
```

### 2. Typography on Green

All headings inside green panels are:
- **Serif display font**, heavy weight (700–900)
- **ALL CAPS** for primary hero/section heads
- Color: `var(--color-cream)` — warm off-white, never pure white
- No text-shadow, no glow — just type on color

```css
.heading-hero {
  font-family: var(--font-display);
  font-size: var(--text-h1);
  font-weight: 800;
  text-transform: uppercase;
  letter-spacing: -0.01em;
  color: var(--color-cream);
  line-height: 1.05;
}

.body-on-green {
  font-family: var(--font-body);
  font-size: var(--text-body);
  color: var(--color-cream);
  opacity: 0.85;  /* slightly softened — not full-contrast */
  line-height: 1.65;
}
```

### 3. Inputs & Forms

Inputs are the most distinctive element: **cream fill on forest green**. They look like paper forms inside a wooden desk.

```css
.field-label {
  font-family: var(--font-body);
  font-size: var(--text-label);
  font-weight: 500;
  letter-spacing: 0.04em;
  color: var(--color-cream);
  display: block;
  margin-bottom: var(--space-xs);
}

.field-input {
  width: 100%;
  background: var(--color-cream);
  border: 1.5px solid var(--color-cream-dark);
  border-radius: var(--radius-input);
  padding: 0.75rem 1rem;
  font-family: var(--font-body);
  font-size: var(--text-body);
  color: var(--color-forest-deep);
  box-shadow: var(--shadow-input);
  transition: border-color 0.15s ease, box-shadow 0.15s ease;
}

.field-input::placeholder {
  color: var(--color-forest);
  opacity: 0.45;
}

.field-input:focus {
  outline: none;
  border-color: var(--color-accent);
  box-shadow: 0 0 0 3px rgba(76, 175, 130, 0.2);
}
```

### 4. Buttons (CTA)

Only ONE button style on green panels: the **spring-green CTA**. It pops off the dark forest without being aggressive.

```css
.btn-primary {
  background: var(--color-accent);
  color: var(--color-forest-deep);
  font-family: var(--font-body);
  font-size: 0.9375rem;
  font-weight: 600;
  padding: 0.65rem 1.75rem;
  border: none;
  border-radius: var(--radius-button);
  cursor: pointer;
  transition: background 0.2s ease, transform 0.1s ease;
}

.btn-primary:hover {
  background: #5BBF8F;
  transform: translateY(-1px);
}

.btn-primary:active {
  transform: translateY(0px);
}
```

### 5. Dividers

Dividers on green panels are subtle — a 1px line at low opacity. Never a dark border.

```css
.panel-divider {
  border: none;
  border-top: 1px solid rgba(245, 239, 230, 0.2);
  margin: var(--space-lg) 0;
}
```

### 6. Icon Buttons (Social Links, Nav Icons)

Square rounded boxes in dark-forest on the green panel — no fill, just border.

```css
.icon-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 2.25rem;
  height: 2.25rem;
  border-radius: 6px;
  border: 1.5px solid rgba(245, 239, 230, 0.35);
  color: var(--color-cream);
  transition: border-color 0.15s, background 0.15s;
}

.icon-btn:hover {
  border-color: var(--color-cream);
  background: rgba(245, 239, 230, 0.1);
}
```

### 7. Brand Wordmark Treatment

The oversized wordmark at the bottom of the page is a signature move of this system. On any major section or footer: **use display serif type at hero scale, color matched to the panel (cream on green), with an illustrated/icon element integrated into the letterforms or overlaid on them**.

```css
.brand-wordmark {
  font-family: var(--font-display);
  font-size: var(--text-hero);
  font-weight: 800;
  color: var(--color-cream);
  opacity: 0.15;  /* ghosted version for background texture */
  /* OR */
  opacity: 1;     /* full for footer wordmark display */
  line-height: 1;
  letter-spacing: -0.02em;
}
```

---

## Page Layout System

Every page is structured as a **vertical stack of panels** on the warm cream background. The page itself is never green — only the panels are.

```
[page-bg: cream]
  ↳ [nav: minimal, transparent or cream bar]
  ↳ [panel: hero section]        — full-width or padded
  ↳ [gap: space-lg]
  ↳ [panel: feature / content]  — can be split-column
  ↳ [gap: space-lg]
  ↳ [panel: CTA / form]         — typically 2-col: copy left, form right
  ↳ [panel: footer]             — contains divider, contact, wordmark
```

**2-Column Split (the primary content layout):**
- Left: heading (ALL CAPS serif) + body copy + supporting info
- Right: form, feature list, or visual
- Ratio: roughly 40/60 or 45/55 — the form/visual side gets more room

---

## Motion Principles

Keep motion **understated and purposeful**:

1. **Panel entrance**: `opacity: 0 → 1` + `translateY(16px → 0)` on scroll-in, ~400ms ease-out. No bouncing.
2. **Input focus**: border-color and box-shadow transition, 150ms. No scale.
3. **Button hover**: `translateY(-1px)`, 100ms. Small lift only.
4. **No looping animations** except illustrative elements (e.g., a subtle plant sway on the brand illustration, 6s ease-in-out, low amplitude).

```css
@keyframes panel-in {
  from { opacity: 0; transform: translateY(16px); }
  to   { opacity: 1; transform: translateY(0); }
}

.panel {
  animation: panel-in 0.4s ease-out both;
}
```

---

## What This Is NOT

Avoid these at all costs — they break the thesis:

| ❌ Wrong | ✓ Right |
|---|---|
| Gradient green (green→teal) | Flat, single-value forest green |
| Round pill inputs | Slightly-rounded rect inputs |
| Sans-serif headings | Slab serif, weight 800 |
| White backgrounds inside panels | Cream (`#F5EFE6`) only |
| Multiple button colors | One CTA color (spring green), rest are ghost |
| Drop shadows on type | No text-shadow, ever |
| Glassmorphism / frosted panels | Opaque panels only |
| Inter / Roboto / system fonts | Playfair or Libre Baskerville + DM Sans |

---

## Applying This to New Pages

When building any new page in this system, ask:

1. **What is the section's primary action?** → Put it in a forest panel.
2. **Is there a form?** → Cream inputs, 2-col layout.
3. **What's the heading?** → ALL CAPS, slab serif, big.
4. **Is there a brand moment?** → Use oversized wordmark at hero scale.
5. **What illustration or icon anchors the brand?** → Integrate it organically into the layout (not as a floating blob, but overlapping text or panels).

---

## Font Loading (Google Fonts)

```html
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700;800;900&family=DM+Sans:wght@400;500;600&display=swap" rel="stylesheet">
```

---

*This document is the source of truth for all UI decisions. When in doubt: go greener, go bigger on type, go warmer on cream.*
