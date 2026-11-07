#!/usr/bin/env python3
"""
Tweede ronde bijwerking naar 2026, als vervolg op apply_2026_updates.py.

Deze ronde:
  1) werkt de cijfers bij die in de eerste ronde nog als "niet bijgewerkt"
     waren gemarkeerd, nu met een bevestigde 2026-bron (box 3 heffingsvrij
     vermogen, ouderenkorting, alleenstaande ouderenkorting, arbeidskorting-
     afbouwgrenzen, eenmalige schenkingsvrijstelling, studievrijstelling,
     erf-/schenkbelasting schijfgrens en partnervrijstelling);
  2) herrekent twee ANONIEME (niet aan een naam gekoppelde) rekenvoorbeelden
     over erfbelasting, omdat de rekenkundige stappen eenvoudig en
     betrouwbaar na te rekenen zijn;
  3) laat NAMED voorbeelden (Andrea, Nancy, Hanneke, Abby, Karel, Léon,
     Patrick, Gerard) nog steeds principieel ongemoeid — zie NOT_UPDATED_2.

Run: python3 scripts/apply_2026_updates_part2.py
"""
import json
import os
import sys
from datetime import date

REPO = "/home/user/nvhp-syllabus"
TODAY = date.today().isoformat()

UPDATES = [
    dict(book="boek1.html", topic="Box 3 — heffingsvrij vermogen (definitie)",
         old="Het heffingsvrijvermogen bedraagt in 2025 € 57.684 per belastingplichtige. Het is het vermogen, waarover de belastingplichtige geen box 3-heffing hoeft te betalen. Voor fiscaal partner geldt een bedrag van € 115.368.",
         new="Het heffingsvrijvermogen bedraagt in 2026 € 59.357 per belastingplichtige. Het is het vermogen, waarover de belastingplichtige geen box 3-heffing hoeft te betalen. Voor fiscaal partner geldt een bedrag van € 118.714.",
         source="SRA / FiscAlert — box 3 percentages, vrijstellingen en bedragen 2026",
         source_url="https://www.sra.nl/nieuws/259001/2026/01/box-3-percentages-vrijstellingen-en-bedragen-2026",
         note="De forfaitaire rendementspercentages zelf blijven buiten deze update — zie wijzigingen.html."),
    dict(book="boek1.html", topic="Box 3 — heffingsvrij vermogen (verwijzing in casus vruchtgebruik/bloot eigendom)",
         old="het heffingsvrijvermogen in box 3 van € 57.684 (2025).",
         new="het heffingsvrijvermogen in box 3 van € 59.357 (2026).",
         source="SRA / FiscAlert — box 3 percentages, vrijstellingen en bedragen 2026",
         source_url="https://www.sra.nl/nieuws/259001/2026/01/box-3-percentages-vrijstellingen-en-bedragen-2026",
         note="Alleen deze losstaande verwijzing is bijgewerkt; de rest van die casus (bloot eigendom € 450.000 -/- € 144.000 = € 306.000) staat hier los van en is ongewijzigd."),
    dict(book="boek1.html", topic="Arbeidskorting — afbouwgrenzen (toelichtende zin)",
         old="De afbouw van de arbeidskorting begint bij een arbeidsinkomen van € 43.071. De afbouw eindigt bij een arbeidsinkomen van € 129.078.",
         new="De afbouw van de arbeidskorting begint bij een arbeidsinkomen van € 45.592. De afbouw eindigt bij een arbeidsinkomen van € 132.920.",
         source="Rendement.nl — arbeidskorting 2026",
         source_url="https://www.rendement.nl/aangifte-loonheffingen/nieuws/arbeidskorting-stijgt-opnieuw-licht-in-2026.html",
         note="De gedetailleerde opbouwtabel direct hieronder (met knikpunten en percentages per schijf, o.a. 8,053% en 30,030%) is NIET bijgewerkt: hiervoor is geen complete, geverifieerde 2026-tabel gevonden. Zie wijzigingen.html."),
    dict(book="boek1.html", topic="Ouderenkorting — tabel",
         old="Ouderenkorting tot inkomen van € 44.770               n.v.t.                   € 2.035120",
         new="Ouderenkorting tot inkomen van € 46.002               n.v.t.                   € 2.067",
         source="Rijksoverheid — ouderenkorting 2026",
         source_url="https://www.rijksoverheid.nl/themas/werk/pensioen/vraag-en-antwoord/inkomstenbelasting/wat-is-een-heffingskorting-en-welke-heffingskortingen-zijn-er",
         note="Voetnootcijfer '120' (PDF-extractieartefact) bij deze gelegenheid verwijderd."),
    dict(book="boek1.html", topic="Alleenstaande ouderenkorting — tabel",
         old="Alleenstaande ouderenkorting                                                   € 531121",
         new="Alleenstaande ouderenkorting                                                   € 540",
         source="Rijksoverheid / Onderneming.nl — alleenstaande ouderenkorting 2026",
         source_url="https://www.onderneming.nl/belasting/inkomstenbelasting/ouderenkorting/",
         note="Voetnootcijfer '121' (PDF-extractieartefact) bij deze gelegenheid verwijderd."),
    dict(book="boek1.html", topic="Alleenstaande ouderenkorting — toelichtende zin",
         old="De alleenstaande ouderenkorting bedraagt € 531.",
         new="De alleenstaande ouderenkorting bedraagt € 540.",
         source="Rijksoverheid / Onderneming.nl — alleenstaande ouderenkorting 2026",
         source_url="https://www.onderneming.nl/belasting/inkomstenbelasting/ouderenkorting/"),

    dict(book="boek2.html", topic="Schenkbelasting — vrijstellingstabel (eenmalig en studie)",
         old="Vrijstellingsbedragen schenkbelasting﻿ Kinderen jaarlijks                                                  €   6.908 Kinderen 18 - 40 jaar (eenmalig, vrij te besteden)                  € 32.195* Kind 18-40 jaar (dure studie)                                       € 67.064*",
         new="Vrijstellingsbedragen schenkbelasting﻿ Kinderen jaarlijks                                                  €   6.908 Kinderen 18 - 40 jaar (eenmalig, vrij te besteden)                  € 33.129 Kind 18-40 jaar (dure studie)                                       € 69.009",
         source="SRA / jongbloed-fiscaaljuristen — schenkingsvrijstellingen 2026",
         source_url="https://www.sra.nl/nieuws/259001/2026/01/wat-mag-u-in-2026-belastingvrij-schenken",
         note="Deze twee bedragen stonden na de eerste update nog op prijspeil 2025 (asterisk '*'); inmiddels wel bevestigd en bijgewerkt."),
    dict(book="boek2.html", topic="Schenking/erfgenaam — schijfgrens overige verkrijgers",
         old="De schenkingsvrijstelling is dan anno 2026 € 2.769 en het tarief tot € 154.197 (bedrag 2025, nog niet herbevestigd voor 2026) 30 procent en erboven 40 procent.",
         new="De schenkingsvrijstelling is dan anno 2026 € 2.769 en het tarief tot € 158.669 30 procent en erboven 40 procent.",
         source="Belastingdienst / Rendement — tarieven erf- en schenkbelasting 2026",
         source_url="https://www.rendement.nl/erfbelasting-en-schenkbelasting/tools/berekening-erfbelasting-en-schenkbelasting.html"),
    dict(book="boek2.html", topic="Erfbelasting — partnervrijstelling en schijfgrens (ongehuwd samenwonenden)",
         old="de hoge partnervrijstelling van € 804.698, het tarief van 10 procent tot € 154.197 aan verkrijging en 20 procent voor zover de verkrijging meer bedraagt dan              33 € 154.197 (bedragen 2025).",
         new="de hoge partnervrijstelling van € 828.035, het tarief van 10 procent tot € 158.669 aan verkrijging en 20 procent voor zover de verkrijging meer bedraagt dan              33 € 158.669 (bedragen 2026).",
         source="Belastingdienst / Rendement — tarieven erf- en schenkbelasting 2026",
         source_url="https://www.rendement.nl/erfbelasting-en-schenkbelasting/tools/berekening-erfbelasting-en-schenkbelasting.html"),
    dict(book="boek2.html", topic="Erfbelasting — tariefgroepentabel (schijfgrens)",
         old="€ 0 - € 154.197          10%                        18%                    30% ≥ € 154.197              20%                        36%                    40%",
         new="€ 0 - € 158.669          10%                        18%                    30% ≥ € 158.669              20%                        36%                    40%",
         source="Belastingdienst / Rendement — tarieven erf- en schenkbelasting 2026",
         source_url="https://www.rendement.nl/erfbelasting-en-schenkbelasting/tools/berekening-erfbelasting-en-schenkbelasting.html"),
    dict(book="boek2.html", topic="Rekenvoorbeeld (anoniem) — erfbelasting kind, € 50.000",
         old="Een kind erft een bedrag van € 50.000. In 2025 is het kind € 2.451 aan erfbelasting verschuldigd (er is geen onderscheid naar leeftijd). Berekening erfbelasting: € 50.000 -/- € 25.490 (vrijstelling) x 10% = € 2.451 (afronding naar beneden, ten gunste van de belastingplichtige).",
         new="Een kind erft een bedrag van € 50.000. In 2026 is het kind € 2.377 aan erfbelasting verschuldigd (er is geen onderscheid naar leeftijd). Berekening erfbelasting: € 50.000 -/- € 26.230 (vrijstelling) x 10% = € 2.377.",
         source="Belastingdienst — vrijstellingen erfbelasting 2026 (herrekend)",
         source_url="https://bankinggeek.com/?p=32279",
         note="Dit is een anoniem (niet aan een naam gekoppeld) rekenvoorbeeld; de uitkomst is herrekend met de 2026-vrijstelling van € 26.230. Geen afronding nodig: € 2.377,00 is exact."),
    dict(book="boek2.html", topic="Rekenvoorbeeld (anoniem) — erfbelasting kind, € 300.000",
         old="Een kind erft een bedrag van € 300.000. In 2025 is het kind € 39.482 aan erfbelasting verschuldigd. Er is geen onderscheid naar leeftijd. Berekening: € 300.000 -/- € 25.490 (vrijstelling) = € 274.510. 1e schijf: 10% x € 154.196 = € 15.419,60 plus 2e schijf: 20% x (€ 274.510 -/- € 154.197) = € 24.062,60. Totaal te betalen erfbelasting € 39.482.",
         new="Een kind erft een bedrag van € 300.000. In 2026 is het kind € 38.887 aan erfbelasting verschuldigd. Er is geen onderscheid naar leeftijd. Berekening: € 300.000 -/- € 26.230 (vrijstelling) = € 273.770. 1e schijf: 10% x € 158.669 = € 15.866,90 plus 2e schijf: 20% x (€ 273.770 -/- € 158.669) = € 23.020,20. Totaal te betalen erfbelasting € 38.887.",
         source="Belastingdienst — vrijstellingen en tarieven erfbelasting 2026 (herrekend)",
         source_url="https://bankinggeek.com/?p=32279",
         note="Anoniem rekenvoorbeeld, herrekend met de 2026-vrijstelling (€ 26.230) en schijfgrens (€ 158.669). Totaal afgerond op hele euro's, net als in het origineel."),

    dict(book="boek4.html", topic="Schenking eigen woning — hoge vrijstelling",
         old="In 2025 is de hoge schenking ten behoeve van de eigen woning maximaal € 32.195.",
         new="In 2026 is de hoge schenking ten behoeve van de eigen woning maximaal € 33.129.",
         source="SRA — schenkingsvrijstellingen 2026",
         source_url="https://www.sra.nl/nieuws/259001/2026/01/wat-mag-u-in-2026-belastingvrij-schenken"),
    dict(book="boek4.html", topic="Schenkingsvrijstelling — jaarlijks en eenmalig (18-40 jaar)",
         old="Ouders mogen in 2025 hun kind jaarlijks maximaal € 6.713 belastingvrij schenken. Dit bedrag geldt voor de ouders samen. Kinderen in de leeftijdscategorie van 18 tot 40 jaar mogen zij eenmalig € 32.195 belastingvrij schenken.",
         new="Ouders mogen in 2026 hun kind jaarlijks maximaal € 6.908 belastingvrij schenken. Dit bedrag geldt voor de ouders samen. Kinderen in de leeftijdscategorie van 18 tot 40 jaar mogen zij eenmalig € 33.129 belastingvrij schenken.",
         source="SRA — schenkingsvrijstellingen 2026",
         source_url="https://www.sra.nl/nieuws/259001/2026/01/wat-mag-u-in-2026-belastingvrij-schenken"),
    dict(book="boek4.html", topic="Schenkingsvrijstelling — jaarlijks en eenmalig (variant)",
         old="In 2025 mogen ouders hun kind € 6.713 belastingvrij schenken. Bovendien mogen zij hun kind tussen de 18 en 40 jaar eenmalig een belastingvrij bedrag schenken van € 32.195.",
         new="In 2026 mogen ouders hun kind € 6.908 belastingvrij schenken. Bovendien mogen zij hun kind tussen de 18 en 40 jaar eenmalig een belastingvrij bedrag schenken van € 33.129.",
         source="SRA — schenkingsvrijstellingen 2026",
         source_url="https://www.sra.nl/nieuws/259001/2026/01/wat-mag-u-in-2026-belastingvrij-schenken"),
    dict(book="boek4.html", topic="Schenkingsvrijstelling — dure studie",
         old="wordt de verhoogde vrijstelling verder verhoogd naar € 67.064.",
         new="wordt de verhoogde vrijstelling verder verhoogd naar € 69.009.",
         source="SRA / jongbloed-fiscaaljuristen — schenkingsvrijstellingen 2026",
         source_url="https://www.sra.nl/nieuws/259001/2026/01/wat-mag-u-in-2026-belastingvrij-schenken"),
]

