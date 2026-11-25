// Local preview of the built site:  node _build/serve.js [port]
// Serves the repository root the way GitHub Pages does, near enough: static
// files, index.html for a folder, a page without its ".html" (/privacy is
// privacy.html), 404.html for anything missing, and nothing from _build/
// itself. No dependencies.
const http = require('http');
const fs = require('fs');
const path = require('path');

const ROOT = path.resolve(__dirname, '..');
const PORT = Number(process.argv[2] || 8765);
const TYPES = {
  '.html': 'text/html; charset=utf-8', '.css': 'text/css', '.js': 'text/javascript',
  '.svg': 'image/svg+xml', '.png': 'image/png', '.webp': 'image/webp',
  '.woff2': 'font/woff2', '.txt': 'text/plain; charset=utf-8', '.ico': 'image/x-icon',
};

http.createServer((req, res) => {
  let rel = decodeURIComponent(new URL(req.url, 'http://x').pathname);
  if (rel.endsWith('/')) rel += 'index.html';
  let file = path.join(ROOT, rel);
  if (!path.extname(rel) && fs.existsSync(file + '.html')) file += '.html';
  const hidden = rel.split('/').some(part => part.startsWith('_') || part.startsWith('.'));
  let status = 200;
  if (hidden || !file.startsWith(ROOT) || !fs.existsSync(file) || fs.statSync(file).isDirectory()) {
    file = path.join(ROOT, '404.html');
    status = 404;
  }
  res.writeHead(status, {
    'Content-Type': TYPES[path.extname(file)] || 'application/octet-stream',
    'Cache-Control': 'no-store',
  });
  fs.createReadStream(file).pipe(res);
  console.log(status, req.method, req.url);
}).listen(PORT, '127.0.0.1', () => console.log(`http://localhost:${PORT}`));
