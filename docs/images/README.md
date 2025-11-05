# Presentation Images

This folder contains screenshots and images used in the executive presentation.

## Naming Convention

Images are **automatically loaded** into slides based on their filename. The system is fully dynamic!

### Format

```
image<NUMBER>-slide-<H>-<V>.<extension>
```

Where:
- `<NUMBER>` = Image number (1, 2, 3, etc.)
- `<H>` = Horizontal slide number (section number)
- `<V>` = Vertical slide number (slide within section)
- `<extension>` = File type (png, jpg, jpeg)

### Examples

**Slide 5.3 (Section 5, Slide 3):**
- `image1-slide-5-3.png`
- `image2-slide-5-3.png`
- `image3-slide-5-3.jpg`

**Slide 2.3 (Section 2, Slide 3):**
- `image1-slide-2-3.png`
- `image2-slide-2-3.png`

**Slide 7.1 (Section 7, Slide 1):**
- `image1-slide-7-1.png`

### Supported Extensions
- `.png` (recommended - best quality)
- `.jpg` / `.jpeg` (smaller file size)

## How It Works

1. Drop your image files into this folder using the naming convention
2. The presentation automatically detects and loads them when you open the HTML
3. Images appear in a responsive grid layout
4. Click any thumbnail to open full-size view in a lightbox
5. Images are sorted by number (image1, image2, image3, etc.)
6. System checks for up to 20 images per slide

## Tips

- **Numbering**: Use sequential numbers (1, 2, 3...) to control display order
- **Format**: PNG recommended for screenshots, JPG for photos
- **Size**: Keep files under 2MB each for faster loading
- **Layout**: Gallery automatically adapts to number of images
- **Slide Numbers**: Check the presentation's slide counter (top right) to see which slide you're on

## Adding Galleries to New Slides

To add an image gallery to any slide in the presentation:

1. **Open** `docs/executive_presentation.html`
2. **Find** the slide where you want the gallery
3. **Add** this HTML code:

```html
<!-- Dynamic image gallery -->
<div data-slide-id="X-Y" class="image-gallery"></div>
<div class="image-placeholder" style="display: none;">
  📸 Drop screenshots into <code>docs/images/</code> folder<br>
  Name them: <code>image1-slide-X-Y.png</code>, <code>image2-slide-X-Y.png</code>, etc.
</div>
```

Replace `X-Y` with your slide number (e.g., `2-3` for section 2, slide 3).

4. **Save** the file
5. **Add images** to this folder with names like `image1-slide-X-Y.png`

## Finding Slide Numbers

The slide number appears in the **top right corner** of the presentation in format `H/V`:
- `5/3` = Section 5, Slide 3 → use `5-3` in filename
- `2/1` = Section 2, Slide 1 → use `2-1` in filename
- `7/0` = Section 7, Title slide → use `7-0` in filename

## No Images Yet?

If no images are found for a slide, the placeholder message appears:
> 📸 Drop screenshots into `docs/images/` folder  
> Name them: `image1-slide-X-Y.png`, `image2-slide-X-Y.png`, etc.
