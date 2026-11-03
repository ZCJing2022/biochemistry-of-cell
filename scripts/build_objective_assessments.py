#!/usr/bin/env python3
"""Generate/check static Quarto assessments from the reviewed objective records.

Run once with --write after changing assessment/*.tsv. Commit the generated QMDs.
Normal Pages publishing does NOT run this script and has no new build dependency.
"""
from __future__ import annotations
import argparse, csv, io, json, random, re
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SLUGS = {8:'bioenergetics-enzymes',9:'glycolysis-cac',10:'etc-oxidative-phosphorylation',11:'lipids-eicosanoids-drugs',12:'cell-signaling-part1'}
TITLES = {8:'Bioenergetics and Enzymes',9:'Glycolysis, Pyruvate, and the Citric Acid Cycle',10:'Electron Transport and Oxidative Phosphorylation',11:'Lipids, Eicosanoids, and Drug Action',12:'Cell Signaling, Part I'}
COUNTS = {8:19,9:20,10:9,11:16,12:14}
EXTRAS = {8:5,9:4,10:5,11:4,12:5}
RETIRED = {'w11-lecture-eicosanoids.jpg':11,'w12-tutorial-rasmap.jpg':12}
GROUPS = [('P1','Glucose, enzymes and pathway direction',15),('P2','Carbon, electrons and compartments',16),('P3','Rates, ATP substrates and adipose tissue',9),('P4','Lipid mediators and drug mechanisms',16),('P5','Receptor activation and reversible switches',12)]
SOURCE_NOTES = '''## Source wording and counting notes {#source-notes}

These assessments follow the supplied Learning Objectives, lecture presentations, tutorials and assigned Alberts chapters. The original objective wording below is retained, with whitespace and mathematical glyphs normalized. Questions make compound requirements explicit rather than silently treating a topic mention as coverage.

- **Week 9, reaction 6:** slide 9:14 calls this substrate-level phosphorylation, whereas slides 9:17–9:18 show production of 1,3-BPG in reaction 6 and direct ATP formation in reaction 7. The questions distinguish these steps and include all three consequences named on slide 9:14, including the NAD+ requirement for anaerobic continuation.
- **Week 9, counting basis:** the overview (9:6) and accounting give two NADH per glucose. Slide 9:19 also contains a one-NADH label. Questions explicitly distinguish per-three-carbon-unit, per-pyruvate, per-cycle-turn and per-glucose counts; they use the complete per-glucose accounting.
- **Week 10, location:** slide 10:3 says the ETC is in the matrix; the detailed structure/ETC slides 10:5 and 10:9 place its proteins in the inner membrane. The assessment uses the explicit membrane/compartment description, also supported by Alberts Chapter 14.
- **Week 11, aspirin target:** slide 11:17 uses “PGH2” in its aspirin explanation, while 11:13–11:14 identify covalent modification of COX/PGHS. Questions distinguish the enzyme PGHS from its product PGH2.
- **Week 11, pharmacology wording:** “bioavailability” follows the lecture's stated operational meaning, the amount of drug in circulation. The TI exercises supply dose values and use TD50/ED50 (or LD50/ED50); the lecture's diagram uses ED50 although adjacent text also says EC50. Exercises are not clinical prescribing advice.
- **Week 12, terminology:** objective 1 says “intracellular”; lecture 12:3 calls the four listed modes **intercellular** signaling. Slides 12:10–12:12 use “GPCRs” as shorthand for the receptor-associated G-protein arrangement; the questions distinguish the seven-pass receptor from its heterotrimeric G protein.
- **Week 12, adaptor connection:** one sentence on lecture 12:20 names Src in the Sos connection. Tutorial 7, PDF p. 15, explicitly describes Grb2–Sos; that is the assembly used in the pathway questions. Ras activates Raf by binding, not by phosphorylating it.

The 38-ATP illustration in Week 10 is labeled FYI. These exams do not require a new ATP-per-carrier convention or add topics outside the learning-objective scope.
'''

def table(name):
    with (ROOT/'assessment'/name).open(encoding='utf-8',newline='') as f:
        rows=list(csv.DictReader(f,delimiter='\t'))
    if not rows or any(None in r or any(v is None for v in r.values()) for r in rows):
        raise ValueError('Malformed tab-separated input: '+name)
    return rows

