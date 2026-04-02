/**
 * Spoon Messenger — Cloudflare Worker
 * Relay для CID списков по ключам кругов
 *
 * KV namespace: SPOON_KV
 *
 * Endpoints:
 *   POST /circle/:key/publish      — добавить CID в круг
 *   GET  /circle/:key/feed         — получить список CID круга
 *   GET  /stats                    — агрегированная статистика
 *   DELETE /circle/:key/cid/:cid   — удалить CID из круга
 */

const CORS_HEADERS = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Methods': 'GET, POST, DELETE, OPTIONS',
  'Access-Control-Allow-Headers': 'Content-Type',
};

const MAX_CIDS_PER_CIRCLE = 100;  // максимум CID в одном круге
const CID_TTL_SECONDS = 60 * 60 * 24 * 90;  // 90 дней

export default {
  async fetch(request, env, ctx) {
    if (request.method === 'OPTIONS') {
      return new Response(null, { headers: CORS_HEADERS });
    }

    const url = new URL(request.url);
    const path = url.pathname;

    try {
      // POST /circle/:key/publish
      if (request.method === 'POST' && path.match(/^\/circle\/[^/]+\/publish$/)) {
        return await handlePublish(request, env, path);
      }

      // GET /circle/:key/feed
      if (request.method === 'GET' && path.match(/^\/circle\/[^/]+\/feed$/)) {
        return await handleFeed(request, env, path);
      }

      // GET /stats
      if (request.method === 'GET' && path === '/stats') {
        return await handleStats(request, env);
      }

      // DELETE /circle/:key/cid/:cid
      if (request.method === 'DELETE' && path.match(/^\/circle\/[^/]+\/cid\/[^/]+$/)) {
        return await handleDelete(request, env, path);
      }

      return jsonResponse({ error: 'Not found' }, 404);

    } catch (error) {
      return jsonResponse({ error: error.message }, 500);
    }
  }
};

async function handlePublish(request, env, path) {
  const key = path.split('/')[2];
  const body = await request.json();

  if (!body.cid) {
    return jsonResponse({ error: 'cid required' }, 400);
  }

  const circleKey = `circle:${key}`;
  const existing = await env.SPOON_KV.get(circleKey, 'json') || [];

  // добавить новый CID с timestamp
  const entry = {
    cid: body.cid,
    published_at: Date.now(),
    expires_at: body.expires_at || null,
  };

  // не дублировать
  const filtered = existing.filter(e => e.cid !== body.cid);
  const updated = [entry, ...filtered].slice(0, MAX_CIDS_PER_CIRCLE);

  await env.SPOON_KV.put(circleKey, JSON.stringify(updated), {
    expirationTtl: CID_TTL_SECONDS
  });

  // обновить счётчик stats
  await incrementStats(env, 'total_messages');

  return jsonResponse({ success: true, cid: body.cid });
}

async function handleFeed(request, env, path) {
  const key = path.split('/')[2];
  const circleKey = `circle:${key}`;

  const entries = await env.SPOON_KV.get(circleKey, 'json') || [];

  // фильтровать истёкшие
  const now = Date.now();
  const active = entries.filter(e => !e.expires_at || e.expires_at > now);

  return jsonResponse({
    circle: key,
    count: active.length,
    entries: active,
  });
}

async function handleStats(request, env) {
  const stats = await env.SPOON_KV.get('stats', 'json') || {};

  return jsonResponse({
    total_messages: stats.total_messages || 0,
    updated_at: Date.now(),
  });
}

async function handleDelete(request, env, path) {
  const parts = path.split('/');
  const key = parts[2];
  const cid = parts[4];

  const circleKey = `circle:${key}`;
  const existing = await env.SPOON_KV.get(circleKey, 'json') || [];
  const updated = existing.filter(e => e.cid !== cid);

  await env.SPOON_KV.put(circleKey, JSON.stringify(updated), {
    expirationTtl: CID_TTL_SECONDS
  });

  return jsonResponse({ success: true });
}

async function incrementStats(env, field) {
  const stats = await env.SPOON_KV.get('stats', 'json') || {};
  stats[field] = (stats[field] || 0) + 1;
  await env.SPOON_KV.put('stats', JSON.stringify(stats));
}

function jsonResponse(data, status = 200) {
  return new Response(JSON.stringify(data), {
    status,
    headers: {
      'Content-Type': 'application/json',
      ...CORS_HEADERS,
    },
  });
}
