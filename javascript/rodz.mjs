// Tiny helper shared by the examples: reads RODZ_API_KEY and calls the Rodz API (Node 18+ fetch).
import { existsSync, readFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

export const ROOT = join(dirname(fileURLToPath(import.meta.url)), '..');
const BASE_URL = process.env.RODZ_BASE_URL || 'https://api.rodz.io';

function apiKey() {
  const envFile = join(ROOT, '.env');
  if (!process.env.RODZ_API_KEY && existsSync(envFile)) {
    for (const line of readFileSync(envFile, 'utf8').split(/\r?\n/)) {
      const m = line.match(/^\s*([A-Z_]+)\s*=\s*(.*)$/);
      if (m && !process.env[m[1]]) process.env[m[1]] = m[2].trim();
    }
  }
  if (!process.env.RODZ_API_KEY) {
    console.error('Set RODZ_API_KEY (copy .env.example to .env and paste your key).');
    process.exit(1);
  }
  return process.env.RODZ_API_KEY;
}

/** Call the API and return the JSON body. Exits with the API's error message on 4xx/5xx. */
export async function rodz(method, path, { query, body } = {}) {
  const url = new URL(BASE_URL + path);
  for (const [k, v] of Object.entries(query || {})) if (v !== undefined) url.searchParams.set(k, v);
  const resp = await fetch(url, {
    method,
    headers: {
      Authorization: `Bearer ${apiKey()}`,
      ...(body ? { 'Content-Type': 'application/json' } : {}),
    },
    body: body ? JSON.stringify(body) : undefined,
  });
  if (!resp.ok) {
    console.error(`${resp.status}: ${await resp.text()}`);
    process.exit(1);
  }
  return resp.json();
}
