import http from 'node:http';
import fs from 'node:fs/promises';
import path from 'node:path';
const root = process.cwd();
http.createServer(async (req, res) => {
  const route = decodeURIComponent(new URL(req.url, 'http://localhost').pathname).replace(/^\/dundas-east-animal-hospital(?=\/|$)/, '');
  const file = path.resolve(root, '.' + (route.endsWith('/') ? route + 'index.html' : route));
  if (!file.startsWith(root + path.sep)) { res.writeHead(403); res.end(); return; }
  try {
    const body = await fs.readFile(file);
    const types = {'.html':'text/html', '.css':'text/css', '.js':'text/javascript', '.jpg':'image/jpeg', '.png':'image/png', '.json':'application/json', '.xml':'application/xml'};
    res.setHeader('Content-Type', types[path.extname(file)] || 'text/plain');
    res.end(body);
  } catch { res.writeHead(404); res.end('Not found'); }
}).listen(4174, '127.0.0.1', () => console.log('Local: http://127.0.0.1:4174/dundas-east-animal-hospital/'));
