from dataclasses import dataclass, field
from datetime import datetime
from dataclasses_json import dataclass_json

@dataclass_json
@dataclass(frozen=True)
class TwitterBackupJob:
    twitter_account: str
    backup_date: datetime = field(default_factory=datetime.now)
    