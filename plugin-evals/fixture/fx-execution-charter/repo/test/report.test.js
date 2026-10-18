import { total } from '../src/report.js';

if (total([{ amount: 1 }, { amount: 2 }]) !== 3) throw new Error('total');
