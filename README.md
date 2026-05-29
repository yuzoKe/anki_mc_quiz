# Anki MC Quiz

**PT** · [EN below](#english)

Plugin para o Anki que adiciona um tipo de nota de múltipla escolha interativo. As alternativas aparecem como botões clicáveis durante a revisão — com feedback visual imediato de certo ou errado — sem depender de internet ou API externa.

## Funcionalidades

- Até 5 alternativas (A–E) por questão
- Alternativas em branco são ocultadas automaticamente
- Ordem das alternativas embaralhada a cada revisão
- Feedback visual ao clicar: verde para certo, vermelho para errado
- Campo de explicação opcional (exibido no verso do card)
- Funciona 100% offline

## Instalação

### Via AnkiWeb *(em breve)*
Pesquise por **"MC Quiz"** na loja de addons do Anki.

### Manual (desenvolvimento)
1. Clone este repositório
2. Copie a pasta `anki_mc_quiz/` para o diretório de addons do Anki:
   - **Windows:** `%APPDATA%\Anki2\addons21\`
   - **macOS:** `~/Library/Application Support/Anki2/addons21/`
   - **Linux:** `~/.local/share/Anki2/addons21/`
3. Reinicie o Anki

O note type **"Multiple Choice Quiz"** será criado automaticamente na primeira inicialização.

## Como usar

1. Crie um novo card e selecione o tipo **Multiple Choice Quiz**
2. Preencha os campos:
   - `Question` — o enunciado da questão
   - `A`, `B`, `C`, `D`, `E` — as alternativas (deixe em branco para ocultar)
   - `Answer` — a letra correta (`A`, `B`, `C`, `D` ou `E`)
   - `Explanation` — explicação opcional exibida no verso
3. Durante a revisão, clique na alternativa que achar correta

## Estrutura do projeto

```
anki_mc_quiz/
├── anki_mc_quiz/
│   ├── __init__.py      # Entry point — cria o note type e registra o addon
│   └── manifest.json    # Metadados do addon para o AnkiWeb
├── .gitignore
├── LICENSE
└── README.md
```

---

<a name="english"></a>

## English

An Anki addon that adds an interactive multiple choice note type. Choices appear as clickable buttons during review — with immediate visual feedback — no internet or external API required.

## Features

- Up to 5 choices (A–E) per card
- Blank choices are hidden automatically
- Answer order shuffled on every review
- Visual feedback on click: green for correct, red for wrong
- Optional explanation field (shown on the card back)
- Works 100% offline

## Installation

### Via AnkiWeb *(coming soon)*
Search for **"MC Quiz"** in the Anki addon store.

### Manual (development)
1. Clone this repository
2. Copy the `anki_mc_quiz/` folder to your Anki addons directory:
   - **Windows:** `%APPDATA%\Anki2\addons21\`
   - **macOS:** `~/Library/Application Support/Anki2/addons21/`
   - **Linux:** `~/.local/share/Anki2/addons21/`
3. Restart Anki

The **"Multiple Choice Quiz"** note type will be created automatically on first launch.

## How to use

1. Create a new card and select the **Multiple Choice Quiz** type
2. Fill in the fields:
   - `Question` — the question text
   - `A`, `B`, `C`, `D`, `E` — the choices (leave blank to hide)
   - `Answer` — the correct letter (`A`, `B`, `C`, `D`, or `E`)
   - `Explanation` — optional explanation shown on the back
3. During review, click the choice you think is correct

## Project structure

```
anki_mc_quiz/
├── anki_mc_quiz/
│   ├── __init__.py      # Entry point — creates the note type and registers the addon
│   └── manifest.json    # Addon metadata for AnkiWeb
├── .gitignore
├── LICENSE
└── README.md
```

## License

MIT © Eduardo Yuzo Kubota