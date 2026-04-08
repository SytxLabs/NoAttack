# NoAttack

NoAttack monitors incoming network traffic and automatically toggles Cloudflare's "Under Attack" mode when traffic exceeds a defined threshold. Notifications are sent via Discord webhook.

---

## Features

- Monitors incoming and outgoing traffic in real time
- Automatically enables "Under Attack" mode when traffic exceeds `MAX_INCOMING_TRAFFIC_MB`
- 5-minute cooldown after activation (configurable via `ATTACK_COOLDOWN_TTL`)
- Sends Discord notifications on mode changes
- Redis for cooldown state management

---

## Requirements

- **Docker & Docker Compose** (recommended)
- **Python 3.12+** (for local usage)

---

## Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/SytxLabs/NoAttack.git
   cd NoAttack
   ```

2. On first run, `config.yaml` is created automatically. Fill in your credentials:
   ```yaml
   CLOUDFLARE:
     API_KEY: "<Your Cloudflare Bearer Token>"
     EMAIL: "<Your Email>"
     ZONE_IDS:
       - "<Zone ID>"

   REDIS:
     HOST: localhost
     PORT: 6379
     PASSWORD: ""

   SETTINGS:
     CHECK_INTERVAL: 60
     MAX_INCOMING_TRAFFIC_MB: 50
     ATTACK_COOLDOWN_TTL: 300
     WEBHOOK: "<Discord Webhook URL>"
     LOGGING: true
   ```

3. Run with Docker Compose:
   ```bash
   docker compose up --build
   ```

   Or locally:
   ```bash
   pip install -r requirements.txt
   python main.py
   ```

---

## Configuration

| Key | Description | Default |
|-----|-------------|---------|
| `SETTINGS.MAX_INCOMING_TRAFFIC_MB` | Incoming traffic threshold in MB/s | `50` |
| `SETTINGS.CHECK_INTERVAL` | Seconds between traffic checks | `60` |
| `SETTINGS.ATTACK_COOLDOWN_TTL` | Cooldown duration in seconds after activation | `300` |
| `SETTINGS.WEBHOOK` | Discord webhook URL for notifications | `""` |
| `SETTINGS.LOGGING` | Enable Discord notifications | `true` |
| `CLOUDFLARE.API_KEY` | Cloudflare Bearer token | |
| `CLOUDFLARE.ZONE_IDS` | List of zone IDs to manage | |
| `REDIS.HOST` | Redis host | `localhost` |
| `REDIS.PORT` | Redis port | `6379` |
| `REDIS.PASSWORD` | Redis password | `""` |

---

## Credits

Inspired by [guidedhacking/cfautouam](https://github.com/guidedhacking/cfautouam).
