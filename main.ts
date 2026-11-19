// make.fun · news-image-20261119
// Writes the day's front page to /output/entry.png.
//
// The artwork is composed ahead of time by tools/make_image.py (Pillow, fixed
// seed) and committed as entry.png; this program only publishes it.  The run
// has no network and must be deterministic: the bytes it writes are the bytes
// in the repository, every time.

import { mkdirSync, readFileSync, writeFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const here = dirname(fileURLToPath(import.meta.url));
const outDir = process.env.MAKEFUN_OUTPUT_DIR ?? "/output";
const source = join(here, "entry.png");
const target = join(outDir, "entry.png");

const bytes = readFileSync(source);

// The brief caps the file at 1 MiB and 1024x1024 pixels: check, never assume.
const LIMIT = 1024 * 1024;
if (bytes.byteLength > LIMIT) {
  throw new Error(`entry.png is ${bytes.byteLength} bytes, over the 1 MiB cap`);
}

// PNG: the signature, then the IHDR chunk's width and height.
const isPng = bytes.subarray(0, 8).equals(Buffer.from([0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a]));
if (isPng) {
  const width = bytes.readUInt32BE(16);
  const height = bytes.readUInt32BE(20);
  if (width > 1024 || height > 1024) {
    throw new Error(`entry.png is ${width}x${height}, over the 1024x1024 cap`);
  }
} else if (bytes[0] !== 0xff || bytes[1] !== 0xd8) {
  throw new Error("entry.png is neither a PNG nor a JPEG");
}

mkdirSync(outDir, { recursive: true });
writeFileSync(target, bytes);

// Read the copy back: a short write must fail the run, not ship a broken file.
const written = readFileSync(target);
if (written.byteLength !== bytes.byteLength || !written.equals(bytes)) {
  throw new Error(`entry.png did not survive the write to ${target}`);
}
console.log(`wrote ${target} (${bytes.byteLength} bytes)`);
