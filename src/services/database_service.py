import os
import re
from typing import List, Dict, Optional
from sqlalchemy import or_
from .models import init_engine, get_session, IODisc, IOReal, IOInt, IOAccess
from .csv_importer import CSVImporter, ImportResult


class DatabaseService:
    def __init__(self, db_path: str = "data/keywords.db"):
        self.db_path = db_path
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self.engine = init_engine(self.db_path)

    def _get_session(self):
        return get_session(self.engine)

    def import_from_csv(self, csv_path: str, mode: str = 'replace') -> ImportResult:
        session = self._get_session()
        try:
            importer = CSVImporter(session)
            return importer.import_from_csv(csv_path, mode)
        finally:
            session.close()

    def search_io_disc(self, text: str) -> List[Dict]:
        if not text:
            return []
        session = self._get_session()
        try:
            pattern = f'%{text}%'
            records = session.query(IODisc).filter(
                or_(
                    IODisc.tag_name.like(pattern),
                    IODisc.comment.like(pattern),
                    IODisc.item_name.like(pattern)
                )
            ).all()
            return [self._record_to_dict(r) for r in records]
        finally:
            session.close()

    def search_io_real(self, text: str) -> List[Dict]:
        if not text:
            return []
        session = self._get_session()
        try:
            pattern = f'%{text}%'
            records = session.query(IOReal).filter(
                or_(
                    IOReal.tag_name.like(pattern),
                    IOReal.comment.like(pattern),
                    IOReal.item_name.like(pattern)
                )
            ).all()
            return [self._record_to_dict(r) for r in records]
        finally:
            session.close()

    def get_all_io_disc(self) -> List[Dict]:
        session = self._get_session()
        try:
            records = session.query(IODisc).order_by(IODisc.tag_name).all()
            return [self._record_to_dict(r) for r in records]
        finally:
            session.close()

    def get_all_io_real(self) -> List[Dict]:
        session = self._get_session()
        try:
            records = session.query(IOReal).order_by(IOReal.tag_name).all()
            return [self._record_to_dict(r) for r in records]
        finally:
            session.close()

    def get_io_disc_by_tagname(self, tag_name: str) -> Optional[Dict]:
        session = self._get_session()
        try:
            record = session.query(IODisc).filter(IODisc.tag_name == tag_name).first()
            return self._record_to_dict(record) if record else None
        finally:
            session.close()

    def get_io_real_by_tagname(self, tag_name: str) -> Optional[Dict]:
        session = self._get_session()
        try:
            record = session.query(IOReal).filter(IOReal.tag_name == tag_name).first()
            return self._record_to_dict(record) if record else None
        finally:
            session.close()

    def search_all_io_tags(self, text: str) -> List[Dict]:
        if not text:
            return []

        disc_results = self.search_io_disc(text)
        real_results = self.search_io_real(text)

        for r in disc_results:
            r['tag_type'] = 'IODisc'
        for r in real_results:
            r['tag_type'] = 'IOReal'

        return disc_results + real_results

    def find_matching_io_real(self, disc_tag_name: str) -> Optional[Dict]:
        if not disc_tag_name:
            return None

        core_id = self._extract_core_identifier(disc_tag_name)
        if not core_id:
            return None

        real_tag = 'r' + core_id
        result = self.get_io_real_by_tagname(real_tag)
        if result:
            return result

        session = self._get_session()
        try:
            pattern = f'%{core_id}%'
            record = session.query(IOReal).filter(IOReal.tag_name.like(pattern)).first()
            return self._record_to_dict(record) if record else None
        finally:
            session.close()

    def extract_core_identifier(self, tag_name: str) -> Optional[str]:
        match = re.match(r'^[mcdg](\w+?)_(\d+[A-Z]?)(?:_.*)?$', tag_name)
        if match:
            return match.group(1) + '_' + match.group(2)

        match = re.match(r'^[mcdg](\w+)$', tag_name)
        if match:
            return match.group(1)

        return None

    def _record_to_dict(self, record) -> Dict:
        if record is None:
            return {}
        return {c.name: getattr(record, c.name) for c in record.__table__.columns}