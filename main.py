"""
LLM + Tool Use demo: Kde je ISS a kto je práve vo vesmíre?

Skript volá OpenAI API (model gpt-4o-mini) s dvoma nástrojmi:
  - get_iss_location()   -> aktuálna poloha ISS (lat/lon) + mapový odkaz
  - get_people_in_space() -> zoznam ľudí, ktorí sú práve vo vesmíre

LLM sa sám rozhodne, ktorý nástroj zavolať, my výsledok vrátime späť
a necháme model sformulovať finálnu odpoveď pre užívateľa.
"""

import json
import os
import sys

import requests
from dotenv import load_dotenv
from openai import OpenAI

# Windows konzola niekedy používa cp1250 — vynútime UTF-8, aby sa diakritika nerozbila.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

load_dotenv(override=True)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

MODEL = "gpt-4o-mini"


def get_iss_location() -> dict:
    """Reálna poloha Medzinárodnej vesmírnej stanice."""
    r = requests.get("https://api.wheretheiss.at/v1/satellites/25544", timeout=10)
    r.raise_for_status()
    data = r.json()
    lat = float(data["latitude"])
    lon = float(data["longitude"])
    return {
        "latitude": round(lat, 4),
        "longitude": round(lon, 4),
        "altitude_km": round(float(data["altitude"]), 1),
        "velocity_kmh": round(float(data["velocity"]), 0),
        "map_url": f"https://www.google.com/maps?q={lat},{lon}",
        "timestamp": data["timestamp"],
    }


def get_people_in_space() -> dict:
    """Kto sa práve nachádza vo vesmíre a na akej lodi."""
    r = requests.get(
        "https://corquaid.github.io/international-space-station-APIs/JSON/people-in-space.json",
        timeout=10,
    )
    r.raise_for_status()
    data = r.json()
    return {
        "count": data["number"],
        "expedition": data.get("iss_expedition"),
        "people": [
            {
                "name": p["name"],
                "country": p.get("country"),
                "agency": p.get("agency"),
                "position": p.get("position"),
                "spacecraft": p.get("spacecraft"),
                "days_in_space": p.get("days_in_space"),
            }
            for p in data["people"]
        ],
    }


TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_iss_location",
            "description": "Vráti aktuálnu zemepisnú polohu Medzinárodnej vesmírnej stanice (ISS).",
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_people_in_space",
            "description": "Vráti zoznam ľudí, ktorí sú práve vo vesmíre, a lode na ktorých sa nachádzajú.",
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
]

TOOL_REGISTRY = {
    "get_iss_location": get_iss_location,
    "get_people_in_space": get_people_in_space,
}


SYSTEM_PROMPT = (
    "Vystupuješ ako komunikačný zamestnanec NASA (Public Affairs Officer), "
    "ktorý verejnosti a novinárom prezentuje aktuálne dianie okolo Medzinárodnej "
    "vesmírnej stanice. Si priateľský, profesionálny a zanietený pre vesmír. "
    "Odpovedaj po slovensky, výlučne v jednom krátkom plynulom odstavci, tak ako "
    "by si odpovedal pri tlačovom brífingu — bez zoznamov, odrážok, nadpisov, "
    "tabuliek a JSON-u. Občas pridaj drobný kontext alebo zaujímavosť (napr. "
    "rýchlosť stanice, národnosť posádky, názov misie), ale zostaň stručný. "
    "Čísla zaokrúhľuj rozumne. Ak užívateľ potrebuje aktuálne informácie o polohe "
    "ISS alebo o ľuďoch vo vesmíre, vždy použi dostupné nástroje — nikdy si údaje "
    "nevymýšľaj."
)


MAX_TOOL_ROUNDS = 10


def ask(messages: list, user_message: str) -> str:
    """Pridá otázku do histórie, spustí tool-use cyklus a vráti odpoveď."""
    messages.append({"role": "user", "content": user_message})

    for _ in range(MAX_TOOL_ROUNDS):
        response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            tools=TOOLS,
        )
        msg = response.choices[0].message
        messages.append(msg)

        if not msg.tool_calls:
            return msg.content

        for call in msg.tool_calls:
            fn = TOOL_REGISTRY[call.function.name]
            args = json.loads(call.function.arguments or "{}")
            result = fn(**args)
            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": call.id,
                    "content": json.dumps(result, ensure_ascii=False),
                }
            )

    return "Prepáč, nepodarilo sa mi dospieť k odpovedi — skús sa opýtať inak."


EXIT_WORDS = {"koniec", "exit", "quit", "q", "bye", "dovi", "dovidenia"}


def main() -> None:
    if not os.getenv("OPENAI_API_KEY"):
        raise SystemExit("Chýba OPENAI_API_KEY v .env súbore.")

    print("Ahoj! Mám aktuálne informácie o polohe Medzinárodnej vesmírnej "
          "stanice a o všetkých astronautoch, ktorí sú práve vo vesmíre. "
          "Pýtaj sa, čo ťa zaujíma.")
    print("(Pre ukončenie napíš 'koniec' alebo stlač Ctrl+C.)\n")

    messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    while True:
        try:
            otazka = input("Otázka: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nMaj sa!")
            return

        if not otazka:
            continue
        if otazka.lower() in EXIT_WORDS:
            print("Maj sa!")
            return

        odpoved = ask(messages, otazka)
        print(f"\n{odpoved}\n")


if __name__ == "__main__":
    main()
