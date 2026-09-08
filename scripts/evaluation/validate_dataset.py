'''校验合成开发集的结构、原文件哈希、证据位置和查询版本范围。'''

import hashlib
import json
import sys
import xml.etree.ElementTree as ET
from collections import Counter
from datetime import datetime
from pathlib import Path
from zipfile import ZipFile

NS = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main',
      's': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}


def require(condition: bool, message: str) -> None:
    '''在数据不满足约束时抛出可定位的问题说明。'''
    if not condition:
        raise ValueError(message)


def load_lines(path: Path) -> list[dict]:
    '''读取 UTF8 JSONL，每行必须是一个非空对象。'''
    result = []
    for line_number, line in enumerate(path.read_text(encoding='utf-8').splitlines(), 1):
        require(bool(line.strip()), f'{path.name}:{line_number} 空行')
        item = json.loads(line)
        require(isinstance(item, dict), f'{path.name}:{line_number} 不是对象')
        result.append(item)
    return result


def xlsx_cells(path: Path, part: str) -> dict[str, str]:
    '''直接从 XLSX XML 读取文本单元格，支持共享字符串和内联字符串。'''
    with ZipFile(path) as archive:
        strings = []
        if 'xl/sharedStrings.xml' in archive.namelist():
            root = ET.fromstring(archive.read('xl/sharedStrings.xml'))
            strings = [''.join(node.text or '' for node in item.findall('.//s:t', NS)) for item in root.findall('s:si', NS)]
        result = {}
        root = ET.fromstring(archive.read(part))
        for cell in root.findall('.//s:c', NS):
            value = cell.find('s:v', NS)
            if cell.get('t') == 's':
                text = strings[int(value.text)]
            elif cell.get('t') == 'inlineStr':
                text = ''.join(node.text or '' for node in cell.findall('.//s:t', NS))
            else:
                text = value.text if value is not None else ''
            result[cell.attrib['r']] = text
        return result


