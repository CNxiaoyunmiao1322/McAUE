from dataclasses import dataclass
from typing import Optional


@dataclass
class DownloadTask:
    url: str
    save: str
    sha256: Optional[str] = None
