import { monthLabel } from '../shared/dates.js';

export function invoiceHeader(invoice) {
  return `Invoice ${invoice.number} for ${monthLabel(new Date(invoice.issuedAt))}`;
}
