from nlp_tools.utils import prune_overlapping_matches

from spacy.tokens import Token
from spacy.tokens import Span
from spacy.matcher import Matcher, PhraseMatcher

Token.set_extension("ignore", default=False, force=True)
Span.set_extension("ssvf_attributes", default=None, force=True)
Span.set_extension("ssvf_rule", default=None, force=True)
Span.set_extension("ssvf_rule", default=None, force=True)


class TargetMatcher:
    name = "target_matcher"

    def __init__(self, nlp):
        self.nlp = nlp
        self._rules = list()
        self._rule_item_mapping = dict()
        self.labels = set()

        self.matcher = Matcher(self.nlp.vocab)
        self.phrase_matcher = PhraseMatcher(self.nlp.vocab, attr="LOWER")

    def add(self, rules):
        """Add a list of SSVFRules to the matcher."""
        i = len(self._rules)
        self._rules += rules

        for rule in rules:
            self.labels.add(rule.category)
            rule_id = f"{rule.category}_{i}"
            rule._rule_id = rule_id
            self._rule_item_mapping[rule_id] = rule
            if rule.pattern is not None:
                self.matcher.add(rule_id, [rule.pattern], on_match=rule.on_match)
            else:
                self.phrase_matcher.add(rule_id, rule.on_match, self.nlp.make_doc(rule.literal.lower()))
            i += 1

    def __call__(self, doc):
        matches = self.matcher(doc)
        matches += self.phrase_matcher(doc)
        matches = prune_overlapping_matches(matches)
        for (rule_id, start, end) in matches:
            rule = self._rule_item_mapping[self.nlp.vocab.strings[rule_id]]
            span = Span(doc, start=start, end=end, label=rule.category)
            span._.ssvf_rule = rule
            if rule.attributes is not None:
                for (attribute, value) in rule.attributes.items():
                    try:
                        setattr(span._, attribute, value)
                    except AttributeError as e:
                        raise e
                span._.ssvf_attributes = rule.attributes
            try:
                doc.ents += (span,)
            # spaCy will raise a value error if the token in span are already
            # part of an entity (ie., as part of an upstream component
            # In that case, let the existing span supercede this one
            except ValueError:
                pass

        return doc

