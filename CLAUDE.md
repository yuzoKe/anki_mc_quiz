# anki_mc_quiz — Instruções para Claude

## Stack e regras básicas
- Addon para o Anki escrito em Python puro
- Templates de card em HTML/CSS/JS embutidos como strings Python
- Arquivo principal: `anki_mc_quiz/__init__.py`
- Config do addon: `anki_mc_quiz/manifest.json`
- **Não usar pip install** — o Anki tem Python embutido (3.13)
- Avisos do Pylance sobre `aqt`, `aqt.qt`, `aqt.utils` são esperados — ignorar
- **Deploy**: `Copy-Item anki_mc_quiz\__init__.py "$env:APPDATA\Anki2\addons21\anki_mc_quiz\__init__.py" -Force`
  - Copiar também `manifest.json` se alterado
  - Depois reiniciar o Anki
- **Não usar `deploy.bat`** — tem `pause` que bloqueia shells não-interativos

## Anki API — padrões usados no projeto
- `mw.col.decks.all_names()` — lista de nomes de baralhos
- `mw.col.decks.id(name)` — ID do baralho pelo nome
- `mw.col.models.by_name(name)` — modelo de nota pelo nome
- `mw.col.new_note(model)` — cria instância de nota (não salva)
- `mw.col.add_note(note, deck_id)` — salva nota na coleção
- `mw.col.find_notes(query)` — retorna lista de NoteId
- `mw.col.get_note(nid)` — retorna objeto Note pelo ID
- `note["FieldName"]` — acesso a campo (Note NÃO tem `.get()`)
- `note.tags = [...]` — define tags (lista de strings)
- `mw.col.tags.split(text)` — converte string de tags para lista
- `mw.addonManager.getConfig(__name__)` — lê config persistida
- `mw.addonManager.writeConfig(__name__, dict)` — salva config
- `mw.reset()` — atualiza UI do Anki após modificar coleção
- `gui_hooks.main_window_did_init.append(fn)` — hook de startup
- `TagEdit` (de `aqt.tagedit`): widget de input de tags com autocomplete nativo do Anki; instanciar com `TagEdit(parent)` e chamar `.setCol(mw.col)`

## Estrutura do arquivo __init__.py

```
Linhas ~1-20    Imports (Qt, aqt, re)
Linhas ~22-60   Constantes: NOTE_TYPE_NAME, PROMPT_MC, PROMPT_CLOZE, FIELDS
Linhas ~62-410  Templates: FRONT_TEMPLATE, BACK_TEMPLATE, CARD_CSS
Linhas ~412-475 TEMPLATE_VERSION + create_note_type()
Linhas ~477-560 Parsers: parse_questions(), parse_cloze()
Linhas ~562-680 Helpers Obsidian: _anki_tags_to_obsidian(), _format_mc_cards(),
                _format_cloze_cards(), _format_mc_callouts(), _format_cloze_callouts(),
                _render_template(), _build_obsidian_note(extra_vars=None)
Linhas ~680+    ImporterDialog (QDialog) — 2 abas: MC e Cloze
Linhas ~980+    _PROP_TYPES, _OBS_DEFAULT_*, _PropertyRow, ObsidianExporterDialog
Linhas ~1750+   Startup: on_main_window_ready(), _register_menu(),
                _open_importer(), _open_obsidian_exporter()
                hook: gui_hooks.main_window_did_init.append(on_main_window_ready)
```

## Funcionalidades implementadas

### 1. Note type "Multiple Choice Quiz"
- Criado automaticamente no primeiro uso via `create_note_type()`
- Campos: Question, A, B, C, D, E, Answer, Explanation
- `TEMPLATE_VERSION = "1.1.0"` — sync automático ao atualizar o addon

### 2. Templates de card (front/back)
- **Front**: múltipla escolha interativa com Fisher-Yates shuffle, IIFE para isolamento de escopo, visual labels A/B/C/D/E em ordem aleatória
- **Back**: mostra todas as alternativas com a correta destacada + banner verde + explicação opcional
- Dark theme via `CARD_CSS`

