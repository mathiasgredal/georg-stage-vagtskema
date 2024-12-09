import json
import dataclasses
from datetime import datetime, timedelta
from georgstage.model import Opgave

class EnhancedJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if dataclasses.is_dataclass(obj):
            return dataclasses.asdict(obj)
        if isinstance(obj, datetime):
            return obj.isoformat()
        else:
            return super().default(obj)

