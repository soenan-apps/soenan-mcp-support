'use strict';

const assert = require('node:assert/strict');
const test = require('node:test');
const vm = require('node:vm');
const { parseOptions, runTrial } = require('./browser_read_benchmark.cjs');

const scope = 'prj_' + 'a'.repeat(32);
const projects = JSON.stringify({ projects: [{ project_id: scope, title: '秘密' }] });
const options = { profile: 'projects', clients: 1, durationMs: 10000,
  requestTimeoutMs: 30000, operationLimit: 1 };
function clocked(fetch) {
  let time = 0;
  return { now: () => time, advance: milliseconds => { time += milliseconds; },
    timeout: milliseconds => ({ deadlineMs: milliseconds }), fetch };
}
function response(status, text) {
  return { status, text: async () => text };
}

test('counts failed attempts, body bytes and latency without returning response content', async () => {
  const bodies = [projects, '{"error":"private failure text"}', '{"private":"body"}'];
  let count = 0;
  const runtime = clocked(async () => {
    const index = count++;
    runtime.advance((index + 1) * 2);
    if (index === 3) throw new Error('network failure with sensitive text');
    return response([200, 503, 200][index], bodies[index]);
  });
  const result = await runTrial({ ...options, operationLimit: 4 }, runtime);
  assert.deepEqual(result.api.status_counts, { 200: 2, 503: 1 });
  assert.equal(result.api.attempts, 4);
  assert.equal(result.api.successful_attempts, 1);
  assert.equal(result.api.failed_attempts, 3);
  assert.equal(result.api.invalid_responses, 1);
  assert.equal(result.api.network_errors, 1);
  assert.equal(result.api.response_bytes, bodies.reduce((total, body) => total + Buffer.byteLength(body), 0));
  assert.equal(result.api.p50_ms, 4);
  assert.equal(result.api.p95_ms, 8);
  assert.equal(result.api.throughput_per_second, 200);
  assert.equal(result.operations.throughput_per_second, 50);
  assert.equal(result.operations.failed, 3);
  assert.equal(JSON.stringify(result).includes('秘密'), false);
  assert.equal(JSON.stringify(result).includes('private'), false);
  assert.equal(JSON.stringify(result).includes(scope), false);
});

test('concurrent 401 responses share one refresh and remain visible in attempt counts', async () => {
  let apiCalls = 0;
  let refreshCalls = 0;
  const runtime = clocked(async (url, request) => {
    runtime.advance(1);
    assert.equal(request.credentials, 'include');
    assert.equal(request.redirect, 'error');
    assert.equal(request.signal.deadlineMs, 30000);
    if (url === '/auth/refresh') {
      refreshCalls += 1;
      assert.equal(request.method, 'POST');
      return response(200, '{}');
    }
    assert.equal(url, '/api/e2ee/projects');
    assert.equal(request.method, 'GET');
    return response(apiCalls++ < 4 ? 401 : 200, projects);
  });
  const result = await runTrial({ ...options, clients: 4, operationLimit: 4 }, runtime);
  assert.equal(refreshCalls, 1);
  assert.equal(result.refresh.attempts, 1);
  assert.deepEqual(result.api.status_counts, { 200: 4, 401: 4 });
  assert.equal(result.api.failed_attempts, 4);
  assert.equal(result.api.successful_attempts, 4);
  assert.equal(result.operations.succeeded, 4);
  assert.equal(result.operations.failed, 0);
});

test('a failed shared refresh is reported without replaying protected requests', async () => {
  const runtime = clocked(async url => {
    runtime.advance(1);
    return response(url === '/auth/refresh' ? 503 : 401, '{}');
  });
  const result = await runTrial({ ...options, clients: 2, operationLimit: 2 }, runtime);
  assert.deepEqual(result.api.status_counts, { 401: 2 });
  assert.deepEqual(result.refresh.status_counts, { 503: 1 });
  assert.equal(result.refresh.failed_attempts, 1);
  assert.equal(result.operations.failed, 2);
  assert.equal(result.api.attempts, 2);
});

test('a late 401 reuses the refresh completed by another client', async () => {
  let calls = 0;
  let releaseLate;
  const late = new Promise(resolve => { releaseLate = resolve; });
  const runtime = clocked(async url => {
    runtime.advance(1);
    if (url === '/auth/refresh') return response(200, '{}');
    const index = calls++;
    if (index === 0) return response(401, '{}');
    if (index === 1) { await late; return response(401, '{}'); }
    releaseLate();
    return response(200, projects);
  });
  const result = await runTrial({ ...options, clients: 2, operationLimit: 2 }, runtime);
  assert.equal(result.refresh.attempts, 1);
  assert.deepEqual(result.api.status_counts, { 200: 2, 401: 2 });
  assert.equal(result.operations.succeeded, 2);
});

test('a body timeout preserves the observed HTTP status and records the failed attempt', async () => {
  const runtime = clocked(async () => ({ status: 200, text: async () => {
    runtime.advance(30000);
    throw Object.assign(new Error('sensitive timeout details'), { name: 'TimeoutError' });
  } }));
  const result = await runTrial(options, runtime);
  assert.deepEqual(result.api.status_counts, { 200: 1 });
  assert.equal(result.api.timeouts, 1);
  assert.equal(result.api.failed_attempts, 1);
  assert.equal(result.api.response_bytes, 0);
  assert.equal(result.api.p95_ms, 30000);
  assert.equal(result.operations.failed, 1);
});

