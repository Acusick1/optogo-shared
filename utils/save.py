import pickle
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from packages.config import global_settings


def save_local(data, save_path: Path, filename: str, stamp=False, uid=False):
    if stamp:
        filename = "_".join(
            [filename, str(datetime.now(timezone.utc).timestamp()).replace(".", "-")]
        )
    if uid:
        filename = "_".join([filename, str(uuid4())])

    file_path = (save_path / filename).with_suffix(".p")

    with file_path.open("wb") as f:
        pickle.dump(data, f)

    return file_path


def save_s3(*args, **kwargs):
    raise NotImplementedError


save = save_s3 if global_settings.s3_bucket else save_local
