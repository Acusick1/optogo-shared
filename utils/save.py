import pickle
from datetime import datetime
from pathlib import Path
from uuid import uuid4

from packages.crawler.config import settings


def save_local(data, save_path: Path, filename: str, stamp=False, uid=False):
    if stamp:
        filename = "_".join(
            [filename, str(datetime.utcnow().timestamp()).replace(".", "-")]
        )
    if uid:
        filename = "_".join([filename, str(uuid4())])

    file_path = (save_path / filename).with_suffix(".p")

    with file_path.open("wb") as f:
        pickle.dump(data, f)

    return file_path


def save_s3():
    raise NotImplementedError


save = save_s3 if settings.s3_bucket else save_local
