import csv
import logging
from typing import Dict, List, Optional
from dataclasses import dataclass, field
from sqlalchemy.orm import Session
from .models import IODisc, IOReal, IOInt, IOAccess

logger = logging.getLogger(__name__)


@dataclass
class ImportResult:
    iodisc_count: int = 0
    ioreal_count: int = 0
    ioint_count: int = 0
    ioaccess_count: int = 0
    errors: List[str] = field(default_factory=list)


IODISC_COLUMNS = ['tag_name', 'group_name', 'comment', 'logged', 'event_logged',
                  'event_logging_priority', 'retentive_value', 'initial_disc',
                  'off_msg', 'on_msg', 'alarm_state', 'alarm_pri', 'd_conversion',
                  'access_name', 'item_use_tagname', 'item_name', 'read_only',
                  'alarm_comment', 'alarm_ack_model', 'dsc_alarm_disable',
                  'dsc_alarm_inhibitor', 'symbolic_name']

IOREAL_COLUMNS = ['tag_name', 'group_name', 'comment', 'logged', 'event_logged',
                  'event_logging_priority', 'retentive_value', 'retentive_alarm_parameters',
                  'alarm_value_deadband', 'alarm_dev_deadband', 'eng_units',
                  'initial_value', 'min_eu', 'max_eu', 'deadband', 'log_deadband',
                  'lolo_alarm_state', 'lolo_alarm_value', 'lolo_alarm_pri',
                  'lo_alarm_state', 'lo_alarm_value', 'lo_alarm_pri',
                  'hi_alarm_state', 'hi_alarm_value', 'hi_alarm_pri',
                  'hihi_alarm_state', 'hihi_alarm_value', 'hihi_alarm_pri',
                  'minor_dev_alarm_state', 'minor_dev_alarm_value', 'minor_dev_alarm_pri',
                  'major_dev_alarm_state', 'major_dev_alarm_value', 'major_dev_alarm_pri',
                  'dev_target', 'roc_alarm_state', 'roc_alarm_value', 'roc_alarm_pri',
                  'roc_time_base', 'min_raw', 'max_raw', 'conversion',
                  'access_name', 'item_use_tagname', 'item_name', 'read_only',
                  'alarm_comment', 'alarm_ack_model', 'lolo_alarm_disable',
                  'lo_alarm_disable', 'hi_alarm_disable', 'hihi_alarm_disable',
                  'min_dev_alarm_disable', 'maj_dev_alarm_disable', 'roc_alarm_disable',
                  'lolo_alarm_inhibitor', 'lo_alarm_inhibitor', 'hi_alarm_inhibitor',
                  'hihi_alarm_inhibitor', 'min_dev_alarm_inhibitor', 'maj_dev_alarm_inhibitor',
                  'roc_alarm_inhibitor', 'symbolic_name']

IOINT_COLUMNS = ['tag_name', 'group_name', 'comment', 'logged', 'event_logged',
                 'event_logging_priority', 'retentive_value', 'retentive_alarm_parameters',
                 'alarm_value_deadband', 'alarm_dev_deadband', 'eng_units',
                 'initial_value', 'min_value', 'max_value', 'deadband', 'log_deadband',
                 'lolo_alarm_state', 'lolo_alarm_value', 'lolo_alarm_pri',
                 'lo_alarm_state', 'lo_alarm_value', 'lo_alarm_pri',
                 'hi_alarm_state', 'hi_alarm_value', 'hi_alarm_pri',
                 'hihi_alarm_state', 'hihi_alarm_value', 'hihi_alarm_pri',
                 'minor_dev_alarm_state', 'minor_dev_alarm_value', 'minor_dev_alarm_pri',
                 'major_dev_alarm_state', 'major_dev_alarm_value', 'major_dev_alarm_pri',
                 'dev_target', 'roc_alarm_state', 'roc_alarm_value', 'roc_alarm_pri',
                 'roc_time_base', 'min_raw', 'max_raw', 'conversion',
                 'access_name', 'item_use_tagname', 'item_name', 'read_only',
                 'alarm_comment', 'alarm_ack_model', 'lolo_alarm_disable',
                 'lo_alarm_disable', 'hi_alarm_disable', 'hihi_alarm_disable',
                 'min_dev_alarm_disable', 'maj_dev_alarm_disable', 'roc_alarm_disable',
                 'lolo_alarm_inhibitor', 'lo_alarm_inhibitor', 'hi_alarm_inhibitor',
                 'hihi_alarm_inhibitor', 'min_dev_alarm_inhibitor', 'maj_dev_alarm_inhibitor',
                 'roc_alarm_inhibitor', 'symbolic_name']

