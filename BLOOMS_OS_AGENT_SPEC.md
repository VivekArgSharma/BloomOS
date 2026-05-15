# BloomOS Landing Page — Agent Specification

> Read this entire file before writing a single line of code.
> This is the complete source of truth for the BloomOS landing page.

---

## 1. Project Summary

Build a single-page landing page for **BloomOS** — a productivity/planning product.

**Core message:** "Your plan is talking. We help you listen."

The page is a hero-only, distraction-free landing page. No navigation clutter. No feature sections. No pricing. No login. Just the product name, tagline, and one CTA.

---

## 2. Page Structure

The page has exactly **three layers**:

```
1. Background layer   — blurred video (user will swap in their own src)
2. Overlay layer      — semi-transparent white wash over the video
3. Content layer      — all text and interactive elements
```

### Sections (top to bottom):

```
[NAV]         — Wordmark only (left). Nothing else.
[HERO]        — Full viewport height, centered vertically and horizontally
[FOOTER]      — One line. Copyright left, status right.
```

**Remove entirely:**
- Nav links (Features, Pricing, About)
- "Sign in" button
- "Now in early access" badge
- "Trusted by 2,400+ planners" strip
- Feature cards (Plan intelligence, Quiet reminders, Honest reflection)

---

## 3. Exact Content

### Wordmark (top-left of nav)
```
BloomOS
```
- Font: DM Serif Display, italic "OS" portion in sage green

### Hero
```
Headline:     Your plan is
              talking.

Tagline:      We help you listen.

CTA Button:   Get started  →
```

- Headline: very large, DM Serif Display, black
- The word "talking." should be italic and sage green (#5a8a6a)
- Tagline: DM Serif Display, italic, muted opacity (~0.5), smaller than headline
- Button: black pill, white text, arrow icon, hover lifts slightly

### Footer (one line)
```
Left:   BloomOS · 2026
Right:  ● All systems calm
```

---

## 4. Typography

| Element       | Font                | Size  | Weight | Style   | Color              |
|---------------|---------------------|-------|--------|---------|--------------------|
| Wordmark      | DM Serif Display    | 20px  | normal | mixed   | #0d0d0d + #5a8a6a  |
| Headline      | DM Serif Display    | 68px  | normal | normal  | #0d0d0d            |
| "talking."    | DM Serif Display    | 68px  | normal | italic  | #5a8a6a            |
| Tagline       | DM Serif Display    | 17px  | normal | italic  | #0d0d0d at 50% opacity |
| CTA button    | DM Sans             | 14px  | 400    | normal  | #ffffff on #0d0d0d |
| Footer        | DM Sans             | 12px  | 300    | normal  | #0d0d0d at 25% opacity |

Import from Google Fonts:
```html
<link href="https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=DM+Sans:wght@300;400&display=swap" rel="stylesheet">
```

---

## 5. Color Palette

| Name       | Hex       | Usage                                      |
|------------|-----------|--------------------------------------------|
| Ink        | #0d0d0d   | All primary text, button background        |
| White      | #ffffff   | Page background, button text               |
| Off-white  | #f8f8f6   | Fallback page bg (if no video)             |
| Sage       | #5a8a6a   | Italic headline word, wordmark "OS", dot   |
| Mist rule  | rgba(13,13,13,0.07) | Footer separator line           |

No other colors. No gradients. No shadows.

---

## 6. Background Video

```html
<video autoplay muted loop playsinline id="bg-video">
  <source src="YOUR_VIDEO_FILE.mp4" type="video/mp4">
</video>
```

CSS for the video:
```css
#bg-video {
  position: fixed;
  top: 0; left: 0;
  width: 100%; height: 100%;
  object-fit: cover;
  z-index: 0;
  filter: blur(18px);
  transform: scale(1.05); /* prevents blur edge bleed */
}
```

White overlay on top of video:
```css
.overlay {
  position: fixed;
  inset: 0;
  background: rgba(255, 255, 255, 0.58);
  z-index: 1;
}
```

All page content sits at `z-index: 10` or higher.

---

## 7. Layout & Spacing

```
Nav:     padding: 28px 56px  (top, sides)
Hero:    min-height: 100vh, display: flex, align-items: center, justify-content: center
         text-align: center, flex-direction: column
         padding: 0 48px
Footer:  padding: 24px 56px 40px
         border-top: 0.5px solid rgba(13,13,13,0.07)
```

Gap between headline and tagline: `12px`
Gap between tagline and CTA: `48px`
Gap between CTA and footer note: hero bottom handles this via flex

---

## 8. CTA Button

```html
<button class="cta-btn">
  Get started
  <svg ...> <!-- right arrow icon --> </svg>
</button>
```

```css
.cta-btn {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  background: #0d0d0d;
  color: #ffffff;
  font-family: 'DM Sans', sans-serif;
  font-size: 14px;
  font-weight: 400;
  letter-spacing: 0.02em;
  padding: 14px 32px;
  border-radius: 100px;
  border: none;
  cursor: pointer;
  transition: transform 0.15s ease, background 0.2s ease;
}

.cta-btn:hover {
  background: #1a2a20;
  transform: translateY(-1px);
}
```

Arrow SVG (inline, 14×14):
```html
<svg width="14" height="14" viewBox="0 0 16 16" fill="none"
     stroke="currentColor" stroke-width="1.8"
     stroke-linecap="round" stroke-linejoin="round">
  <line x1="3" y1="8" x2="13" y2="8"/>
  <polyline points="9,4 13,8 9,12"/>
</svg>
```

---

## 9. Full HTML Skeleton

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>BloomOS — Your plan is talking.</title>
  <link href="https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=DM+Sans:wght@300;400&display=swap" rel="stylesheet">
  <style>
    /* === Reset === */
    *, *::before, *::after { margin: 0; padding: 0; box-sizing: border-box; }

    /* === Video background === */
    #bg-video {
      position: fixed; top: 0; left: 0;
      width: 100%; height: 100%;
      object-fit: cover; z-index: 0;
      filter: blur(18px); transform: scale(1.05);
    }

    /* === White overlay === */
    .overlay {
      position: fixed; inset: 0;
      background: rgba(255,255,255,0.58);
      z-index: 1;
    }

    /* === Page shell === */
    body {
      font-family: 'DM Sans', sans-serif;
      font-weight: 300;
      background: #f8f8f6;
      color: #0d0d0d;
      min-height: 100vh;
      display: flex;
      flex-direction: column;
    }

    /* === All content above video === */
    nav, main, footer { position: relative; z-index: 10; }

    /* === Nav === */
    nav {
      display: flex;
      align-items: center;
      padding: 28px 56px;
    }

    .wordmark {
      font-family: 'DM Serif Display', serif;
      font-size: 20px;
      color: #0d0d0d;
      letter-spacing: -0.02em;
    }

    .wordmark em {
      font-style: italic;
      color: #5a8a6a;
    }

    /* === Hero === */
    main {
      flex: 1;
      display: flex;
      align-items: center;
      justify-content: center;
      text-align: center;
      padding: 0 48px;
      min-height: calc(100vh - 120px);
    }

    .hero-inner {
      display: flex;
      flex-direction: column;
      align-items: center;
    }

    h1 {
      font-family: 'DM Serif Display', serif;
      font-size: 68px;
      line-height: 1.0;
      letter-spacing: -0.03em;
      color: #0d0d0d;
      margin-bottom: 12px;
    }

    h1 em {
      font-style: italic;
      color: #5a8a6a;
    }

    .tagline {
      font-family: 'DM Serif Display', serif;
      font-size: 17px;
      font-style: italic;
      color: rgba(13,13,13,0.5);
      margin-bottom: 48px;
    }

    /* CTA button styles here (see Section 8) */

    /* === Footer === */
    footer {
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 24px 56px 40px;
      border-top: 0.5px solid rgba(13,13,13,0.07);
    }

    .footer-mark {
      font-family: 'DM Serif Display', serif;
      font-size: 12px;
      color: rgba(13,13,13,0.25);
    }

    .footer-mark em { font-style: italic; }

    .status {
      display: flex;
      align-items: center;
      gap: 7px;
      font-size: 11px;
      font-weight: 300;
      color: rgba(13,13,13,0.35);
    }

    .status-dot {
      width: 5px; height: 5px;
      border-radius: 50%;
      background: #5a8a6a;
    }
  </style>
