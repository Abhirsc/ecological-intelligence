#!/usr/bin/env python3
"""Build the public presentation site from the Design canvas sources.

Inputs
  src/canvas.json           slide order (the canvas index exported from Claude Design)
  src/slides/*.dc.html      one Design Component file per slide
  src/slides/Habitat.dc.html  the shared animated habitat scenes
  src/eco.css               the ambient-loop keyframes
  src/assets/               photos and other files (copied as-is)

Output
  site/index.html           one self-contained deck: arrow keys / swipe to navigate,
                            #SlideName links, scales to any screen

The .dc.html files only run inside the Claude Design editor, so this script
flattens them to plain HTML: Habitat imports become inline SVG, template holes
are resolved, and links between slides become #anchors.

Usage:  python3 scripts/build.py
"""
import html
import json
import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / 'src'
SLIDES = SRC / 'slides'
OUT = ROOT / 'site'

# Same sizes as Habitat.dc.html's renderVals(): mode -> (width, height, preserveAspectRatio)
MODES = {
    'full': (1280, 720, 'xMidYMid slice'),
    'band': (1280, 140, 'xMidYMax slice'),
    'half': (560, 720, 'xMidYMid slice'),
    'tile': (360, 190, 'xMidYMid slice'),
}

SITE_TITLE = 'Ecological Intelligence: data-driven nature insights for India'
SITE_DESC = ('A 16-minute primer for students and citizens on how data helps India '
             'understand and protect its biodiversity faster.')


def fail(msg):
    sys.exit(f'build failed: {msg}')


def load_scenes():
    text = (SLIDES / 'Habitat.dc.html').read_text(encoding='utf-8')
    found = re.findall(r'<sc-if value="\{\{is(\w+)\}\}"[^>]*>\s*(<svg.*?</svg>)\s*</sc-if>', text, re.S)
    scenes = {name.lower(): svg for name, svg in found}
    if not scenes:
        fail('no habitat scenes found in Habitat.dc.html')
    return scenes


def scene_html(scenes, habitat, mode):
    if habitat not in scenes:
        fail(f'unknown habitat "{habitat}"')
    if mode not in MODES:
        fail(f'unknown habitat mode "{mode}"')
    w, h, par = MODES[mode]
    svg = scenes[habitat].replace('{{par}}', par).replace('{{w}}', str(w)).replace('{{h}}', str(h))
    fade = '<div class="band-fade"></div>' if mode == 'band' else ''
    return f'<div class="scene" style="width: {w}px; height: {h}px">{svg}{fade}</div>'


def slide_body(path, scenes):
    text = path.read_text(encoding='utf-8')
    title = re.search(r'<title>(.*?)</title>', text, re.S).group(1).strip()
    body = re.search(r'<x-dc>(.*)</x-dc>', text, re.S).group(1)
    body = re.sub(r'<helmet>.*?</helmet>', '', body, flags=re.S)
    body = re.sub(
        r'<dc-import name="Habitat" habitat="(\w+)" mode="(\w+)"[^>]*></dc-import>',
        lambda m: scene_html(scenes, m[1], m[2]), body)
    body = re.sub(r'href="([\w-]+)\.dc\.html"', r'href="#\1"', body)
    # Recap quiz: the Design version keeps show/hide in component state
    body = body.replace('onClick="{{toggle}}"', 'data-action="toggle-answers"')
    body = body.replace('{{buttonLabel}}', 'Show answers')
    body = re.sub(r'<sc-if value="\{\{show\}\}"[^>]*>(.*?)</sc-if>',
                  r'<span class="answer" hidden>\1</span>', body, flags=re.S)
    leftover = re.findall(r'\{\{.*?\}\}|<sc-\w+|<dc-\w+', body)
    if leftover:
        fail(f'{path.name} has template syntax the build does not handle: {leftover[:3]}')
    return title, body.strip()


def slide_order():
    canvas = json.loads((SRC / 'canvas.json').read_text(encoding='utf-8'))
    boards = canvas['boards']
    return [name for name in canvas['order']
            if boards.get(name, {}).get('page') == 'deck' and name != 'Habitat.dc.html']


