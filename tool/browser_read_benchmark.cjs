'use strict';

const fs = require('node:fs');
const path = require('node:path');
const { parseArgs } = require('node:util');

// This function also runs inside the dedicated browser page. Only metrics and
// discovery's public scope IDs leave it; response bodies and cookies stay there.
async function runTrial(options, runtime = {
  fetch: (...args) => fetch(...args),
  now: () => performance.now(),
  timeout: milliseconds => AbortSignal.timeout(milliseconds),
}) {
  const makeStats = () => ({
    attempts: 0, successful_attempts: 0, failed_attempts: 0,
    status_counts: {}, network_errors: 0, timeouts: 0, invalid_responses: 0,
    scope_errors: 0, response_bytes: 0, returned_records: 0, latency: [],
  });
  const api = makeStats();
  const refresh = makeStats();
  const operations = { started: 0, succeeded: 0, failed: 0, latency: [] };
  const started = runtime.now();
  const deadline = started + options.durationMs;
  let refreshPromise = null;
  let refreshGeneration = 0;
  let discoveredScopes;
  const identifier = value => typeof value === 'string' && /^prj_[A-Za-z0-9_-]{1,124}$/.test(value);
  const object = value => value !== null && typeof value === 'object' && !Array.isArray(value);

  function validate(value) {
    if (!object(value)) return false;
    if (options.profile === 'projects') {
      if (!Array.isArray(value.projects) || !value.projects.every(item => object(item) && identifier(item.project_id))) return false;
      const ids = value.projects.map(item => item.project_id);
      if (new Set(ids).size !== ids.length) return false;
      api.returned_records += ids.length;
      if (options.discover) discoveredScopes = ids.slice(0, 32);
      return true;
    }
    if (!object(value.commands)) return false;
    if (options.profile === 'current') {
      if (!Array.isArray(value.records) || value.records.length !== 100 || typeof value.has_more !== 'boolean') return false;
      if (!value.records.every(item => object(item) && item.kind === 'file' && typeof item.record_id === 'string')) return false;
      if (new Set(value.records.map(item => item.record_id)).size !== 100) return false;
      api.returned_records += value.records.length;
      return true;
    }
    if (!Array.isArray(value.scopes) || value.scopes.length !== options.scopeIds.length) return false;
    const remaining = new Set(options.scopeIds);
    let valid = true;
    for (const scope of value.scopes) {
      if (!object(scope) || !remaining.delete(scope.scope_id)) return false;
      if (scope.error !== undefined) {
        api.scope_errors += 1;
        valid = false;
        continue;
      }
      if (!Array.isArray(scope.records) || !Array.isArray(scope.missing_record_ids) || !Array.isArray(scope.remaining_record_ids)) return false;
      if (scope.records.length !== 1 || scope.records[0].record_id !== scope.scope_id || scope.records[0].kind !== 'project' || scope.missing_record_ids.length || scope.remaining_record_ids.length) valid = false;
      api.returned_records += scope.records.length;
    }
    return valid && remaining.size === 0;
  }

  async function request(url, method, body, stats, checkPayload) {
    stats.attempts += 1;
    const requestStarted = runtime.now();
    let status = null;
    try {
      const response = await runtime.fetch(url, {
        method, credentials: 'include', redirect: 'error', cache: 'no-store',
        headers: body === undefined ? {} : { 'Content-Type': 'application/json' },
        body: body === undefined ? undefined : JSON.stringify(body),
        signal: runtime.timeout(options.requestTimeoutMs),
      });
      status = response.status;
      stats.status_counts[status] = (stats.status_counts[status] || 0) + 1;
      const text = await response.text();
      stats.response_bytes += new TextEncoder().encode(text).byteLength;
      let ok = status >= 200 && status < 300;
      if (ok && checkPayload) {
        try { ok = validate(JSON.parse(text)); } catch { ok = false; }
        if (!ok) stats.invalid_responses += 1;
      }
      if (ok) stats.successful_attempts += 1;
      else stats.failed_attempts += 1;
      return { ok, status };
    } catch (error) {
      stats.failed_attempts += 1;
      if (error?.name === 'TimeoutError' || error?.name === 'AbortError') stats.timeouts += 1;
      else stats.network_errors += 1;
      return { ok: false, status };
    } finally {
      stats.latency.push(Math.max(0, runtime.now() - requestStarted));
    }
  }

  async function renew(generation) {
    if (refreshGeneration !== generation) return true;
    if (refreshPromise === null) {
      if (runtime.now() >= deadline) return false;
      refreshPromise = request('/auth/refresh', 'POST', undefined, refresh, false)
        .then(result => {
          if (result.ok) refreshGeneration += 1;
          return result.ok;
        }).finally(() => { refreshPromise = null; });
    }
    return refreshPromise;
  }

  const endpoint = options.profile === 'projects' ? '/api/e2ee/projects'
    : options.profile === 'overview' ? '/api/e2ee/records/read'
      : `/api/e2ee/scopes/${options.hotScope}/current?kind=file&limit=100`;
  const body = options.profile === 'overview' ? {
    scopes: options.scopeIds.map(scope => ({ scope_id: scope, record_ids: [scope] })),
    include_keys: true,
  } : undefined;
  async function worker() {
    while (runtime.now() < deadline && operations.started < (options.operationLimit ?? Infinity)) {
      operations.started += 1;
      const operationStarted = runtime.now();
      const generation = refreshGeneration;
      let result = await request(endpoint, body === undefined ? 'GET' : 'POST', body, api, true);
      if (result.status === 401 && runtime.now() < deadline && await renew(generation) && runtime.now() < deadline) {
        result = await request(endpoint, body === undefined ? 'GET' : 'POST', body, api, true);
      }
      if (result.ok) operations.succeeded += 1;
      else operations.failed += 1;
      operations.latency.push(Math.max(0, runtime.now() - operationStarted));
    }
  }
  await Promise.all(Array.from({ length: options.clients }, () => worker()));
  const elapsed = Math.max(0, runtime.now() - started);
  const finish = stats => {
    const { latency, ...counts } = stats;
    latency.sort((left, right) => left - right);
    const quantile = fraction => latency.length ? latency[Math.ceil(latency.length * fraction) - 1] : null;
    return { ...counts, p50_ms: quantile(0.5), p95_ms: quantile(0.95),
      throughput_per_second: elapsed ? (stats.attempts ?? stats.succeeded) * 1000 / elapsed : 0 };
  };
  return {
    profile: options.profile, clients: options.clients,
    planned_duration_ms: options.durationMs, elapsed_ms: elapsed,
    drain_ms: Math.max(0, elapsed - options.durationMs),
    operations: finish(operations), api: finish(api), refresh: finish(refresh),
    ...(options.discover ? { discoveredScopes } : {}),
  };
}

