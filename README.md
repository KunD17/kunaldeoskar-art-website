# kunaldeoskar.com

Portfolio website for Kunal Deoskar, built with [Astro](https://astro.build) and hosted on Netlify.

## Everyday tasks

| I want to…                       | Edit this file                         |
|----------------------------------|----------------------------------------|
| Add / change an artwork          | `artworks.yaml`                        |
| Change bio, statement or CV      | `src/data/about.md`                    |
| Change email or Instagram        | `src/settings.ts`                      |
| Change the About-page portrait   | top of `src/pages/about.astro`         |
| Change colours or fonts          | top of `src/styles/global.css`         |
| Change the website address       | `SITE_URL` in `astro.config.mjs`       |

### Adding a new artwork
1. Put the high-res original in `original_heavy/` (never uploaded to GitHub).
2. Run `npm run images` - makes a watermarked web copy in `images/`.
3. Add a block for it in `artworks.yaml` (instructions are at the top of that file).

## Commands (run in this folder, in the terminal)

| Command            | What it does                                                    |
|--------------------|-----------------------------------------------------------------|
| `npm install`      | First time only: downloads Astro etc. into `node_modules/`      |
| `npm run dev`      | Live preview at http://localhost:4321 - updates as you save     |
| `npm run build`    | Builds the final site into `dist/` (what Netlify does)          |
| `npm run preview`  | Previews that final build locally                               |
| `npm run images`   | Makes web-optimised, watermarked copies of new originals        |

Requires Node.js 22.23 or newer and Python 3 with Pillow (for `npm run images`).
