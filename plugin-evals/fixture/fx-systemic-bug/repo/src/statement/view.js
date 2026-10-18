import { monthLabel } from '../shared/dates.js';

export function statementTitle(statement) {
  return `Statement, ${monthLabel(new Date(statement.periodEnd))}`;
}
