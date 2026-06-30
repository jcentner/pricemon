# Source Compendium

Researched 2026-06-30 from public RSS/feed/search pages. This file is generic and should not include private config, VPS details, tokens, or chat IDs.

`pricemon` currently works best with RSS/Atom feeds whose item title contains enough information to match rules. Sources without RSS can be tracked later with a source-specific adapter, but should not be scraped by default.

## Best Fits

### Reddit: r/buildapcsales

- URL: `https://www.reddit.com/r/buildapcsales/new/.rss`
- Probe: HTTP 200, Atom feed, 25 entries.
- Observed title format:
  - `[TV] Samsung S84F OLED 55" - $699 (BestBuy or Costco)`
  - `[GPU] Microcenter In Store Only- ASRock AMD Radeon RX 9060 XT Challenger OC Dual Fan 16GB GDDR6 PCIe 5.0 Graphics Card - $389.99`
  - `[Laptop] Acer Swift Go 16 AI Laptop: 16" 2K OLED, Core Ultra 7 355, 32GB DDR5, 1TB SSD+ Free S&H $899.99`
- Link format: Reddit comments URL.
- Rule strategy:
  - Category tags are reliable enough to use: `gpu`, `cpu`, `motherboard`, `ram`, `ssd`, `monitor`, etc.
  - Use `exclude_any` aggressively for `prebuilt`, `laptop`, `refurbished`, `expired`, `sold out`.
  - Price parsing usually works because titles contain `$...`.

### Slickdeals Search RSS

- URL pattern: `https://slickdeals.net/newsearch.php?searcharea=deals&searchin=first&q=<query>&rss=1`
- Probe: HTTP 200, RSS feed, typically 22-25 entries per query.
- Useful watchlist examples:
  - `https://slickdeals.net/newsearch.php?searcharea=deals&searchin=first&q=64gb+ddr5&rss=1`
  - `https://slickdeals.net/newsearch.php?searcharea=deals&searchin=first&q=z890&rss=1`
  - `https://slickdeals.net/newsearch.php?searcharea=deals&searchin=first&q=5070+ti&rss=1`
  - `https://slickdeals.net/newsearch.php?searcharea=deals&searchin=first&q=5080&rss=1`
  - `https://slickdeals.net/newsearch.php?searcharea=deals&searchin=first&q=core+ultra+7+270k&rss=1`
- Observed title format:
  - `THUNDEROBOT Radiant 16: 16" 2560x1600 300Hz, i9-14900HX, RTX 5080, 64GB DDR5, 2TB PCIe SSD $2458.99`
  - `[Micro Center] Gigabyte NVIDIA GeForce RTX 5080 WINDFORCE SFF Overclocked Triple Fan 16GB GPU $1149.99 + Free Store Pickup`
  - `ASRock Z890 Taichi LGA 1851 Intel Z890 ATX Motherboard $200 + Free Shipping`
  - `Select Micro Center Stores: Intel Core Ultra 7 270K Plus 24-Core LGA1851 Processor $250 + Free Pickup`
- Link format: Slickdeals thread URL.
- Rule strategy:
  - No consistent category tags; do not use `categories`.
  - Query feeds are already filtered, but still noisy.
  - Exclude `laptop`, `gaming pc`, `desktop`, `prebuilt`, `cert. refurb`, `refurb`, `omen`, `aegis`, `radiant`, `vector` for GPU-only rules.
  - Good source for Micro Center and manufacturer promotions that may not appear on r/buildapcsales quickly.

### Newegg Product RSS

- URL pattern: `https://www.newegg.com/d/Product/RSS?Submit=ENE&IsNodeId=1&Description=<query>`
- Alternate parameter observed to work: `&d=<query>`.
- Probe: search page exposed an RSS autodiscovery link; product RSS returned HTTP 200.
- Example query: `https://www.newegg.com/d/Product/RSS?Submit=ENE&IsNodeId=1&Description=rtx%205080`
- Observed title format:
  - `$1,449.99 - GIGABYTE Gaming GeForce RTX 5080 16GB GDDR7 PCI Express 5.0 Graphics Card GV-N5080GAMING OC-16GD`
  - `$1,379.99 - ZOTAC GeForce RTX 5080 16GB GDDR7 PCI Express 5.0 x16 ATX Video Card GAMING GeForce RTX 5080 SOLID CORE OC`
  - `$1,399.99 - GIGABYTE WINDFORCE GeForce RTX 5080 16GB GDDR7 PCI Express 5.0 Graphics Card GV-N5080WF3OC-16GD`
- Link format: Newegg product URL with RSS tracking parameters.
- Rule strategy:
  - No category tags; do not use `categories`.
  - Titles start with price, so price parsing works well.
  - This is closer to product listing/inventory monitoring than deal monitoring.
  - Use exact query-specific sources and price ceilings if alert volume is too high.
  - Watch for marketplace/third-party seller noise.

### Tom's Hardware Feed

