import sys
from termcolor import cprint
import time

import MV2.helpers.PulsarREST as PulsarREST


def waiting4namespace(cfg):

    while True:
        namespaces = PulsarREST.get_namespaces(pulsar_admin_url=cfg.pulsar_admin_url,
                                               tenant=cfg.tenant)

        if f"public/{cfg.market_uuid}" not in namespaces:
            cprint(f"Wait for market namespace", "magenta")
            sys.stdout.flush()
            time.sleep(1)
        else:
            break
    return False
