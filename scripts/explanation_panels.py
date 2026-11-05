#!/usr/bin/env python3
"""Authored explanation panels for the static Part II assessment pages.

No browser injection, pre-render dependency, or outside content retrieval is used.
Narratives live in assessment/explanations-*.tsv. The main authoring script calls
add_explanations after rendering its existing questions and answers.
"""
from __future__ import annotations
import csv
import hashlib
import json
import re
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ANSWER = re.compile(r'(?ms)^::: \{\.callout-tip collapse="true" title="Answer"\}\n(.*?)\n:::\s*\n')
EXPLANATION = re.compile(r'(?ms)^::: \{\.callout-note \.question-explanation #[^\s}]+ collapse="true" title="Explanation"\}\n.*?\n:::\n')
SECTION = re.compile(r'(?ms)^### ([^\n]+)\n(.*?)(?=^#{1,3} |\Z)')
COUNTS = {8:59, 9:59, 10:49, 11:55, 12:54}
SLUGS = {8:'bioenergetics-enzymes',9:'glycolysis-cac',10:'etc-oxidative-phosphorylation',11:'lipids-eicosanoids-drugs',12:'cell-signaling-part1'}
NOTICE = '**Answer and reasoning:** Each question has separate **Answer** and **Explanation** arrows below it. Both start closed; opening one does not open the other. The Explanation adds a short narrative about the reasoning. For integrated exam problems, it explains every labeled subpart.\n\n'

def records(name: str) -> list[dict[str, str]]:
    with (ROOT/'assessment'/name).open(encoding='utf-8',newline='') as stream:
        rows = list(csv.DictReader(stream,delimiter='\t'))
    if not rows or any(None in r or any(v is None for v in r.values()) for r in rows):
        raise ValueError('Malformed explanation input: '+name)
    keys=[r['id'] for r in rows]
    if len(keys)!=len(set(keys)):
        raise ValueError('Duplicate explanation ID: '+name)
    for row in rows:
        for field,text in row.items():
            if field.startswith('explanation'):
                if len(text.split())<20 or any(x in text for x in ('\n:::','TODO','PLACEHOLDER')):
                    raise ValueError('Missing or incomplete narrative: '+name+' '+row['id'])
    return rows

def strip_explanations(text: str) -> str:
    return EXPLANATION.sub('',text).replace(NOTICE,'')

def review_links(weeks: set[int]) -> str:
    return '**Review:** '+ ' · '.join(f'[Week {w} study guide](../study-guides/week{w:02d}-{SLUGS[w]}.qmd)' for w in sorted(weeks))+'.'

def load_notes():
    weekly={}
    for w in COUNTS:
        rows=records(f'explanations-week{w:02d}.tsv')
        assert len(rows)==COUNTS[w],(w,len(rows))
        weekly[w]={r['id']:r['explanation'] for r in rows}
    mc={r['id']:r['explanation'] for r in records('explanations-exam-mcq.tsv')}
    parts={r['id']:r for r in records('explanations-exam-integrated.tsv')}
    assert len(mc)==38 and len(parts)==25
    with (ROOT/'assessment/exam-mcq.tsv').open(encoding='utf-8',newline='') as f:
        mc_source=list(csv.DictReader(f,delimiter='\t'))
    with (ROOT/'assessment/exam-integrated.tsv').open(encoding='utf-8',newline='') as f:
        part_source={r['key']:r for r in csv.DictReader(f,delimiter='\t')}
    assert set(mc)=={r['key'] for r in mc_source}
    assert set(parts)==set(part_source)
    return weekly,mc,parts,mc_source,part_source

