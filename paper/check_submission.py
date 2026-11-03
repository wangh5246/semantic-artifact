"""Single-PDF S&P 2027 page/format/reference gates, with explicit scope."""
from pathlib import Path
import re,json
from collections import Counter
from pypdf import PdfReader
from prepare_anonymous_source import anonymous_source
ROOT=Path(__file__).resolve().parent

def require(value,message):
    if not value:raise AssertionError(message)

def included_sources(path,seen=None):
    """Expand local inputs so included tables and proofs share the same gates."""
    seen=set() if seen is None else seen
    path=path.resolve()
    require(path.is_relative_to(ROOT),'input escapes submission directory')
    require(path not in seen,'duplicate or cyclic input: '+path.name)
    seen.add(path)
    source=path.read_text()
    pieces=[source]
    for name in re.findall(r'\\input\{([^}]+)\}',source):
        child=ROOT/name
        if not child.suffix:child=child.with_suffix('.tex')
        pieces.append(included_sources(child,seen))
    return '\n'.join(pieces)

def check_appendix_font_source(source):
    """Reject reduced body size in the appendix; local table sizing is separate."""
    require(source.count(r'\appendices') == 1, 'missing or duplicate appendix boundary')
    appendix = source.split(r'\appendices', 1)[1]
    appendix = re.sub(r'(?m)(?<!\\)%.*$', '', appendix)
    appendix = re.sub(r'\\begin\{table\*?\}.*?\\end\{table\*?\}', '', appendix, flags=re.S)
    require(not re.search(r'\\(?:small|footnotesize|scriptsize|tiny)\b', appendix),
            'format override: reduced appendix body font')


def check_appendix_pdf_font(pages):
    """Check the dominant extracted text size on each appendix page, not tables."""
    for number, page in pages:
        sizes = Counter()
        def count(text, cm, tm, font, size):
            if text.strip():
                sizes[round(abs(float(cm[0])) * float(size), 1)] += len(text.strip())
        page.extract_text(visitor_text=count)
        require(sizes and sizes.most_common(1)[0][0] == 10.0,
                f'appendix page {number}: dominant text is not 10pt')

