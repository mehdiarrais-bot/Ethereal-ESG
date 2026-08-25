"""
Questionnaire de collecte autonome (fichier HTML unique).

Le consultant envoie ce fichier au client, qui le remplit dans son
navigateur — hors ligne, sans compte, sans rien installer — puis renvoie
le CSV produit. Ce CSV est directement réimportable par la plateforme.

Le questionnaire est dérivé de FIELD_SPECS : ajouter un indicateur à
l'import l'ajoute automatiquement ici, avec le bon libellé de colonne.
"""
import html
import json

from import_data import FIELD_SPECS
from branding import validate_colors, _to_hex

SECTION_META = {
    "company": ("Votre entreprise", "Informations générales et identité du rapport."),
    "environmental": ("Environnement", "Énergie, émissions, eau et déchets sur l'exercice."),
    "social": ("Social", "Effectifs, formation, sécurité et relations parties prenantes."),
    "governance": ("Gouvernance", "Conseil, éthique, contrôle et supervision ESG."),
    "taxonomy": ("Taxonomie européenne", "Part des activités durables — laissez vide si non évaluée."),
}

# clé interne -> (libellé lisible, unité, aide)
FIELD_META = {
    "name": ("Nom de l'entreprise", "", "Raison sociale telle qu'elle doit apparaître sur le rapport."),
    "sector": ("Secteur d'activité", "", "Ex. : Industrie manufacturière, Services, Transport, Agroalimentaire."),
    "country": ("Pays", "", ""),
    "revenue_eur": ("Chiffre d'affaires", "€", "Sur l'exercice reporté. Sert à calculer les intensités."),
    "reporting_year": ("Exercice reporté", "", "L'année sur laquelle portent les données."),
    "target_year": ("Horizon des objectifs", "", "Année cible de votre trajectoire, souvent 2030."),
    "presenter_name": ("Personne référente", "", "Qui présentera le rapport en interne."),
    "presenter_title": ("Sa fonction", "", ""),

    "co2_emissions_tonnes": ("Émissions de CO₂ totales", "t CO₂e", "Total tous scopes confondus si vous le connaissez."),
    "energy_consumption_mwh": ("Consommation d'énergie", "MWh", "Toutes énergies : électricité, gaz, carburants."),
    "renewable_energy_percent": ("Part d'énergie renouvelable", "%", "Dans votre mix énergétique total."),
    "water_consumption_m3": ("Consommation d'eau", "m³", "Volume prélevé sur l'exercice."),
    "waste_generated_tonnes": ("Déchets générés", "t", ""),
    "waste_recycled_percent": ("Taux de recyclage des déchets", "%", ""),
    "biodiversity_initiatives": ("Initiatives biodiversité", "nombre", "Actions concrètes menées : plantations, zones protégées, etc."),
    "scope1_emissions": ("Émissions Scope 1", "t CO₂e", "Émissions directes : vos chaudières, votre flotte de véhicules."),
    "scope2_emissions": ("Émissions Scope 2", "t CO₂e", "Liées à l'énergie que vous achetez, principalement l'électricité."),
    "scope3_emissions": ("Émissions Scope 3", "t CO₂e", "Chaîne de valeur : achats, transport, usage des produits vendus."),

    "total_employees": ("Effectif total", "personnes", "En équivalent temps plein à la clôture."),
    "female_employees_percent": ("Part de femmes dans l'effectif", "%", ""),
    "employee_turnover_percent": ("Taux de rotation du personnel", "%", "Départs rapportés à l'effectif moyen."),
    "training_hours_per_employee": ("Formation par salarié", "h/an", "Nombre moyen d'heures de formation par personne."),
    "work_accidents": ("Accidents du travail", "nombre", "Avec arrêt, sur l'exercice."),
    "accident_frequency_rate": ("Taux de fréquence des accidents", "TF", "Accidents avec arrêt × 1 000 000 / heures travaillées."),
    "community_investment_eur": ("Investissement territorial", "€", "Mécénat, partenariats locaux, fondation."),
    "local_suppliers_percent": ("Part de fournisseurs locaux", "%", ""),
    "customer_satisfaction_score": ("Satisfaction client", "/10", ""),
    "disabled_employees_percent": ("Salariés en situation de handicap", "%", ""),

    "board_members": ("Membres du conseil", "nombre", "Conseil d'administration ou de surveillance."),
    "female_board_percent": ("Femmes au conseil", "%", "Seuil légal de référence : 40 %."),
    "independent_board_percent": ("Administrateurs indépendants", "%", "Référence AFEP-MEDEF : 50 %."),
    "ethics_violations": ("Manquements éthiques constatés", "nombre", "Sur l'exercice. Zéro est une réponse valable."),
    "corruption_cases": ("Cas de corruption", "nombre", ""),
    "data_breaches": ("Incidents de cybersécurité", "nombre", "Violations de données déclarées."),
    "csr_budget_eur": ("Budget RSE", "€", "Moyens dédiés à la démarche."),
    "esg_audit_conducted": ("Reporting vérifié par un tiers", "", "Un organisme indépendant a-t-il audité vos données ESG ?"),
    "sustainability_committee": ("Comité de durabilité", "", "Une instance dédiée existe-t-elle au niveau du conseil ?"),

    "turnover_aligned_percent": ("Chiffre d'affaires aligné Taxonomie", "%", ""),
    "capex_aligned_percent": ("Investissements (CapEx) alignés", "%", ""),
    "opex_aligned_percent": ("Dépenses (OpEx) alignées", "%", ""),
}