def add_explanations(out: dict[str,str]):
    weekly,mc,parts,mc_source,part_source=load_notes()
    audit={'version':'explanation-panels-v1','placement':'Independent collapsed sibling immediately after each existing Answer panel','basis':'Existing source-grounded questions, model answers and referenced weekly study guides; no outside scholarship added','pages':{},'integrated_exam_subpart_narratives':0}
    used_weekly={w:set() for w in COUNTS}
    used_mc={f:set() for f in (1,2,3)}
    used_parts={f:set() for f in (1,2,3)}
    for path,original in list(out.items()):
        week_match=re.fullmatch(r'practice/week(\d+)-[^/]+\.qmd',path)
        exam_match=re.fullmatch(r'practice/practice-part2-exam-(\d+)\.qmd',path)
        if not (week_match or exam_match):
            continue
        text=strip_explanations(original)
        old_answers=ANSWER.findall(text)
        seen=[]
        def replace(match):
            heading,body=match[1],match[2]
            answers=list(ANSWER.finditer(body))
            if len(answers)!=1:
                raise ValueError(f'{path}: expected one answer under {heading}, found {len(answers)}')
            if week_match:
                w=int(week_match[1]);anchor=re.search(r'\{#([^}]+)\}',heading)
                if anchor:key=anchor[1]
                else:
                    number=re.search(r'^Integrated Question (\d+)',heading)
                    if not number:raise ValueError('Unrecognized weekly heading: '+heading)
                    key=f'w{w:02d}-ix{int(number[1]):02d}'
                narrative=weekly[w][key];used_weekly[w].add(key);weeks={w};panel_key=key
            else:
                f=int(exam_match[1]);anchor=re.search(r'\{#([^}]+)\}',heading)[1]
                panel_key=f'exam{f:02d}-{anchor}'
                if anchor.startswith('q'):
                    stems=[r for r in mc_source if r[f'stem{f}'] in body.split(':::')[0]]
                    if len(stems)!=1:raise ValueError('Unmatched exam MCQ: '+heading)
                    row=stems[0];narrative=mc[row['key']];used_mc[f].add(row['key'])
                    weeks={int(i[1:3]) for i in row['ids'].split(',')}
                else:
                    keys=re.findall(r'<span id="(p\d[a-z])"></span>',body.split(':::')[0])
                    if not keys:raise ValueError('No labeled exam subparts: '+heading)
                    paragraphs=[];weeks=set()
                    for k in keys:
                        k='P'+k[1:];used_parts[f].add(k)
                        paragraphs.append(f'**({k[-1]})** '+parts[k][f'explanation{f}'])
                        weeks|={int(i[1:3]) for i in part_source[k]['ids'].split(',')}
                    narrative='\n\n'.join(paragraphs)
                    audit['integrated_exam_subpart_narratives']+=len(keys)
            panel=f'\n::: {{.callout-note .question-explanation #explanation-{panel_key} collapse="true" title="Explanation"}}\n{narrative}\n\n{review_links(weeks)}\n:::\n\n'
            a=answers[0];updated=body[:a.end()].rstrip()+'\n'+panel+body[a.end():]
            seen.append(panel_key)
            return '### '+heading+'\n'+updated
        revised=SECTION.sub(replace,text)
        expected=COUNTS[int(week_match[1])] if week_match else 43
        assert len(seen)==len(set(seen))==expected,(path,len(seen))
        assert old_answers==ANSWER.findall(revised),(path,'Answer changed')
        # Removing newly added panels must preserve every question, option,
        # answer, objective source line, heading and anchor apart from whitespace.
        normalize=lambda t:re.sub(r'\s+',' ',t).strip()
        assert normalize(strip_explanations(revised))==normalize(text),(path,'Existing content changed')
        first=re.search(r'(?m)^# (?:Part A|Exam Instructions)',revised)
        assert first is not None,path
        revised=revised[:first.start()]+NOTICE+revised[first.start():]
        out[path]=revised
        audit['pages'][path]={'answers':expected,'explanations':expected,'answer_sha256':hashlib.sha256(json.dumps(old_answers,ensure_ascii=False).encode()).hexdigest(),'panel_ids':seen}
    for w,notes in weekly.items():assert used_weekly[w]==set(notes),(w,'Unused weekly narrative')
    for f in (1,2,3):
        assert used_mc[f]==set(mc),(f,'Missing exam MCQ narrative')
        assert used_parts[f]==set(parts),(f,'Missing integrated subpart narrative')
    assert len(audit['pages'])==8
    assert sum(x['explanations'] for x in audit['pages'].values())==405
    assert audit['integrated_exam_subpart_narratives']==75
    audit['totals']={'weekly_explanations':276,'exam_explanations':129,'explanations':405,'answer_panels_retained':405,'independent_collapsed_panels':810}
    out['assessment/explanation-audit.json']=json.dumps(audit,ensure_ascii=False,indent=2)+'\n'
    out['EXPLANATION_PANELS_AUDIT.md']='''# Question explanations — V1

## Implementation

All five weekly practice banks and all three practice exams have a separate **Explanation** callout immediately after each existing **Answer** callout. Both panels are initially collapsed and use independent controls. An integrated exam problem has one explanation panel with a narrative for every labeled subpart, following its existing grouped model answer.

## Coverage

| Page | Answers retained | Explanations added |
|---|---:|---:|
| Week 8 | 59 | 59 |
| Week 9 | 59 | 59 |
| Week 10 | 49 | 49 |
| Week 11 | 55 | 55 |
| Week 12 | 54 | 54 |
| Exam 1 | 43 | 43 |
| Exam 2 | 43 | 43 |
| Exam 3 | 43 | 43 |
| **Total** | **405** | **405** |

The 15 exam integrated panels contain 75 form-specific subpart narratives. All 114 exam MCQ placements use the matching authored rationale for their common concept; parallel-form stems remain unchanged. Weekly narratives are authored by stable question/objective ID, not generated through keyword matching.

## Source basis and limits

Narratives explain the existing course questions and model answers, preserving the documented source terminology and discrepancies. They do not introduce outside scholarship or constitute a new independent scientific audit. Review links lead to the relevant weekly guide(s). Existing questions, option order, answers, objective wording, source lines, 100-mark exam scheme and 120-minute time budget remain unchanged.

## Reproduction and checks

Edit assessment/explanations-*.tsv. Run `python3 scripts/build_objective_assessments.py --write`, then `--check`; render Quarto and run `--check-html docs`. Checks require complete narrative coverage, unchanged answer text, unique panel IDs, paired Answer/Explanation order, no nesting of panels, initially closed controls, one-to-one collapse targets, existing objective anchors, and valid guide-image paths. Normal Pages publishing continues to render committed static QMD files with no new pre-render dependency.
'''
    return out,audit

