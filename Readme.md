```text
██████╗  ██████╗ ██╗  ██╗███████╗███╗   ███╗ ██████╗ ███╗   ██╗
██╔══██╗██╔═══██╗██║ ██╔╝██╔════╝████╗ ████║██╔═══██╗████╗  ██║
██████╔╝██║   ██║█████╔╝ █████╗  ██╔████╔██║██║   ██║██╔██╗ ██║
██╔═══╝ ██║   ██║██╔═██╗ ██╔══╝  ██║╚██╔╝██║██║   ██║██║╚██╗██║
██║     ╚██████╔╝██║  ██╗███████╗██║ ╚═╝ ██║╚██████╔╝██║ ╚████║
╚═╝      ╚═════╝ ╚═╝  ╚═╝╚══════╝╚═╝     ╚═╝ ╚═════╝ ╚═╝  ╚═══╝
```

# Pokémon Text Adventure – Gen-1 Edition

Willkommen zu diesem Retro-Pokémon-Text-Adventure - Nostalgie pur für Fans der ersten Generation.

Inhaltlich orientiert sich dieses Spiel an den ersten Gameboy-Pokémon-Versionen
mit den Editionen Rot, Blau und Gelb und 151 Pokémons.  

In diesem Spiel schlüpfst du in die Rolle eines Pokémon-Trainers und begibst
dich auf eine Reise durch die Kanto-Region.  

- Wähle deinen Starter-Pokémon (1 von 3)
- Kämpfe gegen wilde Pokémon und andere Trainer
- Sammle alle im Spiel vorhandenen Pokémon
- Werde der beste Pokémon-Trainer, den die Welt je gesehen hat  

Alles findet textbasiert im Terminal statt. Die Basisversion ist funktional, aber bewusst minimal gehalten.
Sie enthält eine kleine Startwelt mit ersten NPCs und Locations, um einen soliden Ausgangspunkt für die weitere Entwicklung zu bieten.
Das Projekt soll von Informatik-Studenten im Rahmen des Anwendungsprojekts im 2. Semester sprintbasiert weiterentwickelt und verbessert werden.
Die Idee ist auf dem bestehenden Code aufzubauen und sich eine eigene kleine Geschichte zu schaffen:
Charaktere erfinden, eine Kanto-inspirierte Welt mit neuen Locations und Pokémon erschaffen, spannende Quests und Dialoge entwickeln, ... der Kreativität sind keine Grenzen gesetzt.
**Das Ziel ist dem Spiel eine Story zu geben, die es spielenswert macht.**

---

## Disclaimer
Dieses Projekt ist ein reines Lehrprojekt an der DHBW Heidenheim.
Pokémon und alle zugehörigen Namen sind Marken von Nintendo/Game Freak.
Das Projekt steht in keiner Verbindung zu Nintendo.

This is an educational project developed as a lecture example at DHBW Heidenheim.
Pokémon and all related names are trademarks of Nintendo/Game Freak.
This project is not affiliated with or endorsed by Nintendo.

---

## Inhaltsverzeichnis

