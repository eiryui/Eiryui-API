<div align="center">

<img src="logo_favicons/logo.png" alt="Eiryui API" width="120" />

# 🌸 Eiryui API v3.2

**An anime streaming API built for scale — search, filter and stream with automatic source extraction.**

![Status](https://img.shields.io/badge/status-archived-critical?style=for-the-badge&logo=archive&logoColor=white)
![Maintenance](https://img.shields.io/badge/maintenance-no%20further%20updates-red?style=for-the-badge)
![Stability](https://img.shields.io/badge/stability-experimental-orange?style=for-the-badge)
![Python](https://img.shields.io/badge/python-3.8+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)

### 🧭 Menu

[🏠 Overview](#-overview) •
[✨ Features](#-features) •
[📦 Installation](#-installation) •
[🗂️ Structure](#️-project-structure) •
[🔎 Endpoints](#-api-endpoints) •
[🎬 Streaming](#-streaming) •
[🧩 Providers](#-native-providers) •
[🔀 Proxy](#-proxy-endpoints) •
[💡 Examples](#-usage-examples) •
[⚙️ Config](#️-configuration) •
[📜 License](#-license)

</div>

---

> [!CAUTION]
> ## 🛑 PROJECT ARCHIVED — NO FURTHER UPDATES
> **This repository is archived and no longer maintained.**
> - ❌ No new features, bug fixes or security patches will be released.
> - ❌ Providers may break at any time as upstream sites change, and they will **not** be repaired.
> - ❌ Issues and pull requests will not be reviewed.
>
> You are free to **fork** it and continue the work on your own.

> [!WARNING]
> ## ⚠️ DISCLAIMER
> This API is **experimental and not reliable**. Stability is **not guaranteed**.
> Expect **occasional downtime**, **breaking changes**, and **inaccurate responses**.
> **Not recommended for critical or production use. Proceed at your own risk.**

> [!NOTE]
> 📅 **Last known status:** 10/26/2026 — working, native providers (no longer monitored).

---

## 🏠 Overview

Eiryui provides a clean REST interface to search, filter, and stream anime content with automatic source extraction and proxy capabilities. Streaming runs on **10 native Python providers** (no sidecars, no external aggregator needed) — every `/extract` call **races all providers concurrently and the fastest success wins**, with a rolling latency table that keeps the closest/fastest provider as the default.

## ✨ Features

| | Feature | Description |
|---|---|---|
| 🔍 | **Smart Search** | Search by anime name or AniList ID |
| ⚡ | **Auto-Extraction** | Races 10 native providers, fastest stream wins |
| 🎧 | **Sub/Dub flags** | `?type=sub\|dub` on extraction, per-audio episode lists |
| 🏁 | **Latency-ranked default** | Fastest provider becomes the default automatically |
| 🎞️ | **Movie Detection** | Automatically handles movies vs episodes |
| 🔓 | **Decryption Pipeline** | Native MegaPlay/FlixCloud extractors in Python |
| 🌐 | **CORS Proxy** | Built-in proxy for bypassing CDN restrictions |
| 📺 | **HLS Streaming** | Full M3U8 playlist and segment proxying |

## 📦 Installation

### 📋 Prerequisites
- Python 3.8+
- pip

### 🚀 Setup

1. Clone the repository:
```bash
git clone <your-eiryui-api-repository>
cd Eiryui-API
```

2. Install dependencies:
```bash
python -m pip install -r requirements.txt
```

3. Run the server:
```bash
uvicorn api:app --reload --host 0.0.0.0 --port 4000
```

4. Access the API:
```
http://127.0.0.1:4000
```

## 🗂️ Project Structure

```
Eiryui-API/
├── src/
│   ├── __init__.py          # Package initializer
│   ├── main.py              # FastAPI app & proxy endpoints
│   ├── endpoints.py         # Anime API routes
│   ├── extractor.py         # AniList data fetchers (+ legacy pipe fallback)
│   ├── providers/           # Native streaming providers (no sidecars)
│   │   ├── _race.py         # Fastest-wins race + latency-ranked default
│   │   ├── _match.py        # Title matching / series selection
│   │   ├── _media.py        # AniList + ARM + AniZip identity
│   │   ├── _http.py         # Shared HTTP helpers
│   │   ├── _cache.py        # TTL cache
│   │   └── anineko.py, anizone.py, anikoto.py, reanime.py, ...
│   ├── parser.py            # Data transformation utilities
│   ├── queries.py           # GraphQL query templates
│   └── config.py            # Configuration & constants
├── api.py                   # Alternative entry point
├── .gitignore               # Git ignore rules
└── README.md                # This file
```

## 🔎 API Endpoints

### 🔍 Search & Discovery

#### `GET /anime/search`
Search anime by keyword with pagination.

**Parameters:**
- `query` (string, required) - Search term
- `page` (int, default: 1) - Page number
- `per_page` (int, default: 20, max: 50) - Results per page

**Example:**
```bash
curl "http://127.0.0.1:4000/anime/search?query=naruto&page=1"
```

#### `GET /anime/suggestions`
Lightweight autocomplete search for dropdowns.

**Parameters:**
- `query` (string, required) - Search term

**Example:**
```bash
curl "http://127.0.0.1:4000/anime/suggestions?query=one%20piece"
```

#### `GET /anime/genres`
List all available genres for filtering.

**Example:**
```bash
curl "http://127.0.0.1:4000/anime/genres"
```

### 📚 Collections

#### `GET /anime/spotlight`
Top 10 trending and popular anime.

```bash
curl "http://127.0.0.1:4000/anime/spotlight"
```

#### `GET /anime/trending`
Currently trending anime with pagination.

**Parameters:** `page` (int, default: 1), `per_page` (int, default: 20, max: 50)

```bash
curl "http://127.0.0.1:4000/anime/trending?page=1&per_page=20"
```

#### `GET /anime/popular`
Most popular anime of all time.

**Parameters:** `page` (int, default: 1), `per_page` (int, default: 20, max: 50)

```bash
curl "http://127.0.0.1:4000/anime/popular"
```

#### `GET /anime/upcoming`
Upcoming anime releases.

**Parameters:** `page` (int, default: 1), `per_page` (int, default: 20, max: 50)

```bash
curl "http://127.0.0.1:4000/anime/upcoming"
```

#### `GET /anime/recent`
Recently aired episodes.

**Parameters:** `page` (int, default: 1), `per_page` (int, default: 20, max: 50)

```bash
curl "http://127.0.0.1:4000/anime/recent"
```

#### `GET /anime/schedule`
Airing schedule for upcoming episodes.

**Parameters:** `page` (int, default: 1), `per_page` (int, default: 20, max: 50)

```bash
curl "http://127.0.0.1:4000/anime/schedule"
```

### 🎛️ Advanced Filtering

#### `GET /anime/filter`
Filter anime by multiple criteria.

**Parameters:**
- `genre` (string, optional) - Genre name (get from /anime/genres)
- `tag` (string, optional) - Tag name
- `year` (int, optional) - Season year
- `season` (string, optional) - Season (WINTER, SPRING, SUMMER, FALL)
- `format` (string, optional) - Format (TV, MOVIE, OVA, ONA, SPECIAL)
- `status` (string, optional) - Status (RELEASING, FINISHED, NOT_YET_RELEASED)
- `sort` (string, default: POPULARITY_DESC) - Sort order
- `page` (int, default: 1)
- `per_page` (int, default: 20, max: 50)

**Sort Options:**
- `SCORE_DESC` - Highest rated
- `POPULARITY_DESC` - Most popular
- `TRENDING_DESC` - Currently trending
- `START_DATE_DESC` - Recently started
- `FAVOURITES_DESC` - Most favorited
- `UPDATED_AT_DESC` - Recently updated

```bash
curl "http://127.0.0.1:4000/anime/filter?genre=Action&sort=SCORE_DESC&year=2024"
```

### 📖 Anime Details

#### `GET /anime/info/{anilist_id}`
Complete anime information including characters, relations, staff, and recommendations.

```bash
curl "http://127.0.0.1:4000/anime/info/21"
```

#### `GET /anime/anime/{anilist_id}/characters`
Character list with voice actors.

**Parameters:** `page` (int, default: 1), `per_page` (int, default: 25, max: 50)

```bash
curl "http://127.0.0.1:4000/anime/anime/21/characters"
```

#### `GET /anime/anime/{anilist_id}/relations`
Related anime (sequels, prequels, spin-offs).

```bash
curl "http://127.0.0.1:4000/anime/anime/21/relations"
```

#### `GET /anime/anime/{anilist_id}/recommendations`
Recommended similar anime.

**Parameters:** `page` (int, default: 1), `per_page` (int, default: 10, max: 25)

```bash
curl "http://127.0.0.1:4000/anime/anime/21/recommendations"
```

## 🎬 Streaming

#### `GET /anime/episodes/{anilist_id}`
Episode lists merged from all native providers concurrently, split by audio (`sub` / `dub`). Falls back to the legacy pipe if no native provider matches.

```bash
curl "http://127.0.0.1:4000/anime/episodes/21"
# → { anilistId, source: "native", providers: { anineko: { episodes: { sub: [...], dub: [...] }, meta }, ... } }
```

#### `GET /anime/extract/{query}`
**✨ Magic endpoint** - Races all native providers concurrently; **fastest success wins** and feeds the latency table that picks the default provider.

**Parameters:**
- `query` (string, required) - AniList ID (21) or anime name (violet evergarden)
- `e` (int, default: 1) - Episode number
- `type` (string, default: `sub`) - Audio: `sub` or `dub`
- `provider` (string, optional) - Force one provider (`anineko`, `anizone`, `anikoto`, `reanime`, `aniwaves`, `kaa`, `anibd`, `animegg`, `mkissa`, `animeonsen`). Omit for fastest-wins race.

**Features:**
- Accepts both numeric IDs and full anime names with spaces
- Automatically searches AniList if name is provided
- Auto-detects movies and plays them regardless of episode parameter
- Sub/dub aware: `?type=dub` only returns dubbed streams (404 with a hint if none exist)
- Manual pick: `?provider=anineko` tries that provider first, falls back to the race (response shows `requestedProvider` vs actual `provider`)
- Response includes `provider` (winner), `defaultProvider` (fastest on record), `streams`, `subtitles`
- Returns HLS/MP4/DASH streams with referer headers where required
- Legacy Miruro pipe is kept as a last-resort fallback

**Examples:**
```bash
# Using AniList ID (subbed)
curl "http://127.0.0.1:4000/anime/extract/21?e=1"

# Dubbed
curl "http://127.0.0.1:4000/anime/extract/21?e=1&type=dub"

# Manual provider pick
curl "http://127.0.0.1:4000/anime/extract/21?e=1&provider=reanime"

# Using anime name (spaces work)
curl "http://127.0.0.1:4000/anime/extract/violet%20evergarden?e=1"

# Using hyphenated name
curl "http://127.0.0.1:4000/anime/extract/my-hero-academia?e=5"

# Movie (episode param ignored)
curl "http://127.0.0.1:4000/anime/extract/a-silent-voice"
```

> [!TIP]
> If search by name fails, use `/anime/search?query=<name>` to get the exact AniList ID first.

#### `GET /anime/providers/status`
Live provider ranking, availability and measured latency. (`/anime/bridge-status` is a deprecated alias.)

```bash
curl "http://127.0.0.1:4000/anime/providers/status"
# → { defaultProvider: "anineko", ranking: [...], available: [...], latency: { anineko: { avg_seconds, failures } } }
```

## 🧩 Native Providers

All ports are pure Python (`src/providers/`, httpx only). Tested 10/09/2026 on Naruto (220 eps), One Piece and Demon Slayer:

| Provider | Episodes | Watch | Audio | Notes |
|---|---|---|---|---|
| **anineko** | ✅ 220 | ✅ 19 HLS | sub + dub | Fast, reliable default |
| **anizone** | ✅ 220 | ✅ HLS + subs | sub (dub empty upstream) | Livewire pagination |
| **anikoto** | ✅ 220 | ✅ 6-8 HLS | sub + dub | MegaPlay AES decrypt |
| **reanime** | ✅ 220 | ✅ HLS (flixcloud) | sub + dub | WASM-transform decrypt |
| **aniwaves** | ✅ 220 | ✅ HLS + embeds | sub + dub | vidplay/datasv/megaplay |
| **kaa** | ✅ 220 | ✅ HLS | sub + dub | JSON API |
| **anibd** | ✅ 220 | ✅ HLS + embed | sub (dub empty upstream) | AniList-keyed API |
| **animegg** | ✅ 220 | ✅ MP4 + embed | sub + dub | HTML scrape |
| **mkissa** | ✅ 440 | ✅ HLS + direct | sub + dub + raw | allanime backend |
| **animeonsen** | ✅ 26 | ✅ DASH | sub only | Needs modern Chrome UA |

Skipped: `2dhive` (partial library, embed-only), `anidbapp` / `animenosub` / `senshi` / `animedunya` (no results on test titles).

> [!WARNING]
> These results reflect testing at the time of the last release. Since the project is archived, providers are **not** being kept up to date and may already be broken.

## 🔀 Proxy Endpoints

#### `GET /proxy_m3u8`
Proxy M3U8 playlists with referer injection and URL rewriting.

**Parameters:**
- `url` (string, required) - M3U8 playlist URL
- `referer` (string, required) - Referer header value

#### `GET /proxy_segment`
Proxy video segments with referer injection.

**Parameters:**
- `url` (string, required) - Segment URL
- `referer` (string, required) - Referer header value

## 💡 Usage Examples

### 🧭 Basic Workflow

1. **Search for anime:**
```bash
curl "http://127.0.0.1:4000/anime/search?query=demon%20slayer"
```

2. **Get anime info (use ID from search):**
```bash
curl "http://127.0.0.1:4000/anime/info/101922"
```

3. **Get episodes:**
```bash
curl "http://127.0.0.1:4000/anime/episodes/101922"
```

4. **Extract streaming source:**
```bash
curl "http://127.0.0.1:4000/anime/extract/101922?e=1"
```

### ⚡ Quick Extraction

Skip all steps and directly extract:
```bash
# By name
curl "http://127.0.0.1:4000/anime/extract/demon%20slayer?e=1"

# By ID
curl "http://127.0.0.1:4000/anime/extract/101922?e=1"
```

## 📬 Response Format

All endpoints return JSON with consistent structure:

### Search/Filter/Collections Response
```json
{
  "page": 1,
  "perPage": 20,
  "total": 1000,
  "hasNextPage": true,
  "results": [...]
}
```

### Streaming Source Response (`/anime/extract`)
```json
{
  "anilistId": 21,
  "episode": 1,
  "type": "sub",
  "provider": "anineko",
  "defaultProvider": "anineko",
  "streams": [
    {
      "type": "hls",
      "url": "https://..../master.m3u8",
      "server": "AniNeko",
      "audio": "sub",
      "referer": "https://..."
    }
  ],
  "subtitles": [...]
}
```

Stream `type` is one of `hls` | `mp4` | `dash` | `embed` (embeds need a client-side player or extractor).

## ⚙️ Configuration

Edit `src/config.py` to customize:
- AniList API URL
- Miruro pipe URL (legacy fallback)
- Request headers
- Timeouts

Tune the race in `src/providers/_race.py`:
- `RANKING` - initial provider order (latency table takes over at runtime)
- `WATCH_TIMEOUT` / `EPISODES_TIMEOUT` - per-provider timeouts
- `WATCH_CACHE_TTL` - short cache for tokenized stream URLs

## 🛠️ Tech Stack

- **FastAPI** - Modern async web framework
- **httpx** - Async HTTP client
- **HLS.js** - Video player for web interface
- **AniList GraphQL API** - Anime metadata
- **Native providers** - Pure-Python scrapers + extractors (`src/providers/`)
- **Miruro Pipe** - Legacy fallback for streaming sources

## 🧑‍💻 Development

Run in development mode with auto-reload:
```bash
uvicorn api:app --reload --host 0.0.0.0 --port 4000
```

## 📝 Notes

- All image URLs are automatically proxied through serveproxy.com
- Provider priority is dynamic: fastest measured latency wins (see `/anime/providers/status`)
- `?type=dub` filters to dubbed streams; dub lists are empty where upstream has none
- Movies automatically default to episode 1
- M3U8 playlists and segments are proxied to bypass referer checks
- CORS is enabled for all origins

## 📜 License

Educational purposes only. Respect content creators and copyright laws.

---

<div align="center">

![Archived](https://img.shields.io/badge/🗄️_ARCHIVED-no_further_updates-red?style=for-the-badge)

**Built with ❤️ for the anime community**

</div>
