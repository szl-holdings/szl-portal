// SZL estate inventory — edge API (Cloudflare Worker).
// Mirrors the FastAPI backend's read-only endpoints so the portal can run
// fully serverless on Cloudflare. Deploy (owner-gated, needs CF account):
//   npm create cloudflare@latest -- szl-portal-api
//   npx wrangler deploy
// Environment: no secrets required — both upstreams are public APIs.

export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);
    const CORS = {
      "Access-Control-Allow-Origin": "*",
      "Access-Control-Allow-Methods": "GET",
    };
    if (request.method !== "GET") {
      return new Response("method not allowed", { status: 405, headers: CORS });
    }

    // cache-first: estate inventory is rate-limited upstream; 15 min is honest
    const cacheTtl = 900;
    const cache = caches.default;
    const cacheKey = new Request(url.toString(), { method: "GET" });
    let cached = await cache.match(cacheKey);

    if (url.pathname === "/healthz") {
      return Response.json({ status: "ok" }, { headers: CORS });
    }

    if (!cached) {
      if (url.pathname === "/v1/summary" || url.pathname === "/v1/snapshot") {
        const [gh, hf] = await Promise.all([
          githubReposPage(),
          fetch("https://huggingface.co/api/models?author=SZLHOLDINGS&limit=1000").then(r => r.json()),
        ]);
        const payload = { summary: summarize(gh), generated_utc: new Date().toISOString() };
        const res = Response.json(payload, { headers: { ...CORS, "Cache-Control": `public, max-age=${cacheTtl}` } });
        ctx.waitUntil(cache.put(cacheKey, res.clone()));
        return res;
      }
      return Response.json({ error: "not found" }, { status: 404, headers: CORS });
    }
    return cached;
  },
};

async function githubReposPage() {
  const r = await fetch(
    "https://api.github.com/search/repositories?q=org:szl-holdings+fork:true&per_page=100&page=1",
    { headers: { "User-Agent": "szl-portal-worker", Accept: "application/json" } }
  );
  const data = await r.json();
  return (data.items || []).map((x) => ({
    name: x.name, language: x.language, archived: !!x.archived,
    html_url: x.html_url, description: x.description, updated_at: x.updated_at,
  }));
}

function summarize(repos) {
  const active = repos.filter((r) => !r.archived);
  const langs = {};
  for (const r of active) { const l = r.language || "Other"; langs[l] = (langs[l] || 0) + 1; }
  return { github: { repos_total: repos.length, repos_active: active.length, languages: langs } };
}
