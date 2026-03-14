import os
import re
from difflib import SequenceMatcher
from typing import List, Dict, Optional, Union
from sqlalchemy import or_, true
from .models import init_engine, get_session, IODisc, IOReal, IOInt, IOAccess, Keyword
from .csv_importer import CSVImporter, ImportResult


class DatabaseService:
    def __init__(self, db_path: str = "data/keywords.db"):
        self.db_path = db_path
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self.engine = init_engine(self.db_path)

    def _get_session(self):
        return get_session(self.engine)

    def _record_to_dict(self, record) -> Dict:
        if record is None:
            return {}
        return {c.name: getattr(record, c.name) for c in record.__table__.columns}

    def import_from_csv(self, csv_path: str, mode: str = 'replace') -> ImportResult:
        session = self._get_session()
        try:
            importer = CSVImporter(session)
            return importer.import_from_csv(csv_path, mode)
        finally:
            session.close()

    DEFAULT_LIMIT = 100
    MAX_LIMIT = 1000

    def search_io_disc(self, text: str, limit: Optional[int] = None) -> List[Dict]:
        if not text:
            return []
        limit = min(limit or self.DEFAULT_LIMIT, self.MAX_LIMIT)
        session = self._get_session()
        try:
            pattern = f'%{text}%'
            records = session.query(IODisc).filter(
                or_(
                    IODisc.tag_name.like(pattern),
                    IODisc.comment.like(pattern),
                    IODisc.item_name.like(pattern)
                )
            ).limit(limit).all()
            return [self._record_to_dict(r) for r in records]
        finally:
            session.close()

    def search_io_real(self, text: str, limit: Optional[int] = None) -> List[Dict]:
        if not text:
            return []
        limit = min(limit or self.DEFAULT_LIMIT, self.MAX_LIMIT)
        session = self._get_session()
        try:
            pattern = f'%{text}%'
            records = session.query(IOReal).filter(
                or_(
                    IOReal.tag_name.like(pattern),
                    IOReal.comment.like(pattern),
                    IOReal.item_name.like(pattern)
                )
            ).limit(limit).all()
            return [self._record_to_dict(r) for r in records]
        finally:
            session.close()

    def get_all_io_disc(self, limit: Optional[int] = None, offset: int = 0) -> List[Dict]:
        limit = min(limit or self.MAX_LIMIT, self.MAX_LIMIT)
        session = self._get_session()
        try:
            records = session.query(IODisc).order_by(IODisc.tag_name).offset(offset).limit(limit).all()
            return [self._record_to_dict(r) for r in records]
        finally:
            session.close()

    def get_all_io_real(self, limit: Optional[int] = None, offset: int = 0) -> List[Dict]:
        limit = min(limit or self.MAX_LIMIT, self.MAX_LIMIT)
        session = self._get_session()
        try:
            records = session.query(IOReal).order_by(IOReal.tag_name).offset(offset).limit(limit).all()
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

    def search_all_io_tags(self, text: str, limit: Optional[int] = None) -> List[Dict]:
        if not text:
            return []
        
        half_limit = (limit or self.DEFAULT_LIMIT * 2) // 2
        disc_results = self.search_io_disc(text, limit=half_limit)
        real_results = self.search_io_real(text, limit=half_limit)

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

    def _extract_core_identifier(self, tag_name: str) -> Optional[str]:
        match = re.match(r'^[mcdg](\w+?)_(\d+[A-Z]?)(?:_.*)?$', tag_name)
        if match:
            return match.group(1) + '_' + match.group(2)

        match = re.match(r'^[mcdg](\w+)$', tag_name)
        if match:
            return match.group(1)

        return None

    def extract_core_identifier(self, tag_name: str) -> Optional[str]:
        match = re.match(r'^[mcdg](\w+?)_(\d+[A-Z]?)(?:_.*)?$', tag_name)
        if match:
            return match.group(1) + '_' + match.group(2)

        match = re.match(r'^[mcdg](\w+)$', tag_name)
        if match:
            return match.group(1)

        return None

    def _normalize_for_comparison(self, tag_name: str) -> str:
        if not tag_name:
            return ''
        
        result = tag_name.lower()
        
        for prefix in ['m', 'c', 'd', 'g', 'r']:
            if result.startswith(prefix):
                result = result[1:]
                break
        
        suffixes = ['_ll', '_hh', '_alm', '_sp', '_pv', '_out']
        for suffix in suffixes:
            if result.endswith(suffix):
                result = result[:-len(suffix)]
                break
        
        return result

    FUZZY_SEARCH_LIMIT = 500

    def fuzzy_search_tag_name(self, text: str, threshold: float = 0.7) -> Optional[Dict]:
        if not text:
            return None
        
        candidates = self._get_fuzzy_candidates(text)
        if not candidates:
            return None
        
        normalized_input = self._normalize_for_comparison(text)
        
        best_match = None
        best_ratio = threshold
        
        for record in candidates:
            tag_name = record.get('tag_name', '')
            if not tag_name:
                continue
            
            normalized_tag = self._normalize_for_comparison(tag_name)
            
            ratio = SequenceMatcher(None, normalized_input, normalized_tag).ratio()
            raw_ratio = SequenceMatcher(None, text.lower(), tag_name.lower()).ratio()
            
            final_ratio = max(ratio, raw_ratio)
            
            if final_ratio > best_ratio:
                best_ratio = final_ratio
                best_match = record
        
        return best_match

    def _get_fuzzy_candidates(self, text: str) -> List[Dict]:
        session = self._get_session()
        try:
            candidates = []
            normalized = self._normalize_for_comparison(text)
            
            if normalized:
                pattern = f'%{normalized}%'
                records = session.query(IOReal).filter(
                    IOReal.tag_name.like(pattern)
                ).limit(self.FUZZY_SEARCH_LIMIT).all()
                candidates = [self._record_to_dict(r) for r in records]
            
            if len(candidates) < self.FUZZY_SEARCH_LIMIT:
                existing_tags = {c.get('tag_name') for c in candidates}
                if existing_tags:
                    extra = session.query(IOReal).filter(
                        ~IOReal.tag_name.in_(existing_tags)
                    ).limit(self.FUZZY_SEARCH_LIMIT - len(candidates)).all()
                else:
                    extra = session.query(IOReal).limit(self.FUZZY_SEARCH_LIMIT).all()
                candidates.extend([self._record_to_dict(r) for r in extra])
            
            return candidates
        finally:
            session.close()

    def search_io_real_by_core_id(self, core_id: str, limit: Optional[int] = None) -> List[Dict]:
        if not core_id:
            return []
        limit = min(limit or self.DEFAULT_LIMIT, self.MAX_LIMIT)
        session = self._get_session()
        try:
            pattern = f'%{core_id}%'
            records = session.query(IOReal).filter(
                IOReal.tag_name.like(pattern)
            ).limit(limit).all()
            return [self._record_to_dict(r) for r in records]
        finally:
            session.close()

    def get_all_keywords(self, limit: Optional[int] = None) -> List[Dict]:
        limit = min(limit or self.MAX_LIMIT, self.MAX_LIMIT)
        session = self._get_session()
        try:
            records = session.query(Keyword).order_by(Keyword.id).limit(limit).all()
            return [self._record_to_dict(r) for r in records]
        finally:
            session.close()

    def add_keyword(self, keyword: str, description: str = '') -> Dict:
        session = self._get_session()
        try:
            new_keyword = Keyword(keyword=keyword, description=description)
            session.add(new_keyword)
            session.commit()
            session.refresh(new_keyword)
            return self._record_to_dict(new_keyword)
        finally:
            session.close()

    def delete_keyword(self, keyword_id: int) -> bool:
        session = self._get_session()
        try:
            record = session.query(Keyword).filter(Keyword.id == keyword_id).first()
            if record:
                session.delete(record)
                session.commit()
                return True
            return False
        finally:
            session.close()