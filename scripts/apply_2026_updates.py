#!/usr/bin/env python3
"""
Bijwerken van een afgebakende set jaarlijks geïndexeerde fiscale/financiële
kerncijfers naar het niveau 2026, met volledige transparantie-log.

BELANGRIJK — reikwijdte (zie ook wijzigingen.html):
Dit script wijzigt UITSLUITEND losstaande, declaratieve vermeldingen van
grensbedragen/tarieven/percentages (definities en tabellen). Het wijzigt
NOOIT cijfers die onderdeel zijn van een doorgerekend (genoemd) voorbeeld
(bijv. "Hanneke", "Abby", "Patrick", "Karel", "Léon"), omdat het aanpassen
van één variabele daarin de rest van de berekening ongeldig zou maken
zonder dat dit hier betrouwbaar kan worden nagerekend. Dergelijke
voorbeelden blijven dus op het prijspeil 2025 staan.

Elke wijziging hieronder is voorzien van een bron. Waar een cijfer wel
herkend maar NIET bijgewerkt is (onvoldoende harde bronbevestiging voor
2026), staat dat toegelicht in NOT_UPDATED hieronder — ook zichtbaar op
wijzigingen.html.

Run: python3 scripts/apply_2026_updates.py
"""
import json
import os
import sys
from datetime import date

REPO = "/home/user/nvhp-syllabus"
TODAY = date.today().isoformat()

