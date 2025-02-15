import asyncio
import time

import psutil
import pyfiglet
from colorama import Fore

from modules import config, cloudflare, webhook

config = config.Config()
cloudflare = cloudflare.Cloudflare()
webhook = webhook.Webhook()

PREFIX = f"{Fore.RED}[\033[38;5;208mNoAttack{Fore.RED}]{Fore.RESET} "


def get_network_speed(duration=1):
    io_counters_start = psutil.net_io_counters()

    time.sleep(duration)

    io_counters_end = psutil.net_io_counters()

    bytes_received = io_counters_end.bytes_recv - io_counters_start.bytes_recv
    bytes_sent = io_counters_end.bytes_sent - io_counters_start.bytes_sent

    mb_received_per_sec = bytes_received / duration / 1024 / 1024
    mb_sent_per_sec = bytes_sent / duration / 1024 / 1024
    return mb_received_per_sec, mb_sent_per_sec


async def main():
    if not config.get("CLOUDFLARE", "ZONE_IDS"):
        print(f"{PREFIX}No Cloudflare zones found.")
        exit(1)

    while True:
        try:
            mb_received_per_sec, mb_sent_per_sec = get_network_speed()
            print(f"{PREFIX}Received: {mb_received_per_sec:.2f} MB/s, Sent: {mb_sent_per_sec:.2f} MB/s")

            if mb_received_per_sec > config.get("SETTINGS", "MAX_INCOMING_TRAFFIC_MB"):
                print(f"{PREFIX}Incoming traffic exceeded {config.get('SETTINGS', 'MAX_INCOMING_TRAFFIC_MB')} MB/s")

                for zone_id in config.get("CLOUDFLARE", "ZONE_IDS"):
                    try:
                        zone = await cloudflare.getZone(zone_id)
                        zone_name = zone["result"]["name"]

                        under_attack_mode = await cloudflare.getZoneUnderAttack(zone_id)
                        if under_attack_mode["result"]["value"] == "under_attack":
                            continue

                        print(f"{PREFIX}Activating Under Attack Mode for {zone_name}")

                        if config.get("SETTINGS", "LOGGING") and config.get("SETTINGS", "WEBHOOK"):
                            await webhook.send(
                                message=f"Activating Under Attack Mode for {zone_name}",
                                color=0xFF0000
                            )

                        await cloudflare.setZoneUnderAttack(zone_id, True)

                    except Exception as e:
                        print(f"{PREFIX}Error handling Cloudflare zone {zone_id}: {e}")

            else:
                print(f"{PREFIX}Incoming traffic is normal.")
                for zone_id in config.get("CLOUDFLARE", "ZONE_IDS"):
                    try:
                        zone = await cloudflare.getZone(zone_id)
                        zone_name = zone["result"]["name"]

                        under_attack_mode = await cloudflare.getZoneUnderAttack(zone_id)
                        if under_attack_mode["result"]["value"] == "essentially_off":
                            continue

                        print(f"{PREFIX}Deactivating Under Attack Mode for {zone_name}")

                        if config.get("SETTINGS", "LOGGING") and config.get("SETTINGS", "WEBHOOK"):
                            await webhook.send(
                                message=f"Deactivating Under Attack Mode for {zone_name}",
                                color=0x00FF00
                            )

                        await cloudflare.setZoneUnderAttack(zone_id, False)

                    except Exception as e:
                        print(f"{PREFIX}Error processing Cloudflare zone {zone_id}: {e}")

        except Exception as e:
            print(f"{PREFIX}Error encountered in main loop: {e}")

        # Sleep for interval
        await asyncio.sleep(config.get("SETTINGS", "CHECK_INTERVAL") or 60)



if __name__ == "__main__":

    print("\033[38;5;208m" + pyfiglet.figlet_format('NoAttack', font='doom') + Fore.RESET)

    if not config.configExists():
        config.createConfig()
        print(f"{PREFIX}Config file created.")

    print(f"{PREFIX}Config file loaded.")
    asyncio.run(main())
