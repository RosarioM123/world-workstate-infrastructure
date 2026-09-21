"""Entry point for the synthetic logistics demo (moved from the repo root).

Run from this directory::

    python ingest.py            # live fetch -> commit one weather-driven intent
    python ingest.py --dry-run  # live fetch -> show the intent, write nothing
    python ingest.py --demo     # live fetch -> commit intent -> rogue agent
                                #   tries to break the rules and gets blocked

See README.md in this directory: this is a synthetic stress-test domain,
not the product demo.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from weather_ingest import main

if __name__ == "__main__":
    main()