# Elke entry: book, old (exacte, unieke substring in het bestand), new,
# topic, source (naam + url), note (toelichting).
UPDATES = [
    # ---------------- BOEK 1: Recht en fiscaliteit ----------------
    dict(book="boek1.html", topic="Box 1 — tarieven (jonger dan AOW-leeftijd)",
         old="De tarieven in box 1 (2025) voor belastingplichtigen jonger dan de AOW-leeftijd zien er als volgt uit 9:",
         new="De tarieven in box 1 (2026) voor belastingplichtigen jonger dan de AOW-leeftijd zien er als volgt uit 9:",
         source="Belastingdienst — tarieven box 1, voorlopige aanslag 2026",
         source_url="https://www.belastingdienst.nl/wps/wcm/connect/nl/voorlopige-aanslag/content/voorlopige-aanslag-tarieven-en-heffingskortingen"),
    dict(book="boek1.html", topic="Box 1 — schijventabel (jonger dan AOW-leeftijd)",
         old="<p>Schijf       Belastbaar inkomen                                   Percentage 1            tot € 38.441                                         35,82 2            vanaf € 38.441 t/m € 76.817                          37,48 3            vanaf € 76.817                                       49,50</p>",
         new="<p>Schijf       Belastbaar inkomen                                   Percentage 1            tot € 38.883                                         35,75 2            vanaf € 38.883 t/m € 78.426                          37,56 3            vanaf € 78.426                                       49,50</p>",
         source="Belastingdienst — tarieven box 1, voorlopige aanslag 2026",
         source_url="https://www.belastingdienst.nl/wps/wcm/connect/nl/voorlopige-aanslag/content/voorlopige-aanslag-tarieven-en-heffingskortingen"),
    dict(book="boek1.html", topic="Box 1 — schijfgrenzen en tarieven (toelichtende tekst)",
         old="In 2025 kennen wij voor belastingplichtigen die de AOW-leeftijd nog niet hebben bereikt drie tarieven: 35,82, 37,48 en 49,50%. De eerste schijf loopt tot een belastbaar inkomen in box 1 van € 38.441, de tweede tot € 76.817.",
         new="In 2026 kennen wij voor belastingplichtigen die de AOW-leeftijd nog niet hebben bereikt drie tarieven: 35,75, 37,56 en 49,50%. De eerste schijf loopt tot een belastbaar inkomen in box 1 van € 38.883, de tweede tot € 78.426.",
         source="Belastingdienst — tarieven box 1, voorlopige aanslag 2026",
         source_url="https://www.belastingdienst.nl/wps/wcm/connect/nl/voorlopige-aanslag/content/voorlopige-aanslag-tarieven-en-heffingskortingen"),
    dict(book="boek1.html", topic="Box 2 — schijfgrens (definitie boxenstructuur)",
         old="box 2: belastbaar inkomen uit aanmerkelijk belang, tot en met € 67.804 24,50 procent en hoger dan € 67.804 31,00 procent.",
         new="box 2: belastbaar inkomen uit aanmerkelijk belang, tot en met € 68.843 24,50 procent en hoger dan € 68.843 31,00 procent.",
         source="Belastingplan 2026 / viajuridica.nl, wetstoelichting tarief box 2",
         source_url="https://www.viajuridica.nl/informatiesoorten/wetstoelichtingen/tarief-box-2-art-2-12-wet-ib-2001"),
    dict(book="boek1.html", topic="Box 2 — schijfgrens (toelichting)",
         old="In 2025 zijn er twee schijven in box 2. Over AB-inkomen tot en met € 67.804 wordt 24,50 procent belasting geheven en daarboven 31 procent.",
         new="In 2026 zijn er twee schijven in box 2. Over AB-inkomen tot en met € 68.843 wordt 24,50 procent belasting geheven en daarboven 31 procent.",
         source="Belastingplan 2026 / viajuridica.nl, wetstoelichting tarief box 2",
         source_url="https://www.viajuridica.nl/informatiesoorten/wetstoelichtingen/tarief-box-2-art-2-12-wet-ib-2001"),
    dict(book="boek1.html", topic="Algemene heffingskorting — afbouwgrens en maximum",
         old="Dat houdt inmiddels in 2025 in dat vanaf een belastbaar inkomen uit werk en woning in box 1 van € 28.406 de algemene heffingskorting lager wordt naarmate dit inkomen stijgt. De algemene heffingskorting is - ongeacht de hoogte van het belastbare inkomen in box 1 - maximaal € 3.068 (vanaf de AOW-gerechtigde leeftijd € 1.536).",
         new="Dat houdt inmiddels in 2026 in dat vanaf een belastbaar inkomen uit werk en woning in box 1 van € 29.736 de algemene heffingskorting lager wordt naarmate dit inkomen stijgt. De algemene heffingskorting is - ongeacht de hoogte van het belastbare inkomen in box 1 - maximaal € 3.115 (vanaf de AOW-gerechtigde leeftijd: bedrag 2025 van € 1.536 hier nog niet herbevestigd voor 2026).",
         source="Belastingdienst / FNV heffingskortingen 2026",
         source_url="https://www.fnv.nl/getmedia/4a4853d6-df54-4b5d-87be-d519894d9f2f/260042-08-heffingskortingen-2026-ia.pdf"),
    dict(book="boek1.html", topic="Algemene heffingskorting — tabeltitel",
         old="<p>In 2025 nog niet de AOW-leeftijd bereikt</p>",
         new="<p>In 2026 nog niet de AOW-leeftijd bereikt</p>",
         source="Belastingdienst / FNV heffingskortingen 2026",
         source_url="https://www.fnv.nl/getmedia/4a4853d6-df54-4b5d-87be-d519894d9f2f/260042-08-heffingskortingen-2026-ia.pdf"),
    dict(book="boek1.html", topic="Algemene heffingskorting — afbouwtabel",
         old="Belastbaar inkomen uit werk en woning vanaf                            tot Algemene heffingskorting 0                      € 28.406        € 3.068 € 28.406                      € 76.817        € 3.068 -/- 6,337% x (belastbaar inkomen uit werk en woning -/- € 28.406) € 76.817                                 -   €0",
         new="Belastbaar inkomen uit werk en woning vanaf                            tot Algemene heffingskorting 0                      € 29.736        € 3.115 € 29.736                      € 78.426        € 3.115 -/- 6,398% x (belastbaar inkomen uit werk en woning -/- € 29.736) € 78.426                                 -   €0",
         source="Belastingdienst / FNV heffingskortingen 2026",
         source_url="https://www.fnv.nl/getmedia/4a4853d6-df54-4b5d-87be-d519894d9f2f/260042-08-heffingskortingen-2026-ia.pdf"),
    dict(book="boek1.html", topic="Overzicht heffingskortingen — algemene heffingskorting en arbeidskorting",
         old="Algemene heffingskorting                              € 3.068115*              € 1.536* Arbeidskorting                                        € 5.599116*              € 2.802*",
         new="Algemene heffingskorting                              € 3.115*              € 1.536** Arbeidskorting                                        € 5.685*              € 2.802**",
         source="Belastingdienst / FNV heffingskortingen 2026 (arbeidskorting: bronnen wijken af tussen € 5.685 en € 5.712 — hier de meest genoemde waarde aangehouden)",
         source_url="https://www.fnv.nl/getmedia/4a4853d6-df54-4b5d-87be-d519894d9f2f/260042-08-heffingskortingen-2026-ia.pdf",
         note="** = AOW-kolom (1.536 / 2.802) hier NIET bijgewerkt: geen harde 2026-bronbevestiging gevonden. Voetnootcijfers 115/116 (PDF-extractieartefact) zijn bij deze gelegenheid verwijderd."),
    dict(book="boek1.html", topic="Arbeidskorting — maximum",
         old="Het maximale bedrag van de arbeidskorting is in 2025 € 5.599.",
         new="Het maximale bedrag van de arbeidskorting is in 2026 € 5.685 (sommige bronnen noemen € 5.712; het Belastingplan 2026 was op het moment van bijwerken nog niet in alle opzichten definitief vastgesteld).",
         source="Rendement.nl / rekenmachinepro.nl, arbeidskorting 2026",
         source_url="https://www.rendement.nl/aangifte-loonheffingen/nieuws/arbeidskorting-stijgt-opnieuw-licht-in-2026.html"),
    dict(book="boek1.html", topic="Eigenwoningforfait — jaartal",
         old="<p>Het eigenwoningforfait is in 2025 gesteld op:</p>",
         new="<p>Het eigenwoningforfait is in 2026 gesteld op:</p>",
         source="Belastingdienst — tabel eigenwoningforfait 2026",
         source_url="https://www.belastingdienst.nl/wps/wcm/connect/nl/koopwoning/content/hoe-werkt-eigenwoningforfait"),
    dict(book="boek1.html", topic="Eigenwoningforfait — hoogste schijf en toeslag",
         old="€ 75.000            € 1.330.000 0,35% van deze waarde € 1.3320.000                          - € 4.655 vermeerderd met 2,35% van de waarde voor zover deze hoger is dan € 1.330.000",
         new="€ 75.000            € 1.350.000 0,35% van deze waarde € 1.350.000                          - € 4.725 vermeerderd met 2,35% van de waarde voor zover deze hoger is dan € 1.350.000",
         source="Belastingdienst — tabel eigenwoningforfait 2026 / Eerste Kamer achtergrondrapport",
         source_url="https://www.belastingdienst.nl/wps/wcm/connect/nl/koopwoning/content/hoe-werkt-eigenwoningforfait",
         note="'€ 1.3320.000' in de brontekst was een PDF-extractiefout (twee cijfers aan elkaar geplakt); bij deze gelegenheid gecorrigeerd én bijgewerkt naar 2026."),
    dict(book="boek1.html", topic="Overdrachtsbelasting — startersgrens",
         old="Tot 2025 was die waarde € 510.000 en vanaf 2025 is dat € 525.000.",
         new="Tot 2025 was die waarde € 525.000 en vanaf 2026 is dat € 555.000.",
         source="Belastingdienst — startersvrijstelling overdrachtsbelasting",
         source_url="https://www.belastingdienst.nl/wps/wcm/connect/bldcontentnl/belastingdienst/prive/woning/overdrachtsbelasting/startersvrijstelling"),
    dict(book="boek1.html", topic="Overdrachtsbelasting — startersgrens (voorwaarde)",
         old="• de woning is maximaal € 525.000.",
         new="• de woning is maximaal € 555.000.",
         source="Belastingdienst — startersvrijstelling overdrachtsbelasting",
         source_url="https://www.belastingdienst.nl/wps/wcm/connect/bldcontentnl/belastingdienst/prive/woning/overdrachtsbelasting/startersvrijstelling"),
    dict(book="boek1.html", topic="Overdrachtsbelasting — algemeen tarief (niet-eigen-bewoning)",
         old="Beleggers in box 3 betalen sinds 2023 10,4 procent.",
         new="Beleggers in box 3 betalen in 2026 8 procent (dit was 10,4 procent van 2023 tot en met 2025).",
         source="SRA — overdrachtsbelasting 2026",
         source_url="https://www.sra.nl/nieuws/259001/2026/01/overdrachtsbelasting-drie-tarieven-en-hogere-startersvrijstelling-in-2026"),
    dict(book="boek1.html", topic="Overdrachtsbelasting — algemeen tarief (niet zelfbewoning)",
         old="Kopers betalen vanaf 1 januari 2023 10,4 procent overdrachtsbelasting als ze niet zelf in de woning gaan wonen.",
         new="Kopers betalen in 2026 8 procent overdrachtsbelasting als ze niet zelf in de woning gaan wonen (van 2023 tot en met 2025 was dit 10,4 procent).",
         source="SRA — overdrachtsbelasting 2026",
         source_url="https://www.sra.nl/nieuws/259001/2026/01/overdrachtsbelasting-drie-tarieven-en-hogere-startersvrijstelling-in-2026"),
    dict(book="boek1.html", topic="Overdrachtsbelasting — tweede woningen",
         old="ook onder het 10,4 procent tarief.",
         new="ook onder het 8 procent tarief (2023-2025: 10,4 procent).",
         source="SRA — overdrachtsbelasting 2026",
         source_url="https://www.sra.nl/nieuws/259001/2026/01/overdrachtsbelasting-drie-tarieven-en-hogere-startersvrijstelling-in-2026"),
    dict(book="boek1.html", topic="Overdrachtsbelasting — wooncoöperaties",
         old="Wooncoöperaties betalen geen 10,4 procent overdrachtsbelasting, maar twee procent",
         new="Wooncoöperaties betalen geen 8 procent overdrachtsbelasting (2023-2025: 10,4 procent), maar twee procent",
         source="SRA — overdrachtsbelasting 2026",
         source_url="https://www.sra.nl/nieuws/259001/2026/01/overdrachtsbelasting-drie-tarieven-en-hogere-startersvrijstelling-in-2026"),

    # ---------------- BOEK 2: Planning ----------------
    dict(book="boek2.html", topic="Schenkbelasting — vrijstellingstabel",
         old="Vrijstellingsbedragen schenkbelasting﻿ Kinderen jaarlijks                                                  €   6.713 Kinderen 18 - 40 jaar (eenmalig, vrij te besteden)                  € 32.195 Kind 18-40 jaar (dure studie)                                       € 67.064 Overige verkrijgers                                                 €   2.690",
         new="Vrijstellingsbedragen schenkbelasting﻿ Kinderen jaarlijks                                                  €   6.908 Kinderen 18 - 40 jaar (eenmalig, vrij te besteden)                  € 32.195* Kind 18-40 jaar (dure studie)                                       € 67.064* Overige verkrijgers                                                 €   2.769",
         source="Belastingdienst — schenkingsvrijstellingen 2026",
         source_url="https://www.belastingdienst.nl/wps/wcm/connect/nl/schenken/content/tot-welk-bedrag-belastingvrij-schenken",
         note="* = bedragen 2025, (nog) niet bijgewerkt: voor de eenmalige vrijstelling (18-40 jaar) en de studievrijstelling is geen harde 2026-bronbevestiging gevonden — controleer voor gebruik bij belastingdienst.nl."),
    dict(book="boek2.html", topic="Schenking — jaarlijkse vrijstelling overige verkrijgers (ex-partner)",
         old="Als er meer wordt betaald dan € 2.690 (2025) per jaar, dan is het meerdere een belaste schenking.",
         new="Als er meer wordt betaald dan € 2.769 (2026) per jaar, dan is het meerdere een belaste schenking.",
         source="Belastingdienst — schenkingsvrijstellingen 2026",
         source_url="https://www.belastingdienst.nl/wps/wcm/connect/nl/schenken/content/tot-welk-bedrag-belastingvrij-schenken"),
    dict(book="boek2.html", topic="Schenking — jaarlijkse vrijstelling overige verkrijgers (erfgenaam)",
         old="De schenkingsvrijstelling is dan anno 2025 € 2.690 en het tarief tot € 154.197 30 procent en erboven 40 procent.",
         new="De schenkingsvrijstelling is dan anno 2026 € 2.769 en het tarief tot € 154.197 (bedrag 2025, nog niet herbevestigd voor 2026) 30 procent en erboven 40 procent.",
         source="Belastingdienst — schenkingsvrijstellingen 2026",
         source_url="https://www.belastingdienst.nl/wps/wcm/connect/nl/schenken/content/tot-welk-bedrag-belastingvrij-schenken"),
    dict(book="boek3.html", topic="Box 2 — schijfgrens en dubbele lage schijf fiscaal partners",
         old="tweemaal de lage schijf toepassen, tot € 135.608.",
         new="tweemaal de lage schijf toepassen, tot € 137.686.",
         source="Belastingplan 2026 / dezaak.nl",
         source_url="https://www.dezaak.nl/financien/belastingen/belastingwijzigingen-2026-dit-staat-ondernemers-te-wachten/",
         note="Alleen de losstaande grensvermelding is bijgewerkt. Een eventuele doorgerekende casus in dezelfde passage is bewust niet aangepast — zie reikwijdte hierboven."),

    # ---------------- BOEK 3: Financieren ----------------
    dict(book="boek3.html", topic="NHG-grens en energiebesparende voorzieningen (ebv)",
         old="Op basis van deze systematiek neemt de NHG-grens in 2025 toe tot € 450.000 (€ 15.000 meer dan in 2024). Om verduurzaming te stimuleren is extra leenruimte beschikbaar. Met Energie Besparende Voorzieningen (ebv) is de NHG-grens in 2025 € 477.000.",
         new="Op basis van deze systematiek neemt de NHG-grens in 2026 toe tot € 470.000 (€ 20.000 meer dan in 2025). Om verduurzaming te stimuleren is extra leenruimte beschikbaar. Met Energie Besparende Voorzieningen (ebv) is de NHG-grens in 2026 € 498.200.",
         source="NHG-normering 2026 / Hypotheker.nl",
         source_url="https://www.hypotheker.nl/actueel/nieuwsberichten/2025/nhg-grens-vastgesteld-voor-2026/"),
    dict(book="boek3.html", topic="NHG-grens woonwagens — vervallen aparte grens",
         old="De NHG-grens voor woonwagens wordt in 2025 verhoogd van € 166.000 naar € 172.000. Inclusief ebv stijgt deze naar € 182.320.",
         new="Tot en met 2025 gold voor woonwagens een eigen, lagere NHG-grens (2025: € 172.000, met ebv € 182.320). Per 1 januari 2026 is deze aparte grens vervallen: woonwagens en standplaatsen vallen nu onder dezelfde (uniforme) kostengrens als andere woningen (€ 470.000, met ebv € 498.200).",
         source="NHG-normering 2026 / Hypotheker.nl",
         source_url="https://www.hypotheker.nl/actueel/nieuwsberichten/2025/nhg-grens-vastgesteld-voor-2026/"),
    dict(book="boek3.html", topic="NHG — nieuwbouw, maximale kostengrens (a t/m i resp. a t/m h)",
         old="het totaal van a t/m i mag maximaal € 477.000 zijn. En het totaal van a t/m h mag maximaal € 450.000 zijn.",
         new="het totaal van a t/m i mag maximaal € 498.200 zijn. En het totaal van a t/m h mag maximaal € 470.000 zijn.",
         source="NHG-normering 2026 / Hypotheker.nl",
         source_url="https://www.hypotheker.nl/actueel/nieuwsberichten/2025/nhg-grens-vastgesteld-voor-2026/"),
    dict(book="boek3.html", topic="NHG — nieuwbouw, A++++ label",
         old="bij koop van een woning met een A++++ label mag het totaal van a, b en i maximaal € 477.000 zijn.",
         new="bij koop van een woning met een A++++ label mag het totaal van a, b en i maximaal € 498.200 zijn.",
         source="NHG-normering 2026 / Hypotheker.nl",
         source_url="https://www.hypotheker.nl/actueel/nieuwsberichten/2025/nhg-grens-vastgesteld-voor-2026/"),
    dict(book="boek3.html", topic="NHG — kostengrens verkrijging bestaande woning (voorwaarde 1)",
         old="Het bedrag voor de verkrijging in eigendom van de woning is maximaal € 450.000.",
         new="Het bedrag voor de verkrijging in eigendom van de woning is maximaal € 470.000.",
         source="NHG-normering 2026 / Hypotheker.nl",
         source_url="https://www.hypotheker.nl/actueel/nieuwsberichten/2025/nhg-grens-vastgesteld-voor-2026/",
         note="Alleen de grensvermelding is bijgewerkt; het eronder getoonde rekenvoorbeeld (€ 205.000, 6%, € 12.300) gebruikt andere, op zichzelf staande bedragen en is ongewijzigd gelaten."),
    dict(book="boek3.html", topic="Box 2 — schijfgrens en tarief",
         old="tegen een inkomstenbelastingtarief van 24,50 procent tot € 67.804 inkomen in box 2 en daarboven van 31 procent (2025).",
         new="tegen een inkomstenbelastingtarief van 24,50 procent tot € 68.843 inkomen in box 2 en daarboven van 31 procent (2026).",
         source="Belastingplan 2026 / viajuridica.nl",
         source_url="https://www.viajuridica.nl/informatiesoorten/wetstoelichtingen/tarief-box-2-art-2-12-wet-ib-2001"),
    dict(book="boek3.html", topic="Box 1 — hoogste schijf en aftrektarief eigenwoningrente",
         old="boven de € 76.817 (2025). In dat geval wordt namelijk wel 49,50 procent inkomstenbelasting geheven over het meerdere inkomen, en is de hypotheekrente ‘slechts’ aftrekbaar tegen 35,82 procent.",
         new="boven de € 78.426 (2026). In dat geval wordt namelijk wel 49,50 procent inkomstenbelasting geheven over het meerdere inkomen, en is de hypotheekrente ‘slechts’ aftrekbaar tegen 35,75 procent.",
         source="Belastingdienst — tarieven box 1, voorlopige aanslag 2026",
         source_url="https://www.belastingdienst.nl/wps/wcm/connect/nl/voorlopige-aanslag/content/voorlopige-aanslag-tarieven-en-heffingskortingen"),
    dict(book="boek3.html", topic="Overdrachtsbelasting — algemeen tarief en startersgrens",
         old="en 10,4 procent voor alle andere onroerende zaken, zoals vakantiewoningen, bedrijfspanden en bijvoorbeeld een garage bij het huis die pas ná de woning wordt gekocht.",
         new="en acht procent voor alle andere onroerende zaken, zoals vakantiewoningen, bedrijfspanden en bijvoorbeeld een garage bij het huis die pas ná de woning wordt gekocht (dit tarief was 10,4 procent van 2023 tot en met 2025).",
         source="SRA — overdrachtsbelasting 2026",
         source_url="https://www.sra.nl/nieuws/259001/2026/01/overdrachtsbelasting-drie-tarieven-en-hogere-startersvrijstelling-in-2026"),
    dict(book="boek3.html", topic="Overdrachtsbelasting — startersgrens",
         old="koopprijs woning is maximaal € 525.000.",
         new="koopprijs woning is maximaal € 555.000 (2025: € 525.000).",
         source="Belastingdienst — startersvrijstelling overdrachtsbelasting",
         source_url="https://www.belastingdienst.nl/wps/wcm/connect/bldcontentnl/belastingdienst/prive/woning/overdrachtsbelasting/startersvrijstelling"),

    # ---------------- BOEK 4: De klant in beeld ----------------
    dict(book="boek4.html", topic="Overdrachtsbelasting — startersgrens (woningwaardegrens)",
         old="De woningwaardegrens is geïndexeerd en is € 525.000 vanaf 2025.",
         new="De woningwaardegrens is geïndexeerd: € 525.000 in 2025, € 555.000 vanaf 2026.",
         source="Belastingdienst — startersvrijstelling overdrachtsbelasting",
         source_url="https://www.belastingdienst.nl/wps/wcm/connect/bldcontentnl/belastingdienst/prive/woning/overdrachtsbelasting/startersvrijstelling"),
    dict(book="boek4.html", topic="Overdrachtsbelasting — algemeen tarief",
         old="Per 1 januari 2023 is de overdrachtsbelasting voor niet-eigen-woningen én niet-woningen verhoogd van acht naar 10,4 procent. Twee procent geldt voor de woning waarin de koper zélf voor langere tijd gaat wonen en waarvoor de startersvrijstelling niet geldt. 10,4 Procent geldt voor alle andere onroerende zaken,",
         new="Van 1 januari 2023 tot en met 2025 was de overdrachtsbelasting voor niet-eigen-woningen én niet-woningen verhoogd naar 10,4 procent; per 1 januari 2026 is dit verlaagd naar acht procent. Twee procent geldt voor de woning waarin de koper zélf voor langere tijd gaat wonen en waarvoor de startersvrijstelling niet geldt. Acht procent geldt voor alle andere onroerende zaken,",
         source="SRA — overdrachtsbelasting 2026",
         source_url="https://www.sra.nl/nieuws/259001/2026/01/overdrachtsbelasting-drie-tarieven-en-hogere-startersvrijstelling-in-2026"),
    dict(book="boek4.html", topic="Overdrachtsbelasting — startersgrens (2026)",
         old="In 2025 is de grens voor de startersvrijstelling verhoogd naar een maximale aankoopprijs van de woning van € 525.000.",
         new="Per 2026 is de grens voor de startersvrijstelling € 555.000 (in 2025 was dat € 525.000).",
         source="Belastingdienst — startersvrijstelling overdrachtsbelasting",
         source_url="https://www.belastingdienst.nl/wps/wcm/connect/bldcontentnl/belastingdienst/prive/woning/overdrachtsbelasting/startersvrijstelling"),
    dict(book="boek4.html", topic="NHG-grens",
         old="De NHG-grens is verhoogd naar € 450.000.",
         new="De NHG-grens is in 2026 € 470.000 (met energiebesparende voorzieningen: € 498.200).",
         source="NHG-normering 2026 / Hypotheker.nl",
         source_url="https://www.hypotheker.nl/actueel/nieuwsberichten/2025/nhg-grens-vastgesteld-voor-2026/",
         note="De direct volgende zin over de extra hypotheekruimte voor alleenstaanden (€ 17.000, prijspeil 2025) is ongewijzigd gelaten: geen 2026-bronbevestiging gevonden."),
]

