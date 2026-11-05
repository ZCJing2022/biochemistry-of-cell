#!/usr/bin/env python3
"""One-time, fail-closed integration of the reviewed V2 narrative additions."""
from __future__ import annotations
import csv
import hashlib
import json
import re
import statistics
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'scripts'))
import explanation_panels as old_panels

BASE_SHA = '6502492aa70b23b5cf4645e7144af421d41a536b'


def read_tsv(path):
    with path.open(encoding='utf-8', newline='') as f:
        reader = csv.DictReader(f, delimiter='\t')
        fields = reader.fieldnames
        rows = list(reader)
    assert fields and rows and all(None not in r and all(v is not None for v in r.values()) for r in rows), path
    return fields, rows


def parse_details(path):
    text = path.read_text(encoding='utf-8')
    entries = re.findall(r'(?ms)^## ([^\n]+)\n\n(.*?)(?=^## |\Z)', text)
    assert entries and len(entries) == len(re.findall(r'(?m)^## ', text)), path
    notes = {k.strip(): v.strip() for k, v in entries}
    assert len(notes) == len(entries), (path, 'duplicate detail key')
    for key, value in notes.items():
        assert len(value.split()) >= 60, (path, key, 'detail too short')
        assert not any(t in value for t in ('\n:::', 'TODO', 'PLACEHOLDER')), (path, key)
    return notes


def replace_once(text, old, new):
    assert text.count(old) == 1, ('patch mismatch', old, text.count(old))
    return text.replace(old, new, 1)


pages = sorted((ROOT/'practice').glob('week*.qmd')) + sorted((ROOT/'practice').glob('practice-part2-exam-*.qmd'))
assert len(pages) == 8
before_pages = {str(p.relative_to(ROOT)): p.read_text(encoding='utf-8') for p in pages}
Path('/tmp/detail-baseline-pages.json').write_text(json.dumps(before_pages, ensure_ascii=False), encoding='utf-8')

sources = sorted((ROOT/'assessment').glob('explanations-*.tsv'))
assert len(sources) == 7
before_sources = {p.name: read_tsv(p) for p in sources}
report = {'version': 'explanation-detail-v2', 'baseline_commit': BASE_SHA, 'scope': 'Every weekly narrative, every common exam MCQ rationale, and all form-specific exam subparts', 'method': 'Question-specific authored elaborations appended to existing source-grounded narratives; no keyword-generated filler or external retrieval', 'fields': [], 'files': {}}