test('stops issuing at the deadline and includes drain time in throughput', async () => {
  const starts = [];
  const runtime = clocked(async () => {
    starts.push(runtime.now());
    runtime.advance(20);
    return response(200, projects);
  });
  const result = await runTrial({ ...options, durationMs: 30, operationLimit: undefined }, runtime);
  assert.deepEqual(starts, [0, 20]);
  assert.equal(result.elapsed_ms, 40);
  assert.equal(result.drain_ms, 10);
  assert.equal(result.api.throughput_per_second, 50);
});

test('does not start a refresh when the last unauthorized request drains past the deadline', async () => {
  const urls = [];
  const runtime = clocked(async url => {
    urls.push(url);
    runtime.advance(20);
    return response(401, '{}');
  });
  const result = await runTrial({ ...options, durationMs: 10 }, runtime);
  assert.deepEqual(urls, ['/api/e2ee/projects']);
  assert.equal(result.refresh.attempts, 0);
  assert.equal(result.operations.failed, 1);
});

test('overview sends one bounded read and reports per-scope errors inside HTTP 200', async () => {
  const runtime = clocked(async (url, request) => {
    runtime.advance(5);
    assert.equal(url, '/api/e2ee/records/read');
    assert.equal(request.method, 'POST');
    assert.deepEqual(JSON.parse(request.body), {
      scopes: [{ scope_id: scope, record_ids: [scope] }], include_keys: true,
    });
    return response(200, JSON.stringify({ commands: {}, scopes: [{ scope_id: scope, error: 'access_denied' }] }));
  });
  const result = await runTrial({ ...options, profile: 'overview', scopeIds: [scope] }, runtime);
  assert.equal(result.api.scope_errors, 1);
  assert.equal(result.api.invalid_responses, 1);
  assert.equal(result.operations.failed, 1);
});

test('current targets the fixture and rejects responses containing another record kind', async () => {
  const runtime = clocked(async (url, request) => {
    runtime.advance(5);
    assert.equal(url, `/api/e2ee/scopes/${scope}/current?kind=file&limit=100`);
    assert.equal(request.method, 'GET');
    return response(200, JSON.stringify({ commands: {}, records: [{ kind: 'project', record_id: scope }], has_more: false }));
  });
  const result = await runTrial({ ...options, profile: 'current', hotScope: scope }, runtime);
  assert.equal(result.api.invalid_responses, 1);
  assert.equal(result.operations.failed, 1);
});

test('discovery keeps the first 32 scopes in server order', async () => {
  const ids = Array.from({ length: 40 }, (_, index) => 'prj_' + index.toString(16).padStart(32, '0'));
  const runtime = clocked(async () => {
    runtime.advance(5);
    return response(200, JSON.stringify({ projects: ids.map(project_id => ({ project_id })) }));
  });
  const result = await runTrial({ ...options, discover: true }, runtime);
  assert.deepEqual(result.discoveredScopes, ids.slice(0, 32));
  assert.equal(result.api.returned_records, 40);
});

test('current accepts exactly 100 distinct file records and rejects short or duplicate pages', async () => {
  const complete = Array.from({ length: 100 }, (_, index) => ({ kind: 'file', record_id: `file-${index}` }));
  for (const [records, success] of [[complete, 1], [[], 0], [complete.slice(1), 0], [[...complete.slice(1), complete[1]], 0]]) {
    const runtime = clocked(async () => {
      runtime.advance(5);
      return response(200, JSON.stringify({ commands: {}, records, has_more: true }));
    });
    const result = await runTrial({ ...options, profile: 'current', hotScope: scope }, runtime);
    assert.equal(result.operations.succeeded, success);
    assert.equal(result.api.invalid_responses, 1 - success);
  }
});

test('validates local targets and bounded options before browser connection', () => {
  const base = ['--cdp-url', 'http://127.0.0.1:9222', '--origin', 'https://arteligo.local.soenan.dev', '--manifest', '/tmp/fixture.json', '--output', '/tmp/metrics.json'];
  const parsed = parseOptions(base);
  assert.deepEqual(parsed.clients, [1, 8, 16]);
  assert.deepEqual(parsed.profiles, ['projects', 'overview', 'current']);
  assert.equal(parsed.durationMs, 30000);
  assert.equal(parsed.repeats, 3);
  assert.equal(parsed.requestTimeoutMs, 30000);
  assert.throws(() => parseOptions([...base, '--clients', '0']));
  assert.throws(() => parseOptions([...base, '--duration-seconds', 'NaN']));
  assert.throws(() => parseOptions([...base, '--profiles', 'delete']));
  assert.throws(() => parseOptions([...base, '--cdp-url', 'http://example.com:9222']));
  assert.throws(() => parseOptions([...base, '--origin', 'https://arteligo.local.soenan.dev.example.com']));
  assert.throws(() => parseOptions([...base, '--origin', 'https://user:secret@arteligo.local.soenan.dev']));
});

test('the browser function runs with browser globals and no Node closure', async () => {
  let elapsed = 0;
  const browserFunction = vm.runInNewContext(`(${runTrial.toString()})`, {
    fetch: async () => { elapsed += 10; return response(200, projects); },
    performance: { now: () => elapsed },
    AbortSignal: { timeout: milliseconds => ({ milliseconds }) }, TextEncoder,
  });
  const result = await browserFunction(options);
  assert.equal(result.operations.succeeded, 1);
  assert.equal(result.api.p50_ms, 10);
  assert.equal(result.api.response_bytes, Buffer.byteLength(projects));
});