def ids(row): return row['ids'].split(',')
def answer(text): return '\n::: {.callout-tip collapse="true" title="Answer"}\n'+text.strip()+'\n:::\n'
def mdlink(label,url): return f'[{label}]({url})'
def weekly_path(w): return f'practice/week{w:02d}-{SLUGS[w]}.qmd'

def source_text(idlist,registry):
    refs=list(dict.fromkeys(registry[i]['source'] for i in idlist))
    return '**Objectives:** '+', '.join(idlist)+'. **Source:** '+'; '.join(refs)+'.'

def render_mc(number,stem,correct,distractors,explanation,target,rng,anchor,source=''):
    wrong=sorted(distractors);rng.shuffle(wrong)
    options=wrong[:];options.insert('ABCD'.index(target),correct)
    result=f'### Question {number} {{#{anchor}}}\n\n{stem}\n\n'
    result+='\n'.join(f'- **{letter}.** {option}' for letter,option in zip('ABCD',options))+'\n'
    result+=answer(f'**Correct answer: {target}.** {correct}\n\n{explanation}'+('\n\n'+source if source else ''))
    return result

def rebalance_old(block,target,rng,number,w):
    option_matches=list(re.finditer(r'(?m)^- \*\*([ABCD])\.\*\* (.+)$',block))
    assert len(option_matches)==4, (w,number,'options')
    correct=re.search(r'Correct answer:\s*([ABCD])\.',block).group(1)
    values={m.group(1):m.group(2) for m in option_matches}
    special=any(re.search(r'(?i)(all of the above|both [ABCD] and [ABCD]|none of the above)',s) for s in values.values())
    if special:
        assert target==correct
    else:
        wrong=sorted(v for k,v in values.items() if k!=correct);rng.shuffle(wrong)
        out=wrong[:];out.insert('ABCD'.index(target),values[correct])
        for m,v in reversed(list(zip(option_matches,out))):
            block=block[:m.start()]+f'- **{m.group(1)}.** {v}'+block[m.end():]
        block=re.sub(r'(Correct answer:\s*)[ABCD](\.)',lambda m:m[1]+target+m[2],block,count=1)
    lines=block.strip().splitlines()
    heading=re.sub(r'\s*\{#[^}]+\}\s*$','',lines[0])
    heading=re.sub(r'^### Question \d+',f'### Question {number}',heading)
    lines[0]=heading+f' {{#w{w:02d}-mc{number:02d}}}'
    return '\n'.join(lines)+'\n'

def weekly(w,objectives,topups):
    old=(ROOT/weekly_path(w)).read_text(encoding='utf-8')
    blocks=re.findall(r'(?ms)^### Question \d+[^\n]*\n.*?(?=^### (?:Question|Integrated)|^# |\Z)',old)
    mc=[b for b in blocks if len(re.findall(r'(?m)^- \*\*[ABCD]\.\*\* ',b))==4]
    assert len(mc) in ({35} if w==8 else {30,35}), (w,len(mc))
    new=topups if len(mc)==30 else []
    assert len(mc)+len(new)==35
    oldkeys=[];fixed={}
    for n,b in enumerate(mc):
        k=re.search(r'Correct answer:\s*([ABCD])\.',b).group(1);oldkeys.append(k)
        if re.search(r'(?im)^- \*\*[ABCD]\.\*\*.*(?:all of the above|both [ABCD] and [ABCD]|none of the above)',b):fixed[n]=k
    counts=Counter(dict(zip('ABCD',[9,9,9,8])))
    for k in fixed.values():counts[k]-=1
    pool=[k for k in 'ABCD' for _ in range(counts[k])];rng=random.Random(700+w);rng.shuffle(pool)
    targets=[]
    for n in range(35):targets.append(fixed[n] if n in fixed else pool.pop())
    title=f'Week {w} Practice — {TITLES[w]}'
    text=f'---\ntitle: "{title}"\ntoc-depth: 2\n---\n\n<!-- objective-coverage-v2 -->\n\n**35 multiple-choice questions**, followed by **{len(objectives)} objective-led questions** and retained integrated practice. Each original learning-objective item has its own question and worked answer, including every part of compound objectives. Answers are initially collapsed.\n\n[Check objective coverage across the weekly bank and all three exams](learning-objective-coverage.qmd#week-{w}). The final integrated questions are additional practice, not substitutes for the objective questions.\n\n# Part A — Multiple Choice\n\n'
    for n,b in enumerate(mc,1):text+=rebalance_old(b,targets[n-1],rng,n,w)+'\n'
    for n,row in enumerate(new,len(mc)+1):
        text+=render_mc(n,row['stem'],row['correct'],[row[f'd{i}'] for i in range(1,4)],row['explanation'],targets[n-1],rng,f'w{w:02d}-mc{n:02d}','**Related objectives:** '+row['ids'])+'\n'
    text+='# Part B — Every Learning Objective\n\nAnswer each prompt before opening its model answer. The source sheet supplies the objective; the task underneath makes the required components explicit.\n\n'
    for n,row in enumerate(objectives,1):
        text+=f'### Objective {row["id"]} — {row["theme"]} {{#w{w:02d}-lo{n:02d}}}\n\n**Original objective:** {row["objective"]}\n\n{row["question"]}\n'
        text+=answer(row['answer']+'\n\n**Source:** '+row['source']+'.')+'\n'
    oldmarker='# Part D — Integrated Practice' if w==8 and '<!-- objective-coverage-v2 -->' not in old else '# Part C — Integrated Practice'
    assert oldmarker in old,(w,'missing integrated section')
    extra=old.split(oldmarker,1)[1].strip()
    if not extra.startswith('### Integrated Question'):
        index=iter(range(1,EXTRAS[w]+1))
        extra=re.sub(r'(?m)^### Question \d+',lambda _:f'### Integrated Question {next(index)}',extra)
    assert len(re.findall(r'(?m)^### Integrated Question ',extra))==EXTRAS[w]
    text+='# Part C — Integrated Practice\n\n'+extra+'\n'
    assert text.count('collapse="true"')==35+len(objectives)+EXTRAS[w]
    return text,Counter(targets)

