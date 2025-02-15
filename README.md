# NoAttack

NoAttack is a tool designed to monitor incoming network traffic and automatically enable or disable Cloudflare's "Under Attack" mode based on defined thresholds. It integrates various components, including Redis, Cloudflare, and a Discord Webhook for notification purposes.

---

## Features
- Monitors incoming network traffic in real time.
- Automatically enables "Under Attack" mode in Cloudflare when traffic exceeds a predefined threshold.
- Sends alerts via a Discord webhook during critical events.
- Includes Redis for caching operations.

---

## Installation

### Requirements
Before starting, make sure the following are installed:
- **Docker** and **Docker Compose**
- **Python 3.12** or later (if not using Docker Compose)

### Steps
1. **Clone the repository:**
   ```bash
   git clone https://github.com/SytxLabs/NoAttack.git
   cd NoAttack
   ```

2. **Setup configuration:**
   Edit the `config.yaml` file to include your Cloudflare credentials and other settings:
     ```yaml
     CLOUDFLARE:
       API_KEY: "<Your Cloudflare API Key>"
       EMAIL: "<Your Email Address>"
       ZONE_IDS: [
         "<Zone ID 1>",
         "<Zone ID 2>"
       ]
     REDIS:
       HOST: "<Redis Host>"
       PASSWORD: "<Redis Password>"
       PORT: 6379
     SETTINGS:
       CHECK_INTERVAL: 60   # Monitoring interval in seconds
       MAX_INCOMING_TRAFFIC_MB: 50  # Maximum threshold for incoming traffic
       WEBHOOK: "<Discord Webhook URL>"
     ```

3. **Build and run using Docker Compose:**
   ```bash
   docker-compose up --build
   ```

4. **Install dependencies manually (if not using Docker Compose):**
   - Install dependencies via pip:
     ```bash
     pip install -r requirements.txt
     ```
   - Run the script:
     ```bash
     python main.py
     ```

---

## Usage

NoAttack monitors incoming network traffic and takes automated actions based on the configuration.

### Key Functionalities
1. **Monitor Traffic:**
   - Logs real-time data about incoming and outgoing traffic in MB/s.
   
2. **Activate Cloudflare "Under Attack" Mode:**
   - If traffic exceeds the `MAX_INCOMING_TRAFFIC_MB` limit, Cloudflare's "Under Attack" mode is activated for all specified zones.

3. **Deactivate Cloudflare "Under Attack" Mode:**
   - When traffic drops below the threshold, the "Under Attack" mode is deactivated.

4. **Notifications:**
   - Sends real-time updates regarding the activation or deactivation of the "Under Attack" mode to the specified Discord webhook.

### Running the Application
- Simply run the application using:
  ```bash
  docker-compose up
  ```
  or
  ```bash
  python main.py
  ```

### Logs
- If logging is enabled (`SETTINGS.LOG: true`), network activity and Cloudflare actions will be printed in the console.

### Additional Notes
- **Redis Integration:** Used for caching to optimize performance.
- **Discord Webhook:** Sends notifications about changes to ensure visibility for administrators.

---

## Configuration Details

| Key                          | Description                                                   | Example                          |
|------------------------------|---------------------------------------------------------------|----------------------------------|
| `SETTINGS.MAX_INCOMING_TRAFFIC_MB` | Maximum allowed incoming traffic before enabling Cloudflare's "Under Attack" mode. | `50`                            |
| `SETTINGS.CHECK_INTERVAL`    | Time interval (in seconds) between traffic checks.            | `60`                            |
| `SETTINGS.WEBHOOK`           | Discord webhook URL for notifications.                       | `https://discord.com/api/...`   |
| `CLOUDFLARE.API_KEY`         | Your Cloudflare API key.                                      | `example_cloudflare_api_key`    |
| `CLOUDFLARE.ZONE_IDS`        | List of Cloudflare Zone IDs to manage.                       | `[zone_1_id, zone_2_id]`        |
| `REDIS.HOST`                 | Redis host address.                                           | `127.0.0.1`                     |
| `REDIS.PASSWORD`             | Redis password (if any).                                     | `redis_password`                |
| `REDIS.PORT`                 | Redis port number.                                           | `6379`                          |

---

## Development

### Docker Development
For development purposes:
- Add changes to the application code and rebuild the Docker container:
  ```bash
  docker-compose up --build
  ```

### Local Development
- After modifying the code and or `config.yaml`, run the Python application:
   ```bash
   python main.py
   ```

---

## Troubleshooting

1. **Cloudflare API Errors:**
   - Ensure your API key and Zone IDs are correct in `config.yaml`.
   - Verify your internet connection.