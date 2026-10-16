# Ecological Intelligence

A 16-minute, 17-slide primer for students and citizens on how data helps India understand and protect its biodiversity faster. Each slide has an animated Indian habitat (forest, grassland, Thar desert, wetland, Sundarbans coast, Himalaya, night) running continuous ambient loops in plain SVG + CSS.

**Live deck:** https://abhirsc.github.io/ecological-intelligence/ (after the first deploy)

Navigate with ← → / Page Up / Page Down / swipe. Every slide has its own link, e.g. `#Tigers`.

## Contents

| Part | Slides |
|---|---|
| 1 · Why it matters | India's living wealth · six habitats · web of life · eight pressures |
| 2 · Data in action | the intelligence loop · tech workflow · tigers · birds · Great Indian Bustard · forests from space |
| 3 · Laws | 50 years of laws · six ideas worth discussing |
| 4 · Your role | 7-day starter path · recap & quick check · references (APA 7) |

## Repository layout

```
src/
  canvas.json          slide order (Claude Design canvas index)
  slides/*.dc.html     one file per slide, editable in Claude Design
  slides/Habitat.dc.html  the seven shared animated scenes
  eco.css              ambient-loop keyframes
  assets/              photos for the [PHOTO] placeholders
scripts/build.py       flattens src/ into one static page → site/
.github/workflows/pages.yml  builds and deploys to GitHub Pages on every push to main
```

The `.dc.html` files only run inside the Claude Design editor. `scripts/build.py` turns them into a plain HTML deck (no dependencies beyond Python 3).

## Preview locally

```bash
python3 scripts/build.py
python3 -m http.server 8000 -d site
```

Then open http://localhost:8000.

## Editing

- Change slide text in `src/slides/<Slide>.dc.html`, then rebuild.
- Add or reorder slides in `src/canvas.json` (`order`, and a `boards` entry with `"page": "deck"`).
- Replace a `[PHOTO: …]` placeholder: put the image in `src/assets/` and swap the placeholder box for `<img src="assets/your-photo.jpg" alt="…">`. Credit the photographer on the slide.

## Sources

All figures are cited on the slides and listed in full on the References slide. Laws are summarised for awareness and are not legal advice.

## License

- **Code** (`scripts/`, `.github/`, `src/eco.css`, and the HTML/JS structure of the deck): [MIT](LICENSE).
- **Content** (slide text, the animated habitat illustrations in `src/slides/`, and the built deck): [CC BY 4.0](LICENSE-CONTENT). You may share and adapt it for any purpose with credit: *"Ecological Intelligence" by Abhimanyu Raj Singh, CC BY 4.0*.
- **Third-party material** (photos in `src/assets/`, cited data, logos) keeps its own licence and is credited where it appears. It is not covered by the licences above.