function parseOptions(args) {
  const { values } = parseArgs({ args, options: {
    'cdp-url': { type: 'string' }, origin: { type: 'string' },
    manifest: { type: 'string' }, output: { type: 'string' },
    clients: { type: 'string', default: '1,8,16' },
    profiles: { type: 'string', default: 'projects,overview,current' },
    'duration-seconds': { type: 'string', default: '30' },
    repeats: { type: 'string', default: '3' },
    'request-timeout-seconds': { type: 'string', default: '30' },
  }, strict: true, allowPositionals: false });
  const origin = new URL(values.origin);
  const cdp = new URL(values['cdp-url']);
  if (origin.protocol !== 'https:' || !origin.hostname.endsWith('.local.soenan.dev') || origin.username || origin.password || origin.pathname !== '/' || origin.search || origin.hash
      || !['http:', 'https:', 'ws:', 'wss:'].includes(cdp.protocol) || !['localhost', '127.0.0.1', '[::1]'].includes(cdp.hostname) || cdp.username || cdp.password || cdp.search || cdp.hash) throw new Error('local_fixture_target_required');
  const clients = values.clients.split(',').map(Number);
  const profiles = values.profiles.split(',');
  const durationMs = Number(values['duration-seconds']) * 1000;
  const requestTimeoutMs = Number(values['request-timeout-seconds']) * 1000;
  const repeats = Number(values.repeats);
  if (!clients.length || clients.length > 8 || new Set(clients).size !== clients.length || clients.some(count => !Number.isInteger(count) || count < 1 || count > 64)
      || !profiles.length || new Set(profiles).size !== profiles.length || profiles.some(profile => !['projects', 'overview', 'current'].includes(profile))
      || !Number.isInteger(repeats) || repeats < 1 || repeats > 10
      || !Number.isInteger(durationMs) || durationMs < 100 || durationMs > 300000
      || !Number.isInteger(requestTimeoutMs) || requestTimeoutMs < 100 || requestTimeoutMs > 120000
      || !values.manifest || !values.output) throw new Error('invalid_benchmark_options');
  return { origin: origin.origin, cdpURL: cdp.href, manifest: path.resolve(values.manifest),
    output: path.resolve(values.output), clients, profiles, durationMs, requestTimeoutMs, repeats };
}

