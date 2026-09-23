"""Typographie des nombres dans les livrables — point de passage unique.

Constat (DETTE.md § 5) : l'ancien générateur et le composer écrivaient les
nombres à l'anglaise (« 21,500 MWh », « TF 6.2 », « 42% ») dans des textes
français, et le texte analytique ajouté le 2026-09-24 les écrivait à la
française : les deux formats cohabitaient dans un même rapport.

Plutôt que de corriger chaque f-string (plusieurs dizaines, dans une dizaine
de modules, avec le risque d'en oublier une), la mise en forme française est
appliquée au RENDU, en un point par format :
  - PDF (rapport, synthèse une page) : pdf_kit.clean(), par où passe tout
    texte composé, sous `with language(request.language)` ;
  - Word et PowerPoint : fix_docx() / fix_pptx(), un passage sur le document
    fini, juste avant l'enregistrement.
Le texte anglais n'est jamais modifié.
"""
import re
from contextlib import contextmanager
from contextvars import ContextVar

NBSP = " "  # espace insécable (présente en cp1252, contrairement à U+202F)

_LANG: ContextVar[str | None] = ContextVar("deliverable_language", default=None)

# 21,500 / 1,234,567 : groupes de milliers à l'anglaise (jamais précédés ou
# suivis d'un chiffre, d'un point ou d'une virgule)
_THOUSANDS = re.compile(r"(?<![\d.,])(\d{1,3}(?:,\d{3})+)(?![\d,])")
# 6.2 / 62.3 : point décimal entre deux chiffres
_DECIMAL = re.compile(r"(?<=\d)\.(?=\d)")
# 42% / 42 % : espace insécable avant le signe pourcentage
_PERCENT = re.compile(r"(\d)[  ]?%")


def fr_numbers(text: str) -> str:
    """« 21,500.5 MWh, 42% » -> « 21 500,5 MWh, 42 % » (insécables)."""
    text = _THOUSANDS.sub(lambda m: m.group(1).replace(",", NBSP), text)
    text = _DECIMAL.sub(",", text)
    return _PERCENT.sub(r"\1" + NBSP + "%", text)


@contextmanager
def language(lang: str):
    """Langue du livrable en cours de composition (sûr en concurrence :
    ContextVar est propre à chaque requête)."""
    token = _LANG.set(lang)
    try:
        yield
    finally:
        _LANG.reset(token)


def fix(text: str) -> str:
    """Typographie de la langue du livrable en cours (identité hors français)."""
    return fr_numbers(text) if _LANG.get() == "fr" and text else text


def _fix_paragraphs(paragraphs, lang: str) -> None:
    for p in paragraphs:
        for run in p.runs:
            if run.text:
                run.text = fr_numbers(run.text) if lang == "fr" else run.text


def fix_docx(doc, lang: str) -> None:
    """Passage final sur un document python-docx : corps, tableaux, en-têtes."""
    if lang != "fr":
        return

    def tables(tbls):
        for t in tbls:
            for row in t.rows:
                for cell in row.cells:
                    _fix_paragraphs(cell.paragraphs, lang)
                    tables(cell.tables)

    _fix_paragraphs(doc.paragraphs, lang)
    tables(doc.tables)
    for section in doc.sections:
        for part in (section.header, section.footer):
            _fix_paragraphs(part.paragraphs, lang)
            tables(part.tables)


def fix_pptx(prs, lang: str) -> None:
    """Passage final sur une présentation python-pptx : formes, groupes,
    tableaux et notes de l'orateur."""
    if lang != "fr":
        return

    def shapes(items):
        for sh in items:
            if getattr(sh, "shape_type", None) == 6:  # MSO_SHAPE_TYPE.GROUP
                shapes(sh.shapes)
            if getattr(sh, "has_text_frame", False) and sh.has_text_frame:
                _fix_paragraphs(sh.text_frame.paragraphs, lang)
            if getattr(sh, "has_table", False) and sh.has_table:
                for row in sh.table.rows:
                    for cell in row.cells:
                        _fix_paragraphs(cell.text_frame.paragraphs, lang)

    for slide in prs.slides:
        shapes(slide.shapes)
        if slide.has_notes_slide:
            _fix_paragraphs(slide.notes_slide.notes_text_frame.paragraphs, lang)