- URL: `https://www.tomshardware.com/feeds.xml`
- Probe: HTTP 200, Atom/RSS feed, 50 entries.
- Observed title format:
  - `Grab this epic Razer Wolverine V3 controller for a record-low Amazon price, now just $64.99 ...`
  - News/article titles mixed with occasional deal posts.
- Link format: Tom's Hardware article URL.
- Rule strategy:
  - Low fit for immediate product alerts; good for article/deal awareness.
  - Use only narrow source-specific rules if enabled.

## Reddit Candidates

These are RSS-compatible in principle, but the probe hit Reddit `429 Too Many Requests` from this environment after checking r/buildapcsales. Test individually before enabling.

### r/hardwareswap

- URL: `https://www.reddit.com/r/hardwareswap/new/.rss`
- Probe: HTTP 429 during research.
- Expected fit: used-market hardware listings.
- Expected title style to verify before enabling: location + have/want pattern, often like `[USA-XX] [H] ... [W] PayPal/local`.
- Rule strategy:
  - Do not use `categories` unless observed titles support them.
  - Use strict `include_any` and exclude `wanted`, `[w]`, `local only`, `laptop`, `prebuilt` as needed.

### r/homelabsales

- URL: `https://www.reddit.com/r/homelabsales/new/.rss`
- Probe: HTTP 429 during research.
- Expected fit: server, storage, networking, and occasional memory/SSD deals.
- Rule strategy:
  - Better for storage/RAM/networking than consumer GPU alerts.
  - Use strict source-specific rules.

### r/buildapcmonitors

- URL: `https://www.reddit.com/r/buildapcmonitors/new/.rss`
- Probe: HTTP 429 during research.
- Expected fit: monitor discussion/deals; likely noisier than r/buildapcsales.

### r/sffpcswap

- URL: `https://www.reddit.com/r/sffpcswap/new/.rss`
- Probe: HTTP 429 during research.
- Expected fit: SFF cases, mini-ITX motherboards, SFX PSUs.

### r/bapcsalescanada

- URL: `https://www.reddit.com/r/bapcsalescanada/new/.rss`
- Probe: HTTP 429 during research.
- Expected fit: Canadian deals only; likely not useful for US-focused buying.

## Poor Fits Or Adapter Candidates

### TechBargains

- URLs probed:
  - `https://www.techbargains.com/rss.xml`
  - `https://www.techbargains.com/rss`
  - `https://www.techbargains.com/categories/computers`
- Probe: HTTP 403 Cloudflare challenge.
- Current fit: poor. Do not add to RSS config.

### DealNews

- URL probed: `https://www.dealnews.com/rss.xml`
- Probe: HTTP 404 with maintenance page.
- Current fit: poor until a stable feed URL is found.

### Micro Center

- URL probed: `https://www.microcenter.com/search/search_results.aspx?Ntt=rtx%205080`
- Probe: HTTP 403 Cloudflare challenge.
- Current fit: poor for direct tracking.
- Practical alternative: Slickdeals and r/buildapcsales often surface Micro Center deals.

### B&H Photo Video

- URL probed: `https://www.bhphotovideo.com/c/search?q=rtx%205080&sts=ma`
- Probe: HTTP 403 Cloudflare challenge.
- Current fit: poor for direct tracking.

### Best Buy

- URL probed: `https://www.bestbuy.com/site/searchpage.jsp?st=rtx+5080`
- Probe: request timeout from this environment.
- Current fit: poor for direct tracking.

### Woot

- URLs probed:
  - `https://www.woot.com/feed` returned HTTP 404.
  - `https://www.woot.com/blog/rss.aspx` returned HTTP 404.
  - `https://www.woot.com/category/computers` returned HTTP 200 HTML with no RSS autodiscovery found.
- Current fit: needs an adapter or a third-party feed.

### PCPartPicker

- URL probed: `https://pcpartpicker.com/products/video-card/`
- Probe: HTTP 200 HTML with no RSS autodiscovery found.
- Current fit: useful for manual price context, not a direct RSS alert source.

## Recommended Additions

Start with source-specific Slickdeals query feeds and Newegg query feeds. Keep r/buildapcsales as the primary source.

Example source additions:

```toml
[[sources]]
name = "slickdeals-5080"
url = "https://slickdeals.net/newsearch.php?searcharea=deals&searchin=first&q=5080&rss=1"

[[sources]]
name = "newegg-5080"
url = "https://www.newegg.com/d/Product/RSS?Submit=ENE&IsNodeId=1&Description=rtx%205080"
```

Example source-specific rules:

```toml
[[rules]]
name = "sd-rtx-5080"
sources = ["slickdeals-5080"]
include_any = ["rtx 5080", "5080"]
exclude_any = ["laptop", "desktop", "gaming pc", "prebuilt", "refurb", "omen", "aegis", "radiant", "vector"]

[[rules]]
name = "newegg-rtx-5080"
sources = ["newegg-5080"]
include_any = ["rtx 5080", "5080"]
exclude_any = ["refurbished", "renewed"]
```

Avoid adding every query at once. Add one or two, run `--dry-run`, then tune excludes before enabling notifications.