### 3. ImporterDialog — Menu Tools > Import from NotebookLM
Janela Qt com layout:
```
[Prompt MC 📋]  [Prompt Cloze 📋]
[Tab: Multiple Choice | Cloze]
  Cada aba: QTextEdit (paste) + QListWidget preview (atualiza via textChanged)
[Destination deck: QComboBox]
[Etiquetas: TagEdit (autocomplete nativo Anki)]
[Cancel]  [Import →]
```

#### parse_questions(text) → list[dict]
- Remove preamble antes do primeiro `1.` (título do relatório NotebookLM)
- Fallback: remove linhas ALL CAPS iniciais (formato sem numeração)
- Regex de "cauda": `Resposta: [A-E] Explicação: frase.` como unidade atômica
- Suporta formato numerado (`1. Enunciado`) e sem numeração
- Retorna lista de dicts com chaves: `question, A, B, C, D, E, answer, explanation`

#### parse_cloze(text) → list[str]
- Filtra linhas não-vazias que contêm `{{c` (marcador Cloze)

#### Duplicate detection
- `_is_duplicate_mc(question)`: query `"note:{NOTE_TYPE_NAME}" "Question:{question}"`
- `_is_duplicate_cloze(card_text)`: query `"note:Cloze" "Text:{card_text}"`
- Duplicatas puladas; contagem exibida no relatório final

#### Tags
- `_get_tags()`: `mw.col.tags.split(self.tags_input.text())`
- Aplicadas a todas as notas da sessão

### 4. ObsidianExporterDialog — Menu Tools > Export to Obsidian
Janela Qt com 2 abas:

**Aba "Exportar":**
```
[Template: QComboBox]  ← espelha o combo do Modelo; troca atualiza quick fields
[Source deck: QComboBox]  ← seleciona baralho existente no Anki
[Cards: N total (X MC, Y Cloze)  QListWidget h=120]
─ ⚡ Campos rápidos (só aparece se template tem propriedades marcadas com ⚡) ─
  [label: QLineEdit]  [+1 se campo for numérico]
  ...
─────────────────────────────────────────────────────────────────────────────
[Vault: QLineEdit (read-only) + Browse...]
[Output folder: QLineEdit + Browse...]
[Note title: QLineEdit]
[Cancelar]  [Export →]
```

**Aba "Modelo":**
```
[Template: QComboBox] [Novo] [Duplicar] [Excluir] [Salvar]
[Nome do ficheiro: QLineEdit]  ex: {{title}}.md
[Variáveis disponíveis: hint label]
[Propriedades: QScrollArea com _PropertyRow widgets]
  cada row: [tipo ▼] [chave] [valor/{{var}}] [⚡] [×]
  ⚡ = campo rápido — aparece na aba Exportar
[+ Adicionar propriedade]
[Conteúdo da nota: QTextEdit]
[Repor padrões]
```

#### _PropertyRow
- `type_combo` (QComboBox, 110px): Ab Text / ≡ List / # Number / ☑ Checkbox / 📅 Date / ⏰ Datetime
- `key_edit` (QLineEdit, 120px): nome da propriedade
- `val_edit` (QLineEdit, stretch): valor ou `{{variável}}`
- `quick_btn` (QPushButton ⚡, checkable): marca como campo rápido
- `del_btn` (QPushButton ×, 26px): remove a row
- `ptype()` → str com key interno do tipo
- `is_quick()` → bool
- Serialização: `[key, val, ptype, is_quick]` — backward compat: old `[key, val, ptype]` migra com `is_quick=False`

#### Template variables
| Variável       | Valor                                                    |
|---------------|----------------------------------------------------------|
| `{{title}}`   | campo "Note title" (user-typed)                          |
| `{{date}}`    | data de hoje ISO (2026-06-04)                            |
| `{{deck}}`    | nome do baralho selecionado                              |
| `{{tags}}`    | tags em YAML (`  - tag` por linha)                       |
| `{{cards}}`   | corpo completo (MC + Cloze em markdown)                  |
| `{{mc_cards}}`| só questões MC                                           |
| `{{cloze_cards}}`| só cards Cloze                                        |
| `{{cards_callouts}}`| MC + Cloze formatados como callouts Obsidian      |
| `{{mc_cards_callouts}}`| só MC como callouts `> [!question]`            |
| `{{cloze_cards_callouts}}`| só Cloze como callouts `> [!info]`          |
| `{{chave}}`   | qualquer propriedade marcada como ⚡ (quick field)        |

