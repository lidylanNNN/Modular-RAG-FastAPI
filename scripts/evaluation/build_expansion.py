'''从已生成的原文件建立修订开发集和独立文档族验证集，不安装依赖。'''

import copy
import hashlib
import json
import shutil
import uuid
from pathlib import Path

if __package__:
    from .validate_dataset import xlsx_cells
else:
    from validate_dataset import xlsx_cells

ROOT = Path(__file__).resolve().parents[2] / 'evaluation'
OLD = ROOT / 'datasets/archive/synthetic-v1'


def read_json(path: Path) -> dict | list:
    '''显式按 UTF-8 读取结构化输入。'''
    return json.loads(path.read_text(encoding='utf-8'))


def write_json(path: Path, value: dict | list) -> None:
    '''写入可人工审阅的 UTF-8 JSON。'''
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def digest(value: bytes) -> str:
    '''计算源文件及规范化清单的 SHA-256。'''
    return hashlib.sha256(value).hexdigest()


def anchor_for(unit: dict, anchor_id: str, quotes: list[str]) -> tuple[dict, dict]:
    '''将明确的原文子串转换成不可变字符区间；不存在或不唯一时拒绝生成。'''
    spans = []
    for quote in quotes:
        text = unit['canonical_text']
        if not quote or text.count(quote) != 1:
            raise ValueError(f'ambiguous or missing quote: {anchor_id}: {quote}')
        start = text.index(quote)
        spans.append({'unit_id': unit['unit_id'], 'char_start': start, 'char_end': start + len(quote)})
    anchor = {key: unit[key] for key in ('document_id', 'revision_id', 'parse_artifact_id')}
    anchor.update(anchor_id=anchor_id, source_spans=spans)
    note = {'anchor_id': anchor_id, 'locator': unit['locator'], 'quote': '\n'.join(quotes)}
    return anchor, note


def row_quotes(unit: dict, multi_span: bool = False, full: bool = False) -> list[str]:
    '''选择记录的对象、适用条件和规则；仅在结论依赖备注时保留备注。'''
    lines = unit['canonical_text'].splitlines()
    if 'record_key' not in unit['locator']:
        return [unit['canonical_text']]
    if lines[1].startswith('现象:'):
        return ['\n'.join(lines[2:4])]
    if multi_span:
        rule = lines[3].removeprefix('规则: ')
        return ['\n'.join(lines[1:3]), *[part + '。' for part in rule.split('。') if part]]
    return ['\n'.join(lines[1:] if full else lines[1:4])]


def narrow_legacy(cases: list[dict], notes: list[dict], units: list[dict]) -> None:
    '''在新数据集中细化旧题锚点，并令 DEV-013 真正需要历史和规范两类事实。'''
    lookup = {(u['parse_artifact_id'], u['unit_id']): u for u in units}
    for case, annotation in zip(cases, notes, strict=True):
        annotation['label_revision'] = 'synthetic-v2'
        annotation['revision_note'] = '缩小到回答所需原文；人工复核待完成。'
        annotation['evidence_notes'] = []
        for group in case['evidence_groups']:
            for old_anchor in group['alternatives']:
                unit = lookup[(old_anchor['parse_artifact_id'], old_anchor['source_spans'][0]['unit_id'])]
                text = unit['canonical_text']
                number = int(case['case_id'].split('-')[1])
                if 'record_key' in unit['locator']:
                    lines = text.splitlines()
                    if number == 10:
                        quotes = [lines[3]]
                    elif number == 13:
                        quotes = ['\n'.join(lines[1:3])]
                    elif number == 14:
                        quotes = [lines[4]]
                    else:
                        quotes = ['\n'.join(lines[2:]) if number == 11 else '\n'.join(lines[2:4])]
                elif number in {1, 2, 7, 8, 13, 15, 16}:
                    quotes = [text.split('。')[0] + '。']
                elif number == 3:
                    quotes = [text.split('。')[1] + '。']
                elif number == 4:
                    quotes = [text.split('。')[1] + '。']
                elif number == 6:
                    quotes = ['。'.join(text.split('。')[:2]) + '。']
                else:
                    quotes = [text]
                anchor, note = anchor_for(unit, old_anchor['anchor_id'], quotes)
                old_anchor.update(anchor)
                annotation['evidence_notes'].append(note)
        if case['case_id'] == 'DEV-013':
            case['question'] = 'SYN-F001 记录了什么误报现象和旧实现根因？结合当前规范，说明应采用的超时判定及具体阈值。'
            case['reference_answer'] = '调度抖动时出现通信超时误报，旧实现累加丢帧次数且未用最后有效帧时间戳；应按时间差判定，当前版在启动屏蔽结束后达到 150 ms 置位。'
            case['required_facts'] = ['F001 的现象为调度抖动时通信超时误报', '旧实现按丢帧次数累加且未使用时间戳', '改用最后有效帧时间差', '启动屏蔽结束后达到 150 ms 置位']