IOACCESS_COLUMNS = ['access_name', 'application', 'topic', 'advise_active', 'dde_protocol',
                    'sec_application', 'sec_topic', 'sec_advise_active', 'sec_dde_protocol',
                    'failover_expression', 'failover_deadband', 'dfo_flag', 'fbd_flag',
                    'failback_deadband']

IODISC_IMPORT_COLUMNS = ['tag_name', 'comment', 'access_name', 'item_name']
IOREAL_IMPORT_COLUMNS = ['tag_name', 'comment', 'eng_units', 'min_eu', 'max_eu',
                         'lolo_alarm_state', 'lolo_alarm_value', 'lolo_alarm_pri',
                         'lo_alarm_state', 'lo_alarm_value', 'lo_alarm_pri',
                         'hi_alarm_state', 'hi_alarm_value', 'hi_alarm_pri',
                         'hihi_alarm_state', 'hihi_alarm_value', 'hihi_alarm_pri',
                         'access_name', 'item_name']


class CSVImporter:
    def __init__(self, session: Session):
        self.session = session
        self.csv_encoding = 'gbk'

    def parse_csv_sections(self, csv_path: str) -> Dict[str, Dict]:
        sections = {}
        current_section = None
        current_data = []

        with open(csv_path, 'r', encoding=self.csv_encoding, errors='ignore') as f:
            reader = csv.reader(f)
            for row in reader:
                if not row:
                    continue

                first_cell = row[0].strip() if row[0] else ''

                if first_cell.startswith(':') and not first_cell.startswith(':"'):
                    if current_section and current_data:
                        sections[current_section] = {'data': current_data}

                    current_section = first_cell[1:]
                    current_data = []
                elif current_section:
                    non_empty_cells = [cell.strip() for cell in row if cell.strip()]
                    if non_empty_cells:
                        values = [self._clean_value(v.strip()) for v in row]
                        current_data.append(values)

        if current_section and current_data:
            sections[current_section] = {'data': current_data}

        return sections

    def _clean_value(self, val: str) -> Optional[str]:
        if val is None or val == '':
            return None
        val = val.strip()
        if val.upper() == 'YES':
            return 'Yes'
        if val.upper() == 'NO':
            return 'No'
        return val if val else None

    def _map_row_by_position(self, row: List, column_names: List, import_columns: List) -> Dict:
        result = {}
        col_to_idx = {name: i for i, name in enumerate(column_names)}
        
        for col in import_columns:
            if col in col_to_idx:
                idx = col_to_idx[col]
                if idx < len(row):
                    result[col] = row[idx]
        
        return result

    def import_from_csv(self, csv_path: str, mode: str = 'replace') -> ImportResult:
        result = ImportResult()

        try:
            sections = self.parse_csv_sections(csv_path)
            logger.info(f"解析CSV完成，共 {len(sections)} 个区块: {list(sections.keys())}")

            if 'IODisc' in sections:
                result.iodisc_count = self._import_iodisc(sections['IODisc'], mode)

            if 'IOReal' in sections:
                result.ioreal_count = self._import_ioreal(sections['IOReal'], mode)

            if 'IOInt' in sections:
                result.ioint_count = self._import_ioint(sections['IOInt'], mode)

            if 'IOAccess' in sections:
                result.ioaccess_count = self._import_ioaccess(sections['IOAccess'], mode)

            self.session.commit()
            logger.info(f"导入完成: IODisc={result.iodisc_count}, IOReal={result.ioreal_count}")

        except Exception as e:
            self.session.rollback()
            result.errors.append(str(e))
            logger.error(f"导入失败: {e}")

        return result

    def _import_iodisc(self, section: Dict, mode: str) -> int:
        if mode == 'replace':
            self.session.query(IODisc).delete()

        data = section['data']
        count = 0

        for row in data:
            mapped = self._map_row_by_position(row, IODISC_COLUMNS, IODISC_IMPORT_COLUMNS)
            if mapped.get('tag_name'):
                record = IODisc(**mapped)
                self.session.add(record)
                count += 1

        return count

    def _import_ioreal(self, section: Dict, mode: str) -> int:
        if mode == 'replace':
            self.session.query(IOReal).delete()

        data = section['data']
        count = 0

        for row in data:
            mapped = self._map_row_by_position(row, IOREAL_COLUMNS, IOREAL_IMPORT_COLUMNS)
            if mapped.get('tag_name'):
                mapped = self._convert_numeric_fields(mapped)
                record = IOReal(**mapped)
                self.session.add(record)
                count += 1

        return count

    def _import_ioint(self, section: Dict, mode: str) -> int:
        if mode == 'replace':
            self.session.query(IOInt).delete()

        data = section['data']
        count = 0

        for row in data:
            mapped = self._map_row_by_position(row, IOINT_COLUMNS, 
                ['tag_name', 'comment', 'eng_units', 'min_value', 'max_value',
                 'lolo_alarm_state', 'lolo_alarm_value', 'lolo_alarm_pri',
                 'lo_alarm_state', 'lo_alarm_value', 'lo_alarm_pri',
                 'hi_alarm_state', 'hi_alarm_value', 'hi_alarm_pri',
                 'hihi_alarm_state', 'hihi_alarm_value', 'hihi_alarm_pri',
                 'access_name', 'item_name'])
            if mapped.get('tag_name'):
                mapped = self._convert_numeric_fields(mapped, is_real=False)
                record = IOInt(**mapped)
                self.session.add(record)
                count += 1

        return count

    def _import_ioaccess(self, section: Dict, mode: str) -> int:
        if mode == 'replace':
            self.session.query(IOAccess).delete()

        data = section['data']
        count = 0

        for row in data:
            mapped = self._map_row_by_position(row, IOACCESS_COLUMNS,
                ['access_name', 'application', 'topic', 'advise_active', 'dde_protocol'])
            if mapped.get('access_name'):
                record = IOAccess(**mapped)
                self.session.add(record)
                count += 1

        return count

    def _convert_numeric_fields(self, data: Dict, is_real: bool = True) -> Dict:
        int_fields = ['lolo_alarm_state', 'lolo_alarm_pri', 'lo_alarm_state', 'lo_alarm_pri',
                      'hi_alarm_state', 'hi_alarm_pri', 'hihi_alarm_state', 'hihi_alarm_pri']
        float_fields = ['min_eu', 'max_eu', 'min_value', 'max_value',
                        'lolo_alarm_value', 'lo_alarm_value', 'hi_alarm_value', 'hihi_alarm_value']

        result = dict(data)
        for field in int_fields:
            if field in result and result[field] is not None:
                try:
                    val = result[field]
                    if isinstance(val, str) and val.upper() in ['ON', 'OFF', 'NONE']:
                        result[field] = 0
                    else:
                        result[field] = int(val) if val else 0
                except (ValueError, TypeError):
                    result[field] = 0

        for field in float_fields:
            if field in result and result[field] is not None:
                try:
                    result[field] = float(result[field]) if result[field] else 0.0
                except (ValueError, TypeError):
                    result[field] = 0.0

        return result