#### Conversão de tags Anki → Obsidian
`UNIVESP::COM130` → `UNIVESP/COM130` (substitui `::` por `/`, preserva hierarquia nativa do Obsidian)

#### Quick fields
- Propriedades com `is_quick=True` aparecem como inputs na aba Exportar
- Campos numéricos ganham botão `+1`
- Valores salvos em `obs_quick_values[template_name]` e restaurados na próxima abertura
- Valores injetados em `all_vars` durante o export (sobrescrevem built-ins com mesmo nome)
- `_build_obsidian_note(..., extra_vars=quick_vals)` — parâmetro opcional

#### Template ↔ Deck auto-link
- Ao trocar deck, salva `obs_tmpl_deck_link[template_name] = deck_name`
- Ao trocar template (no combo do Exportar), restaura o deck salvo para aquele template

#### Config persistida (manifest.json / mw.addonManager)
```json
{
  "obsidian_vault_path": "",
  "obsidian_last_folder": "",
  "obs_active_template": "Default",
  "obs_templates": [
    {
      "name": "Default",
      "filename": "{{title}}.md",
      "prop_rows": [["tags","{{tags}}","list",false], ["created","{{date}}","date",false], ["anki-deck","{{deck}}","text",false]],
      "content": "{{cards}}"
    }
  ],
  "obs_quick_values": {"Default": {}},
  "obs_tmpl_deck_link": {"Default": "deck name"}
}
```
- `_load_config` migra automaticamente formato antigo (`obs_prop_rows` flat) para `obs_templates`

### 5. Botões de prompt (clipboard)
- "Prompt Múltipla Escolha 📋" e "Prompt Cloze 📋" no topo do ImporterDialog
- Copia `PROMPT_MC` / `PROMPT_CLOZE` para o clipboard
- Feedback visual: texto muda para "Copiado! ✓" por 1.5s via QTimer

## Contexto do projeto
- Desenvolvido durante o Clube da Programação da Laura Dubugras (4 semanas)
- Objetivo: automatizar o fluxo de estudo da faculdade (UNIVESP — Engenharia de Computação)
- Publicado publicamente: https://github.com/yuzoKe/anki_mc_quiz

## Fluxo de estudo do autor
- Semanas 1-7 (aprender): Material da aula → NotebookLM (prompt Cloze) → Import from NotebookLM → revisar com Cloze no Anki
- Semana 8/9 (testar): Material acumulado → NotebookLM (prompt MC) → Import from NotebookLM → revisar com múltipla escolha no Anki
- Após revisão: Export to Obsidian → nota .md linkada às anotações do vault

## Prompts do NotebookLM

**PROMPT MÚLTIPLA ESCOLHA:**
```
Crie um Relatório Personalizado transformando todas as atividades avaliativas das fontes em questões de múltipla escolha. Siga exatamente este formato para cada questão:
1. [Enunciado]
A) [Alternativa A]
...
Resposta: A
Explicação: [Uma frase]
Regras: numeração sequencial, letras maiúsculas, uma linha em branco entre questões, sem títulos ou gabarito separado.
```

**PROMPT CLOZE:**
```
Crie um Relatório Personalizado transformando todos os conceitos das fontes em flashcards no formato Cloze.

Formato obrigatório — cada card deve ocupar exatamente UMA linha isolada:
{{c1::termo ou conceito}} é/são [definição ou contexto em uma frase].

Regras:
- Uma linha por card, seguida de uma linha em branco
- Nunca agrupe vários cards no mesmo parágrafo
- Use apenas {{c1::}}, sem {{c2::}} ou outras numerações
- Sem numeração, títulos, subtítulos ou texto introdutório
- Sem duplicatas

Exemplo correto:
{{c1::TCP/IP}} é o conjunto de protocolos que governa a transmissão de dados na internet.

{{c1::DNS}} é o sistema responsável por traduzir nomes de domínio em endereços IP.
```
