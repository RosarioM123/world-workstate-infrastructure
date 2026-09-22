"""WORLD client SDK, packaged.

Layout:
    world_sdk.client  - WorldClient: offline-first client over a local ledger
    world_sdk.ledger  - LocalLedger: client-owned hash-chained ledger in the
                        same entry format as the server ledger
    world_sdk.index   - EmbeddingSidecar: client-owned sqlite3 sidecar for
                        embedding vectors and the timestamp index

The SDK is stdlib-only (plus sqlite3, which ships with Python). It reuses
the server's pure policy function (``check_constraints``) and seed constants
so client-side validation can never drift from the server's verdicts, but it
never imports the API layer and never needs a running server. The timestamp
and embedding indexes live in a separate sidecar file, never in the ledger,
so they stay out of the integrity path: ``verify_chain()`` sees only the
hash chain.
"""

from world_sdk.client import WorldClient
from world_sdk.index import EmbeddingSidecar
from world_sdk.ledger import LocalLedger

__version__ = "0.1.0"

__all__ = ["EmbeddingSidecar", "LocalLedger", "WorldClient"]