def mixed_order(mc,form):
    rng=random.Random(5100+form);buckets={w:[] for w in range(8,13)}
    for r in mc:buckets[int(ids(r)[0][1:3])].append(r)
    for b in buckets.values():rng.shuffle(b)
    order=[]
    while any(buckets.values()):
        weeks=[w for w,b in buckets.items() if b];rng.shuffle(weeks)
        for w in weeks:order.append(buckets[w].pop())
    return order

def exam(form,mc,parts,registry):
    order=mixed_order(mc,form);rng=random.Random(9100+form)
    letters=list('A'*10+'B'*10+'C'*9+'D'*9);rng.shuffle(letters)
    modes={1:'Mechanisms and explanation',2:'Diagnosing misconceptions',3:'Application and prediction'}
    text=f'---\ntitle: "Practice Exam {form} — Part II (Weeks 8–12)"\nsubtitle: "{modes[form]} · Complete learning-objective coverage"\ntoc-depth: 2\ntoc-title: "Practice Exam Contents"\n---\n\n<!-- objective-coverage-v2 -->\n\n# Exam Instructions\n\n**Time: 120 minutes. Total: 100 marks.** All 78 items in the supplied Week 8–12 Learning Objectives are assessed in this exam, through 38 mixed-order MCQs and five structured integrated problems. Complete every subpart; naming a topic alone is not a complete answer to an explanation or comparison prompt.\n\nAllocate **42 minutes to Section A**, **68 minutes to Section B**, and **10 minutes to checking**. Timing is a design budget, not a student-pilot measurement. Use brief explanations, labeled sequences and compact accounting tables rather than long essays. A basic calculator is sufficient. Pharmacology questions assess course mechanisms, not clinical recommendations.\n\nAnswers are hidden initially. Each question has an Answer arrow. Objective tags and sources are inside the answers so the MCQ order is not a week-by-week checklist. The [coverage map](learning-objective-coverage.qmd) is for checking after the attempt.\n\n# Section A — Multiple Choice\n\n**38 questions × 1 mark = 38 marks. Choose one best answer.**\n\n'
    locations={}
    for n,(r,letter) in enumerate(zip(order,letters),1):
        text+=render_mc(n,r[f'stem{form}'],r['correct'],[r[f'd{i}'] for i in range(1,4)],r['explanation'],letter,rng,f'q{n:02d}',source_text(ids(r),registry))+'\n'
        for ident in ids(r):locations[ident]=f'Q{n}|q{n:02d}'
    text+='# Section B — Integrated Short Answer\n\n**62 marks. Answer all five problems and every subpart.**\n\n'
    for g,title,minutes in GROUPS:
        rows=[r for r in parts if r['key'].startswith(g)];marks=sum(int(r['marks']) for r in rows)
        text+=f'### Integrated Problem {g[1:]} — {title} {{#{g.lower()}}}\n\n**{marks} marks · Suggested time: {minutes} minutes.**\n\n'
        answers=[]
        for r in rows:
            letter=r['key'][-1];anchor=r['key'].lower()
            text+=f'<span id="{anchor}"></span>\n\n**({letter}) [{r["marks"]} marks]** {r[f"prompt{form}"]}\n\n'
            answers.append(f'**({letter})** {r[f"answer{form}"]}\n\n'+source_text(ids(r),registry))
            for ident in ids(r):locations[ident]=f'P{g[1:]}({letter})|{anchor}'
        text+=answer('\n\n'.join(answers))+'\n'
    text+='# Coverage and self-check\n\nThis parallel form covers the same 78 objectives as the other forms, but uses different MCQ stems, mixed order, answer positions and structured tasks. Repeated concepts are intentional; these are not independent topic samples. Use the [objective-by-objective map](learning-objective-coverage.qmd) to locate omissions in your own answers. A model answer is a self-marking guide, not a prediction of the instructor’s examination.\n'
    assert set(locations)==set(registry),(form,sorted(set(registry)-set(locations)))
    assert text.count('collapse="true"')==43
    return text,locations,Counter(letters)

