// Print every lead a signal produced (pages through all of them). Free.
//   node list-leads.mjs <signalId> [sinceISO8601]
import { rodz } from './rodz.mjs';

const [signalId, since] = process.argv.slice(2);
if (!signalId) {
  console.error('Usage: node list-leads.mjs <signalId> [since]');
  process.exit(1);
}

let offset = 0;
let page;
do {
  page = await rodz('GET', `/api/v1/signals/${signalId}/leads`, { query: { limit: 100, offset, since } });
  for (const { signal, contact, company } of page.leads) {
    // contact is "" for a company-level lead (e.g. a funding round without persona targeting)
    const who = contact ? `${contact.first_name} ${contact.last_name} (${contact.title}) ${contact.email}` : '-';
    console.log(`${signal.last_signal_date}  ${company.name.padEnd(30)} ${who}`);
  }
  offset += page.limit;
} while (page.hasMore);
console.log(`${page.total} leads`);