for path in sources:
    fields, rows = before_sources[path.name]
    if path.name == 'explanations-exam-integrated.tsv':
        notes = {}
        for problem in range(1, 6):
            current = parse_details(ROOT/f'assessment/_detail_exam_p{problem}.md')
            assert not set(current) & set(notes)
            notes.update(current)
        expected = {r['id']+'-'+str(f) for r in rows for f in (1, 2, 3)}
    else:
        suffix = path.stem.removeprefix('explanations-').replace('-', '_')
        notes = parse_details(ROOT/f'assessment/_detail_{suffix}.md')
        expected = {r['id'] for r in rows}
    assert set(notes) == expected, (path, 'coverage mismatch', sorted(expected-set(notes)), sorted(set(notes)-expected))
    for row in rows:
        for field in fields:
            if not field.startswith('explanation'):
                continue
            key = row['id'] if field == 'explanation' else row['id']+'-'+field.removeprefix('explanation')
            original = row[field]
            revised = original.rstrip()+'\n\n'+notes[key]+'\n'
            n0, n1 = len(original.split()), len(revised.split())
            assert n1 >= 90 and n1 >= 1.75*n0, (path, key, n0, n1)
            row[field] = revised.rstrip()
            report['fields'].append({'file': path.name, 'id': row['id'], 'field': field, 'before_words': n0, 'after_words': n1, 'before_sha256': hashlib.sha256(original.encode()).hexdigest(), 'after_sha256': hashlib.sha256(row[field].encode()).hexdigest()})
    with path.open('w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fields, delimiter='\t', lineterminator='\n')
        writer.writeheader()
        writer.writerows(rows)
    # A readback detects malformed multiline quoting or lost identifiers.
    read_fields, read_rows = read_tsv(path)
    assert read_fields == fields and read_rows == rows
    records = [r for r in report['fields'] if r['file'] == path.name]
    report['files'][path.name] = {'narrative_fields': len(records), 'before_words': sum(r['before_words'] for r in records), 'after_words': sum(r['after_words'] for r in records), 'after_min': min(r['after_words'] for r in records), 'after_max': max(r['after_words'] for r in records)}

assert len(report['fields']) == 389
report['totals'] = {'authored_narrative_fields': 389, 'question_explanation_panels': 405, 'exam_subpart_narratives': 75, 'before_words': sum(r['before_words'] for r in report['fields']), 'after_words': sum(r['after_words'] for r in report['fields']), 'all_narratives_expanded': True, 'minimum_expansion_ratio': round(min(r['after_words']/r['before_words'] for r in report['fields']), 3)}

helper = ROOT/'scripts/explanation_panels.py'
text = helper.read_text(encoding='utf-8')
text = replace_once(text, 'NOTICE = ', 'LEGACY_NOTICE = ')
new_notice = '**Answer and reasoning:** Each question has separate **Answer** and **Explanation** arrows below it. Both start closed; opening one does not open the other. The Explanation develops the reasoning in detail, including the relevant concepts, calculation steps where needed, and common points of confusion. Integrated exam explanations address every labeled subpart.\n\n'
text = replace_once(text, '\ndef records(', '\nNOTICE = '+repr(new_notice)+'\n\ndef records(')
text = replace_once(text, "return EXPLANATION.sub('',text).replace(NOTICE,'')", "return EXPLANATION.sub('',text).replace(NOTICE,'').replace(LEGACY_NOTICE,'')")
text = replace_once(text, 'len(text.split())<20', "len(text.split())<90 or '\\n\\n' not in text")
text = replace_once(text, "'version':'explanation-panels-v1'", "'version':'explanation-panels-v2'")
text = replace_once(text, '# Question explanations — V1', '# Question explanations — V2: detailed narratives')
text = replace_once(text, '## Coverage\n\n| Page', '''## Narrative depth

Every existing explanation has been expanded with question-specific reasoning rather than repeated generic advice. MCQ explanations clarify the relevant concept and distinguish competing answers. Objective-led and integrated explanations work through the requested parts, connect mechanisms to consequences, and show calculation setup, substitution, units and interpretation where applicable. Exam subparts use the numbers and conditions of their own form. Paragraph breaks keep longer explanations readable inside the existing closed panels.

The original short rationale remains as an opening summary, followed by the fuller explanation. The course's documented source discrepancies and terminology remain explicit. An additional historical revision record, `assessment/explanation-detail-audit.json`, compares all 389 authored narrative fields with the pre-expansion baseline; the 38 exam MCQ rationales serve 114 matched question placements.

## Coverage

| Page''')
text = replace_once(text, '| Page | Answers retained | Explanations added |', '| Page | Answers retained | Explanations expanded |')
text = replace_once(text, 'Checks require complete narrative coverage,', 'Checks require complete narrative coverage, at least two paragraphs and 90 words per authored narrative field,')
stat_code = '''    groups = {
        'weekly_mcq': [s for values in weekly.values() for k,s in values.items() if '-mc' in k],
        'weekly_objective': [s for values in weekly.values() for k,s in values.items() if '-lo' in k],
        'weekly_integrated': [s for values in weekly.values() for k,s in values.items() if '-ix' in k],
        'exam_mcq_concepts': list(mc.values()),
        'exam_subparts': [r[f'explanation{f}'] for r in parts.values() for f in (1,2,3)],
    }
    audit['narrative_statistics'] = {}
    for name,narratives in groups.items():
        lengths = sorted(len(s.split()) for s in narratives)
        audit['narrative_statistics'][name] = {'count':len(lengths),'min_words':min(lengths),'max_words':max(lengths),'total_words':sum(lengths)}
    assert sum(s['count'] for s in audit['narrative_statistics'].values()) == 389
'''
text = replace_once(text, "    out['assessment/explanation-audit.json']=", stat_code+"    out['assessment/explanation-audit.json']=")
append_code = '''    out['EXPLANATION_PANELS_AUDIT.md'] += '\\n## Current authored narrative lengths\\n\\n| Narrative type | Fields | Words per field | Total words |\\n|---|---:|---:|---:|\\n'
    for name,stats in audit['narrative_statistics'].items():
        out['EXPLANATION_PANELS_AUDIT.md'] += f"| {name.replace('_',' ')} | {stats['count']} | {stats['min_words']}–{stats['max_words']} | {stats['total_words']} |\\n"
    out['EXPLANATION_PANELS_AUDIT.md'] += '\\nLengths are whitespace-delimited counts of the authored explanation fields, excluding review links. Counts establish coverage and depth of revision, not an independent scientific audit.\\n'
'''
text = replace_once(text, '    return out,audit', append_code+'    return out,audit')
helper.write_text(text, encoding='utf-8')

subprocess.run([sys.executable, '-m', 'py_compile', 'scripts/explanation_panels.py', 'scripts/build_objective_assessments.py'], cwd=ROOT, check=True)
subprocess.run([sys.executable, 'scripts/build_objective_assessments.py', '--write'], cwd=ROOT, check=True)
subprocess.run([sys.executable, 'scripts/build_objective_assessments.py', '--check'], cwd=ROOT, check=True)

normalize = lambda s: re.sub(r'\s+', ' ', old_panels.strip_explanations(s).replace(new_notice, '')).strip()
for relative, original in before_pages.items():
    revised = (ROOT/relative).read_text(encoding='utf-8')
    assert old_panels.ANSWER.findall(original) == old_panels.ANSWER.findall(revised), (relative, 'answer changed')
    assert normalize(original) == normalize(revised), (relative, 'non-explanation content changed')
    assert len(old_panels.EXPLANATION.findall(original)) == len(old_panels.EXPLANATION.findall(revised)), relative
report['preservation'] = {'pages_checked': 8, 'answer_panels_unchanged': 405, 'all_non_explanation_content_unchanged_apart_from_notice_and_whitespace': True}
(ROOT/'assessment/explanation-detail-audit.json').write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
print(json.dumps({'detail_totals': report['totals'], 'files': report['files'], 'preservation': report['preservation']}, indent=2))
print('DETAIL SOURCE PASS: 389 authored narratives expanded; all 405 question answers and all original assessment content preserved.')