def append_workbook(folder: Path, definition: dict, sources: list[dict], units: list[dict], lookup: dict) -> None:
    '''读取实际导出的 XLSX，核对所有种子记录并生成稳定原文定位目录。'''
    path = folder / 'corpus' / definition['file']
    document_id = str(uuid.uuid5(uuid.NAMESPACE_URL, 'synthetic-expansion/' + definition['key']))
    content_hash = digest(path.read_bytes())
    revision = digest(f'{document_id}:{content_hash}'.encode())
    artifact = digest(f'{revision}:fixture-locator-v1'.encode())
    source = dict(key=definition['key'], document_id=document_id, revision_id=revision,
                  parse_artifact_id=artifact, content_hash=content_hash, file_name=path.name,
                  path=f'corpus/{path.name}', file_type='xlsx', version='1.0', is_current=True)
    sources.append(source)
    cells = xlsx_cells(path, 'xl/worksheets/sheet1.xml')
    for row_number, expected in enumerate(definition['rows'], 5):
        actual = [cells[f'{col}{row_number}'] for col in 'ABCDE']
        if actual != expected:
            raise ValueError(f'export differs from source: {path.name}:{row_number}')
    count = len(definition['rows']) + definition.get('distractor_count', 0)
    for row in range(5, 5 + count):
        key = cells[f'A{row}']
        unit = {key: source[key] for key in ('document_id', 'revision_id', 'parse_artifact_id')}
        unit.update(unit_id=f'record-row-{row}', canonical_text='\n'.join(f'{cells[f"{col}4"]}: {cells[f"{col}{row}"]}' for col in 'ABCDE'),
                    locator=dict(sheet=definition['sheet'], sheet_part='xl/worksheets/sheet1.xml', row=row,
                                 header_row=4, columns='ABCDE', record_key=key))
        units.append(unit)
        lookup[f'{definition["key"]}:{key}'] = unit


def render_cases(folder: Path, cases: list[dict], notes: list[dict]) -> None:
    '''输出与 JSONL 同步的人读题目、证据和拒答依据。'''
    result = ['# 合成评测题', '', '所有参数和记录均为虚构；人工复核待完成，不是冻结发布测试集。', '']
    for case, note in zip(cases, notes, strict=True):
        result += [f'## {case["case_id"]} {case["question_type"]}', '', f'问题：{case["question"]}', '',
                   f'答案：{case["reference_answer"] or "拒答：" + case["expected_refusal_reason"]}', '',
                   f'模式：{case["version_mode"]}；过滤：`{json.dumps(case["filters"], ensure_ascii=False)}`', '',
                   '必需事实：' + '；'.join(case['required_facts']), '']
        for group in case['evidence_groups']:
            result += [f'证据组 {group["group_id"]}（组内 OR）：' + ' / '.join(a['anchor_id'] for a in group['alternatives']), '']
        for evidence in note['evidence_notes']:
            result += [f'锚点 {evidence["anchor_id"]}，位置 `{json.dumps(evidence["locator"], ensure_ascii=False)}`', '',
                       '> ' + evidence['quote'].replace('\n', '\n> '), '']
        if note.get('unanswerable_rationale'):
            result += ['拒答依据：' + note['unanswerable_rationale'], '']
    (folder / 'cases.md').write_text('\n'.join(result), encoding='utf-8')


