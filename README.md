# IPTV Curated

Curated IPTV-org playlists for Stremio / NexoTV.

## Playlists

- Mexico: `playlists/mexico.m3u`
- USA: `playlists/usa.m3u`
- Sports (English and Spanish): `playlists/sports.m3u`

These files are generated from IPTV-org's public country playlists, but keep only
the channels selected in `config/mexico.json` and `config/usa.json`.
Sports uses the public sports category playlist and `config/sports.json`.

## NexoTV URLs

Use these public playlist URLs:

```text
https://raw.githubusercontent.com/fer98morales/iptv-curated/main/playlists/mexico.m3u
```

```text
https://raw.githubusercontent.com/fer98morales/iptv-curated/main/playlists/usa.m3u
```

```text
https://raw.githubusercontent.com/fer98morales/iptv-curated/main/playlists/sports.m3u
```

Paste a URL into NexoTV's M3U playlist field.

## Automatic refresh

GitHub Actions runs `scripts/refresh.py` every day and can also be run manually
from the Actions tab.

The script downloads:

- `https://iptv-org.github.io/iptv/countries/mx.m3u`
- `https://iptv-org.github.io/iptv/countries/us.m3u`
- `https://iptv-org.github.io/iptv/categories/sports.m3u`

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
- Sports: 38 channels

## Sports selection

The sports whitelist focuses on recognizable English and Spanish feeds, grouped
by sport. Language metadata was checked against IPTV-org's feeds API. Separate
English and Spanish editions are intentional; duplicate regional/quality feeds,
general entertainment channels, and feeds marked Geo-blocked or Not 24/7 were
excluded at selection time.

On 2026-09-23, all 38 selected stream URLs returned HTTP 200 and an HLS playlist
from the setup machine. This checks the initial playlist only, not video segments,
audio language, full playback, or availability from NexoTV's servers. Some channels
show highlights and replays; inclusion does not promise live coverage of any event.
The daily refresh updates URLs and metadata; it does not perform playback checks.

Eight candidates failed the initial check and were left out: Claro Sports,
beIN SPORTS XTRA en Espanol, ESPN Deportes, TyC Sports, Real Madrid TV Spanish,
NFL Network, Racer Network, and Golf Channel Latin America. They can be reconsidered
later if their upstream streams recover.

| Group | Channels |
| --- | --- |
| General & News | Azteca Deportes Network (1080p), beIN SPORTS XTRA (1080p), CBS Sports HQ (720p), NBC Sports NOW (1080p), Fubo Sports Network (1080p), Fox Sports 1 (720p), Fox Deportes (720p), Pluto TV Deportes, Stadium (720p), Teledeporte |
| Football | CBS Sports Golazo Network (720p), FIFA+ (720p), FIFA+ Hispanic America (720p), FIFA+ Women (720p), Real Madrid TV English |
| US Leagues & College | NBA TV (1080p), NFL Channel (720p), MLB (720p), NHL Network (1080p), ACC Digital Network (1080p), ESPNU HD (720p), Pac-12 Insider (1080p) |
| Motorsports & Action | Rally TV (1080p), NHRA TV (1080p), FloRacing (1080p), Red Bull TV US (1080p), Red Bull TV ES (1080p), FUEL TV (1080p) |
| Combat Sports | DAZN Combat (684p), Bellator MMA, PFL MMA (720p), FITE 24/7 (1080p), Swerve Combat (1080p) |
| Tennis & Golf | Tennis Channel (1080p), Tennis Channel 2 (1080p), PGA Tour (1080p) |
| More Sports | Willow Sports (1080p), ESPN8: The Ocho (1080p) |

Source project: [IPTV-org](https://github.com/iptv-org/iptv)