</head>
<body>

  <!-- Background video (swap src) -->
  <video autoplay muted loop playsinline id="bg-video">
    <source src="YOUR_VIDEO_FILE.mp4" type="video/mp4">
  </video>

  <!-- White wash overlay -->
  <div class="overlay"></div>

  <!-- Nav: wordmark only -->
  <nav>
    <div class="wordmark">Bloom<em>OS</em></div>
  </nav>

  <!-- Hero: full viewport, centered -->
  <main>
    <div class="hero-inner">
      <h1>Your plan is<br><em>talking.</em></h1>
      <p class="tagline">We help you listen.</p>
      <button class="cta-btn">
        Get started
        <svg width="14" height="14" viewBox="0 0 16 16" fill="none"
             stroke="currentColor" stroke-width="1.8"
             stroke-linecap="round" stroke-linejoin="round">
          <line x1="3" y1="8" x2="13" y2="8"/>
          <polyline points="9,4 13,8 9,12"/>
        </svg>
      </button>
    </div>
  </main>

  <!-- Footer: one line -->
  <footer>
    <div class="footer-mark">Bloom<em>OS</em> · 2026</div>
    <div class="status">
      <div class="status-dot"></div>
      All systems calm
    </div>
  </footer>

</body>
</html>
```

---

## 10. What NOT to Build

The agent must not add any of the following:

- [ ] Navigation links (Features, Pricing, About, Sign in)
- [ ] "Now in early access" badge or pill
- [ ] "Trusted by X users" social proof
- [ ] Feature cards or feature sections
- [ ] Pricing section
- [ ] Login / signup form on this page
- [ ] Any decorative illustrations or icons in the hero
- [ ] Gradient backgrounds
- [ ] Drop shadows
- [ ] Any second accent color beyond sage (#5a8a6a)
- [ ] Bold text in body copy

---

## 11. Definition of Done

The page is complete when:

- [ ] Video background is present and blurred, with white overlay
- [ ] Nav shows wordmark only — nothing else
- [ ] Hero headline reads "Your plan is / *talking.*" with italic sage on "talking."
- [ ] Tagline reads "We help you listen." in muted italic serif
- [ ] CTA button is a black pill labeled "Get started →"
- [ ] Footer shows wordmark + year on left, "● All systems calm" on right
- [ ] Zero nav links, zero badges, zero feature cards anywhere on page
- [ ] Page looks clean on 1440px desktop and 375px mobile

---

*End of spec. Do not deviate from this document.*
