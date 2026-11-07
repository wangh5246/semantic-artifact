"""Prepare an anonymous build input without changing the editable author draft."""
from pathlib import Path
import re
ROOT=Path(__file__).resolve().parent

def anonymous_source(source):
    matches=list(re.finditer(r'\\author\s*\{',source))
    if len(matches)!=1:raise ValueError('expected exactly one author declaration')
    m=matches[0];depth=1;i=m.end()
    while i<len(source) and depth:
        if source[i]=='\\':i+=2;continue
        if source[i]=='{':depth+=1
        elif source[i]=='}':depth-=1
        i+=1
    if depth:raise ValueError('unclosed author declaration')
    return source[:m.start()]+r'\author{}'+source[i:]

if __name__=='__main__':
    build=ROOT/'build';build.mkdir(exist_ok=True)
    (build/'submission-anonymous.tex').write_text(anonymous_source((ROOT/'submission.tex').read_text()))