def build(split: str) -> None:
    '''保留旧夹具，生成新清单、题目和派生标注；仅重建机器草案。'''
    definitions = read_json(ROOT / 'seeds/expansion_sources.json')['workbooks']
    raw_cases = read_json(ROOT / 'seeds/expansion_cases.json')[split]
    relative = 'datasets/dev/synthetic-v2' if split == 'dev' else 'datasets/validation/synthetic-cooling-v1'
    folder = ROOT / relative
    # 人工登记后禁止构建器覆盖复核内容。
    existing = folder / 'annotations.jsonl'
    if existing.exists():
        for line in existing.read_text(encoding='utf-8').splitlines():
            if json.loads(line)['human_review_status'] != 'pending':
                raise ValueError('refusing to overwrite human review')
    sources, units, cases, notes, lookup = [], [], [], [], {}
    if split == 'dev':
        sources = copy.deepcopy(read_json(OLD / 'corpus_manifest.json')['sources'])
        units = copy.deepcopy(read_json(OLD / 'source_units.json'))
        for source in sources:
            shutil.copyfile(OLD / source['path'], folder / source['path'])
        cases = [json.loads(line) for line in (OLD / 'cases.jsonl').read_text(encoding='utf-8').splitlines()]
        notes = [json.loads(line) for line in (OLD / 'annotations.jsonl').read_text(encoding='utf-8').splitlines()]
        narrow_legacy(cases, notes, units)
        for unit in units:
            if 'record_key' in unit['locator']:
                lookup['failures:' + unit['locator']['record_key']] = unit
    for definition in definitions:
        if definition['dataset'] == relative:
            append_workbook(folder, definition, sources, units, lookup)
    manifest = dict(dataset_id=relative.removeprefix('datasets/').replace('/', '-'), synthetic=True, split=split,
                    parser_identity='fixture-locator-v1', sources=sources,
                    notice='合成资料，非真实业务效果证据。')
    manifest['corpus_manifest_id'] = digest(json.dumps(manifest, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode())
    by_key = {s['key']: s for s in sources}
    for raw in raw_cases:
        groups, evidence_notes, conflicts = [], [], []
        raw_groups = raw['groups'] or ([[ref] for ref in raw.get('conflict_refs', [])])
        for gi, refs in enumerate(raw_groups, 1):
            alternatives = []
            for ai, ref in enumerate(refs, 1):
                unit = lookup[ref]
                include_notes = ref in {'conflict:X02', 'interfaces:X01', 'cooling:C04', 'cooling:C05', 'cooling:C07'}
                anchor, note = anchor_for(unit, f'{raw["id"]}-G{gi}-A{ai}',
                                          row_quotes(unit, raw.get('multi_span', False), include_notes))
                alternatives.append(anchor)
                evidence_notes.append(note)
            if raw['a'] is None:
                conflicts.extend(alternatives)
            else:
                groups.append(dict(group_id=f'{raw["id"]}-G{gi}', alternatives=alternatives))
        filters = copy.deepcopy(raw.get('filters', {}))
        if raw.get('documents'):
            filters['document_ids'] = [by_key[key]['document_id'] for key in raw['documents']]
        if raw.get('versions'):
            filters['revision_ids'] = [by_key[key]['revision_id'] for key in raw['versions']]
        cases.append(dict(case_id=raw['id'], question=raw['q'], reference_answer=raw['a'], required_facts=raw['facts'],
                          evidence_groups=groups, answerable=raw['a'] is not None, expected_refusal_reason=raw.get('reason'),
                          question_type=raw['type'], filters=filters, version_mode=raw.get('mode', 'latest')))
        note = dict(case_id=raw['id'], synthetic=True, split=split, human_review_status='pending',
                    leakage_group='synthetic-control-family' if split == 'dev' else 'synthetic-cooling-family',
                    evidence_notes=evidence_notes, unanswerable_rationale=raw.get('note'), label_revision='expansion-1')
        if conflicts:
            note['conflict_anchors'] = conflicts
        notes.append(note)
    for case in cases:
        case['corpus_manifest_id'] = manifest['corpus_manifest_id']
    for name, value in [('corpus_manifest.json', manifest), ('source_units.json', units)]:
        write_json(folder / name, value)
    for name, rows in [('cases.jsonl', cases), ('annotations.jsonl', notes)]:
        (folder / name).write_text(''.join(json.dumps(row, ensure_ascii=False) + '\n' for row in rows), encoding='utf-8')
    render_cases(folder, cases, notes)
    for log in (folder / 'corpus').glob('*.inspect.ndjson'):
        log.unlink()
    print(f'{relative}: {len(cases)} cases, {len(sources)} files, {len(units)} source units')


if __name__ == '__main__':
    build('dev')
    build('validation')
