import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { webcrypto } from 'node:crypto';
import vm from 'node:vm';

const source = readFileSync(new URL('../../demo/movie-client/movie_booking/static/cinema.js', import.meta.url), 'utf8');

function page(crypto) {
  const nodes = new Map(), calls = [];
  function node() {
    return { dataset: {}, children: [], classList: { toggle() {}, remove() {} },
      setAttribute(name, value) { this[name] = value; }, getAttribute(name) { return this[name]; },
      append(...values) { this.children.push(...values); },
      replaceChildren(...values) { this.children = values; this.value = values[0]?.value; } };
  }
  const document = { documentElement: { dataset: { theme: 'dark' } },
    querySelector(selector) { if (!nodes.has(selector)) nodes.set(selector, node()); return nodes.get(selector); },
    querySelectorAll() { return []; }, createElement: node, createElementNS: node };
  const show = { id: 'show-001', movie: 'The Last Horizon', theatre: 'Grand Cinema', time: '19:30', price_paise: 25000 };
  const context = vm.createContext({ crypto, document, Intl, localStorage: { setItem() {} },
    Option: function(text, value) { return { text, value }; },
    fetch: async (path, options) => {
      calls.push({ path, options });
      const data = path === '/health' ? { revision: 'working-files' }
        : path === '/api/providers' ? [] : path === '/api/shows' ? [show]
        : path.endsWith('/seats') ? [{ id: 'A1', available: true }] : {};
      return { ok: true, json: async () => data };
    } });
  return { context, nodes, calls };
}

for (const secure of [false, true]) {
  test(`CinemaFlow loads movie, theatre and seat selection on ${secure ? 'HTTPS/localhost' : 'phone HTTP'} origins`, async () => {
    const crypto = { getRandomValues: array => webcrypto.getRandomValues(array) };
    if (secure) crypto.randomUUID = () => webcrypto.randomUUID();
    const { context, nodes, calls } = page(crypto);
    vm.runInContext(source, context);
    await new Promise(resolve => setImmediate(resolve));
    assert.ok(calls.some(call => call.path === '/api/shows'));
    assert.equal(nodes.get('#movie-select').children[0].text, 'The Last Horizon');
    assert.equal(nodes.get('#movie-select').disabled, false);
    assert.equal(nodes.get('#theatre-select').children[0].text, 'Grand Cinema');
    const seat = nodes.get('#seats').children[0].children[1];
    const before = vm.runInContext('key', context);
    seat.onclick();
    const after = vm.runInContext('key', context);
    assert.match(after, /^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i);
    assert.notEqual(before, after);
    assert.equal(nodes.get('#book').disabled, false);
  });
}
