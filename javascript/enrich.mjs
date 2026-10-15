// Enrich a person or a company.
//   node enrich.mjs contact https://www.linkedin.com/in/some-profile   # 0.25 credits (cached)
//   node enrich.mjs email Marie Dupont doctolib.fr                     # find a professional email
//   node enrich.mjs company doctolib.fr                                # size, industry, HQ...
import { rodz } from './rodz.mjs';

const [kind, ...args] = process.argv.slice(2);

if (kind === 'contact') {
  // freshness=cached: 0.25 credits, profile at most 8 days old, ~1 s.
  // freshness=live (default): 0.5 credits, fetched at request time.
  const { data } = await rodz('GET', '/api/v1/enrichment/contact', { query: { url: args[0], freshness: 'cached' } });
  console.log(`${data.person.name} - ${data.person.headline} - ${data.person.location}`);
} else if (kind === 'email') {
  const [firstName, lastName, domain] = args;
  const { data } = await rodz('GET', '/api/v1/enrichment/find-email', { query: { firstName, lastName, domain } });
  console.log(JSON.stringify(data, null, 2));
} else if (kind === 'company') {
  const { data } = await rodz('GET', '/api/v1/enrichment/firmographic', { query: { domain: args[0] } });
  const f = data.company.firmographics;
  console.log(`${f.name} - ${f.companySize} employees - ${f.industries} - ${f.HQcity}, ${f.HQcountry}`);
} else {
  console.error('Usage: node enrich.mjs contact <LinkedIn URL> | email <first> <last> <domain> | company <domain>');
  process.exit(1);
}
