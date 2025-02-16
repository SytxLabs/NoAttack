import asyncio
import sys
import time

import aiohttp
import psutil
import pyfiglet
from colorama import Fore

from modules import cloudflare, config, webhook

config = config.Config()
cloudflare = cloudflare.Cloudflare()
webhook = webhook.Webhook()

PREFIX = f"{Fore.RED}[\033[38;5;208mNoAttack{Fore.RED}]{Fore.RESET} "


def get_network_speed(duration=1):
    """
    Measure network speed over a given duration.
    """
    io_counters_start = psutil.net_io_counters()

    time.sleep(duration)

    io_counters_end = psutil.net_io_counters()

    bytes_received = io_counters_end.bytes_recv - io_counters_start.bytes_recv
    bytes_sent = io_counters_end.bytes_sent - io_counters_start.bytes_sent

    mb_received_per_sec = bytes_received / duration / 1024 / 1024
    mb_sent_per_sec = bytes_sent / duration / 1024 / 1024
    return mb_received_per_sec, mb_sent_per_sec


async def main():
    """
    Main function to monitor network speed and manage Cloudflare zones.
    """
    if not config.get("CLOUDFLARE", "ZONE_IDS"):
        print(f"{PREFIX}No Cloudflare zones found.")
        sys.exit(1)

    while True:
        try:
            mb_received_per_sec, mb_sent_per_sec = get_network_speed()
            print(f"{PREFIX}Received: {mb_received_per_sec:.2f} MB/s, "
                  f"Sent: {mb_sent_per_sec:.2f} MB/s")

            if mb_received_per_sec > config.get("SETTINGS", "MAX_INCOMING_TRAFFIC_MB"):
                print(f"{PREFIX}Incoming traffic exceeded "
                      f"{config.get('SETTINGS', 'MAX_INCOMING_TRAFFIC_MB')} MB/s")

                for zone_id in config.get("CLOUDFLARE", "ZONE_IDS"):
                    await handle_zone(zone_id, True)

            else:
                print(f"{PREFIX}Incoming traffic is normal.")
                for zone_id in config.get("CLOUDFLARE", "ZONE_IDS"):
                    await handle_zone(zone_id, False)

        except (aiohttp.ClientError, ValueError) as e:
            print(f"{PREFIX}Error encountered in main loop: {e}")

        await asyncio.sleep(config.get("SETTINGS", "CHECK_INTERVAL") or 60)


async def handle_zone(zone_id, under_attack):
    """
    Handle Cloudflare zone based on the traffic condition.
    """
    try:
        zone = await cloudflare.get_zone(zone_id)
        zone_name = zone["result"]["name"]

        under_attack_mode = await cloudflare.get_zone_under_attack(zone_id)
        if under_attack and under_attack_mode["result"]["value"] != "under_attack":
            print(f"{PREFIX}Activating Under Attack Mode for {zone_name}")
            await set_zone_under_attack(zone_id, zone_name, True)
        elif not under_attack and under_attack_mode["result"]["value"] != "essentially_off":
            print(f"{PREFIX}Deactivating Under Attack Mode for {zone_name}")
            await set_zone_under_attack(zone_id, zone_name, False)

    except (aiohttp.ClientError, ValueError) as e:
        print(f"{PREFIX}Error handling Cloudflare zone {zone_id}: {e}")


async def set_zone_under_attack(zone_id, zone_name, under_attack):
    """
    Set the Cloudflare zone under attack mode.
    """
    if config.get("SETTINGS", "LOGGING") and config.get("SETTINGS", "WEBHOOK"):
        await webhook.send(
            message=f"{'Activating' if under_attack else 'Deactivating'} "
                    f"Under Attack Mode for {zone_name}",
            color=0xFF0000 if under_attack else 0x00FF00
        )

    await cloudflare.set_zone_under_attack(zone_id, under_attack)


if __name__ == "__main__":
    print("\033[38;5;208m" + pyfiglet.figlet_format('NoAttack', font='doom') + Fore.RESET)

    if not config.config_exists():
        config.create_config()
        print(f"{PREFIX}Config file created.")

    print(f"{PREFIX}Config file loaded.")
    asyncio.run(main())
