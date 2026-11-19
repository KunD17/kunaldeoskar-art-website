// Small helpers so every page gets artworks the same way, in the order of artworks.yaml.
import { getCollection, type CollectionEntry } from 'astro:content';

export type Artwork = CollectionEntry<'artworks'>;

export async function getArtworks(): Promise<Artwork[]> {
  const all = await getCollection('artworks');
  return all.sort((a, b) => a.data.order - b.data.order); // same order as artworks.yaml
}

/** "Oil on canvas · 60 × 50 cm" style caption line. */
export function details(a: Artwork): string {
  return [a.data.medium, a.data.size].filter(Boolean).join(' · ');
}
