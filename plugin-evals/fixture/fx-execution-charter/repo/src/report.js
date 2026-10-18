export function total(entries) {
  let t = 0;
  for (const e of entries) t = t + e.amount;
  return t;
}

export function byCategory(entries) {
  const out = {};
  for (const e of entries) out[e.category] = (out[e.category] || 0) + e.amount;
  return out;
}
