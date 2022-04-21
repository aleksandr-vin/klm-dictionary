##
## Convert an .html file that was exported from .docx file consisting a table with 3 columns:
##
##  |--------|------|------------|
##  | Phrase | Abbr | Definition |
##  |--------|------|------------|
##
from bs4 import BeautifulSoup
import re
import logging


def mark_kref(text, terms):
  for term in sorted(terms, reverse=True):
    text = re.sub(f"([ .(]){term}(s?)([ .)])", f'\\1<kref>{term}</kref>\\2\\3', text)
    text = re.sub(f"^{term}(s?)([ .)])", f'<kref>{term}</kref>\\1\\2', text)
    text = re.sub(f"([ .(]){term}(s?)$", f'\\1<kref>{term}</kref>\\2', text)
    text = re.sub(f"^{term}(s?)$", f'<kref>{term}</kref>\\1', text)
  logging.info(text)
  return text

def test_mark_ref():
  assert mark_kref("BE", ["BE"]) == "<kref>BE</kref>"
  assert mark_kref("BE BE", ["BE"]) == "<kref>BE</kref> <kref>BE</kref>"
  assert mark_kref("BEE", ["BE"]) == "BEE"
  assert mark_kref("EBE", ["BE"]) == "EBE"
  assert mark_kref("EBEE", ["BE"]) == "EBEE"
  assert mark_kref("E BE E", ["BE"]) == "E <kref>BE</kref> E"
  assert mark_kref("E(BE.E", ["BE"]) == "E(<kref>BE</kref>.E"
  assert mark_kref(" BEs.", ["BE"]) == " <kref>BE</kref>s."
  assert mark_kref("one half", ["half", "one half"]) == "<kref>one half</kref>"

def mark_examples(text):
  return re.sub('\\b(Examples?):\\s([^.]+)\\.', '<ex type="exm"><ex_orig>\\1: \\2.</ex_orig></ex>', text)

def test_mark_examples():
  assert mark_examples("BE") == "BE"
  assert mark_examples("BE. Example: foo, bar baz") == 'BE. Example: foo, bar baz'
  assert mark_examples("BE. Example: foo, bar. baz") == 'BE. <ex type="exm"><ex_orig>Example: foo, bar.</ex_orig></ex> baz'
  assert mark_examples("BE. Examples: foo, bar. baz") == 'BE. <ex type="exm"><ex_orig>Examples: foo, bar.</ex_orig></ex> baz'

PLURALIZABLE_WORDS = list(sorted(set(map(lambda x: x.lower(), [
  "seat", "transfer", "type", "number", "code", "type", "subtype",
  "flight", "bag", "channel", "version", "message", "tier", "airport"
  "destination", "printer", "group", "pool", "record", "point", "service",
  "fare", "list", "tracking", "load", "boarding", "ticket", "cabin",
  "coupon", "sheet", "deck", "traveler", "sale", "reader", "agent",
  "agreement", "quota", "leg", "link", "administrator", "market", "airline",
  "segment", "aircraft", "airport", "manifest", "passenger", "element",
  "reason", "reservation", "map", "preference", "segment", "keyword",
  "request", "station", "sublink", "terminal", "carrier"
]))))

def is_pluralizable(phrase):
  words = phrase.split(" ")
  return words[-1].lower() in PLURALIZABLE_WORDS

def test_is_pluralizable():
  assert not is_pluralizable("A")
  assert not is_pluralizable("AB")
  assert not is_pluralizable("super")
  assert not is_pluralizable("super types")
  assert not is_pluralizable("alliance")
  assert is_pluralizable("foo seat")
  assert is_pluralizable("foo transfer")
  assert is_pluralizable("foo type")
  assert is_pluralizable("foo bar number")
  assert is_pluralizable("foo code")
  assert is_pluralizable("foo type")
  assert is_pluralizable("foo Version")

def pluralize(phrases):
  return [item for phrase in phrases for item in ([phrase, phrase + 's'] if is_pluralizable(phrase) else [phrase])]

def test_pluralize():
  assert pluralize(["A", "alliance"]) == ["A", "alliance"]
  assert pluralize(["foo bar number", "foo type"]) == ["foo bar number", "foo bar numbers", "foo type", "foo types"]

def norm_text(text):
  return re.sub("’", "'", re.sub('&','&amp;', re.sub('\\s+', ' ', text.strip())))

def test_norm_text():
  assert norm_text("a & B") == "a &amp; B"
  assert norm_text("a & & B") == "a &amp; &amp; B"
  assert norm_text("f    d") == "f d"
  assert norm_text("f’s") == "f's"
  assert norm_text("f\nd") == "f d"

def import_doc(path):
    with open(path) as page:
      soup = BeautifulSoup(page,'html.parser')

    t = soup.html.body.div.table
    rows = list(filter(lambda x: x.name == 'tr', t.children))
    rows = filter(lambda x: x.th == None, rows)

    defs = {}
    for r in rows:
        phrase, abbr, definition = list(map(lambda x: norm_text(x.text), filter(lambda x: x.name == 'td', r.children)))
        phrase = phrase.replace('<kref>', '').replace('</kref>', '')
        k = "\n".join(set([item.strip() for e in [phrase, abbr] for item in e.split("/") if len(item) > 0]))
        defs[k] = definition
    terms = sorted(set([item for joined in defs.keys() for item in joined.split("\n") if len(item) > 1]), key=len, reverse=True)
    for k in sorted(defs.keys()):
        phrases = sorted(k.split("\n"), key=len, reverse=True)
        phrases = pluralize(phrases)
        definition = defs[k]
        definition = mark_kref(definition, [term for term in terms if term not in phrases])
        definition = mark_examples(definition)
        ks = "\n      ".join([f"<k>{phrase}</k>" for phrase in phrases])
        out = f"""    <ar>
      {ks}
      <def>
        <deftext>
          {definition}
        </deftext>
      </def>
    </ar>"""
        print(out)


if __name__ == '__main__':
    import_doc('xx.html')