async function boundedEvaluate(page, options) {
  let timer;
  try {
    return await Promise.race([
      page.evaluate(runTrial, options),
      new Promise((_, reject) => { timer = setTimeout(() => reject(new Error('benchmark_trial_timeout')), options.durationMs + options.requestTimeoutMs + 5000); }),
    ]);
  } finally { clearTimeout(timer); }
}

function saveReport(filename, report) {
  fs.mkdirSync(path.dirname(filename), { recursive: true });
  const temporary = `${filename}.${process.pid}.tmp`;
  fs.writeFileSync(temporary, JSON.stringify(report, null, 2) + '\n', { mode: 0o600 });
  fs.renameSync(temporary, filename);
}

async function main(args) {
  const options = parseOptions(args);
  if (fs.existsSync(options.output) || options.output === options.manifest) throw new Error('benchmark_output_exists');
  const manifest = JSON.parse(fs.readFileSync(options.manifest, 'utf8'));
  if (manifest.version !== 1 || manifest.state !== 'ready' || manifest.origin !== options.origin || !/^prj_[a-f0-9]{32}$/.test(manifest.scope_id)) throw new Error('fixture_manifest_invalid');
  const testing = require.resolve('@playwright/test');
  const { chromium } = require(require.resolve('playwright', { paths: [path.dirname(testing)] }));
  const browser = await chromium.connectOverCDP(options.cdpURL, { timeout: 30000 });
  let page;
  const report = { version: 1, state: 'running', configuration: {
    clients: options.clients, profiles: options.profiles, duration_seconds: options.durationMs / 1000,
    repeats: options.repeats, request_timeout_seconds: options.requestTimeoutMs / 1000,
    response_bytes_kind: 'decoded_utf8_body', throughput_duration_includes_drain: true,
  }, trials: [] };
  try {
    const source = browser.contexts().flatMap(context => context.pages())
      .find(candidate => { try { return new URL(candidate.url()).origin === options.origin; } catch { return false; } });
    if (!source) throw new Error('browser_page_missing');
    page = await source.context().newPage();
    await page.route('**/flutter_bootstrap.js', route => route.fulfill({ status: 200, contentType: 'application/javascript', body: '' }));
    await page.goto(options.origin + '/', { waitUntil: 'domcontentloaded', timeout: 30000 });
    if (new URL(page.url()).origin !== options.origin) throw new Error('browser_origin_changed');
    const discovery = await boundedEvaluate(page, {
      profile: 'projects', clients: 1, durationMs: options.requestTimeoutMs * 3,
      requestTimeoutMs: options.requestTimeoutMs, operationLimit: 1, discover: true,
    });
    const scopeIds = discovery.discoveredScopes;
    delete discovery.discoveredScopes;
    report.discovery = discovery;
    if (discovery.operations.succeeded !== 1 || !Array.isArray(scopeIds) || !scopeIds.length) throw new Error('benchmark_discovery_failed');
    report.overview_scope_count = scopeIds.length;
    report.overview_includes_fixture = scopeIds.includes(manifest.scope_id);
    saveReport(options.output, report);
    for (const profile of options.profiles) {
      for (const clients of options.clients) {
        for (let repeat = 1; repeat <= options.repeats; repeat += 1) {
          const result = await boundedEvaluate(page, { profile, clients,
            durationMs: options.durationMs, requestTimeoutMs: options.requestTimeoutMs,
            hotScope: manifest.scope_id, scopeIds });
          const trial = { repeat, ...result };
          report.trials.push(trial);
          saveReport(options.output, report);
          process.stdout.write(JSON.stringify(trial) + '\n');
        }
      }
    }
    report.state = 'complete';
    saveReport(options.output, report);
  } catch {
    report.state = 'failed';
    saveReport(options.output, report);
    throw new Error('benchmark_failed');
  } finally {
    if (page) await page.close({ runBeforeUnload: false }).catch(() => {});
    // Disconnecting by process exit keeps the user's browser and original tabs open.
  }
}

module.exports = { runTrial, parseOptions, main };
if (require.main === module) {
  main(process.argv.slice(2)).then(() => process.exit(0), () => {
    process.stderr.write('{"error":"browser_read_benchmark_failed"}\n');
    process.exit(1);
  });
}
