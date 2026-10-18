import fs from 'node:fs';

const FILE = process.env.LEDGER_FILE || 'ledger.json';

export function readEntries() {
  return fs.existsSync(FILE) ? JSON.parse(fs.readFileSync(FILE, 'utf8')) : [];
}

export function writeEntries(entries) {
  fs.writeFileSync(FILE, JSON.stringify(entries, null, 2));
}
