# Vibe Coding DÚ 1 — LLM + Tool Use (ISS asistent)

Python skript, ktorý demonštruje **tool use** (function calling) s OpenAI API
formou jednoduchého konverzačného chatbota v termináli.

Téma: **Asistent, ktorý pozná aktuálnu polohu a posádku Medzinárodnej vesmírnej
stanice (ISS).** Po spustení sa skript pozdraví, čaká na otázku a odpovedá
v prirodzenej reči — jedným krátkym odstavcom, bez zoznamov a JSON-u. Konverzácia
pokračuje v slučke a model si pamätá predošlé otázky, takže zvláda aj nadväzujúce
otázky ("A kto je tam z Ruska?").

## Prečo je v úlohe LLM potrebné?

Bez LLM by šlo len o obyčajné HTTP volanie — `print(get_iss_location())`.
LLM pridáva:

- **porozumenie prirodzenej reči** (pochopí "Kde lieta?", "Where is ISS?", preklepy),
- **samostatné rozhodnutie**, ktorý nástroj zavolať a kedy,
- **formulovanie odpovede** po slovensky, prirodzene, v kontexte dialógu.

A tool zas dáva LLM to, čo sám nevie — **aktuálne real-time dáta**, ktoré nie sú
v tréningových dátach. Bez toolu by si polohu ISS vymyslel.

## Nástroje (tools)

| Nástroj | Popis | Zdroj dát |
|---|---|---|
| `get_iss_location()` | Aktuálna poloha ISS (lat/lon, výška, rýchlosť, mapa) | `api.wheretheiss.at` |
| `get_people_in_space()` | Zoznam ľudí vo vesmíre (meno, krajina, agentúra, pozícia, loď, dni vo vesmíre) | `corquaid.github.io` |

Obe API sú verejné a nevyžadujú kľúč.

## Inštalácia

```bash
python -m venv .venv
.venv\Scripts\activate           # Windows (CMD / PowerShell)
# source .venv/Scripts/activate   # Git Bash na Windows
# source .venv/bin/activate        # macOS / Linux
pip install -r requirements.txt
```

## Konfigurácia

1. Skopíruj `.env.example` do `.env`.
2. Doplň svoj OpenAI API kľúč (získaš ho na <https://platform.openai.com/api-keys>):

```env
OPENAI_API_KEY=sk-...
```

## Spustenie

```bash
python main.py
```

Pre ukončenie napíš `koniec` (alebo `exit`, `quit`, `q`) alebo stlač `Ctrl+C`.

## Príklad komunikácie

```
Ahoj! Mám aktuálne informácie o polohe a posádke Medzinárodnej vesmírnej stanice. Pýtaj sa, čo ťa zaujíma.
(Pre ukončenie napíš 'koniec' alebo stlač Ctrl+C.)

Ty: Koľko ľudí je teraz na ISS?

Na Medzinárodnej vesmírnej stanici (ISS) sa momentálne nachádza 10 ľudí. Patria sem astronauti z rôznych krajín vrátane Číny, Ruska, USA a Francúzska.

Ty: Je tam nejaký slovák alebo čech?

Na Medzinárodnej vesmírnej stanici nie sú momentálne žiadni Slováci ani Česi. Všetci astronauti, ktorí sú tam teraz, pochádzajú z Číny, Ruska, USA a Francúzska.

Ty: A kde sa aktuálne ISS nachádza?

Medzinárodná vesmírna stanica sa aktuálne nachádza na súradniciach 27,0° južnej šírky a 42,0° východnej dĺžky, vo výške približne 430 km nad zemským povrchom a pohybuje sa rýchlosťou okolo 27 549 km/h. Môžeš sa na ňu pozrieť aj na tomto odkaze [mapa](https://www.google.com/maps?q=-27.037734359685,42.04388607141).

Ty: Nad akou krajinou to presne je?

Aktuálne sa Medzinárodná vesmírna stanica nachádza nad Indickým oceánom, približne južne od afrického kontinentu.

Ty: koniec
Maj sa!
```

Všimni si, že pri poslednej otázke *"Nad akou krajinou to presne je?"* model
**nezavolal žiadny tool znova** — odvodil odpoveď z predošlých súradníc, ktoré
si pamätá z histórie konverzácie.

## Ako to vnútorne funguje (tool-use cyklus)

1. Skript pošle otázku modelu spolu s definíciou dostupných nástrojov.
2. Model sa rozhodne — buď odpovie priamo, alebo vráti `tool_calls` so zoznamom
   nástrojov, ktoré chce zavolať.
3. Skript tieto funkcie skutočne vykoná a výsledok pridá do konverzácie ako
   správu s rolou `tool`.
4. Model dostane výsledky a sformuluje finálnu odpoveď pre užívateľa.
5. Ak model potrebuje ďalšie volanie, cyklus sa opakuje. Inak odpoveď ide
   rovno do terminálu.

Použitý model: **`gpt-4o-mini`** (rýchly a lacný, ideálny pre tento typ úlohy).
