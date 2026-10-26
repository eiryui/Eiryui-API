from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from src.endpoints import router
from src.config import HEADERS
import httpx
from pathlib import Path

app = FastAPI(title="Eiryui API", version="3.2")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = Path(__file__).resolve().parent.parent
LOGO_DIR = BASE_DIR / "logo_favicons"
if LOGO_DIR.is_dir():
    app.mount("/logo_favicons", StaticFiles(directory=str(LOGO_DIR)), name="logo_favicons")

app.include_router(router, prefix="/anime")

from fastapi import Query
from fastapi.responses import Response


def _norm_url(url: str) -> str | None:
    url = (url or "").strip()
    if url.startswith("//"):
        return "https:" + url
    if url.startswith("http://") or url.startswith("https://"):
        return url
    return None


@app.get("/proxy_m3u8")
async def proxy_m3u8(url: str, referer: str, proxy_base: str = "/proxy_m3u8"):
    url = _norm_url(url)
    if not url:
        return Response(content='{"detail":"bad proxy url"}', status_code=400,
                        media_type="application/json")
    async with httpx.AsyncClient(timeout=10.0) as client:
        h = HEADERS.copy()
        h["Referer"] = referer
        resp = await client.get(url, headers=h)

        content = resp.text
        lines = []
        from urllib.parse import quote, urljoin

        proxy_base = proxy_base.rstrip("?&")
        segment_base = proxy_base.rsplit("/", 1)[0] + "/proxy_segment"

        def proxy_url(endpoint: str, target: str) -> str:
            query = f"url={quote(target, safe='')}&referer={quote(referer, safe='')}"
            return f"{endpoint}?{query}&proxy_base={quote(proxy_base, safe=':/')}"

        for line in content.split('\n'):
            stripped = line.strip()
            if stripped and not stripped.startswith('#'):
                absolute_url = urljoin(url, stripped)
                if '.m3u8' in stripped:
                    line = proxy_url(proxy_base, absolute_url)
                else:
                    line = proxy_url(segment_base, absolute_url)
            lines.append(line)

        return Response(content='\n'.join(lines), media_type="application/vnd.apple.mpegurl")


@app.get("/proxy_segment")
async def proxy_segment(url: str, referer: str):
    url = _norm_url(url)
    if not url:
        return Response(content='{"detail":"bad proxy url"}', status_code=400,
                        media_type="application/json")
    async with httpx.AsyncClient(timeout=30.0) as client:
        h = HEADERS.copy()
        h["Referer"] = referer
        resp = await client.get(url, headers=h)
        return Response(content=resp.content, media_type="video/mp2t")


