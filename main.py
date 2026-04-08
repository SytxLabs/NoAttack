import asyncio
import logging
import sys

import psutil
import pyfiglet
from colorama import Fore

from modules.config import get_config, ConfigNotFoundError
from modules.cloudflare import Cloudflare
from modules.webhook import Webhook
from modules.redis import RedisCache

logger = logging.getLogger("noattack")

PREFIX = f"{Fore.RED}[\033[38;5;208mNoAttack{Fore.RED}]{Fore.RESET} "


async def get_network_speed():
    """Measure incoming and outgoing traffic in MB/s over 1 second."""
    snap1 = psutil.net_io_counters()
    await asyncio.sleep(1)
    snap2 = psutil.net_io_counters()
    recv = (snap2.bytes_recv - snap1.bytes_recv) / 1024 / 1024
    sent = (snap2.bytes_sent - snap1.bytes_sent) / 1024 / 1024
    return recv, sent


async def handle_zone(cloudflare, webhook, zone_id, under_attack):
    """Activate or deactivate Under Attack mode for a zone if the state needs to change."""
    zone_name = await cloudflare.get_zone(zone_id)
    if zone_name is None:
        return

    currently_attacking = await cloudflare.get_zone_under_attack(zone_id)
    if currently_attacking is None:
        return

    if under_attack and not currently_attacking:
        logger.info("Activating Under Attack Mode for %s", zone_name)
        if await cloudflare.set_zone_under_attack(zone_id, True):
            await webhook.send("Under Attack Activated", zone_name, color=0xFF0000)

    elif not under_attack and currently_attacking:
        logger.info("Deactivating Under Attack Mode for %s", zone_name)
        if await cloudflare.set_zone_under_attack(zone_id, False):
            await webhook.send("Under Attack Deactivated", zone_name, color=0x00FF00)


async def main():
    """Main monitoring loop."""
    config = get_config()
    cloudflare = Cloudflare()
    webhook = Webhook()
    redis_cache = RedisCache()

    zone_ids = config.get("CLOUDFLARE", "ZONE_IDS")
    if not zone_ids:
        logger.critical("No zone IDs configured.")
        sys.exit(1)

    if not await redis_cache.check():
        logger.critical("Cannot connect to Redis.")
        sys.exit(1)

    check_interval = config.get("SETTINGS", "CHECK_INTERVAL") or 60
    threshold = config.get("SETTINGS", "MAX_INCOMING_TRAFFIC_MB")
    logger.info("Started | interval: %ds | threshold: %s MB/s | zones: %d",
                check_interval, threshold, len(zone_ids))

    try:
        while True:
            try:
                if await redis_cache.is_under_attack():
                    remaining = await redis_cache.ttl()
                    logger.info("Cooldown active, %ds remaining", remaining)
                else:
                    recv, sent = await get_network_speed()
                    logger.info("Traffic – recv: %.2f MB/s  sent: %.2f MB/s", recv, sent)

                    if recv > threshold:
                        logger.warning("Traffic %.2f MB/s exceeded threshold %s MB/s",
                                       recv, threshold)
                        for zone_id in zone_ids:
                            await handle_zone(cloudflare, webhook, zone_id, True)
                        await redis_cache.set_under_attack()
                    else:
                        for zone_id in zone_ids:
                            await handle_zone(cloudflare, webhook, zone_id, False)

            except Exception as exc:  # pylint: disable=broad-except
                logger.error("Error in main loop: %s", exc)

            await asyncio.sleep(max(0, check_interval - 1))
    finally:
        await cloudflare.close()


if __name__ == "__main__":
    print("\033[38;5;208m" + pyfiglet.figlet_format("NoAttack", font="doom") + Fore.RESET)

    try:
        get_config()
    except ConfigNotFoundError as config_error:
        print(f"{PREFIX}{config_error}")
        sys.exit(1)

    logging.basicConfig(
        level=logging.INFO,
        format="[%(asctime)s] [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    asyncio.run(main())