def main():
    source=(ROOT/'submission.tex').read_text();app=(ROOT/'appendix.tex').read_text()
    pre=(ROOT/'preamble.tex').read_text();combined=included_sources(ROOT/'submission.tex')
    require((ROOT/'build/submission-anonymous.tex').read_text()==anonymous_source(source),'anonymous build input differs from current source')
    check_appendix_font_source(source)
    require(r'\documentclass[conference,compsoc]{IEEEtran}' in source,'wrong document class')
    require('Document Class: IEEEtran 2015/08/26 V1.8b' in (ROOT/'build/current/submission.log').read_text(),'class is not IEEEtran 1.8b')
    require(r'\externaldocument' not in pre,'external PDF dependency remains')
    require(r'\input{citations}' not in source,'uncited bibliography forced into submission')
    require(source.count(r'\printbibliography')==1 and r'\printbibliography' not in app,'duplicate bibliography')
    require(not re.search(r'\\(?:usepackage|RequirePackage)(?:\[[^\]]*\])?\s*\{[^}]*\bgeometry\b',combined),
            'format override: geometry package')
    require(not re.search(r'\\(?:geometry|newgeometry|restoregeometry)\b',combined),
            'format override: geometry command')
    for token in ('baselinestretch','vspace{-','fontsize'):
        require(token not in combined,'format override: '+token)
    require(not re.search(r'\\(?:setlength|addtolength)\s*\{\\(?:textheight|textwidth|topmargin|oddsidemargin)\}',combined),'page layout length override')
    labels=re.findall(r'\\label\{([^}]+)\}',combined)
    require(not [k for k,v in Counter(labels).items() if v>1],'duplicate labels')
    refs=re.findall(r'\\(?:ref|eqref|autoref)\{([^}]+)\}',combined)
    require(not set(refs)-set(labels),'unresolved source references')
    for label in ('def:trace-closure','sec:boundaries','prop:rectangularity-main',
                  'thm:interface-separation-main','thm:main-semantic-closure',
                  'sec:eval-ladder','eq:window-quota','eq:final-report-set','sec:threat'):
        require(r'\label{'+label+'}' in combined,'core object missing from body: '+label)
    for token in ('weak-trust-protocol','independent-native','Game~3','Game~4','v7','schema-v2','PLONK'):
        require(token not in combined,'removed branch remains: '+token)
    prose=re.sub(r'(?m)^\s*%.*$', '', combined)
    prose=re.sub(r'\\(?:label|input)\{[^}]*\}', '', prose)
    # Library type names and call syntax belong in the reproducibility artifact.
    # Public protocol names such as Prio3Histogram remain ordinary prose.
    internal_patterns=(r'\bXof[A-Z][A-Za-z0-9_]*\b', r'\bField128\b',
                       r'Prio3Histogram\s*\(', r'\\texttt\{[^}]*\}')
    for pattern in internal_patterns:
        require(not re.search(pattern,prose),'internal code in manuscript source: '+pattern)
    for pattern in (r'\bV[234]\b', r'\bversion-[234]\b', r'\b(?=[0-9a-f]{16,64}\b)(?=[0-9a-f]*[a-f])[0-9a-f]+\b',
                    r'\bSHA-256\b', r'\bartifact manifest\b', r'\bmanifest-selection\b'):
        require(not re.search(pattern,prose),'internal manuscript material: '+pattern)
    log=(ROOT/'build/final.log').read_text()
    for token in ('undefined references','undefined on input line','multiply defined',
                  'Label(s) may have changed','Rerun to get','Please rerun',
                  'Overfull \\hbox','Overfull \\vbox','destination with the same identifier'):
        require(token not in log,'LaTeX gate failed: '+token)
    reader=PdfReader(ROOT/'submission.pdf')
    require((reader.metadata.get('/Author') or '')=='','PDF author identity remains')
    texts=[page.extract_text() or '' for page in reader.pages]
    pdf_prose='\n'.join(texts)
    for pattern in internal_patterns[:3]:
        require(not re.search(pattern,pdf_prose),'internal code in manuscript PDF: '+pattern)
    author=re.search(r'\\author\s*\{([^{}]*)\}',source)
    if author and author.group(1).strip():
        name=' '.join(author.group(1).split()).casefold()
        require(name not in ' '.join(' '.join(t.split()) for t in texts).casefold(),'visible author name remains in PDF')
    for page in reader.pages:
        require(abs(float(page.mediabox.width)-612)<.01 and abs(float(page.mediabox.height)-792)<.01,'page is not US Letter')
    aux=(ROOT/'build/current/submission.aux').read_text()
    def label_page(name):
        match=re.search(r'\\newlabel\{'+re.escape(name)+r'\}\{\{[^}]*\}\{(\d+)\}',aux)
        require(match is not None,'missing PDF boundary: '+name)
        return int(match.group(1))
    references=label_page('boundary:references');appendix=label_page('boundary:appendix')
    body_pages=references-1;ref_pages=appendix-references;app_pages=len(reader.pages)-appendix+1
    check_appendix_pdf_font(enumerate(reader.pages[appendix-1:], start=appendix))
    require(body_pages<=13,'body exceeds 13 pages')
    require(ref_pages+app_pages<=5,'references + appendix exceed 5 pages')
    require(len(reader.pages)<=18,'total exceeds 18 pages')
    require(texts[references-1].lstrip().startswith('References'),'references boundary not explicit')
    require(texts[appendix-1].lstrip().startswith('Appendix A.'),'appendix boundary not explicit')
    for i in range(13,len(texts)):
        require(i+1>=references,'body text past page 13')
    require(not any('??' in t for t in texts),'unresolved PDF marker')
    for token in ('/Users/','researcher','Supplementary','Supplemental Material','Appendix J'):
        require(not any(token in t for t in texts),'PDF anonymity/scope token: '+token)
    entries=re.findall(r'\\entry\{([^}]+)\}',(ROOT/'build/current/submission.bbl').read_text())
    cited=set()
    for group in re.findall(r'\\cite\{([^}]+)\}',combined):cited.update(x.strip() for x in group.split(','))
    require(set(entries)==cited,'bibliography is not the cited set')
    result={'all_passed':True,'body_pages':body_pages,'reference_pages':ref_pages,
            'appendix_pages':app_pages,'total_pages':len(reader.pages),'cited_references':len(entries),
            'format':'IEEEtran 1.8b conference,compsoc; US Letter; appendix dominant text 10pt',
            'limits':['font checks cover direct source size switches and dominant PDF text, not every glyph or macro expansion',
                      'format/source checks do not establish acceptance or complete research validity',
                      'repository anonymity and HotCRP disclosures require separate author preparation']}
    (ROOT/'build/submission-check.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
if __name__=='__main__':main()
