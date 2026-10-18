import { readEntries, writeEntries } from './store.js';
import { total } from './report.js';

const [cmd, amount, category] = process.argv.slice(2);
const entries = readEntries();
if (cmd === 'add') {
  entries.push({ amount: Number(amount), category, at: new Date().toISOString() });
  writeEntries(entries);
} else if (cmd === 'total') {
  console.log(total(entries).toFixed(2));
}