NOT_UPDATED = [
    dict(topic="Box 1 — AOW-overgangstarieven (geboren op/na 1946 en vóór 1946)",
         books="boek1.html",
         reason="Twee afzonderlijke tabellen met verlaagde/afwijkende schijf-1-tarieven voor AOW-gerechtigden "
                "(17,92% resp. grens € 40.502) zijn niet bijgewerkt: de gevonden 2026-bronnen bevestigen een "
                "vergelijkbaar maar niet exact overeenkomend cijfer (17,85% bij een grens van € 41.123) voor een "
                "net iets andere doelgroep-indeling, en het risico op een onjuiste 1-op-1 koppeling was te groot "
                "om hier zonder nadere verificatie door te voeren."),
    dict(topic="Box 3 — heffingsvrij vermogen en forfaitaire rendementspercentages",
         books="boek1.html, boek3.html",
         reason="Het heffingsvrij vermogen (2025: € 57.684) stijgt naar € 59.357 (2026) en de meeste bronnen "
                "bevestigen dit, maar de forfaitaire percentages voor banktegoeden en schulden voor 2026 waren op "
                "het moment van bijwerken nog 'voorlopig' (definitieve vaststelling pas begin 2027 verwacht). "
                "Om geen cijfers te publiceren die nog kunnen wijzigen, is dit onderdeel geheel buiten deze ronde "
                "gehouden — zie belastingdienst.nl voor de actuele stand."),
    dict(topic="AOW-leeftijd en pensioenrichtleeftijd",
         books="boek2.html",
         reason="De tabel in het boek (2025 t/m 2030, oplopend naar 67 jaar en 3 maanden) kwam bij controle al "
                "overeen met de huidige (2026) planning en is daarom ongewijzigd gelaten. De status van de "
                "RVU-regeling na 31 december 2025 is niet geverifieerd voor deze update."),
    dict(topic="Mogelijke tegenstrijdigheid aftrektarief 'grondslagverminderende posten'",
         books="boek1.html, boek4.html",
         reason="Boek 1 noemt het basistarief voor deze aftrekpost 35,82 procent (schijf 1), boek 4 noemt in een "
                "vergelijkbare passage (het voorbeeld van 'Karel') 37,48 procent (schijf 2). Dit lijkt een "
                "inconsistentie in het bronmateriaal zelf. Omdat niet met zekerheid is vast te stellen welk "
                "percentage hier bedoeld is, zijn beide passages ongewijzigd gelaten — dit verdient navraag bij "
                "de NVHP."),
    dict(topic="Doorgerekende (genoemde) voorbeelden",
         books="alle vier boeken",
         reason="Cijfers die onderdeel zijn van een voorbeeld met een naam (o.a. Hanneke, Abby, Patrick Smabers, "
                "Karel, Léon, Gerard en Nancy) zijn principieel niet aangepast: het wijzigen van één grensbedrag "
                "of tarief daarin vereist het herrekenen van de rest van dat voorbeeld, wat buiten de "
                "betrouwbaar te verifiëren reikwijdte van deze update valt."),
    dict(topic="Overige jaartal- en cijfervermeldingen (‘(2025)’ e.d.)",
         books="alle vier boeken",
         reason="Deze update betreft een afgebakende set veelgebruikte, jaarlijks geïndexeerde kerncijfers "
                "(belastingschijven, heffingskortingen, box 2-grens, eigenwoningforfait, NHG-grens, "
                "overdrachtsbelasting, een deel van de schenkingsvrijstellingen). Er resteren nog diverse andere "
                "jaartal- en bedragvermeldingen (circa 400 in totaal) die niet individueel zijn gecontroleerd. "
                "Zie ook wijzigingen.html."),
]


