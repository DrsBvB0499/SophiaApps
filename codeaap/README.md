# CodeAap — Leer Coderen voor Kinderen

Een lokale desktop applicatie voor kinderen om op een speelse manier te leren coderen.

## Vereisten

- Python 3.11+
- pygame 2.5.2

```bash
pip install -r requirements.txt
```

## Starten

```bash
cd codeaap
python main.py
```

## Optionele fonts

Download en plaats in `assets/fonts/`:
- `FredokaOne-Regular.ttf` — Google Fonts
- `Nunito-Regular.ttf` — Google Fonts

Zonder fonts gebruikt de app automatisch een systeem-fallback (Arial).

## Optionele geluiden

Plaats `.wav`-bestanden in `assets/sounds/`:
- `click.wav`, `correct.wav`, `wrong.wav`, `win.wav`, `badge.wav`

Zonder bestanden genereert de app zelf eenvoudige tonen.

## Levels uitbreiden

Pas `data/levels.json` aan — geen code-wijziging nodig.
Voortgang wordt automatisch opgeslagen in `data/progress.json`.
