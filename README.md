# Vibe Coding kurz - Domáca úloha 1 — LLM + Tool Use (ISS asistent)

Python chatbot v termináli, ktorý cez **OpenAI API** (model `gpt-4o-mini`) odpovedá na otázky o Medzinárodnej vesmírnej stanici a astronautoch vo vesmíre. Aktuálne dáta (poloha ISS, astronauti) si ťahá cez **tool use** z verejných API.

## Práca s LLM API

Bez LLM by to bolo len obyčajné HTTP volanie. LLM pridáva **porozumenie reči**,
**samostatné rozhodnutie** ktorý nástroj kedy zavolať, **formuláciu odpovede**
a **pamäť konverzácie** (nadväzujúce otázky fungujú).

## Nástroje

| Nástroj | Popis | Zdroj |
|---|---|---|
| `get_iss_location()` | Poloha ISS (lat/lon, výška, rýchlosť) | `api.wheretheiss.at` |
| `get_people_in_space()` | Posádka (meno, krajina, agentúra, loď, dni v kozme) | `corquaid.github.io` |

Obe API sú verejné a bez kľúča.

## Inštalácia

```bash
python -m venv .venv
.venv\Scripts\activate          # Windows
# source .venv/bin/activate      # macOS / Linux
pip install -r requirements.txt
```

## Konfigurácia

Skopíruj `.env.example` do `.env` a doplň svoj OpenAI API kľúč
(<https://platform.openai.com/api-keys>):

```env
OPENAI_API_KEY=sk-...
```

## Spustenie

```bash
python main.py
```

Ukončenie: `koniec` (alebo `exit`, `quit`, `q`) či `Ctrl+C`.

## Príklad komunikácie

```
Ahoj! Mám aktuálne informácie o polohe Medzinárodnej vesmírnej stanice a o všetkých astronautoch, ktorí sú práve vo vesmíre. Pýtaj sa, čo ťa zaujíma.
(Pre ukončenie napíš 'koniec' alebo stlač Ctrl+C.)

Otázka: Koľko ľudí je aktuálne vo vesmíre?

Aktuálne je vo vesmíre 10 astronautov z rôznych krajín, ktorí sa nachádzajú na troch rôznych vesmírnych lodiach. Medzi nimi sú aj štyria astronauti z Číny na lodi Shenzhou 22, traja z USA na lodi Crew-12 Dragon a dvaja z Ruska na lodi Soyuz MS-28, pričom misia Expedície 74 prebieha v plnom prúde. Napríklad, Jessica Meir z NASA je vo vesmíre už 204 dní, zatiaľ čo Wu Fei z Číny je na svojej prvej misii.

Otázka: Je tam nejaký slovák?

Momentálne nie je žiadny Slovák medzi astronautami, ktorí sú vo vesmíre. Napriek tomu Slovensko má ambície v oblasti vesmírneho výskumu a technológie, a slovenskí vedci a inžinieri sa aktívne zapájajú do medzinárodných vesmírnych projektov a iniciatív. Veríme, že v budúcnosti sa aj slovenskí astronauti dostanú na medzinárodnú scénu.

Otázka: koniec
Maj sa!
```

Pri druhej otázke model **nevolal tool znova** — dáta o posádke má v histórii
konverzácie z prvej odpovede.

## Ako funguje tool-use cyklus

1. Skript pošle otázku + definíciu nástrojov modelu.
2. Model buď odpovie priamo, alebo vráti `tool_calls`.
3. Skript zavolá funkciu a výsledok pošle späť ako správu `role: "tool"`.
4. Model sformuluje finálnu odpoveď. Ak potrebuje ďalší tool, cyklus sa opakuje.
5. Celá história (vrátane predošlých otázok a odpovedí) sa posiela pri každom volaní, takže konverzácia má pamäť.
