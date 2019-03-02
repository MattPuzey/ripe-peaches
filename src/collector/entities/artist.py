from typing import List
from dataclasses import dataclass
from dataclasses_json import dataclass_json
from src.collector.entities.release import Release

@dataclass_json
@dataclass
class Artist:
    id: str
    name: str
    releases: List[Release]
