# Amardev AP — Portfolio

## Folder layout

```
index.html               the page
make_manifest.py         builds assets/manifest.js from the files below
shrink_images.py         shrinks large images before they are committed
assets/
  intro.mp4              top intro video (loops)
  sea.jpg                sea background
  motion/                Motion Graphics files (videos or images)
  design/                Graphic Design files
  brand/                 Branding files
  fonts/                 optional: regular.woff2 and bold.woff2 (licensed font files)
  manifest.js            created by make_manifest.py, do not edit by hand
```

## Adding or changing files

1. Put files in `assets/motion`, `assets/design` or `assets/brand`.
   Name them with numbers to set their order inside each shape group: `01-clip.mp4`, `02-poster.jpg`.
2. Shrink large images (only needed after adding images):
   ```
   py shrink_images.py
   ```
   Originals move to a folder called `portfolio-originals` next to the project, not into the repo.
3. Rebuild the list of files:
   ```
   py make_manifest.py
   ```
4. Commit and push:
   ```
   git add .
   git commit -m "Update portfolio files"
   git push
   ```
   Vercel redeploys automatically.

## How the rows are made

Within each section, files are grouped by shape:

- Portrait files (taller than wide): rows of 3.
- Landscape files (wider than tall): rows of 2.
- Square files: rows of 4.

Groups appear in that order, and file-name order is kept inside each group.
If a group has a leftover file, it forms its own row and stretches to the full width.
Adding or removing one file in that group fixes the row.

Use "Fit" in edit mode to show a whole file without cropping.

## Notes

- Keep videos under 100 MB, since GitHub rejects larger files. `shrink_images.py` lists any that are too large.
- Use MP4 (H.264) for videos. `.mov` files often don't play in Chrome.
- Text, colours and the typeface name can be changed in edit mode, but those changes are saved only in the browser you use.