def apply_updates():
    applied = []
    failed = []
    for upd in UPDATES:
        path = os.path.join(REPO, upd["book"])
        with open(path, encoding="utf-8") as f:
            content = f.read()
        count = content.count(upd["old"])
        if count != 1:
            failed.append((upd, count))
            continue
        content = content.replace(upd["old"], upd["new"], 1)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        applied.append(upd)

    print(f"Toegepast: {len(applied)} / {len(UPDATES)}")
    if failed:
        print("MISLUKT (anker niet precies 1x gevonden):")
        for upd, count in failed:
            print(f"  [{upd['book']}] {upd['topic']!r} -> gevonden {count}x")
        sys.exit(1)

    log = {
        "applied_on": TODAY,
        "updates": [
            {k: v for k, v in u.items() if k not in ("old", "new")} | {
                "oud_fragment": u["old"][:140] + ("…" if len(u["old"]) > 140 else ""),
                "nieuw_fragment": u["new"][:140] + ("…" if len(u["new"]) > 140 else ""),
            }
            for u in applied
        ],
        "not_updated": NOT_UPDATED,
    }
    with open(os.path.join(REPO, "scripts", "changelog_data.json"), "w", encoding="utf-8") as f:
        json.dump(log, f, ensure_ascii=False, indent=2)
    print(f"Changelog weggeschreven naar scripts/changelog_data.json ({len(applied)} wijzigingen, {len(NOT_UPDATED)} toelichtingen).")


if __name__ == "__main__":
    apply_updates()
