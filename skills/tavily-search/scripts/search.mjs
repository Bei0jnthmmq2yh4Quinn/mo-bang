#!/usr/bin/env node

function usage() {
  console.error(`Usage: search.mjs "query" [-n 5] [--deep] [--topic general|news] [--days 7]`);
  process.exit(2);
}

const args = process.argv.slice(2);
if (args.length === 0 || args[0] === "-h" || args[0] === "--help") usage();

const query = args[0];
let n = 5;
let searchDepth = "basic";
let topic = "general";
let days = null;

for (let i = 1; i < args.length; i++) {
  const a = args[i];
  if (a === "-n") {
    n = Number.parseInt(args[i + 1] ?? "5", 10);
    i++;
    continue;
  }
  if (a === "--deep") {
    searchDepth = "advanced";
    continue;
  }
  if (a === "--topic") {
    topic = args[i + 1] ?? "general";
    i++;
    continue;
  }
  if (a === "--days") {
    days = Number.parseInt(args[i + 1] ?? "7", 10);
    i++;
    continue;
  }
  console.error(`Unknown arg: ${a}`);
  usage();
}

function parseApiKeys() {
  // Supports:
  // - TAVILY_API_KEY="key"
  // - TAVILY_API_KEY="key1&key2&key3" (round-robin)
  // - TAVILY_API_KEY="key1 key2 key3" (whitespace-separated)
  const raw = String(process.env.TAVILY_API_KEY ?? "").trim();
  if (!raw) return [];
  const parts = raw
    .split(/\s*&\s*|\s+/g)
    .map((s) => s.trim())
    .filter(Boolean);
  // de-dup while preserving order
  const seen = new Set();
  const keys = [];
  for (const k of parts) {
    if (seen.has(k)) continue;
    seen.add(k);
    keys.push(k);
  }
  return keys;
}

const apiKeys = parseApiKeys();
if (apiKeys.length === 0) {
  console.error("Missing TAVILY_API_KEY");
  process.exit(1);
}

// Simple deterministic round-robin by minute+query hash.
function pickKey(keys, queryStr) {
  const minute = Math.floor(Date.now() / 60000);
  let h = 2166136261;
  const s = `${minute}:${queryStr}`;
  for (let i = 0; i < s.length; i++) {
    h ^= s.charCodeAt(i);
    h = Math.imul(h, 16777619);
  }
  const idx = Math.abs(h) % keys.length;
  return keys[idx];
}

const apiKey = pickKey(apiKeys, query);

const body = {
  api_key: apiKey,
  query: query,
  search_depth: searchDepth,
  topic: topic,
  max_results: Math.max(1, Math.min(n, 20)),
  include_answer: true,
  include_raw_content: false,
};

if (topic === "news" && days) {
  body.days = days;
}

const resp = await fetch((process.env.TAVILY_BASE_URL || "https://api.tavily.com") + "/search", {
  method: "POST",
  headers: {
    "Content-Type": "application/json",
  },
  body: JSON.stringify(body),
});

if (!resp.ok) {
  const text = await resp.text().catch(() => "");
  throw new Error(`Tavily Search failed (${resp.status}): ${text}`);
}

const data = await resp.json();

// Print AI-generated answer if available
if (data.answer) {
  console.log("## Answer\n");
  console.log(data.answer);
  console.log("\n---\n");
}

// Print results
const results = (data.results ?? []).slice(0, n);
console.log("## Sources\n");

for (const r of results) {
  const title = String(r?.title ?? "").trim();
  const url = String(r?.url ?? "").trim();
  const content = String(r?.content ?? "").trim();
  const score = r?.score ? ` (relevance: ${(r.score * 100).toFixed(0)}%)` : "";

  if (!title || !url) continue;
  console.log(`- **${title}**${score}`);
  console.log(`  ${url}`);
  if (content) {
    console.log(`  ${content.slice(0, 300)}${content.length > 300 ? "..." : ""}`);
  }
  console.log();
}