class AssetParser(HTMLParser):
    def __init__(self):super().__init__();self.images=[];self.ids=set();self.collapsed=0
    def handle_starttag(self,tag,attrs):
        d=dict(attrs)
        if d.get('id'):self.ids.add(d['id'])
        if tag=='img':self.images.append(d.get('src',''))
        if tag=='div' and 'callout-collapse' in d.get('class','').split():
            assert 'show' not in d.get('class','').split(),'An answer is initially open'
            self.collapsed+=1

def check_html(outdir):
    out=ROOT/outdir
    data=json.loads((ROOT/'assessment/coverage-audit.json').read_text())
    for w in range(8,13):
        p=out/weekly_path(w).replace('.qmd','.html');a=AssetParser();a.feed(p.read_text())
        assert a.collapsed==35+COUNTS[w]+EXTRAS[w],(p,a.collapsed)
        for n in range(1,COUNTS[w]+1):assert f'w{w:02d}-lo{n:02d}' in a.ids
    for form in (1,2,3):
        p=out/f'practice/practice-part2-exam-{form:02d}.html';a=AssetParser();a.feed(p.read_text())
        assert a.collapsed==43,(p,a.collapsed)
        for row in data['objectives']:
            anchor=row[f'exam{form}'].split('|')[1];assert anchor in a.ids,(p,anchor)
    for w in range(8,13):
        p=out/f'study-guides/week{w:02d}-{SLUGS[w]}.html';a=AssetParser();a.feed(p.read_text())
        for src in a.images:
            if src.startswith(('http:','https:','data:')):continue
            assert not any(name in src for name in RETIRED),(p,src)
            assert (p.parent/src.split('?')[0]).resolve().exists(),(p,src)
    print('HTML PASS: weekly/objective/exam answers collapsed; all 78 exam links resolve; retained guide assets exist.')

