# Presentation Style Guide

> **Source:** `executive_presentation.html`  
> **Version:** 1.0.0  
> **Last Updated:** November 2025

This document captures the design system, color palette, component patterns, and technical implementation used in the executive presentation. Use this as a reference for creating future presentations with consistent styling.

---

## Table of Contents
1. [Color Palette](#color-palette)
2. [Typography](#typography)
3. [Layout Patterns](#layout-patterns)
4. [Component Library](#component-library)
5. [Animation & Transitions](#animation--transitions)
6. [Image Gallery System](#image-gallery-system)
7. [Technical Stack](#technical-stack)
8. [Implementation Examples](#implementation-examples)

---

## Color Palette

### Primary Colors
```css
--primary-blue: #005ea2;        /* Main headings, borders, primary elements */
--secondary-blue: #0074c8;      /* Gradients, secondary headings */
--gradient-blue: linear-gradient(135deg, #005ea2 0%, #0074c8 100%);
```

### Status Colors
```css
--success-green: #28a745;       /* Success badges, positive highlights */
--warning-yellow: #ffc107;      /* Warning badges, caution items */
--info-blue: #17a2b8;          /* Info badges */
--badge-primary: #005ea2;       /* Primary badges */
```

### Neutral Colors
```css
--light-gray: #f8f9fa;         /* Backgrounds, metric cards */
--border-gray: #ccc;           /* Borders, placeholders */
--text-gray: #666;             /* Secondary text */
--text-dark: #333;             /* Primary text */
--white: #ffffff;              /* Text on colored backgrounds */
```

### Highlight Backgrounds
```css
--highlight-info: #e8f4f8;     /* Info boxes */
--highlight-warning: #fff3cd;   /* Warning boxes */
--highlight-success: #d4edda;   /* Success boxes */
```

---

## Typography

### Font Family
```css
font-family: Arial, Calibri, sans-serif;
```

### Heading Sizes
```css
h1: 2em;      /* Title slides */
h2: 1.5em;    /* Section titles, content slides */
h3: 1.2em;    /* Subsections */
```

### Content Text Sizes
```css
.content-slide ul: 0.75em;
.badge: 0.7em;
.metric-label: 0.7em;
.checklist: 0.7em;
```

### Line Heights
```css
line-height: 1.5;   /* List items */
line-height: 1.6;   /* Questions list */
line-height: 1.2;   /* Metrics, headings */
```

---

## Layout Patterns

### Table of Contents Slide (NEW!)
Navigable table of contents with block-style links:
```html
<section class="toc-slide">
  <h2>📑 Table of Contents</h2>
  <ul>
    <li><a href="#/2">📋 Project Overview</a></li>
    <li><a href="#/3">📊 Current Progress</a></li>
    <!-- More sections -->
  </ul>
</section>
```

**Style:**
- Clean block links with light background (#f0f4f8)
- Blue left border accent (4px solid #005ea2)
- Hover effect: brightens, slides right, adds shadow
- Compact font sizing (0.65em) to fit many sections
- No bullet points (list-style: none)

```css
.toc-slide a {
  display: block;
  padding: 0.5em 0.8em;
  background: #f0f4f8;
  border-left: 4px solid #005ea2;
  border-radius: 4px;
}

.toc-slide a:hover {
  background: #e8f4f8;
  transform: translateX(5px);
  box-shadow: 0 2px 4px rgba(0, 94, 162, 0.15);
}
```

### Section Title Slides
Full-screen colored background with centered content:
```html
<section class="section-title">
  <h2>📋 Section Name</h2>
</section>
```

**Style:**
- Blue gradient background
- White text
- Vertically and horizontally centered
- 100% height

### Content Slides
Left-aligned text with bullet points and optional components:
```html
<section class="content-slide">
  <h2>Slide Title</h2>
  <ul>
    <li class="fragment">Point 1</li>
    <li class="fragment">Point 2</li>
  </ul>
</section>
```

**Style:**
- Left-aligned text
- 1em padding
- Max height 85vh with scroll overflow
- Font size 0.75em for lists

### Two-Column Layout
```html
<div class="two-column">
  <div class="col">
    <h3>Left Column</h3>
    <ul>...</ul>
  </div>
  <div class="col">
    <h3>Right Column</h3>
    <ul>...</ul>
  </div>
</div>
```

---

## Component Library

### Badges
Status indicators for milestones, tasks, etc.

```html
<span class="badge badge-success">✅ COMPLETE</span>
<span class="badge badge-warning">🚧 IN PROGRESS</span>
<span class="badge badge-info">ℹ️ INFO</span>
<span class="badge badge-primary">📌 PRIMARY</span>
```

**CSS:**
```css
.badge {
  display: inline-block;
  padding: 0.3em 0.6em;
  border-radius: 4px;
  font-size: 0.7em;
  font-weight: bold;
  margin: 0 0.2em;
}
```

### Metric Cards
Display key numbers with labels:
```html
<div class="metrics">
  <div class="metric-card fragment">
    <div class="metric-value">≥80%</div>
    <div class="metric-label">Cancellations Filled<br>Within 2 Hours</div>
  </div>
  <!-- Repeat for more metrics -->
</div>
```

**Design:**
- Flexbox container with space-around
- Blue border (2px solid #005ea2)
- Light gray background
- Min-width: 140px, Max-width: 200px
- Responsive wrapping

### Highlight Boxes
Colored boxes with left border accent:
```html
<div class="highlight-box">
  <strong>Key Point:</strong> Important information here
</div>

<div class="highlight-box warning">
  <strong>Warning:</strong> Caution information
</div>

<div class="highlight-box success">
  <strong>Success:</strong> Positive information
</div>
```

**Variants:**
- Default: Blue background (#e8f4f8), blue border
- Warning: Yellow background (#fff3cd), yellow border
- Success: Green background (#d4edda), green border

### Architecture Diagrams
Text-based diagrams with monospace font:
```html
<div class="architecture-box">
┌─────────────┐         ┌──────────────┐
│  Component  │────────>│  Component   │
└─────────────┘         └──────────────┘
</div>
```

### Checklist Items
Simple task lists:
```html
<div class="checklist">
  <ul>
    <li>☐ Incomplete task</li>
    <li>✅ Complete task</li>
  </ul>
</div>
```

---

## Animation & Transitions

### Fragment Reveals
Reveal.js fragment system for step-by-step content:
```html
<li class="fragment">Appears on click</li>
<div class="metric-card fragment">Appears on click</div>
```

### Fragment Grey-Out Effect (NEW!)
Previously shown fragments automatically fade to grey:
```css
/* Previously visible fragments fade out */
.fragment.visible:not(.current-fragment) {
  opacity: 0.45;
  color: #888;
  transition: opacity 0.5s ease, color 0.5s ease;
}

/* Current fragment stays bright */
.fragment.current-fragment {
  opacity: 1 !important;
  color: inherit !important;
}
```

**Effect:** When clicking through bullet points, previous items grey out (45% opacity) while the current item remains fully visible. This focuses attention on new content.

### Configuration
```javascript
Reveal.initialize({
  fragments: true,
  fragmentInURL: false,
  transition: 'slide',
  pdfSeparateFragments: false
});
```

### Hover Effects
```css
.image-gallery a:hover {
  transform: scale(1.15);
  box-shadow: 0 3px 6px rgba(0, 94, 162, 0.4);
  border-color: #0074c8;
}
```

---

## Image Gallery System

### Compact Icon View with Lightbox
Small thumbnail icons that expand to full-size lightbox on click.

**HTML Structure:**
```html
<!-- Dynamic gallery populated by JavaScript -->
<div data-slide-id="2-3" class="image-gallery"></div>
<div class="image-placeholder" style="display: none;">
  📸 Drop screenshots into <code>docs/images/</code> folder<br>
  Name them: <code>image1-slide-2-3.png</code>, etc.
</div>
```

**File Naming Convention:**
```
images/image1-slide-2-3.png
images/image2-slide-2-3.jpg
images/image3-slide-5-1.png
```
Format: `imageN-slide-X-Y.{ext}`
- N = sequential number (1, 2, 3...)
- X-Y = slide coordinates (section-subsection)
- ext = png, jpg, or jpeg

**Features:**
- Auto-discovers images by naming pattern
- Supports PNG, JPG, JPEG formats
- Shows picture emoji icon (🖼️) with semi-transparent image preview
- Hover effect: scale + shadow
- Click opens GLightbox full-screen viewer
- Gallery groups by slide ID
- Auto-sorts by image number

**CSS:**
```css
.image-gallery {
  display: flex;
  flex-wrap: wrap;
  gap: 0.3em;
  margin: 0.5em 0;
  align-items: center;
}

.image-gallery a {
  display: flex;
  width: 50px;
  height: 50px;
  border: 2px solid #005ea2;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s;
}

.image-gallery a::before {
  content: '🖼️';
  font-size: 24px;
  position: absolute;
  z-index: 1;
}

.image-gallery img {
  opacity: 0.3;
}
```

---

## Technical Stack

### Core Libraries
```html
<!-- Reveal.js for presentation -->
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/reveal.js@5.2.0/dist/reveal.css">
<script src="https://cdn.jsdelivr.net/npm/reveal.js@5.2.0/dist/reveal.js"></script>

<!-- GLightbox for image galleries -->
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/glightbox@3.2.0/dist/css/glightbox.min.css">
<script src="https://cdn.jsdelivr.net/npm/glightbox@3.2.0/dist/js/glightbox.min.js"></script>
```

### Configuration
```javascript
Reveal.initialize({
  hash: true,
  controls: true,
  progress: true,
  center: false,          // Left-align content
  transition: 'slide',
  slideNumber: 'h/v',     // Show horizontal/vertical numbers
  showSlideNumber: 'all',
  pdfMaxPagesPerSlide: 1,
  pdfSeparateFragments: false
});
```

---

## Implementation Examples

### Complete Slide with All Components
```html
<section class="content-slide">
  <h2>Feature Overview</h2>
  <div style="font-size: 0.75em;">
    <p><span class="badge badge-success">✅ COMPLETE</span> <strong>Phase 1</strong></p>
    <ul>
      <li class="fragment">Feature description here</li>
      <li class="fragment">Another feature point</li>
    </ul>
    
    <div class="highlight-box success fragment">
      <strong>Key Insight:</strong> Important takeaway message
    </div>
    
    <div class="metrics">
      <div class="metric-card fragment">
        <div class="metric-value">95%</div>
        <div class="metric-label">Success Rate</div>
      </div>
    </div>
    
    <!-- Image gallery -->
    <div data-slide-id="3-2" class="image-gallery"></div>
  </div>
</section>
```

### Gantt Chart Pattern
```html
<table style="width: 100%; border-collapse: collapse;">
  <thead>
    <tr style="background: #005ea2; color: white;">
      <th style="padding: 0.5em;">Task</th>
      <th style="padding: 0.5em;">Week 1</th>
      <th style="padding: 0.5em;">Week 2</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td style="padding: 0.3em;">Task name</td>
      <td style="background: #66bb6a; border: 1px solid white;"></td>
      <td></td>
    </tr>
  </tbody>
</table>

<!-- Legend -->
<div style="display: flex; gap: 1em; font-size: 0.8em;">
  <span><span style="width: 15px; height: 10px; background: #66bb6a;"></span> Development</span>
  <span><span style="width: 15px; height: 10px; background: #ffa726;"></span> Review</span>
</div>
```

---

## Best Practices

### Content Guidelines
1. **Keep slides concise** - 5-7 bullet points max per slide
2. **Use fragments** - Progressive reveal for complex content
3. **Visual hierarchy** - Use badges, boxes, and spacing
4. **Consistent sizing** - Stick to defined font-size scales
5. **White space** - Don't overcrowd slides

### Image Guidelines
1. **File naming** - Follow `imageN-slide-X-Y.ext` convention
2. **Formats** - Prefer PNG for screenshots, JPG for photos
3. **Resolution** - Use 1920x1080 or higher for full-screen images
4. **Thumbnails** - System auto-generates from full images
5. **Placement** - Put galleries after related content

### Color Usage
1. **Consistency** - Use defined palette colors only
2. **Accessibility** - Maintain sufficient contrast ratios
3. **Semantic meaning** - Green=success, Yellow=warning, Blue=info
4. **Backgrounds** - Light colors for text, dark for headers

### Animation Guidelines
1. **Fragment order** - Logical reveal sequence
2. **Not too much** - Don't fragment every single item
3. **Meaningful groups** - Fragment related concepts together
4. **Performance** - Avoid heavy CSS animations on many elements

---

## Quick Start Template

```html
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>My Presentation</title>
  
  <!-- Reveal.js -->
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/reveal.js@5.2.0/dist/reset.css">
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/reveal.js@5.2.0/dist/reveal.css">
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/reveal.js@5.2.0/dist/theme/white.css">
  
  <!-- GLightbox -->
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/glightbox@3.2.0/dist/css/glightbox.min.css">
  
  <style>
    /* Copy styles from executive_presentation.html */
    /* See sections: Typography, Layout, Components above */
  </style>
</head>
<body>
  <div class="reveal">
    <div class="slides">
      
      <!-- Title Slide -->
      <section>
        <h1>Presentation Title</h1>
        <h3>Subtitle</h3>
      </section>
      
      <!-- Section Title -->
      <section class="section-title">
        <h2>Section Name</h2>
      </section>
      
      <!-- Content Slide -->
      <section class="content-slide">
        <h2>Slide Title</h2>
        <ul>
          <li class="fragment">Point 1</li>
          <li class="fragment">Point 2</li>
        </ul>
      </section>
      
    </div>
  </div>
  
  <script src="https://cdn.jsdelivr.net/npm/reveal.js@5.2.0/dist/reveal.js"></script>
  <script src="https://cdn.jsdelivr.net/npm/glightbox@3.2.0/dist/js/glightbox.min.js"></script>
  <script>
    Reveal.initialize({
      hash: true,
      controls: true,
      progress: true,
      center: false,
      transition: 'slide',
      slideNumber: 'h/v',
      showSlideNumber: 'all',
      fragments: true
    });
    
    /* Copy image loading script from executive_presentation.html */
  </script>
</body>
</html>
```

---

## Customization Notes

### Changing Colors
Replace color variables in the `<style>` section:
```css
:root {
  --primary: #005ea2;    /* Change to your brand color */
  --secondary: #0074c8;
}

.reveal h1 { color: var(--primary); }
```

### Adding New Sections
Follow the pattern: Section title slide → Content slides
```html
<section>
  <section class="section-title">
    <h2>New Section</h2>
  </section>
  <section class="content-slide">
    <!-- Content here -->
  </section>
</section>
```

### Custom Components
Add new component classes following existing naming patterns:
- `.component-name` for the container
- `.component-name-item` for child elements
- Use flexbox for responsive layouts
- Follow color palette for consistency

---

## Resources

- **Reveal.js Documentation:** https://revealjs.com/
- **GLightbox Documentation:** https://github.com/biati-digital/glightbox
- **Source File:** `docs/executive_presentation.html`

---

**Document History:**
- v1.0.0 (Nov 2025): Initial style guide extracted from executive presentation