@app.get("/", response_class=HTMLResponse)
async def home():

    return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Eiryui API — Anime. Anytime. Anywhere.</title>
    <meta name="description" content="Eiryui API — anime metadata, episode discovery, and streaming source extraction.">
    <link rel="icon" type="image/png" sizes="32x32" href="/logo_favicons/favicon-32x32.png">
    <link rel="icon" type="image/png" sizes="16x16" href="/logo_favicons/favicon-16x16.png">
    <link rel="shortcut icon" href="/logo_favicons/favicon.ico">
    <link rel="apple-touch-icon" sizes="180x180" href="/logo_favicons/apple-touch-icon-180x180.png">
    <link rel="manifest" href="/logo_favicons/site.webmanifest">
    <meta name="theme-color" content="#0B0813">
    <meta name="application-name" content="Eiryui API">
    <link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&family=Inter:wght@300;400;500&display=swap" rel="stylesheet">
    <script src="https://cdn.jsdelivr.net/npm/lucide@latest/dist/umd/lucide.min.js"></script>
    <style>
        :root {
            --bg: #0B0813;
            --fg: #FFFFFF;
            --accent: #8F5CF8;
            --muted: #161224;
            --panel: #1a1330;
            --border: rgba(168,118,245,.16);
            --text-muted: #9A95B0;
            --cyan: #22d3ee;
        }

        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            font-family: 'Inter', sans-serif;
            scrollbar-width: thin;
            scrollbar-color: var(--accent) var(--bg);
        }

        html {
            min-height: 100%;
            background: var(--bg);
            color-scheme: dark;
        }

        body {
            min-height: 100vh;
            background-color: var(--bg);
            background-image: radial-gradient(circle at 50% 0%, #17102c 0%, var(--bg) 62%);
            background-attachment: fixed;
            color: var(--fg);
            line-height: 1.6;
            -webkit-font-smoothing: antialiased;
        }

        .container {
            max-width: 900px;
            margin: 0 auto;
            padding: 64px 24px;
        }

        header { margin-bottom: 60px; text-align: left; }

        .brand-logo { width: 72px; height: 72px; object-fit: contain; margin-bottom: 20px; filter: drop-shadow(0 0 24px rgba(143,92,248,.45)); }

        h1 { font-family: 'Space Grotesk', sans-serif; font-size: 3.5rem; font-weight: 700; letter-spacing: -0.05em; line-height: 1; }
        .subtitle { font-size: 1.1rem; color: var(--text-muted); font-weight: 300; margin: 12px 0 20px; }
        .v-badge { display: inline-flex; align-items: center; gap: 7px; background: rgba(143,92,248,.12); border: 1px solid rgba(143,92,248,.28); padding: 5px 12px; border-radius: 99px; font-size: 0.8rem; color: #c5a7ff; }

        .warning-box {
            background: rgba(249, 115, 22, .08);
            border: 1px solid rgba(249, 115, 22, .24);
            backdrop-filter: blur(10px);
            -webkit-backdrop-filter: blur(10px);
            border-radius: 8px;
            padding: 16px 20px;
            margin-bottom: 40px;
            color: #fdba74;
            font-size: 0.9rem;
            font-weight: 500;
        }
        .warning-box strong { color: #fb923c; }

        .lbl {
            font-size: 0.75rem;
            text-transform: uppercase;
            letter-spacing: 0.2em;
            color: var(--text-muted);
            margin: 60px 0 24px;
            display: block;
            border-bottom: 1px solid var(--border);
            padding-bottom: 8px;
        }

        .card {
            background: rgba(22,18,36,.72);
            border: 1px solid var(--border);
            border-radius: 12px;
            margin-bottom: 24px;
            padding: 24px;
            transition: border-color 0.2s;
        }
        .card:hover { border-color: rgba(143,92,248,.48); box-shadow: 0 14px 40px rgba(0,0,0,.2); }

        .meta { display: flex; align-items: center; justify-content: space-between; margin-bottom: 12px; flex-wrap: wrap; gap: 12px; }
        .method { font-size: 0.75rem; font-weight: 700; padding: 5px 9px; background: rgba(143,92,248,.14); color: #c5a7ff; border: 1px solid rgba(143,92,248,.25); border-radius: 6px; display: inline-flex; align-items: center; gap: 6px; }
        .method svg { width: 13px; height: 13px; }
        .tag { border: 1px solid var(--border); padding: 1px 6px; border-radius: 4px; font-size: 0.6rem; text-transform: uppercase; color: var(--text-muted); }
        .path { font-family: monospace; font-size: 0.95rem; }

        .desc { font-size: 0.9rem; color: var(--text-muted); margin-bottom: 20px; }

        /* playground interactive elements */
        .sandbox { display: flex; gap: 8px; margin-bottom: 12px; }
        .in-url {
            flex: 1;
            background: var(--panel);
            border: 1px solid var(--border);
            border-radius: 6px;
            padding: 8px 12px;
            color: var(--fg);
            font-family: monospace;
            font-size: 0.85rem;
            outline: none;
        }
        .in-url:focus { border-color: #555; }

        .try-btn { background: var(--accent); color: #fff; border: none; padding: 8px 16px; border-radius: 6px; font-size: 0.85rem; font-weight: 600; cursor: pointer; transition: opacity .2s, transform .2s; white-space: nowrap; }
        .try-btn:hover { opacity: .9; transform: translateY(-1px); }

        pre { font-family: monospace; font-size: 0.75rem; color: var(--text-muted); background: var(--muted); padding: 16px; border-radius: 6px; border: 1px solid var(--border); margin-top: 16px; white-space: pre-wrap; word-break: break-all; }

        .res-box { margin-top: 20px; display: none; max-height: 400px; overflow-y: auto; }
        .loading { font-size: 0.8rem; color: var(--text-muted); display: none; margin-top: 10px; }

        .player-wrap { margin-top: 24px; display: none; background: #000; border-radius: 8px; overflow: hidden; border: 1px solid var(--border); aspect-ratio: 16/9; position: relative; }
        video { width: 100%; height: 100%; display: block; }

        .curl-box { margin-top: 16px; display: none; background: var(--muted); border: 1px solid var(--border); border-radius: 6px; padding: 12px; position: relative; }
        .curl-box code { font-family: monospace; font-size: 0.75rem; color: var(--fg); word-break: break-all; display: block; }
        .copy-curl { position: absolute; top: 8px; right: 8px; background: var(--fg); color: var(--bg); border: none; padding: 4px 10px; border-radius: 4px; font-size: 0.7rem; cursor: pointer; font-weight: 600; }
        .copy-curl:hover { opacity: 0.8; }

        footer {
            margin-top: 100px;
            padding: 40px 24px;
            border-top: 1px solid var(--border);
            background: rgba(11, 8, 19, .92);
            color: var(--text-muted);
            font-size: 0.8rem;
            line-height: 1.8;
            text-align: center;
        }
        .footer-logo { height: 42px; width: auto; margin-bottom: 12px; opacity: .9; }
    </style>
    <script src="https://cdn.jsdelivr.net/npm/hls.js@latest"></script>
</head>
<body>
    <div class="container">
        <header>
            <img class="brand-logo" src="/logo_favicons/Eiryui.png" alt="Eiryui">
            <h1>Eiryui API</h1>
            <p class="subtitle">Anime metadata and streaming sources, built for Eiryui Project.</p>
        <div class="v-badge"><i data-lucide="radio"></i> v3.2 — live testing enabled</div>
        </header>

        <div class="warning-box">
        ⚠ <strong>Experimental API:</strong> Stability is not guaranteed. Expect occasional downtime, breaking changes, and inaccurate responses. Not recommended for critical or production use. Proceed at your own risk.
        </div>

        <span class="lbl">anime endpoints explorer</span>

        <div class="card">
            <div class="meta">
                <div><span class="method">GET</span> <span class="path">search</span></div>
                <div class="tag">full metadata</div>
            </div>
            <div class="desc">global anime search. returns full metadata titles and covers.</div>
            <div class="sandbox">
                <input type="text" class="in-url" value="/anime/search?query=violet evergarden&page=1">
                <button class="try-btn" onclick="test(this)">execute</button>
            </div>
            <div class="loading">working...</div>
            <div class="res-box"><pre></pre></div>
        </div>

        <div class="card">
            <div class="meta">
                <div><span class="method">GET</span> <span class="path">suggestions</span> <span class="tag">lite</span></div>
            </div>
            <div class="desc">lightweight autocomplete search. minimal data footprint.</div>
            <div class="sandbox">
                <input type="text" class="in-url" value="/anime/suggestions?query=violet evergarden">
                <button class="try-btn" onclick="test(this)">execute</button>
            </div>
            <div class="loading">working...</div>
            <div class="res-box"><pre></pre></div>
        </div>

        <div class="card">
            <div class="meta">
                <div><span class="method">GET</span> <span class="path">spotlight</span> <span class="tag">hot</span></div>
            </div>
            <div class="desc">curated hot list of top trending shows in focus.</div>
            <div class="sandbox">
                <input type="text" class="in-url" value="/anime/spotlight">
                <button class="try-btn" onclick="test(this)">execute</button>
            </div>
            <div class="loading">working...</div>
            <div class="res-box"><pre></pre></div>
        </div>

        <div class="card">
            <div class="meta">
                <div><span class="method">GET</span> <span class="path">filter</span></div>
            </div>
            <div class="desc">advanced logic to combine genres, years, formats and sorting.</div>
            <div class="sandbox">
                <input type="text" class="in-url" value="/anime/filter?genre=Action&sort=SCORE_DESC">
                <button class="try-btn" onclick="test(this)">execute</button>
            </div>
            <div class="loading">working...</div>
            <div class="res-box"><pre></pre></div>
        </div>

        <div class="card">
            <div class="meta">
                <div><span class="method">GET</span> <span class="path">genres</span></div>
            </div>
            <div class="desc">list all available genres for filtering.</div>
            <div class="sandbox">
                <input type="text" class="in-url" value="/anime/genres">
                <button class="try-btn" onclick="test(this)">execute</button>
            </div>
            <div class="loading">working...</div>
            <div class="res-box"><pre></pre></div>
        </div>

        <div class="card">
            <div class="meta">
                <div><span class="method">GET</span> <span class="path">info/{id}</span></div>
                <div class="tag">full info</div>
            </div>
            <div class="desc">complete anime page chunk — characters, relations, staff, and recs.</div>
            <div class="sandbox">
                <input type="text" class="in-url" value="/anime/info/21827">
                <button class="try-btn" onclick="test(this)">execute</button>
            </div>
            <div class="loading">working...</div>
            <div class="res-box"><pre></pre></div>
        </div>

        <div class="card">
            <div class="meta">
                <div><span class="method">GET</span> <span class="path">anime/{id}/characters</span></div>
            </div>
            <div class="desc">character list with voice actors.</div>
            <div class="sandbox">
                <input type="text" class="in-url" value="/anime/anime/21827/characters">
                <button class="try-btn" onclick="test(this)">execute</button>
            </div>
            <div class="loading">working...</div>
            <div class="res-box"><pre></pre></div>
        </div>

        <div class="card">
            <div class="meta">
                <div><span class="method">GET</span> <span class="path">anime/{id}/relations</span></div>
            </div>
            <div class="desc">related anime (sequels, prequels, spin-offs).</div>
            <div class="sandbox">
                <input type="text" class="in-url" value="/anime/anime/21827/relations">
                <button class="try-btn" onclick="test(this)">execute</button>
            </div>
            <div class="loading">working...</div>
            <div class="res-box"><pre></pre></div>
        </div>

        <div class="card">
            <div class="meta">
                <div><span class="method">GET</span> <span class="path">anime/{id}/recommendations</span></div>
            </div>
            <div class="desc">recommended similar anime.</div>
            <div class="sandbox">
                <input type="text" class="in-url" value="/anime/anime/21827/recommendations">
                <button class="try-btn" onclick="test(this)">execute</button>
            </div>
            <div class="loading">working...</div>
            <div class="res-box"><pre></pre></div>
        </div>

        <div class="card">
            <div class="meta">
                <div><span class="method">GET</span> <span class="path">trending</span></div>
            </div>
            <div class="desc">currently trending anime.</div>
            <div class="sandbox">
                <input type="text" class="in-url" value="/anime/trending?page=1">
                <button class="try-btn" onclick="test(this)">execute</button>
            </div>
            <div class="loading">working...</div>
            <div class="res-box"><pre></pre></div>
        </div>

        <div class="card">
            <div class="meta">
                <div><span class="method">GET</span> <span class="path">popular</span></div>
            </div>
            <div class="desc">most popular anime of all time.</div>
            <div class="sandbox">
                <input type="text" class="in-url" value="/anime/popular?page=1">
                <button class="try-btn" onclick="test(this)">execute</button>
            </div>
            <div class="loading">working...</div>
            <div class="res-box"><pre></pre></div>
        </div>

        <div class="card">
            <div class="meta">
                <div><span class="method">GET</span> <span class="path">upcoming</span></div>
            </div>
            <div class="desc">upcoming anime releases.</div>
            <div class="sandbox">
                <input type="text" class="in-url" value="/anime/upcoming?page=1">
                <button class="try-btn" onclick="test(this)">execute</button>
            </div>
            <div class="loading">working...</div>
            <div class="res-box"><pre></pre></div>
        </div>

        <div class="card">
            <div class="meta">
                <div><span class="method">GET</span> <span class="path">recent</span></div>
            </div>
            <div class="desc">recently aired episodes.</div>
            <div class="sandbox">
                <input type="text" class="in-url" value="/anime/recent?page=1">
                <button class="try-btn" onclick="test(this)">execute</button>
            </div>
            <div class="loading">working...</div>
            <div class="res-box"><pre></pre></div>
        </div>

        <div class="card">
            <div class="meta">
                <div><span class="method">GET</span> <span class="path">schedule</span></div>
            </div>
            <div class="desc">airing schedule for upcoming episodes.</div>
            <div class="sandbox">
                <input type="text" class="in-url" value="/anime/schedule?page=1">
                <button class="try-btn" onclick="test(this)">execute</button>
            </div>
            <div class="loading">working...</div>
            <div class="res-box"><pre></pre></div>
        </div>

        <div class="card">
            <div class="meta">
                <div><span class="method">GET</span> <span class="path">episodes/{id}</span></div>
            </div>
            <div class="desc">grabs internal mappings and episode lists.</div>
            <div class="sandbox">
                <input type="text" class="in-url" value="/anime/episodes/178005">
                <button class="try-btn" onclick="test(this)">execute</button>
            </div>
            <div class="loading">working...</div>
            <div class="res-box"><pre></pre></div>
        </div>

        <div class="card">
            <div class="meta">
                <div><span class="method">GET</span> <span class="path">episodes/{id}</span></div>
            </div>
            <div class="desc">grabs internal mappings and episode lists.</div>
            <div class="sandbox">
                <input type="text" class="in-url" value="/anime/episodes/21827">
                <button class="try-btn" onclick="test(this)">execute</button>
            </div>
            <div class="loading">working...</div>
            <div class="res-box"><pre></pre></div>
        </div>

        <div class="card">
            <div class="meta">
                <div><span class="method">GET</span> <span class="path">providers/status</span></div>
                <div class="tag">monitoring</div>
            </div>
            <div class="desc">provider availability, ranking, latency, and failure status.</div>
            <div class="sandbox">
                <input type="text" class="in-url" value="/anime/providers/status">
                <button class="try-btn" onclick="test(this)">execute</button>
            </div>
            <div class="loading">working...</div>
            <div class="res-box"><pre></pre></div>
        </div>

        <div class="card">
            <div class="meta">
                <div><span class="method">GET</span> <span class="path">bridge-status</span></div>
                <div class="tag">deprecated alias</div>
            </div>
            <div class="desc">compatibility alias for provider status monitoring.</div>
            <div class="sandbox">
                <input type="text" class="in-url" value="/anime/bridge-status">
                <button class="try-btn" onclick="test(this)">execute</button>
            </div>
            <div class="loading">working...</div>
            <div class="res-box"><pre></pre></div>
        </div>

        <div class="card">
            <div class="meta">
                <div><span class="method">GET</span> <span class="path">sources</span></div>
                <div class="tag">legacy</div>
            </div>
            <div class="desc">resolve sources through the legacy provider pipe using an episode mapping.</div>
            <div class="sandbox">
                <input type="text" class="in-url" value="/anime/sources?episodeId=anineko-1&provider=anineko&anilistId=21827&category=sub">
                <button class="try-btn" onclick="test(this)">execute</button>
            </div>
            <div class="loading">working...</div>
            <div class="res-box"><pre></pre></div>
        </div>

        <span class="lbl">all-in-one automation</span>

        <div class="card">
            <div class="meta">
                <div><span class="method" style="background:#fff;color:#000">GET</span> <span class="path">extract</span> <span class="tag">magic</span></div>
            </div>
            <div class="desc">use anilist id (21827) or full anime name (violet evergarden). get id from /anime/search if needed. movies auto-detect. pick a provider or leave on auto for fastest-wins.</div>
            <div class="sandbox">
                <input type="text" class="in-url" value="/anime/extract/violet-evergarden?e=1">
                <button class="try-btn" onclick="test(this)">execute</button>
            </div>
            <div class="sandbox">
                <select class="in-url in-prov">
                    <option value="">auto (fastest wins)</option>
                    <option value="anineko">anineko</option>
                    <option value="anizone">anizone</option>
                    <option value="anikoto">anikoto</option>
                    <option value="reanime">reanime</option>
                    <option value="aniwaves">aniwaves</option>
                    <option value="kaa">kaa</option>
                    <option value="anibd">anibd</option>
                    <option value="animegg">animegg</option>
                    <option value="mkissa">mkissa</option>
                    <option value="animeonsen">animeonsen</option>
                </select>
                <select class="in-url in-type">
                    <option value="sub">sub</option>
                    <option value="dub">dub</option>
                </select>
            </div>
            <div class="loading">working...</div>
            <div class="player-wrap"><video id="hls-player" controls @play="refreshReferer"></video></div>
            <div class="curl-box">
                <button class="copy-curl" onclick="copyCurl(this)">copy</button>
                <code></code>
            </div>
            <div class="res-box"><pre></pre></div>
        </div>

        <span class="lbl">stream proxy</span>

        <div class="card">
            <div class="meta">
                <div><span class="method">GET</span> <span class="path">proxy_m3u8</span></div>
                <div class="tag">HLS</div>
            </div>
            <div class="desc">proxy an HLS playlist and rewrite its segment URLs with the required referer.</div>
            <div class="sandbox">
                <input type="text" class="in-url" value="/proxy_m3u8?url=https%3A%2F%2Fexample.com%2Fmaster.m3u8&referer=https%3A%2F%2Fexample.com%2F">
                <button class="try-btn" onclick="test(this)">execute</button>
            </div>
            <div class="loading">working...</div>
            <div class="res-box"><pre></pre></div>
        </div>

        <div class="card">
            <div class="meta">
                <div><span class="method">GET</span> <span class="path">proxy_segment</span></div>
                <div class="tag">HLS</div>
            </div>
            <div class="desc">proxy a video segment with the required referer header.</div>
            <div class="sandbox">
                <input type="text" class="in-url" value="/proxy_segment?url=https%3A%2F%2Fexample.com%2Fsegment.ts&referer=https%3A%2F%2Fexample.com%2F">
                <button class="try-btn" onclick="test(this)">execute</button>
            </div>
            <div class="loading">working...</div>
            <div class="res-box"><pre></pre></div>
        </div>

        <footer>
            <img class="footer-logo" src="/logo_favicons/logo.png" alt="Eiryui">
            <div>Eiryui API · Anime. Anytime. Anywhere.</div>
        </footer>
    </div>

    <script>
        async function test(btn) {
            const card = btn.closest('.card');
            const input = card.querySelector('.in-url');
            let endpoint = input.value;
            const prov = card.querySelector('.in-prov');
            const typ = card.querySelector('.in-type');
            if (prov && prov.value) {
                endpoint += (endpoint.includes('?') ? '&' : '?') + 'provider=' + encodeURIComponent(prov.value);
            }
            if (typ && typ.value) {
                endpoint += (endpoint.includes('?') ? '&' : '?') + 'type=' + encodeURIComponent(typ.value);
            }
            const resBox = card.querySelector('.res-box');
            const pre = resBox.querySelector('pre');
            const loader = card.querySelector('.loading');

            resBox.style.display = 'none';
            loader.style.display = 'block';

            try {
                const response = await fetch(endpoint);
                const data = await response.json();
                pre.textContent = JSON.stringify(data, null, 2);
                resBox.style.display = 'block';

                // init player if streams exist in extraction
                if (data.streams && data.streams.length > 0) {
                    const hlsStream = data.streams.find(s => s.type === 'hls');
                    if (hlsStream && Hls.isSupported()) {
                        const video = document.getElementById('hls-player');
                        const hls = new Hls({
                            xhrSetup: function(xhr, url) {
                                // force all requests through our server
                                if (url.startsWith('http') && !url.includes('127.0.0.1') && !url.includes('localhost')) {
                                    return;
                                }
                            }
                        });
                        // we use an internal proxy to inject the required referer per stream response
                        const proxyUrl = `/proxy_m3u8?url=${encodeURIComponent(hlsStream.url)}&referer=${encodeURIComponent(hlsStream.referer)}`;
                        hls.loadSource(proxyUrl);
                        hls.attachMedia(video);
                        card.querySelector('.player-wrap').style.display = 'block';

                        // add curl command for m3u8
                        const curlCmd = `curl -H "Referer: ${hlsStream.referer}" "${hlsStream.url}"`;
                        const curlBox = card.querySelector('.curl-box');
                        if (curlBox) {
                            curlBox.querySelector('code').textContent = curlCmd;
                            curlBox.style.display = 'block';
                        }
                    }
                }
            } catch (err) {
                pre.textContent = 'error: ' + err.message;
                resBox.style.display = 'block';
            } finally {
                loader.style.display = 'none';
            }
        }

        function copyCurl(btn) {
            const code = btn.parentElement.querySelector('code').textContent;
            navigator.clipboard.writeText(code);
            btn.textContent = 'copied!';
            setTimeout(() => btn.textContent = 'copy', 2000);
        }

        if (window.lucide) lucide.createIcons();
    </script>
</body>
</html>"""