def outputs():
    objs={w:table(f'week{w:02d}.tsv') for w in range(8,13)}
    for w,rows in objs.items():assert [r['id'] for r in rows]==[f'W{w:02d}-{i:02d}' for i in range(1,COUNTS[w]+1)]
    registry={r['id']:r for rows in objs.values() for r in rows};assert len(registry)==78
    mc=table('exam-mcq.tsv');parts=table('exam-integrated.tsv');topups=table('weekly-topups.tsv')
    assert len(mc)==38 and len(parts)==25 and len(topups)==20
    assert sum(int(r['marks']) for r in parts)==62
    assert len({r[f'stem{f}'] for r in mc for f in (1,2,3)})==114,'Repeated exact exam MCQ stem'
    for r in mc+parts+topups:assert set(ids(r))<=set(registry)
    out={};weekly_keys={};exam_keys={};maps={}
    for w in range(8,13):out[weekly_path(w)],weekly_keys[w]=weekly(w,objs[w],[r for r in topups if int(r['week'])==w])
    for f in (1,2,3):out[f'practice/practice-part2-exam-{f:02d}.qmd'],maps[f],exam_keys[f]=exam(f,mc,parts,registry)
    records=[]
    for w,rows in objs.items():
        for n,r in enumerate(rows,1):records.append({'id':r['id'],'week':w,'objective':r['objective'],'weekly':f'{weekly_path(w)}#w{w:02d}-lo{n:02d}',**{f'exam{f}':maps[f][r['id']] for f in (1,2,3)},'source':r['source']})
    page='---\ntitle: "Learning Objectives — Complete Practice Coverage"\ntoc-depth: 2\n---\n\n## How to use this map\n\nThe five original Learning Objectives sheets contain **78 items: 19 + 20 + 9 + 16 + 14**. Each has a dedicated weekly question with a worked answer. Each two-hour exam also assesses all 78 items; compound objectives are assigned to a question/subpart that explicitly asks for their components.\n\nThe map is an assessment-design record, not a claim that a keyword match proves understanding. Read the whole prompt and answer. Exam timing is planned rather than empirically validated. The three forms cover the same syllabus deliberately.\n\n'
    for w,rows in objs.items():
        page+=f'## Week {w} {{#week-{w}}}\n\nSource: `Week {w} Learning objectives.pdf`, PDF p. 1, items 1–{COUNTS[w]} in original order.\n\n| ID | Original objective | Weekly practice | Exam 1 | Exam 2 | Exam 3 |\n|---|---|---|---|---|---|\n'
        for n,r in enumerate(rows,1):
            cells=[r['id'],r['objective'].replace('|','/'),mdlink('Worked question',f'week{w:02d}-{SLUGS[w]}.qmd#w{w:02d}-lo{n:02d}')]
            for f in (1,2,3):
                label,anchor=maps[f][r['id']].split('|');cells.append(mdlink(label,f'practice-part2-exam-{f:02d}.qmd#{anchor}'))
            page+='| '+' | '.join(cells)+' |\n'
        page+='\n'
    page+=SOURCE_NOTES
    out['practice/learning-objective-coverage.qmd']=page
    audit={'version':'objective-coverage-v2','source_objectives':78,'weekly_counts':{str(w):{'mcq':35,'objective_questions':COUNTS[w],'integrated_extra':EXTRAS[w],'answers':35+COUNTS[w]+EXTRAS[w]} for w in range(8,13)},'exam_counts':{'mcq':38,'integrated_problems':5,'integrated_subparts':25,'marks':100,'minutes':120,'answer_callouts':43,'objectives_each':78},'weekly_answer_letters':weekly_keys,'exam_answer_letters':exam_keys,'objectives':records,'retired_raster_images':list(RETIRED),'limits':'Coverage IDs/anchors/counts are machine checked. Source alignment and answer completeness were editorially reviewed. Timing has not been student-piloted.'}
    out['assessment/coverage-audit.json']=json.dumps(audit,ensure_ascii=False,indent=2)+'\n'
    buf=io.StringIO();writer=csv.DictWriter(buf,fieldnames=list(records[0]),lineterminator='\n');writer.writeheader();writer.writerows(records);out['assessment/coverage-map.csv']=buf.getvalue()
    index=(ROOT/'practice/index.qmd').read_text()
    marker='## Learning-objective coverage'
    if marker not in index:
        index+='\n\n'+marker+'\n\n[Open the complete objective-to-question map](learning-objective-coverage.qmd). All **78** source objectives have worked weekly questions and assessed locations in **each** of the three 120-minute exams. Weekly banks contain 35 MCQs plus objective-led and integrated responses. Each exam has 38 MCQs, five integrated problems and 100 marks.\n'
    out['practice/index.qmd']=index
    for name,w in RETIRED.items():
        path=f'study-guides/week{w:02d}-{SLUGS[w]}.qmd';text=(ROOT/path).read_text()
        text,n=re.subn(r'\n*<figure\b[^>]*>\s*(?:(?!</figure>).)*'+re.escape(name)+r'(?:(?!</figure>).)*</figure>','',text,flags=re.S)
        assert n in (0,1),(name,n)
        assert name not in text
        out[path]=text
    report='# Learning-objective and image-quality audit — V2\n\n'
    report+='## Verified structure\n\n78 source objectives in original order; 35 MCQs per weekly bank; one explicit worked question per objective; 23 retained integrated weekly questions. Total weekly items: 276. Each exam: 38 MCQs + 5 integrated problems (25 subparts), 100 marks, 120-minute planning budget. Every exam maps all 78 objective IDs. Correct-letter counts differ by at most one within each bank/form; exact exam MCQ stems are distinct across forms. Conceptual overlap is intentional.\n\n'
    report+='## Images\n\nRemoved the two remaining low-resolution raster slide images from the Week 11 and Week 12 guides and active assets. Their existing sharp course diagrams remain. The source slide artwork itself contains raster material; enlarging or re-saving it is not evidence of recovered detail. The three textbook source-vector figures from PR #8 remain. No new image-generation or archive-extraction step is introduced.\n\n'
    report+='## Reproduction\n\nEdit assessment/*.tsv; run `python3 scripts/build_objective_assessments.py --write`, then `--check`, render Quarto, then `--check-html docs`. Commit the generated QMD/coverage files. Normal Pages builds read the static QMDs; no pre-render hook is added. Source text/counts were checked against the five uploaded Learning Objectives PDFs, not inferred from the guides.\n\n'
    report+='## Limits\n\nThe automated checks establish IDs, counts, option/answer structure, coverage links and generated-output consistency; they do not mechanically prove the scientific correctness of prose. Timing is a design budget, not a student-pilot result.\n\n'+SOURCE_NOTES
    out['OBJECTIVE_COVERAGE_AUDIT.md']=report
    for path in ('QA_AUDIT.md','PRACTICE_EXAMS_AUDIT.md'):
        if (ROOT/path).exists():
            t=(ROOT/path).read_text();notice='> Historical audit: current counts and objective-level coverage are superseded by `OBJECTIVE_COVERAGE_AUDIT.md` and `assessment/coverage-map.csv`.\n\n'
            if not t.startswith(notice):t=notice+t
            out[path]=t
    path='SOURCE_FIGURE_PERMISSIONS_REGISTER.md';reg=(ROOT/path).read_text();ret=[];kept=[]
    for line in reg.splitlines():
        if '## Retired low-resolution slide copies' not in reg and line.startswith('|') and any(name in line for name in RETIRED):ret.append(line)
        else:kept.append(line)
    if ret:
        reg='\n'.join(kept).rstrip()+'\n\n## Retired low-resolution slide copies\n\nRemoved from the displayed guides and active assets during the objective-coverage revision; sharp course diagrams remain. This retains the source history and does not assert permission.\n\n| ID | Week | Former asset | Source type | Source | PDF page | Figure | Former placement | Prior permission status |\n|---|---:|---|---|---|---:|---|---|---|\n'+'\n'.join(ret)+'\n'
    out[path]=reg
    path='SOURCE_FIGURE_LAYER_AUDIT.md';t=(ROOT/path).read_text();note='> Current update: the low-resolution Week 11 and Week 12 raster source slides have been retired. The three sharp textbook source-vector figures remain. See `OBJECTIVE_COVERAGE_AUDIT.md`.\n\n'
    if not t.startswith(note):t=note+t
    out[path]=t
    path='VISUAL_STUDY_GUIDE_STANDARD_LOCKED.md';t=(ROOT/path).read_text();note='\n\n## Image-quality gate — objective-coverage revision\n\nDo not retain an original source image merely for provenance if its labels are unreadable at a useful display size. Use a verified sharp source extraction, or remove the low-resolution copy while retaining the explanatory diagram. Do not treat upscaling or a larger saved pixel count as recovered detail. Keep inline originals compact and provide enlargement links for retained vector detail.\n'
    if '## Image-quality gate — objective-coverage revision' not in t:t=t.rstrip()+note
    out[path]=t
    return out,audit

