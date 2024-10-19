import json
import logging
from pathlib import Path
from typing import Optional

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from sqlalchemy.sql.expression import func

from shared.sql import models, schemas
from shared.sql.database import engine
from shared.utils.paths import rmdir

# TODO: Should have a generic Job class (move to utils) and create a subclass for ETL related functionality
# TODO: Should static methods be abstracted? And should methods such as update_status/get_status be static/abstracted
#  also?


class Job:
    completed_dir = "completed"
    failed_dir = "failed"
    request_file = "request.json"

    def __init__(
        self,
        request: schemas.Request | schemas.RequestCreate,
        reset: bool = False,
        save_path: Optional[Path] = None,
    ):
        if isinstance(request, schemas.RequestCreate):
            self.request = self._post_request(request)
        else:
            # Make sure request is up-to-date
            self.request = self._pull_request(request.id)

        if save_path is None:
            save_path = self.request.get_save_path()

        self.logger = self.request.adapt_logger(logging.getLogger(__name__))

        if reset and save_path.exists():
            rmdir(save_path)

        self.save_path = save_path
        self.url = self.request.get_url()

        self.setup_path()

    @staticmethod
    def _pull_request(request_id):
        with Session(engine) as session:
            request_db = session.query(models.Request).filter_by(id=request_id).first()
            if request_db is None:
                raise ValueError(
                    f"No job found for request id: {request_id}, ensure job has been created"
                )

        return schemas.Request(**request_db.__dict__)

    def setup_path(self):
        self.save_path.mkdir(exist_ok=True, parents=True)
        (self.save_path / self.completed_dir).mkdir(exist_ok=True)
        (self.save_path / self.failed_dir).mkdir(exist_ok=True)

        request_path = self.save_path / self.request_file

        if not request_path.exists():
            self.save(request_path)

    def get_status(self):
        with Session(engine) as session:
            status = (
                session.query(models.Request.status)
                .filter_by(id=self.request.id)
                .scalar()
            )

        return status

    def update_status(self, status: str):
        with Session(engine) as session:
            session.query(models.Request).filter_by(id=self.request.id).update(
                {"status": status}
            )
            session.commit()

        self.request.status = status
        self.logger.info(f"Status updated: {status.upper()}")

    def fail(self):
        self.update_status("failed")

    def success(self):
        self.update_status("finished")

    def get_request_from_file(self):
        with Path.open(self.save_path / self.request_file, "r") as f:
            request = schemas.Request(**json.load(f))

        return request

    def save(self, path: Optional[Path] = None):
        if path is None:
            path = self.save_path

        with Path.open(path, "w") as f:
            json.dump(self.request.dict(), f, indent=2, default=str)

    def remove_path(self):
        if self.save_path.exists():
            rmdir(self.save_path)

    @staticmethod
    def id_from_dir(directory: Path):
        return int(directory.name.split("-")[-1].split("id")[-1])

    @staticmethod
    def from_dir(path: Path, *args, **kwargs):
        request_id = Job.id_from_dir(path)

        with Session(engine) as session:
            request_db = session.query(models.Request).filter_by(id=request_id).first()

        if request_db is not None:
            request = schemas.Request(**request_db.__dict__)
            # Passing save_path as directory path to ensure saving to input directory
            return Job(request=request, save_path=path, *args, **kwargs)


def post_request_to_db(request: schemas.RequestCreate):
    with Session(engine) as session:
        request_db = models.Request(**request.dict())

        try:
            session.add(request_db)
            session.commit()
            session.refresh(request_db)

        except IntegrityError:
            session.rollback()

            # Should not have to do this, but workaround for (sqlalchemy) bug that tries to insert from pk=1 again
            last_id = session.query(func.max(models.Request.id)).first()
            if last_id is not None:
                request_db.id = last_id[0] + 1

                session.add(request_db)
                session.commit()
                session.refresh(request_db)

    return schemas.Request(**request_db.__dict__)


def update_request_status(request: models.Request, status: str):
    with Session(engine) as session:
        session.query(models.Request).filter_by(id=request.id).update(
            {"status": status.upper()}
        )
        session.commit()
