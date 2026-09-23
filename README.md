# IPTV Curated

Curated IPTV-org playlists for Stremio / NexoTV.

## Playlists

- Mexico: `playlists/mexico.m3u`
- USA: `playlists/usa.m3u`

These files are generated from IPTV-org's public country playlists, but keep only
the channels selected in `config/mexico.json` and `config/usa.json`.

## NexoTV URLs

After this repository is public at `fer98morales/iptv-curated`, use:

```text
https://raw.githubusercontent.com/fer98morales/iptv-curated/main/playlists/mexico.m3u
```

```text
https://raw.githubusercontent.com/fer98morales/iptv-curated/main/playlists/usa.m3u
```

Paste either URL into NexoTV's M3U playlist field.

## Automatic refresh

GitHub Actions runs `scripts/refresh.py` every day and can also be run manually
from the Actions tab.

The script downloads:

- `https://iptv-org.github.io/iptv/countries/mx.m3u`
- `https://iptv-org.github.io/iptv/countries/us.m3u`

It matches channels by `tvg-id`, so IPTV-org can change a stream URL, logo, or
channel name without requiring you to rebuild the curated playlist manually.

If an upstream channel disappears, the workflow prints a warning and simply
omits that channel until it returns or you update the whitelist.

## Edit the selection

Each config item looks like:

```json
{
  "tvg_id": "ADN40.mx@SD",
  "group": "Mexico | News",
  "name": "ADN 40 (720p)"
}
```

To remove a channel, delete its object from the appropriate JSON config.
To add a channel, add its IPTV-org `tvg-id`, choose a group, then run the
workflow manually.

## Current curated size

- Mexico: 48 channels
- USA: 108 channels

Source project: IPTV-org
