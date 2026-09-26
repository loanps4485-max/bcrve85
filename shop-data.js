import { getStore } from "@netlify/blobs";

const STORE_NAME = "bcrve85-shop";
const KEY = "catalog";

function headers() {
  return {
    "content-type": "application/json; charset=utf-8",
    "cache-control": "no-store",
    "access-control-allow-origin": "*",
    "access-control-allow-headers": "Content-Type, X-Admin-Key",
    "access-control-allow-methods": "GET, POST, OPTIONS"
  };
}

export default async (request) => {
  if (request.method === "OPTIONS") return new Response("", { status: 204, headers: headers() });

  const store = getStore(STORE_NAME);
  const existing = await store.get(KEY, { type: "json" });
  const fallback = existing || { categories: ["Sélection", "Nouveautés", "Packs"], products: [] };

  if (request.method === "GET") {
    return new Response(JSON.stringify(fallback), { status: 200, headers: headers() });
  }

  if (request.method !== "POST") {
    return new Response(JSON.stringify({ error: "Method not allowed" }), { status: 405, headers: headers() });
  }

  const expected = process.env.BCRVE85_ADMIN_KEY;
  const provided = request.headers.get("x-admin-key");
  if (!expected || provided !== expected) {
    return new Response(JSON.stringify({ error: "Unauthorized" }), { status: 401, headers: headers() });
  }

  let body;
  try { body = await request.json(); } catch {
    return new Response(JSON.stringify({ error: "Invalid JSON" }), { status: 400, headers: headers() });
  }

  if (!Array.isArray(body.categories) || !Array.isArray(body.products)) {
    return new Response(JSON.stringify({ error: "categories/products required" }), { status: 400, headers: headers() });
  }

  const data = { categories: body.categories.slice(0, 100), products: body.products.slice(0, 1000), updatedAt: new Date().toISOString() };
  await store.setJSON(KEY, data);
  return new Response(JSON.stringify({ ok: true, data }), { status: 200, headers: headers() });
};