def _fields_by_section():
    """[(section, [(csv_label, key, type, meta), ...]), ...] dans l'ordre."""
    out, order = {}, []
    for section, key, typ, labels in FIELD_SPECS:
        if section not in out:
            out[section] = []
            order.append(section)
        meta = FIELD_META.get(key, (key.replace("_", " ").capitalize(), "", ""))
        # labels[0] est l'en-tête écrit dans le CSV, capitalisé comme le modèle
        out[section].append((labels[0].capitalize(), key, typ, meta))
    return [(s, out[s]) for s in order]


def generate_questionnaire_html(company_name: str = "", year: int = None,
                                consultant: str = "", custom_colors: dict = None) -> str:
    """Fichier HTML autonome, hors ligne, prêt à être envoyé au client."""
    primary, accent = "#1B3A6B", "#F39C12"
    v = validate_colors(custom_colors) if custom_colors else None
    if v:
        primary, accent = _to_hex(v[0]), _to_hex(v[1])

    sections = _fields_by_section()
    # Structure exploitée par le JS pour reconstruire le CSV
    schema = [{"section": s,
               "fields": [{"csv": csv_label, "key": k, "type": t} for csv_label, k, t, _ in flds]}
              for s, flds in sections]

    esc = html.escape
    body = []
    for section, fields in sections:
        title, intro = SECTION_META.get(section, (section.capitalize(), ""))
        body.append(f'<section class="card" data-section="{esc(section)}">')
        body.append(f'<h2>{esc(title)}</h2>')
        if intro:
            body.append(f'<p class="intro">{esc(intro)}</p>')
        body.append('<div class="fields">')
        for csv_label, key, typ, (label, unit, hint) in fields:
            fid = f"f_{key}"
            unit_html = f'<span class="unit">{esc(unit)}</span>' if unit else ""
            hint_html = f'<span class="hint">{esc(hint)}</span>' if hint else ""
            if typ == "bool":
                control = (
                    f'<div class="yn" role="group">'
                    f'<button type="button" class="yn-btn" data-for="{fid}" data-val="Oui">Oui</button>'
                    f'<button type="button" class="yn-btn" data-for="{fid}" data-val="Non">Non</button>'
                    f'<button type="button" class="yn-btn ghost" data-for="{fid}" data-val="">Je ne sais pas</button>'
                    f'<input type="hidden" id="{fid}" data-key="{esc(key)}">'
                    f'</div>')
            else:
                itype = "text" if typ == "str" else "number"
                step = ' step="any"' if typ == "num" else ""
                control = (f'<div class="inputwrap">'
                           f'<input type="{itype}"{step} id="{fid}" data-key="{esc(key)}" '
                           f'autocomplete="off" placeholder="—">{unit_html}</div>')
            body.append(
                f'<div class="field"><label for="{fid}">{esc(label)}{hint_html}</label>{control}</div>')
        body.append('</div></section>')

    title_txt = f"Collecte ESG — {company_name}" if company_name else "Collecte de données ESG"
    year_txt = f"Exercice {year}" if year else "Exercice à préciser"
    by_txt = f"Questionnaire préparé par {consultant}" if consultant else ""
    fname = "".join(ch if ch.isalnum() else "_" for ch in (company_name or "collecte"))[:40]

    return f"""<!doctype html>
<html lang="fr"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title_txt)}</title>
<style>
  :root {{ --primary: {primary}; --accent: {accent}; }}
  * {{ box-sizing: border-box; }}
  body {{ margin: 0; background: #f4f6f9; color: #1f2937;
         font-family: -apple-system, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; }}
  header {{ background: var(--primary); color: #fff; padding: 30px 24px 26px; }}
  .hwrap {{ max-width: 880px; margin: 0 auto; }}
  header h1 {{ margin: 0 0 6px; font-size: 26px; }}
  header .sub {{ opacity: .85; font-size: 14px; }}
  header .by {{ margin-top: 12px; font-size: 12.5px; opacity: .7; }}
  .bar {{ height: 5px; background: var(--accent); }}
  main {{ max-width: 880px; margin: 0 auto; padding: 22px 20px 130px; }}
  .notice {{ background: #fff; border-left: 4px solid var(--accent); border-radius: 0 8px 8px 0;
             padding: 14px 18px; font-size: 13.5px; line-height: 1.55; margin-bottom: 22px; }}
  .card {{ background: #fff; border-radius: 12px; padding: 22px 24px; margin-bottom: 18px;
           box-shadow: 0 1px 3px rgba(0,0,0,.07); }}
  .card h2 {{ margin: 0 0 4px; font-size: 18px; color: var(--primary); }}
  .intro {{ margin: 0 0 18px; font-size: 13px; color: #6b7280; }}
  .fields {{ display: grid; grid-template-columns: 1fr 1fr; gap: 16px 24px; }}
  .field {{ display: flex; flex-direction: column; gap: 6px; }}
  label {{ font-size: 13px; font-weight: 600; display: flex; flex-direction: column; gap: 2px; }}
  .hint {{ font-weight: 400; font-size: 11.5px; color: #6b7280; line-height: 1.4; }}
  .inputwrap {{ display: flex; align-items: center; gap: 8px; }}
  input[type=text], input[type=number] {{
    flex: 1; width: 100%; padding: 9px 11px; font-size: 14px;
    border: 1px solid #d1d5db; border-radius: 8px; background: #fff; }}
  input:focus {{ outline: none; border-color: var(--primary);
                 box-shadow: 0 0 0 3px rgba(0,0,0,.05); }}
  .unit {{ font-size: 12px; color: #6b7280; min-width: 46px; }}
  .yn {{ display: flex; gap: 6px; flex-wrap: wrap; }}
  .yn-btn {{ padding: 8px 14px; font-size: 13px; border: 1px solid #d1d5db;
             background: #fff; border-radius: 8px; cursor: pointer; }}
  .yn-btn.ghost {{ color: #6b7280; font-size: 12px; }}
  .yn-btn.on {{ background: var(--primary); color: #fff; border-color: var(--primary); }}
  footer {{ position: fixed; bottom: 0; left: 0; right: 0; background: #fff;
            border-top: 1px solid #e5e7eb; padding: 14px 20px; }}
  .fwrap {{ max-width: 880px; margin: 0 auto; display: flex; align-items: center;
            gap: 16px; flex-wrap: wrap; }}
  .prog {{ flex: 1; min-width: 160px; }}
  .prog-bg {{ height: 7px; background: #e5e7eb; border-radius: 99px; overflow: hidden; }}
  .prog-fill {{ height: 100%; background: var(--accent); width: 0%; transition: width .25s; }}
  .prog-lab {{ font-size: 12px; color: #6b7280; margin-top: 5px; }}
  .btn {{ padding: 11px 20px; font-size: 14px; font-weight: 700; border-radius: 8px;
          border: none; cursor: pointer; background: var(--primary); color: #fff; }}
  .btn.sec {{ background: #fff; color: #6b7280; border: 1px solid #d1d5db; font-weight: 600; }}
  .saved {{ font-size: 12px; color: #059669; }}
  @media (max-width: 700px) {{ .fields {{ grid-template-columns: 1fr; }} }}
  @media print {{ footer, .notice {{ display: none; }} }}
</style></head>
<body>
<header><div class="hwrap">
  <h1>{esc(title_txt)}</h1>
  <div class="sub">{esc(year_txt)} · Questionnaire de collecte ESG / RSE</div>
  {f'<div class="by">{esc(by_txt)}</div>' if by_txt else ''}
</div></header>
<div class="bar"></div>

<main>
  <div class="notice">
    <strong>Comment procéder.</strong> Renseignez ce que vous connaissez et laissez vide le reste —
    une donnée absente sera signalée comme « non renseignée » dans le rapport, ce qui est une
    information utile en soi. <strong>Ne devinez pas un chiffre.</strong> Votre saisie est
    enregistrée automatiquement dans ce navigateur : vous pouvez fermer et reprendre plus tard.
    Quand vous avez terminé, cliquez sur « Télécharger le fichier » en bas et renvoyez le fichier obtenu.
    <br><br>
    Ce document fonctionne <strong>entièrement hors ligne</strong> : rien n'est envoyé sur Internet.
  </div>
  {''.join(body)}
</main>

<footer><div class="fwrap">
  <div class="prog">
    <div class="prog-bg"><div class="prog-fill" id="pf"></div></div>
    <div class="prog-lab"><span id="pl">0 champ renseigné</span> · <span class="saved" id="sv"></span></div>
  </div>
  <button class="btn sec" id="clear" type="button">Tout effacer</button>
  <button class="btn" id="dl" type="button">⬇ Télécharger le fichier</button>
</div></footer>

<script>
const SCHEMA = {json.dumps(schema, ensure_ascii=False)};
const STORE = "esg_collecte_{esc(fname)}";
const all = () => Array.from(document.querySelectorAll("[data-key]"));

function save() {{
  const d = {{}};
  all().forEach(el => {{ if (el.value !== "") d[el.dataset.key] = el.value; }});
  try {{ localStorage.setItem(STORE, JSON.stringify(d)); }} catch (e) {{}}
  const n = Object.keys(d).length, tot = all().length;
  document.getElementById("pf").style.width = (100 * n / tot) + "%";
  document.getElementById("pl").textContent =
    n + (n > 1 ? " champs renseignés" : " champ renseigné") + " sur " + tot;
  const sv = document.getElementById("sv");
  sv.textContent = "enregistré";
  clearTimeout(window._t); window._t = setTimeout(() => sv.textContent = "", 1600);
}}

function restore() {{
  let d = {{}};
  try {{ d = JSON.parse(localStorage.getItem(STORE) || "{{}}"); }} catch (e) {{}}
  all().forEach(el => {{ if (d[el.dataset.key] !== undefined) el.value = d[el.dataset.key]; }});
  document.querySelectorAll(".yn-btn").forEach(b => {{
    const hidden = document.getElementById(b.dataset.for);
    if (hidden && hidden.value === b.dataset.val && b.dataset.val !== "") b.classList.add("on");
  }});
  save();
}}

document.addEventListener("input", e => {{ if (e.target.dataset.key) save(); }});
document.querySelectorAll(".yn-btn").forEach(btn => {{
  btn.addEventListener("click", () => {{
    const hidden = document.getElementById(btn.dataset.for);
    document.querySelectorAll('.yn-btn[data-for="' + btn.dataset.for + '"]')
      .forEach(b => b.classList.remove("on"));
    if (btn.dataset.val !== "") btn.classList.add("on");
    hidden.value = btn.dataset.val;
    save();
  }});
}});

document.getElementById("clear").addEventListener("click", () => {{
  if (!confirm("Effacer toutes les réponses saisies ?")) return;
  all().forEach(el => el.value = "");
  document.querySelectorAll(".yn-btn").forEach(b => b.classList.remove("on"));
  try {{ localStorage.removeItem(STORE); }} catch (e) {{}}
  save();
}});

document.getElementById("dl").addEventListener("click", () => {{
  const vals = {{}};
  all().forEach(el => vals[el.dataset.key] = el.value);
  // Format « Champ;Valeur » — celui que la plateforme sait réimporter
  const rows = [["Champ", "Valeur"]];
  SCHEMA.forEach(sec => sec.fields.forEach(f => rows.push([f.csv, vals[f.key] || ""])));
  const csv = rows.map(r => r.map(c => {{
    const s = String(c);
    return /[";\\n]/.test(s) ? '"' + s.replace(/"/g, '""') + '"' : s;
  }}).join(";")).join("\\r\\n");
  const blob = new Blob(["\\ufeff" + csv], {{ type: "text/csv;charset=utf-8" }});
  const a = document.createElement("a");
  a.href = URL.createObjectURL(blob);
  a.download = "donnees_esg_{esc(fname)}.csv";
  document.body.appendChild(a); a.click();
  setTimeout(() => {{ document.body.removeChild(a); URL.revokeObjectURL(a.href); }}, 200);
}});

restore();
</script>
</body></html>
"""