1. [Setup & Starten](#setup--starten)
2. [Spielbefehle](#spielbefehle)
3. [Projektstruktur](#projektstruktur)
4. [Daten erweitern](#daten-erweitern)
5. [Architektur-Entscheidungen](#architektur-entscheidungen)
6. [Dialogue-System](#dialogue-system)
7. [Optimierungsmöglichkeiten](#optimierungsmöglichkeiten)
8. [Stretch Goals](#stretch-goals)

---

## Setup & Starten

**Voraussetzungen:**
- Python 3.11 oder höher
- Keine externen Dependencies – alles läuft mit der Python-Standardbibliothek

**Starten:**
```bash
python main.py
```

Das Spiel startet im Terminal mit dem Hauptmenü.
Spielstände werden automatisch im Ordner `saves/` abgelegt.

---

## Spielbefehle

| Befehl             | Alias               | Beschreibung                                      |
|--------------------|---------------------|---------------------------------------------------|
| `look`             | `schau`             | Aktuelle Location anzeigen (Karte + Beschreibung) |
| `go <ziel>`        | `gehe <ziel>`       | Zu einer verbundenen Location navigieren          |
| `talk <npc>`       | `rede <npc>`        | Mit einem NPC sprechen                            |
| `team`             | `team`              | Eigenes Pokémon-Team anzeigen                     |
| `inventory`, `ìnv` | `inventar`, `inv`   | Inventar anzeigen                                 |
| `take`             | `nimm`              | Item aufnehmen                                    |
| `inspect <thing>`  | `untersuche <ding>` | Gegenstand untersuchen                            |
| `walk <zone>`      | `betrete <zone>`    | Zone betreten (z.B. `walk gras`)                  |
| `find`             | -                   | Nach wilden Pokémon suchen (nur in Zone)          |
| `leave`            | `verlasse`          | Zone verlassen                                    |
| `save [name]`      | `speichern`         | Spielstand speichern (Standard: `savegame`)       |
| `load [name]`      | `laden`             | Spielstand laden                                  |
| `menu`             | `hauptmenu`         | Zurück ins Hauptmenü                              |
| `help`, `?`        | `hilfe`, `?`        | Befehlsübersicht anzeigen                         |
| `quit`             | `beenden`           | Spiel beenden                                     |

**Navigation:** Das Ziel bei `go` kann entweder der Connection-Key (`go north`) oder die Location-ID (`go route_01`) sein – beides funktioniert.

---

## Projektstruktur

```
pokemon/
├── main.py                    # Einstiegspunkt
├── data/                      # Statische JSON-Daten (Spielinhalte)
│   ├── pokemons.json          # Pokémon-Datenbank
│   ├── items.json             # Item-Definitionen
│   ├── npcs.json              # NPC-Daten inkl. Dialogue-Trees
│   └── locations.json         # Weltkarte (Locations + Verbindungen)
├── saves/                     # Spielstände (wird automatisch erstellt)
├── models/                    # Datenmodelle (reine Datenstrukturen, keine Logik)
│   ├── characters/
│   │   ├── character.py       # Basis-Klasse für Spieler und NPCs
│   │   ├── player.py          # Spieler (Position, Geld, Team, Inventar)
│   │   └── npc.py             # NPC (Typ, Dialogue-State)
│   ├── pokemon/
│   │   ├── pokemon.py         # Pokémon (Stats, Attacken, Evolution)
│   │   ├── pokemon_type.py    # Enum für Pokémon-Typen
│   │   ├── attack.py          # Attacken + Statuseffekte
│   │   └── stats.py           # Kampfwerte (HP, Attack, Defense, Initiative)
│   ├── world/
│   │   ├── world.py           # Container für alle Locations
│   │   ├── location.py        # Einzelner Ort (Grid, Verbindungen, NPCs, Items)
│   │   └── tile.py            # Einzelnes Feld im Grid (TileType, HabitatType)
│   └── item.py                # Items (Typ, Heilwert, Menge)
├── game/                      # Spiellogik
│   ├── game.py                # Game-Klasse: Hauptmenü + Spielloop
│   ├── context.py             # GameContext: zentraler Spielzustand
│   ├── commands.py            # Befehls-Parsing und -Ausführung
│   ├── dialogue.py            # Dialogue-Engine für NPC-Gespräche
│   ├── encounter.py           # Wilde Pokémon-Begegnungen
│   ├── battle.py              # Kampflogik (Spieler- und Gegnerzug)
│   └── game_result.py         # Enum für Spielloop-Rückgabewerte
├── utils/                     # Hilfsfunktionen
│   ├── data_loader.py         # JSON → Python-Objekte
│   └── save_manager.py        # Spielstände speichern/laden
└── views/                     # Darstellungsschicht (nur Output, keine Logik)
    ├── intro.py               # ASCII-Logo beim Start
    ├── location_view.py       # ASCII-Grid Rendering
    └── styles.py              # ANSI-Formatierung (fett, kursiv, ...)
```

**Schichten-Prinzip:**
- Models kennen keine Views oder Game-Logik.
- Views kennen keine Game-Logik.
- Nur `game/` und `utils/` verbinden alles.

---

## Daten erweitern

Die Spielinhalte sind vollständig in JSON definiert.
Um die Welt zu vergrößern und mehr Lebewesen einzufügen,
müssen ausschließlich die JSONs erweitert werden.

### Pokémon hinzufügen (`data/pokemons.json`)

#### Beispiel: Pikachu
```json
{
  "id": 25,
  "name": "Pikachu",
  "types": ["Elektro"],
  "evolution": {
    "evolves_to": 26,
    "evolution_level": 28
  },
  "stats": {
    "hp": 35,
    "attack": 55,
    "defense": 30,
    "initiative": 90
  },
  "attacks": [
    {
      "name": "Donnerschock",
      "type": "Elektro",
      "power": 40,
      "accuracy": 1.0,
      "required_level": 1,
      "category": "special",
      "status_effect": null
    }
  ],
  "habitat": ["Gras"],
  "catch_rate": 190,
  "spawn_probability": 0.3
}
```

**Wichtig:**
- `types` und `habitat` müssen Werte aus den vorhandenen Enums in `models/pokemon/pokemon_type.py` bzw. `models/world/tile.py` nutzen (z.B. Feuer, Wasser, Pflanze bzw. Gras, Wasser)
- `spawn_probability`: 0.0 = erscheint nie wild, 1.0 = erscheint sehr häufig
- `catch_rate`: 255 = sehr leicht zu fangen, 3 = sehr schwer (wie im Original)
- `category`: `"physical"`, `"special"` oder `"status"`
- Für Infos: https://www.bisafans.de/pokedex/index.php

### Location hinzufügen (`data/locations.json`)

```json
{
  "id": "route_02",
  "name": "Route 2",
  "description": "Ein schmaler Pfad durch dichten Wald.",
  "type": "Route",
  "size": [5, 10],
  "auto_boundary": true,
  "special_tiles": [
    {"x": 1, "y": 3, "type": "Gras"}
  ],
  "connections": {
    "south": "city_vertania",
    "north": "city_marmoria"
  },
  "npcs": [],
  "items": []
}
```

**Wichtig:**
- Location-`type` muss ein Wert aus den vorhandenen Enums in `models/world/location.py` nutzen (z.B. Route, Cave, City).
- `size`: Die Größe beschreibt den **inneren Bereich** der Location.
- `auto_boundary`: Wenn `true`, wird von View automatisch ein Rahmen (Bäume, Zäune, Mauern) um die Location außen herum hinzugefügt.
- Je nach Location-type sind unterschiedliche `DEFAULT_TILES` und `DEFAULT_BOUNDARIES` definiert.
- Koordinaten in `special_tiles` beziehen sich auf den inneren Bereich (0-indexed).

Damit Spieler die neue Location auch erreichen können, muss eine bestehende Location eine Verbindung zur neuen haben:

```json
// In city_vertania connections ergänzen:
"connections": {
  "south": "route_01",
  "north": "route_02"   // ← neu
}
```

### NPC hinzufügen (`data/npcs.json`)

Minimalbeispiel:
```json
{
  "id": "misty",
  "name": "Misty",
  "description": "Eine junge Trainerin mit roten Haaren.",
  "npc_type": "Trainer",
  "dialogue": [
    {
      "id": "start",
      "text": "Hey {player_name}! Willst du kämpfen?",
      "next": "end"
    }
  ],
  "team": [1],
  "inventory": []
}
```

Den NPC dann in der gewünschten Location unter `"npcs"` eintragen:
```json
"npcs": ["misty"]
```

**Aktuell verfügbare NPC-Typen sind in `models/characters/npc.py` als Enums definiert (z.B. Trainer, Questgeber).**

---

## Architektur-Entscheidungen

Hier sind einige implizite Design-Entscheidungen, die nicht sofort offensichtlich sind:

### GameContext

`GameContext` (`game/context.py`) ist der zentrale Spielzustand und wird durch alle Spiellogik-Funktionen gereicht. Er enthält Referenzen auf `player`, `world`, `npcs_db`, `items_db` und `pokemons_db`. Statt viele Parameter zu übergeben, gibt es immer nur `ctx`.

### Pokémon-Datenbank vs. Instanzen

`pokemons_db` in `GameContext` enthält die Pokémon als **Rohdaten** (Python-Dicts direkt aus JSON). Erst wenn ein Pokémon wirklich gebraucht wird (z.B. beim Fangen oder Erhalten vom NPC), wird daraus eine `Pokemon`-Instanz erstellt:

```python
pokemon = DataLoader.create_pokemon_from_data(poke_data, level=5)
```

Das hält den Speicherverbrauch gering und macht es einfach, neue Pokémon zur DB hinzuzufügen.

### Location-Größe und Koordinaten

`size` in einer Location beschreibt immer den **inneren Bereich** ohne Rahmen. Der Rahmen (z.B. Bäume bei Städten, Zäune bei Routen) wird erst im View außen drum gelegt. Das bedeutet:

- Eine Location mit `size: [5, 4]` hat intern 5×4 Felder
- Mit Rahmen wird sie als 7×6 Grid gerendert
- `special_tiles` Koordinaten sind immer auf den inneren Bereich bezogen

### Navigation

`go <ziel>` akzeptiert sowohl den Connection-Key als auch die Ziel-ID:
- `go north` → sucht den Key `"north"` in `connections`
- `go route_01` → sucht den Wert `"route_01"` in `connections`

Beides führt zum gleichen Ergebnis.

### Zonen-System
Spieler haben keine Tile-Position innerhalb einer Location.
Stattdessen können bestimmte Tile-Typen (Gras, Wasser) als Zone betreten werden (`walk gras`). 
Die verfügbaren Zonen einer Location werden automatisch aus den `special_tiles` abgeleitet.
`TILE_TO_HABITAT` in `tile.py` verbindet TileType mit HabitatType und bestimmt welche Tiles betretbar sind.
Wilde Pokémon-Begegnungen werden explizit via `find` getriggert und sind nur innerhalb der Zonen möglich.

### Spielstand speichern

Gespeichert werden:
Spieler-Daten (Position, Geld, Team mit aktuellen HP), Inventar und der World-State (welche Items wurden aufgehoben, NPC-Dialogue-Fortschritte).
Die statischen Daten (Pokémon-DB, Item-Definitionen) werden beim Laden immer neu aus den JSON-Dateien geladen.
Dadurch sind auch später hinzugefügte neue Pokémons oder Items sofort im Spiel verfügbar, ohne alte Spielstände zu invalidieren.

---

## Dialogue-System

NPC-Gespräche sind als **Dialogue-Trees** in `npcs.json` definiert. Jeder NPC hat eine Liste von Knoten (`dialogue`), die durch `next`-Verweise verbunden sind.

### Aufbau eines Knotens

```json
{
  "id": "start",                   // eindeutige ID des Knotens
  "text": "Hallo {player_name}!",  // {player_name} wird automatisch ersetzt
  "next": "ask"                    // nächster Knoten (oder "end" zum Beenden)
}
```

### Auswahlmöglichkeiten (`choices`)

```json
{
  "id": "ask",
  "text": "Willst du ein Pokémon?",
  "choices": [
    { "answer": "ja",   "next": "give_pokemon" },
    { "answer": "nein", "next": "bye" }
  ]
}
```

### Aktionen (`action`)

Ein Knoten kann eine Aktion ausführen, bevor er weitergeht:

```json
{
  "id": "give_pokemon",
  "text": "Hier, nimm dieses Pokémon!",
  "action": { "type": "give_pokemon", "pokemon_id": 1 },
  "next": "end"
}
```

**Aktuell verfügbare Aktionen sind in `_execute_action()` in `game/dialogue.py` definiert (z.B. `give_pokemon`, `give_item`).**

### Automatische Verzweigung (`auto_branch`)

Der NPC prüft selbst eine Bedingung und wählt den nächsten Knoten – ohne Spielereingabe:

```json
{
  "id": "check_pokemons",
  "text": "Hast du schon ein Pokémon?",
  "auto_branch": [
    { "condition": { "type": "has_pokemons" }, "next": "do_something" },
    { "next": "send_away" }
  ]
}
```

Der erste Branch ohne Bedingung ist der Fallback.

**Aktuell verfügbare Bedingungen sind in `_check_condition` in `game/dialogue.py` definiert (z.B. `has_pokemons`, `has_item`).**

### Dialogue-Fortschritt (`next_start`)

Standardmäßig beginnt jedes Gespräch beim Knoten `"start"`.
Mit `next_start` kann gesteuert werden, bei welchem Knoten das **nächste** Gespräch einsteigt:

```json
{
  "id": "give_starter",
  "text": "Hier ist dein erstes Pokémon!",
  "action": { "type": "give_pokemon", "pokemon_id": 1 },
  "next_start": "revisit",   // beim nächsten Gespräch hier einsteigen, um nicht nochmal ein Starter-Pokemon zu übergeben
  "next": "revisit"
}
```

⚠️ **Wichtig:**
Jeder Knoten, der zu `"end"` führt, sollte `next_start` setzen.
Ansonsten bleibt der NPC beim letzten Knoten stecken und das nächste Gespräch schlägt still fehl.

---

## Optimierungsmöglichkeiten

Die Basis-Version bietet einen ersten Einstieg für das Projekt, um nicht alles von Grund auf entwickeln zu müssen.
Häufig sind bereits Vorbereitungen für zukünftige Features enthalten, auch wenn sie aktuell noch nicht genutzt werden.
Dennoch ist diese Version bewusst unvollständig und bietet viele Möglichkeiten zur Erweiterung und Verbesserung.
Folgende Punkte bieten Potenzial für die Sprints:

**Technische Schulden:**
- `special_tiles` sind aktuell untypisierte Dicts mit TileType-abhängigen optionalen Feldern (`door_target`, `items`, `name`, ...). 
- `action["type"]` und `condition["type"]` im Dialogue-System sind plain Strings, nicht typsicher.
- `location.items` ist eine Liste von Dicts (nicht typisiert).
- Zone wird als str gespeichert, könnte auf HabitatType umgestellt werden
- Dialoge haben aktuell keinen Abbruch-Mechanismus, um das laufende Gespräch vorzeitig zu beenden.
- Kampfschaden ignoriert Stats – nur `attack.power` wird genutzt.
- Keine Tests vorhanden – Unit Tests für DataLoader, Dialogue-Engine, Commands wären sinnvoll.

---

## Stretch Goals

Ein paar Ideen zur individuellen Erweiterung für Teams, die ambitioniert sind:
- **Nutzerfreundlichere Eingabe:** Die Commands könnten fehlertoleranter gebaut werden oder ggf. auch natürlich-sprachliche Eingaben zulassen.
- **Tile-basierte Bewegung:** Aktuell wechselt der Spieler zwischen ganzen Locations. Eine mögliche Erweiterung wäre Bewegung Tile für Tile innerhalb einer Location (mit Pfeiltasten oder `n/s/e/w`). Das erfordert einen Umbau der Positions-Logik: der Spieler bräuchte eine `(x, y)`-Koordinate innerhalb der Location, Kollisionserkennung gegen nicht-begehbare Tiles und eine angepasste Darstellung.
- **KI-generierte Dialoge:** NPC-Texte dynamisch per LLM generieren lassen.
- **Erweitertes Quest-System:** Mehrschrittige Quests mit Fortschrittsverfolgung auf Basis des bestehenden Dialogue-Systems
- **Positionsabhängige Events:** Aktuell haben NPCs und Items keine festen Positionen im JSON (zufällige Zuweisung beim Laden). Mit fest Positionen wären auch wandernde NPCs oder positionsabhängige Story-Events (z.B. ein Item erscheint erst, wenn der Spieler einen bestimmten Tile betritt oder ein NPC taucht erst auf, wenn der Spieler eine bestimmte Location besucht hat) möglich.

---

# Viel Erfolg und viel Spaß! 🎮