def validate(root: Path) -> dict:
    '''核对整个夹具包并返回统计；不执行检索或模型效果评测。'''
    manifest = json.loads((root / 'corpus_manifest.json').read_text(encoding='utf-8'))
    require(manifest['synthetic'] is True and manifest['split'] in {'dev', 'validation'}, '必须标记为合成开发或验证资料')
    payload = dict(manifest)
    manifest_id = payload.pop('corpus_manifest_id')
    expected = hashlib.sha256(json.dumps(payload, sort_keys=True, ensure_ascii=False, separators=(',', ':')).encode()).hexdigest()
    require(manifest_id == expected, 'corpus manifest hash mismatch')
    sources = {}
    currents = Counter()
    for source in manifest['sources']:
        file = (root / source['path']).resolve()
        require(file.is_relative_to((root / 'corpus').resolve()), 'source path escapes corpus')
        require(file.suffix in {'.docx', '.xlsx'}, 'unsupported source fixture')
        actual_hash = hashlib.sha256(file.read_bytes()).hexdigest()
        require(actual_hash == source['content_hash'], f'源文件哈希不一致: {file.name}')
        expected_revision = hashlib.sha256(f"{source['document_id']}:{actual_hash}".encode()).hexdigest()
        require(source['revision_id'] == expected_revision, 'revision_id mismatch')
        expected_artifact = hashlib.sha256(f"{expected_revision}:{manifest['parser_identity']}".encode()).hexdigest()
        require(source['parse_artifact_id'] == expected_artifact, 'parse artifact mismatch')
        require(source['file_type'] == file.suffix[1:], 'source file type mismatch')
        require(source['revision_id'] not in sources, 'duplicate revision')
        sources[source['revision_id']] = source
        if source['is_current']:
            currents[source['document_id']] += 1
    require(all(currents[doc] == 1 for doc in {s['document_id'] for s in sources.values()}), 'each document needs one current revision')
    units = {}
    for unit in json.loads((root / 'source_units.json').read_text(encoding='utf-8')):
        source = sources[unit['revision_id']]
        require(unit['document_id'] == source['document_id'], 'unit document mismatch')
        require(unit['parse_artifact_id'] == source['parse_artifact_id'], 'unit artifact mismatch')
        location = unit['locator']
        file = root / source['path']
        if source['file_type'] == 'docx':
            with ZipFile(file) as archive:
                body = ET.fromstring(archive.read(location['part'])).find('w:body', NS)
                position = location['body_child_1based']
                require(type(position) is int and 1 <= position <= len(body), 'invalid DOCX position')
                element = list(body)[position - 1]
                actual = ''.join(node.text or '' for node in element.findall('.//w:t', NS))
        else:
            cells = xlsx_cells(file, location['sheet_part'])
            row, header = location['row'], location['header_row']
            actual = '\n'.join(f'{cells[f"{col}{header}"]}: {cells[f"{col}{row}"]}' for col in location['columns'])
            require(cells[f'A{row}'] == location['record_key'], 'record key mismatch')
        require(actual == unit['canonical_text'], f'原文定位不一致: {unit["unit_id"]}')
        key = (unit['parse_artifact_id'], unit['unit_id'])
        require(key not in units, 'duplicate source unit')
        units[key] = unit
    cases = load_lines(root / 'cases.jsonl')
    annotations = load_lines(root / 'annotations.jsonl')
    require(bool(cases), 'empty dataset')
    ids = [item['case_id'] for item in cases]
    require(len(set(ids)) == len(ids), 'duplicate case_id')
    require(len({item['case_id'] for item in annotations}) == len(annotations) == len(cases), 'duplicate or missing annotations')
    notes = {item['case_id']:item for item in annotations}
    require(set(notes) == set(ids), 'annotation case IDs mismatch')
    for case in cases:
        label = case['case_id']
        require(case['corpus_manifest_id'] == manifest_id, f'{label}: manifest mismatch')
        require('relevant_chunk_ids' not in case, 'gold must not bind chunk ids')
        require(bool(case['question'].strip()), f'{label}: empty question')
        require(type(case['answerable']) is bool, f'{label}: answerable must be boolean')
        require(case['version_mode'] in {'latest','explicit','compare'}, f'{label}: invalid mode')
        require(notes[label]['synthetic'] is True and notes[label]['split'] == manifest['split'], 'annotation provenance invalid')
        require(notes[label]['human_review_status'] in {'pending','reviewed'}, 'invalid review status')
        require(bool(notes[label]['leakage_group'].strip()), 'missing leakage group')
        if notes[label]['human_review_status'] == 'reviewed':
            require(all(isinstance(notes[label].get(key), str) and notes[label][key].strip()
                        for key in ('reviewer', 'reviewed_at', 'review_notes')), 'review metadata missing')
            reviewed_at = datetime.fromisoformat(notes[label]['reviewed_at'])
            require(reviewed_at.tzinfo is not None, 'review timestamp needs timezone')
        filters = case['filters']
        require(isinstance(filters, dict) and set(filters) <= {'document_ids', 'revision_ids', 'file_types', 'sheet'}, 'unknown filter')
        for key in ('document_ids', 'revision_ids', 'file_types'):
            values = filters.get(key)
            if values is not None:
                require(isinstance(values, list) and 1 <= len(values) <= 100
                        and all(isinstance(value, str) and value.strip() for value in values)
                        and len(set(values)) == len(values), f'invalid filter: {key}')
        if filters.get('file_types') is not None:
            require(set(filters['file_types']) <= {'docx', 'pdf', 'pptx', 'xlsx'}, 'invalid file type filter')
        if filters.get('sheet') is not None:
            require(isinstance(filters['sheet'], str) and bool(filters['sheet'].strip()), 'invalid sheet filter')
        selected = case['filters'].get('revision_ids')
        if case['version_mode'] == 'latest':
            require(selected is None, f'{label}: latest cannot specify revisions')
            allowed = {revision for revision, source in sources.items() if source['is_current']}
        else:
            require(isinstance(selected,list) and len(set(selected)) == len(selected), f'{label}: invalid revision list')
            require(len(selected) >= (2 if case['version_mode'] == 'compare' else 1), f'{label}: insufficient revisions')
            allowed = set(selected)
            require(allowed <= sources.keys(), f'{label}: unknown revision')
        for revision in list(allowed):
            source = sources[revision]
            if (filters.get('document_ids') is not None and source['document_id'] not in filters['document_ids']
                    or filters.get('file_types') is not None and source['file_type'] not in filters['file_types']):
                allowed.remove(revision)
        if not case['answerable']:
            require(case['reference_answer'] is None and not case['required_facts'] and not case['evidence_groups'], f'{label}: invalid refusal fields')
            require(case['expected_refusal_reason'] in {'insufficient_evidence', 'version_conflict', 'unsupported_claim'}, f'{label}: invalid refusal reason')
            require(bool(notes[label]['unanswerable_rationale']), f'{label}: missing refusal rationale')
            if case['expected_refusal_reason'] == 'version_conflict':
                require(len(notes[label].get('conflict_anchors', [])) >= 2, 'missing conflict anchors')
        else:
            require(bool(case['reference_answer']) and bool(case['required_facts']) and bool(case['evidence_groups']), f'{label}: missing gold')
            require(case['expected_refusal_reason'] is None, f'{label}: answer/refusal conflict')
        evidence_notes = {note['anchor_id']:note for note in notes[label]['evidence_notes']}
        groups = case['evidence_groups']
        require(len({group['group_id'] for group in groups}) == len(groups), 'duplicate group ID')
        if not case['answerable'] and case['expected_refusal_reason'] == 'version_conflict':
            groups = [{'alternatives': notes[label]['conflict_anchors']}]
        seen_anchors = set()
        for group in groups:
            require(bool(group['alternatives']), f'{label}: empty evidence group')
            for anchor in group['alternatives']:
                require(anchor['anchor_id'] not in seen_anchors, 'duplicate anchor ID')
                seen_anchors.add(anchor['anchor_id'])
                require(anchor['revision_id'] in allowed, f'{label}: evidence violates version filter')
                require(bool(anchor['source_spans']), 'empty source spans')
                pieces = []
                for span in anchor['source_spans']:
                    unit = units[(anchor['parse_artifact_id'],span['unit_id'])]
                    require(filters.get('sheet') is None or unit['locator'].get('sheet') == filters['sheet'], 'evidence violates sheet filter')
                    require(unit['revision_id'] == anchor['revision_id'] and unit['document_id'] == anchor['document_id'], f'{label}: cross revision anchor')
                    start, end = span['char_start'], span['char_end']
                    require(type(start) is int and type(end) is int and 0 <= start < end <= len(unit['canonical_text']), f'{label}: span out of bounds')
                    pieces.append(unit['canonical_text'][start:end])
                require('\n'.join(pieces) == evidence_notes[anchor['anchor_id']]['quote'], f'{label}: quote mismatch')
        require(seen_anchors == set(evidence_notes) and len(evidence_notes) == len(notes[label]['evidence_notes']), 'evidence notes mismatch')
    reviewed = sum(note['human_review_status'] == 'reviewed' for note in annotations)
    return {'cases':len(cases),'answerable':sum(case['answerable'] for case in cases),
            'unanswerable':sum(not case['answerable'] for case in cases),
            'source_files':len(sources),'source_units':len(units),
            'human_review':'reviewed' if reviewed == len(cases) else 'partial' if reviewed else 'pending',
            'reviewed_cases':reviewed, 'split':manifest['split'], 'model_evaluation':'not_run'}


if __name__ == '__main__':
    folder = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parents[2] / 'evaluation/datasets/dev/synthetic-v2'
    try:
        print(json.dumps(validate(folder), ensure_ascii=False, indent=2))
    except (ValueError, KeyError, OSError, ET.ParseError) as error:
        print(f'INVALID DATASET: {error}', file=sys.stderr)
        sys.exit(1)
