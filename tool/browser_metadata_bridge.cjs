const readline = require('node:readline');
const path = require('node:path');
const testing = require.resolve('@playwright/test');
const { chromium } = require(require.resolve('playwright', { paths: [path.dirname(testing)] }));

async function main() {
  const [cdpURL, origin] = process.argv.slice(2);
  const browser = await chromium.connectOverCDP(cdpURL, { timeout: 30000 });
  const authenticated = browser.contexts().flatMap(context => context.pages())
    .find(candidate => candidate.url().startsWith(origin + '/'));
  if (!authenticated) throw new Error('browser_page_missing');
  const page = await authenticated.context().newPage();
  await page.route('**/flutter_bootstrap.js', route => route.fulfill({
    status: 200, contentType: 'application/javascript', body: '',
  }));
  await page.goto(origin + '/', { waitUntil: 'domcontentloaded', timeout: 30000 });
  const input = readline.createInterface({ input: process.stdin, crlfDelay: Infinity });
  for await (const line of input) {
    try {
      const command = JSON.parse(line);
      let result;
      if (command.action === 'device') {
        result = await page.evaluate(async subject => {
          if (typeof window.__arteligoReadDevice !== 'function') return null;
          return window.__arteligoReadDevice(subject);
        }, command.subject);
      } else if (command.action === 'request') {
        result = await page.evaluate(async request => {
          const url = new URL(request.url);
          if (url.origin !== location.origin ||
              (!url.pathname.startsWith('/api/') && url.pathname !== '/auth/refresh')) {
            throw new Error('request_scope_invalid');
          }
          const response = await fetch(url, {
            method: request.method,
            headers: request.body ? { 'Content-Type': 'application/json' } : {},
            body: request.body || undefined,
            credentials: 'include', redirect: 'error', signal: AbortSignal.timeout(30000),
          });
          return { status: response.status, body: await response.text(),
            requestId: response.headers.get('x-request-id') };
        }, command);
      } else {
        throw new Error('command_invalid');
      }
      process.stdout.write(JSON.stringify({ result }) + '\n');
    } catch {
      process.stdout.write(JSON.stringify({ error: 'browser_bridge_failed' }) + '\n');
    }
  }
  await page.close();
  // The browser belongs to the interactive acceptance runner.
  process.exit(0);
}

main().catch(() => {
  process.stdout.write(JSON.stringify({ error: 'browser_bridge_unavailable' }) + '\n');
  process.exitCode = 1;
});
