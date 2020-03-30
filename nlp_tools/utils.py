"""This module contains helper functions for working with spaCy and spaCy matches.
"""

from spacy.tokens import Span

def build_nlp(model="en_core_web_sm", disable=None, cycontext_rules="default", sectionizer_patterns="default"):
    import spacy
    if disable is None:
        disable = []
    if isinstance(model, str):
        nlp = spacy.load(model, disable=disable)
    else:
        nlp = model

    # Add a preprocessor
    from nlp_tools.nlp_preprocessor import Preprocessor
    nlp.tokenizer = Preprocessor(nlp.tokenizer)

    # Add a target matcher
    from nlp_tools.target_matcher import TargetMatcher
    nlp.add_pipe(TargetMatcher(nlp))

    # Add cycontext
    from cycontext import ConTextComponent
    nlp.add_pipe(ConTextComponent(nlp, rules=cycontext_rules))

    # Add a sectionizer
    from sectionizer import Sectionizer
    nlp.add_pipe(Sectionizer(nlp, patterns=sectionizer_patterns))

    # Add a PostProcessor
    from nlp_tools.nlp_postprocessor import Postprocessor
    nlp.add_pipe(Postprocessor())

    return nlp


def prune_overlapping_matches(matches, strategy="longest"):
    if strategy != "longest":
        raise NotImplementedError()

    # Make a copy and sort
    unpruned = sorted(matches, key=lambda x: (x[1], x[2]))
    pruned = []
    num_matches = len(matches)
    if num_matches == 0:
        return matches
    curr_match = unpruned.pop(0)

    while True:
        if len(unpruned) == 0:
            pruned.append(curr_match)
            break
        next_match = unpruned.pop(0)

        # Check if they overlap
        if overlaps(curr_match, next_match):
            # Choose the larger span
            longer_span = max(curr_match, next_match, key=lambda x: (x[2] - x[1]))
            pruned.append(longer_span)
            if len(unpruned) == 0:
                break
            curr_match = unpruned.pop(0)
        else:
            pruned.append(curr_match)
            curr_match = next_match
    # Recursive base point
    if len(pruned) == num_matches:
        return pruned
    # Recursive function call
    else:
        return prune_overlapping_matches(pruned)

def overlaps(a, b):
    if _span_overlaps(a, b) or _span_overlaps(b, a):
        return True
    return False

def _span_overlaps(a, b):
    _, a_start, a_end = a
    _, b_start, b_end = b
    if a_start >= b_start and a_start < b_end:
        return True
    if a_end > b_start and a_end <= b_end:
        return True
    return False

def matches_to_spans(doc, matches, set_label=True):
    spans = []
    for (rule_id, start, end) in matches:
        if set_label:
            label = doc.vocab.strings[rule_id]
        else:
            label = None
        spans.append(Span(doc, start=start, end=end, label=label))
    return spans
