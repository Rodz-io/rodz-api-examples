// How many credits are left on the account. Free.
//   node check-credits.mjs
import { rodz } from './rodz.mjs';

const balance = await rodz('GET', '/api/v1/account/credits');
console.log(`${balance.credits} credits left (${balance.companyName ?? 'your account'})`);

// Where the credits went over the last 7 days, by endpoint.
const usage = await rodz('GET', '/api/v1/account/credits/usage', { query: { interval: 'day' } });
console.log(`Last 7 days: ${usage.totalCredits} credits over ${usage.totalCalls} calls`);
for (const row of usage.byEndpoint) {
  console.log(`  ${row.endpoint.padEnd(40)} ${row.credits} credits, ${row.calls} calls`);
}
