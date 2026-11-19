// @ts-check
import { defineConfig } from 'astro/config';

// ─────────────────────────────────────────────────────────────────────────────
// The public address of the website. This is the ONLY place it is set.
// While you're testing on Netlify you can put your Netlify address here
// (e.g. 'https://your-site-name.netlify.app'); once kunaldeoskar.com is
// connected, change it back to 'https://kunaldeoskar.com'.
// It's used for link previews (Instagram/WhatsApp/etc.) and search engines.
// ─────────────────────────────────────────────────────────────────────────────
const SITE_URL = 'https://kunaldeoskar.com';

export default defineConfig({
  site: SITE_URL,
  output: 'static',          // plain HTML files - fast and cheap to host
  trailingSlash: 'ignore',
  build: { format: 'directory' },  // pages live at /works/ rather than /works.html
});
