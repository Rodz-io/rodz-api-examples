// Create a signal from one of the bodies in ../signals/.
//
//   node create-signal.mjs job-changes             # people who just started a new job
//   node create-signal.mjs fundraising             # companies that just raised a round
//   node create-signal.mjs job-offers              # companies hiring for a role
//   node create-signal.mjs competitor-connections  # people connecting with your competitors' teams
//
//   node create-signal.mjs job-changes --activate --webhook https://your-server.example/webhooks/rodz
//
// The bodies create a DRAFT: nothing runs and nothing is charged until the signal is active.
// An active signal is charged per lead delivered, up to its dailyLeadLimit.
import { readFileSync } from 'node:fs';
import { join } from 'node:path';
import { ROOT, rodz } from './rodz.mjs';

const CREATE = {
  'job-changes': 'POST /api/v1/signals/job-changes',
  fundraising: 'POST /api/v1/signals/fundraising',
  'job-offers': 'POST /api/v1/signals/job-offers',
  'competitor-connections': 'POST /api/v1/signals/competitor-connections',
};

const [signal, ...flags] = process.argv.slice(2);
if (!CREATE[signal]) {
  console.error(`Usage: node create-signal.mjs ${Object.keys(CREATE).join('|')} [--activate] [--webhook URL]`);
  process.exit(1);
}
const body = JSON.parse(readFileSync(join(ROOT, 'signals', `${signal}.json`), 'utf8'));
if (flags.includes('--activate')) body.status = 'active';
const w = flags.indexOf('--webhook');
if (w !== -1) body.webhookUrl = flags[w + 1];

const [method, path] = CREATE[signal].split(' ');
const created = await rodz(method, path, { body });
console.log(`Created ${created.signalTypeId} signal ${created.id} (${created.status})`);
for (const warning of created.warnings ?? []) console.log(`  warning [${warning.code}]: ${warning.message}`);
