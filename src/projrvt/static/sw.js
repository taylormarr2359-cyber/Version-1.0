// ATLAS Service Worker — caches the shell for offline use
const CACHE = "atlas-v1";
const SHELL = ["/", "/static/manifest.json"];

self.addEventListener("install", (e) => {
  e.waitUntil(
    caches.open(CACHE).then((c) => c.addAll(SHELL)).then(() => self.skipWaiting())
  );
});

self.addEventListener("activate", (e) => {
  e.waitUntil(
    caches.keys().then((keys) =>
      Promise.all(keys.filter((k) => k !== CACHE).map((k) => caches.delete(k)))
    ).then(() => self.clients.claim())
  );
});

self.addEventListener("fetch", (e) => {
  const url = new URL(e.request.url);

  // API calls: network-first (must be fresh)
  if (url.pathname.startsWith("/chat") ||
      url.pathname.startsWith("/calendar") ||
      url.pathname.startsWith("/email") ||
      url.pathname.startsWith("/notes") ||
      url.pathname.startsWith("/smart-home") ||
      url.pathname.startsWith("/briefing") ||
      url.pathname.startsWith("/insights") ||
      url.pathname.startsWith("/diagnostics") ||
      url.pathname.startsWith("/health")) {
    e.respondWith(
      fetch(e.request).catch(() =>
        new Response(JSON.stringify({ error: "Offline — ATLAS server unreachable." }), {
          headers: { "Content-Type": "application/json" },
        })
      )
    );
    return;
  }

  // Shell: cache-first
  e.respondWith(
    caches.match(e.request).then((cached) => cached || fetch(e.request))
  );
});