NOT_UPDATED_2 = [
    dict(topic="Named rekenvoorbeelden (vervolg)",
         books="boek4.html (Andrea, Nancy), en overige in alle boeken",
         reason="Blijft principieel ongewijzigd: het voorbeeld van Andrea (verhoogde schenkingsvrijstelling) en van Nancy/Gerard "
                "(erfbelasting met nabestaandenpensioenimputatie) zijn aan een naam gekoppelde, meerstaps-berekeningen. Zie ook "
                "de eerste ronde (wijzigingen.html) voor de volledige lijst en motivatie."),
    dict(topic="Jonggehandicaptenkorting",
         books="boek1.html",
         reason="Geen 2026-bedrag gevonden in de geraadpleegde bronnen (2025: € 909). Blijft op prijspeil 2025 staan."),
    dict(topic="Inkomensafhankelijke combinatiekorting",
         books="boek1.html",
         reason="Geen expliciet bevestigd 2026-bedrag gevonden (2025: € 2.986 / € 1.495). Blijft op prijspeil 2025 staan."),
    dict(topic="Arbeidskorting — volledige opbouw-/afbouwtabel per schijf",
         books="boek1.html",
         reason="Alleen de twee kale grensbedragen in de toelichtende zin zijn bijgewerkt. De tabel met knikpunten en "
                "opbouwpercentages (8,053% / 30,030% / 2,258% / 6,510% en de bijbehorende inkomensgrenzen van € 12.169 en "
                "€ 26.288) is NIET bijgewerkt: hiervoor ontbreekt een volledige, geverifieerde 2026-bron."),
    dict(topic="Box 3 — forfaitaire rendementspercentages",
         books="boek1.html, boek3.html",
         reason="Zoals in de eerste ronde: de percentages voor banktegoeden en schulden waren bij het bijwerken nog "
                "'voorlopig' (definitieve vaststelling pas begin 2027). Niet bijgewerkt om geen voorlopige cijfers als "
                "definitief te presenteren."),
]


