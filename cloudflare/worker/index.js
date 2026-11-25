// SZL estate inventory — edge API (Cloudflare Worker).
// Contract: portal-summary/v1 — GET /v1/summary returns
//   { github: { repos_total, repos_active, languages },
//     huggingface: { models_public, datasets_public },  // counts; null if upstream failed
//     generated_utc }
// consumed directly by frontend/index.html. Mirrors the FastAPI backend's
// read-only endpoints so the portal runs fully serverless on Cloudflare.
// Deploy (cd cloudflare/worker): npx wrangler deploy — no secrets required.
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
        const [gh, huggingface] = await Promise.all([
          githubReposPage(),
          huggingfaceCounts(),
        ]);
        const payload = { github: summarize(gh), huggingface, generated_utc: new Date().toISOString() };
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
  if (!r.ok) throw new Error("github " + r.status); // fail-closed: 5xx -> static fallback on the frontend
  const data = await r.json();
  return (data.items || []).map((x) => ({
    name: x.name, language: x.language, archived: !!x.archived,
    html_url: x.html_url, description: x.description, updated_at: x.updated_at,
  }));
}

async function huggingfaceCounts() {
  // fail-closed honesty: counts are numbers, or null when an upstream call
  // failed — never a stale guess. The frontend renders null as "—".
  try {
    const get = async (kind) => {
      const r = await fetch("https://huggingface.co/api/" + kind + "?author=SZLHOLDINGS&limit=1000");
      if (!r.ok) throw new Error(kind + " " + r.status);
      const arr = await r.json();
      if (!Array.isArray(arr)) throw new Error(kind + " shape");
      return arr.length;
    };
    const [models, datasets] = await Promise.all([get("models"), get("datasets")]);
    return { models_public: models, datasets_public: datasets };
  } catch (e) {
    return { models_public: null, datasets_public: null };
  }
}

function summarize(repos) {
  const active = repos.filter((r) => !r.archived);
  const langs = {};
  for (const r of active) { const l = r.language || "Other"; langs[l] = (langs[l] || 0) + 1; }
  return { repos_total: repos.length, repos_active: active.length, languages: langs };
}
