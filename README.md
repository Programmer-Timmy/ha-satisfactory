[![gitlocalized ](https://gitlocalize.com/repo/10697/whole_project/badge.svg)](https://gitlocalize.com/repo/10697?utm_source=badge)

![Satisfactory Icon](/custom_components/satisfactory/brand/icon@2x.png)

# Ha-satisfactory

Ha-Satisfactory is a Home Assistant integration for monitoring a Satisfactory Dedicated Server. It uses the [Satisfactory Dedicated Server API](https://satisfactory.wiki.gg/wiki/Dedicated_servers/HTTPS_API) to poll the server state and exposes the data as sensors in Home Assistant.

## Installation

### HACS (recommended)

1. Open HACS in Home Assistant.
2. Go to **Integrations** → click the three-dot menu → **Custom repositories**.
3. Add `https://github.com/Programmer-Timmy/ha-satisfactory` with category **Integration**.
4. Search for **Satisfactory** and click **Download**.
5. Restart Home Assistant.

### Manual

1. Download the latest release from [GitHub](https://github.com/Programmer-Timmy/ha-satisfactory/releases).
2. Copy the `custom_components/satisfactory` folder into your Home Assistant `config/custom_components/` directory.
3. Restart Home Assistant.

## Configuration

Go to **Settings → Devices & Services → Add Integration** and search for **Satisfactory**.

| Parameter | Description | Default |
|---|---|---|
| Host | IP address or hostname of the Satisfactory Dedicated Server | — |
| Port | HTTPS API port of the server | `7777` |
| Admin password | The administrator password of the server | — |
| Disable SSL verification | Skip SSL certificate verification (recommended for self-signed certs) | `true` |

## Supported sensors

| Sensor | Description | Unit |
|---|---|---|
| Connected players | Number of players currently on the server | players |
| Player limit | Maximum number of players allowed | players |
| Tech tier | Current research tech tier | — |
| Average tick rate | Server tick rate | ticks/s |
| Total game duration | Total hours the game has been running | h |
| Active session | Name of the active game session | — |
| Game phase | Current game phase | — |

## Removal

1. Go to **Settings → Devices & Services**.
2. Find the **Satisfactory** integration and click **Delete**.
3. Optionally remove the `custom_components/satisfactory` folder and restart Home Assistant.

## Disclaimer

This Home Assistant integration is an unofficial, community-made project.  
It is **not created, affiliated with, or endorsed by Coffee Stain Studios**, the developers of Satisfactory.