def main():
    parser=argparse.ArgumentParser();g=parser.add_mutually_exclusive_group(required=True);g.add_argument('--write',action='store_true');g.add_argument('--check',action='store_true');g.add_argument('--check-html',metavar='OUTPUT_DIR');args=parser.parse_args()
    if args.check_html:check_html(args.check_html);return
    out,audit=outputs()
    if args.write:
        for path,text in out.items():p=ROOT/path;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(text,encoding='utf-8')
        for name in RETIRED:(ROOT/'assets/source-figures'/name).unlink(missing_ok=True)
        print(f'Wrote {len(out)} text files; removed {len(RETIRED)} low-resolution assets.')
    else:
        bad=[p for p,t in out.items() if not (ROOT/p).exists() or (ROOT/p).read_text()!=t]
        assert not bad,'Generated files out of date: '+', '.join(bad)
        assert not any((ROOT/'assets/source-figures'/name).exists() for name in RETIRED)
        for key in ('weekly_answer_letters','exam_answer_letters'):
            for _,c in audit[key].items():assert max(c.values())-min(c.values())<=1
        print('SOURCE PASS: 78 objectives; 35 MCQs per week; all 78 in each 38+5 exam; 100 marks; balanced keys; idempotent static output.')
if __name__=='__main__':main()
