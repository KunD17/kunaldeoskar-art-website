// Tells Astro what an artwork looks like, and reads them all from artworks.yaml.
// If a detail is missing or mistyped in artworks.yaml, the build stops with a
// message naming the artwork and the field, instead of publishing a broken page.
import { defineCollection } from 'astro:content';
import { file } from 'astro/loaders';
import { z } from 'astro/zod';
import { parse } from 'yaml';

const artworks = defineCollection({
  // Each entry gets an `order` number from its position in the file,
  // so the website always shows works in the same order as artworks.yaml.
  loader: file('artworks.yaml', {
    parser: (text) => (parse(text) as Record<string, unknown>[]).map((entry, i) => ({ ...entry, order: i })),
  }),
  schema: ({ image }) =>
    z.object({
      title: z.string(),
      year: z.number().int(),
      medium: z.string(),
      size: z.string(),
      series: z.string().optional(),
      image: image(), // checks the file exists and lets Astro optimise it
      alt: z.string(),
      description: z.string().optional(),
      hero: z.boolean().default(false),
      selected: z.boolean().default(false),
      order: z.number(), // added automatically above - don't write this in artworks.yaml
    }),
});

export const collections = { artworks };