def apply_updates():
    applied, failed = [], []
    for upd in UPDATES:
        path = os.path.join(REPO, upd["book"])
        with open(path, encoding="utf-8") as f:
            content = f.read()
        expected = upd.get("count", 1)
        found = content.count(upd["old"])
        if found != expected:
            failed.append((upd, found, expected))
            continue
        content = content.replace(upd["old"], upd["new"])
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        applied.append(upd)

    print(f"Toegepast: {len(applied)} / {len(UPDATES)}")
    if failed:
        print("MISLUKT:")
        for upd, found, expected in failed:
            print(f"  [{upd['book']}] {upd['topic']!r} -> gevonden {found}x, verwacht {expected}x")
        sys.exit(1)

    # merge into existing changelog
    log_path = os.path.join(REPO, "scripts", "changelog_data.json")
    with open(log_path, encoding="utf-8") as f:
        log = json.load(f)
    log["applied_on"] = TODAY
    for u in applied:
        log["updates"].append({k: v for k, v in u.items() if k not in ("old", "new", "count")} | {
            "oud_fragment": u["old"][:140] + ("…" if len(u["old"]) > 140 else ""),
            "nieuw_fragment": u["new"][:140] + ("…" if len(u["new"]) > 140 else ""),
        })
    log["not_updated"].extend(NOT_UPDATED_2)
    with open(log_path, "w", encoding="utf-8") as f:
        json.dump(log, f, ensure_ascii=False, indent=2)
    print(f"Changelog bijgewerkt: {len(log['updates'])} wijzigingen totaal, {len(log['not_updated'])} toelichtingen totaal.")


if __name__ == "__main__":
    apply_updates()