class PanelParser(HTMLParser):
    """Inspect Quarto callouts without any third-party parsing dependency."""
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack=[];self.panels=[];self.ids=[]
    def handle_starttag(self,tag,attrs):
        attrs=dict(attrs);classes=attrs.get('class','').split()
        if attrs.get('id'):self.ids.append(attrs['id'])
        if tag!='div':return
        parents=[p for p in self.stack if p is not None]
        current=parents[-1] if parents else None
        if 'callout' in classes:
            if current is not None:raise AssertionError('Nested callouts; explanations must be siblings')
            typ='Explanation' if 'question-explanation' in classes else 'Answer' if 'callout-tip' in classes else 'Other'
            current={'type':typ,'id':attrs.get('id'),'headers':[],'bodies':[],'text':[]}
            self.panels.append(current);self.stack.append(current)
        else:
            self.stack.append(None)
        if current is not None:
            if 'callout-header' in classes:
                assert attrs.get('aria-expanded')=='false' and 'collapsed' in classes,attrs
                current['headers'].append(attrs)
            if 'callout-collapse' in classes:
                assert 'collapse' in classes and 'show' not in classes,attrs
                current['bodies'].append(attrs)
    def handle_endtag(self,tag):
        if tag=='div' and self.stack:self.stack.pop()
    def handle_data(self,data):
        parents=[p for p in self.stack if p is not None]
        if parents:parents[-1]['text'].append(data)

def validate_explanation_html(outdir: str):
    root=ROOT/outdir;audit=json.loads((ROOT/'assessment/explanation-audit.json').read_text())
    total=0
    for path,record in audit['pages'].items():
        html=(root/path.replace('.qmd','.html')).read_text()
        p=PanelParser();p.feed(html)
        assert len(p.ids)==len(set(p.ids)),(path,'Duplicate DOM IDs')
        assert len(p.panels)==record['answers']*2,(path,len(p.panels))
        assert [x['type'] for x in p.panels]==['Answer','Explanation']*record['answers'],path
        body_ids=[];selectors=[]
        for panel in p.panels:
            assert len(panel['headers'])==len(panel['bodies'])==1,(path,panel['id'])
            header=panel['headers'][0];body=panel['bodies'][0]
            assert header.get('aria-controls')==body.get('id'),(path,'Mismatched target')
            selector=header.get('data-bs-target','')
            assert selector.startswith('.') and selector[1:] in body.get('class','').split(),(path,selector)
            body_ids.append(body['id']);selectors.append(selector)
            assert panel['type'] in ''.join(panel['text']),(path,'Panel title missing')
        assert len(body_ids)==len(set(body_ids))==len(set(selectors)),(path,'Shared controls')
        assert [x['id'] for x in p.panels if x['type']=='Explanation']==['explanation-'+i for i in record['panel_ids']],path
        if 'exam-' in path:
            narrative=' '.join(''.join(x['text']) for x in p.panels if x['type']=='Explanation')
            assert len(re.findall(r'\([a-f]\)',narrative))==25,(path,'Missing subpart explanations')
        total+=record['explanations']
    assert total==405
    print('EXPLANATION HTML PASS: 405 paired explanations; 810 independently closed panels; 75 integrated subpart narratives; unique targets and IDs.')
