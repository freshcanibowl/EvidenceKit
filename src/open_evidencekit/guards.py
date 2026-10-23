"""Conservative English cue-based abstention, not semantic verification or NER.

These guards trade coverage for review. They are incomplete, may over-abstain,
and cannot prove that an input without a matched cue is safe or factual.
"""
import re

SUBJECT = re.compile(r'^([A-Z][a-z]{1,30})\s+(?:ate|drank|walked|slept|played|barked|sat|rested|is|was|has|had|did|finished|refused|approached|went)\b')
STOP_SUBJECTS = {'The','This','That','There','One','Some','Nothing','Someone','Everyone','Nobody'}

def leading_subject(text):
    m=SUBJECT.match(text.strip())
    return m.group(1) if m and m.group(1) not in STOP_SUBJECTS else None

def guard_reasons(claim, evidence):
    reasons=set()
    if re.search(r'\d',claim['text']): reasons.add('NUMERIC_CLAIM_REQUIRES_REVIEW')
    subject=leading_subject(claim['text'])
    for e in evidence:
        text=e['text']
        if any(ch in text for ch in ('"','“','”','`')):
            reasons.add('QUOTED_TEXT_REQUIRES_REVIEW')
        other=leading_subject(text)
        if subject and other and subject!=other:
            reasons.add('SUBJECT_ALIGNMENT_REQUIRES_REVIEW')
        if re.search(r'\b(?:no|not|unobserved)\b[^.!?]{0,90}\b(?:observ\w*|record\w*|information|assessment|confirm\w*)\b',text,re.I):
            reasons.add('OBSERVATION_GAP_REQUIRES_REVIEW')
        if re.search(r'\b(?:might|may|possibly|unconfirmed|unclear)\b',text,re.I):
            reasons.add('UNCERTAINTY_REQUIRES_REVIEW')
    return sorted(reasons)