PAGE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{desc}">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,500;12..96,700&amp;family=Noto+Sans:wght@400;500;600&amp;display=swap" rel="stylesheet">
<link rel="stylesheet" href="eco.css">
<style>
:root{{color-scheme:dark}}
html,body{{margin:0;background:#0b1712;color:#EEF2E6;font-family:'Noto Sans',system-ui,sans-serif}}
a{{color:#E9A93A}}a:hover{{color:#f5c56e}}
.slide{{width:1280px;height:720px;position:relative;overflow:hidden;margin:0 auto 24px}}
.scene{{position:relative;overflow:hidden;background:#10241C}}
.scene svg{{display:block}}
.band-fade{{position:absolute;left:0;right:0;top:0;height:36px;background:linear-gradient(#10241C,rgba(16,36,28,0));pointer-events:none}}
.js body{{overflow:hidden}}
.js .deck{{position:fixed;inset:0}}
.js .slide{{display:none;position:absolute;left:50%;top:50%;margin:0;transform:translate(-50%,-50%) scale(var(--s,1))}}
.js .slide.active{{display:block}}
.controls{{display:none}}
.js .controls{{display:flex;position:fixed;left:12px;bottom:12px;gap:6px;align-items:center;font-size:13px;color:#A9B8A6;z-index:2}}
.controls button{{min-width:44px;min-height:44px;border-radius:999px;border:1px solid #3B6450;background:rgba(16,36,28,.85);color:#EEF2E6;font:500 18px 'Noto Sans',sans-serif;cursor:pointer}}
.controls button:focus-visible,.slide a:focus-visible,.slide button:focus-visible{{outline:3px solid #E9A93A;outline-offset:2px}}
.progress{{display:none}}
.js .progress{{display:block;position:fixed;left:0;bottom:0;height:4px;background:#E9A93A;transition:width .3s;z-index:2}}
</style>
</head>
<body>
<main class="deck">
{slides}
</main>
<div class="controls" aria-label="Slide controls">
<button type="button" data-action="prev" aria-label="Previous slide">←</button>
<button type="button" data-action="next" aria-label="Next slide">→</button>
<span class="counter" aria-live="polite"></span>
</div>
<div class="progress" aria-hidden="true"></div>
<script>
(function () {{
  document.documentElement.classList.add('js');
  var slides = Array.prototype.slice.call(document.querySelectorAll('.slide'));
  var ids = slides.map(function (s) {{ return s.id; }});
  var counter = document.querySelector('.counter');
  var bar = document.querySelector('.progress');
  var cur = -1;
  function fit() {{
    var s = Math.min(window.innerWidth / 1280, window.innerHeight / 720);
    document.documentElement.style.setProperty('--s', s);
  }}
  function show(i) {{
    i = Math.max(0, Math.min(slides.length - 1, i));
    if (i === cur) return;
    slides.forEach(function (s, k) {{
      var on = k === i;
      s.classList.toggle('active', on);
      s.setAttribute('aria-hidden', on ? 'false' : 'true');
      s.inert = !on;
    }});
    cur = i;
    counter.textContent = (i + 1) + ' / ' + slides.length;
    bar.style.width = ((i + 1) / slides.length * 100) + '%';
    document.title = slides[i].getAttribute('aria-label') + ' · Ecological Intelligence';
    if (location.hash.slice(1) !== ids[i]) history.replaceState(null, '', '#' + ids[i]);
  }}
  function fromHash() {{
    var i = ids.indexOf(location.hash.slice(1));
    show(i < 0 ? 0 : i);
  }}
  window.addEventListener('hashchange', fromHash);
  window.addEventListener('resize', fit);
  document.addEventListener('keydown', function (e) {{
    if (e.altKey || e.ctrlKey || e.metaKey) return;
    var onControl = e.target.closest && e.target.closest('a,button,input,textarea');
    if (e.key === 'ArrowRight' || e.key === 'PageDown' || (e.key === ' ' && !onControl)) {{ e.preventDefault(); show(cur + 1); }}
    else if (e.key === 'ArrowLeft' || e.key === 'PageUp') {{ e.preventDefault(); show(cur - 1); }}
    else if (e.key === 'Home') show(0);
    else if (e.key === 'End') show(slides.length - 1);
  }});
  document.addEventListener('click', function (e) {{
    var t = e.target.closest('[data-action]');
    if (!t) return;
    var a = t.getAttribute('data-action');
    if (a === 'next') show(cur + 1);
    else if (a === 'prev') show(cur - 1);
    else if (a === 'toggle-answers') {{
      var answers = t.closest('.slide').querySelectorAll('.answer');
      var reveal = answers.length && answers[0].hidden;
      answers.forEach(function (n) {{ n.hidden = !reveal; }});
      t.textContent = reveal ? 'Hide answers' : 'Show answers';
    }}
  }});
  var x0 = null;
  document.addEventListener('touchstart', function (e) {{ x0 = e.touches[0].clientX; }}, {{ passive: true }});
  document.addEventListener('touchend', function (e) {{
    if (x0 === null) return;
    var dx = e.changedTouches[0].clientX - x0;
    if (Math.abs(dx) > 50) show(cur + (dx < 0 ? 1 : -1));
    x0 = null;
  }});
  fit();
  fromHash();
}})();
</script>
</body>
</html>
"""


def main():
    scenes = load_scenes()
    sections = []
    for name in slide_order():
        path = SLIDES / name
        if not path.exists():
            fail(f'{name} is listed in canvas.json but missing from src/slides/')
        title, body = slide_body(path, scenes)
        sid = name[:-len('.dc.html')]
        sections.append(f'<section class="slide" id="{sid}" aria-label="{html.escape(title, quote=True)}">\n{body}\n</section>')
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir()
    (OUT / 'index.html').write_text(
        PAGE.format(title=html.escape(SITE_TITLE), desc=html.escape(SITE_DESC, quote=True),
                    slides='\n'.join(sections)),
        encoding='utf-8')
    shutil.copy(SRC / 'eco.css', OUT / 'eco.css')
    if (SRC / 'assets').exists():
        shutil.copytree(SRC / 'assets', OUT / 'assets', ignore=shutil.ignore_patterns('.gitkeep'))
    (OUT / '.nojekyll').write_text('')
    print(f'built {len(sections)} slides -> {OUT / "index.html"}')


if __name__ == '__main__':
    main()
