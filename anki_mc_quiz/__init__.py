# anki_mc_quiz/__init__.py
#
# Entry point for the Anki Multiple Choice Quiz addon.
# Anki loads this file automatically when the addon is installed.
#
# What happens here:
#   1. We hook into Anki's startup sequence
#   2. Once the main window is ready, we check if our note type exists
#   3. If it doesn't exist yet, we create it (first-time install)

from aqt.qt import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QTextEdit, QComboBox, QPushButton, QTabWidget, QWidget,
    QListWidget, QAbstractItemView, QListWidgetItem,
    QLineEdit, QFileDialog, QMessageBox,
    QScrollArea, QFrame, QApplication, QStyle, Qt, QEvent
)
import re
from aqt import mw, gui_hooks
from aqt.tagedit import TagEdit


# ---------------------------------------------------------------------------
# i18n — language strings and helpers
# ---------------------------------------------------------------------------

_STRINGS: dict = {
    "pt": {
        "tag_placeholder": "adicionar etiqueta…",
        # ImporterDialog
        "importer_title": "Import from NotebookLM",
        "btn_prompt_mc": "Prompt Múltipla Escolha  📋",
        "btn_prompt_mc_copied": "Copiado! ✓",
        "btn_prompt_cloze": "Prompt Cloze  📋",
        "btn_prompt_cloze_copied": "Copiado! ✓",
        "tooltip_prompt_mc": "Copia o prompt de múltipla escolha para o clipboard",
        "tooltip_prompt_cloze": "Copia o prompt Cloze para o clipboard",
        "tab_mc": "Múltipla Escolha",
        "tab_cloze": "Cloze",
        "lbl_deck": "Baralho de destino:",
        "lbl_tags": "Etiquetas:",
        "btn_cancel": "Cancelar",
        "btn_import": "Importar →",
        "mc_instructions": (
            "Cole o texto do quiz gerado pelo NotebookLM abaixo.\n"
            "Cada questão deve seguir o formato:\n"
            "  1. Enunciado\n"
            "  A) Alternativa A   B) Alternativa B\n"
            "  Resposta: A\n"
            "  Explicação: Texto"
        ),
        "mc_placeholder": "Cole o texto do NotebookLM aqui...",
        "cloze_instructions": (
            "Cole o texto Cloze gerado pelo NotebookLM abaixo.\n"
            "Um card por linha. Formato:\n"
            "  {{c1::termo}} é/são [contexto]."
        ),
        "cloze_placeholder": "Cole o texto Cloze do NotebookLM aqui...",
        "lbl_preview": "Preview:",
        "preview_bad_format": "Formato não reconhecido — use o Prompt Múltipla Escolha 📋 no NotebookLM",
        "preview_no_questions": "Nenhuma questão detectada — verifique o formato",
        "preview_no_cloze": "Nenhum card Cloze detectado — verifique o formato",
        "warn_no_text": "Cole algum texto antes de importar.",
        "warn_no_questions": (
            "Nenhuma questão encontrada.\n\n"
            "Verifique se o texto segue o formato esperado:\n"
            "1. Enunciado\n"
            "A) Alternativa A\n"
            "Resposta: A\n"
            "Explicação: Texto"
        ),
        "warn_no_cloze": "Nenhum card Cloze encontrado.\n\nCada linha deve conter {{c1::termo}}.",
        "warn_no_note_type": "Tipo de nota não encontrado. Reinicie o Anki.",
        "warn_no_cloze_type": "Tipo Cloze nativo não encontrado na coleção.",
        "confirm_import_title": "Confirmar importação",
        "confirm_mc_body": "<b>{n}</b> card(s) serão adicionado(s)",
        "confirm_cloze_body": "<b>{n}</b> card(s) Cloze encontrado(s)",
        "confirm_deck_lbl": "Baralho:",
        "confirm_tags_lbl": "Etiquetas:",
        "confirm_none": "(nenhuma)",
        "confirm_proceed": "Deseja importar?",
        "success_mc": "{created} card(s) adicionado(s) a '{deck}'.",
        "success_skipped": " {skipped} duplicata(s) ignorada(s).",
        "success_cloze": "{created} card(s) Cloze adicionado(s) a '{deck}'.",
        # ObsidianExporterDialog
        "exporter_title": "Export to Obsidian",
        "tab_export": "Exportar",
        "tab_model": "Modelo",
        "lbl_template": "Template:",
        "lbl_source_deck": "Source deck:",
        "lbl_cards": "Cards:",
        "lbl_vault": "Vault:",
        "vault_hint": "Clique em Browse para selecionar o vault",
        "btn_browse": "Browse...",
        "lbl_output": "Output folder:",
        "output_hint": "Pasta relativa dentro do vault (opcional)",
        "lbl_note_title": "Note title:",
        "title_hint": "ex: COM130 Semana 3 — Revisão Anki",
        "btn_cancel_exp": "Cancelar",
        "btn_export": "Export →",
        "cards_summary": "{total} total ({mc} MC, {cloze} Cloze)",
        "no_cards": "Nenhum card encontrado",
        "btn_new": "Novo",
        "btn_duplicate": "Duplicar",
        "btn_delete": "Excluir",
        "btn_save": "Salvar",
        "lbl_filename": "Nome do ficheiro:",
        "lbl_vars": (
            "Variáveis: {{title}}  {{date}}  {{deck}}  {{tags}}\n"
            "{{cards}}  {{mc_cards}}  {{cloze_cards}}\n"
            "{{cards_callouts}}  {{mc_cards_callouts}}  {{cloze_cards_callouts}}"
        ),
        "col_type": "Tipo",
        "col_property": "Propriedade",
        "col_value": "Valor",
        "btn_add_prop": "+ Adicionar propriedade",
        "btn_import_obs": "Importar do Obsidian",
        "lbl_content": "Conteúdo da nota:",
        "btn_reset": "Repor padrões",
        "prop_key_hint": "Propriedade",
        "prop_val_hint": "Valor ou {{variável}}",
        "dlg_vault_title": "Selecionar Vault do Obsidian",
        "dlg_folder_title": "Selecionar pasta de saída",
        "obs_props_imported": "{n} propriedade(s) disponíveis.\nClica em '+ Adicionar propriedade' e escolhe da lista.",
        "template_saved": "Template '{name}' guardado.",
        "dlg_new_tmpl_title": "Novo template",
        "dlg_new_tmpl_label": "Nome do novo template:",
        "warn_tmpl_exists": "Já existe um template com o nome '{name}'.",
        "dlg_dup_tmpl_title": "Duplicar template",
        "dlg_dup_tmpl_label": "Nome do template duplicado:",
        "dlg_del_tmpl_title": "Excluir template",
        "dlg_del_tmpl_body": "Excluir o template '{name}'?",
        "warn_last_tmpl": "Não é possível excluir o único template.",
        "warn_config_save": "Erro ao guardar configuração:\n{e}",
        "warn_no_vault_props": "Vault não configurado.\nConfigure o vault na aba Exportar antes de importar propriedades.",
        "warn_types_not_found": "Ficheiro não encontrado:\n{path}\n\nCertifica-te de que o vault está correto e tem propriedades definidas.",
        "warn_types_error": "Erro ao ler types.json:\n{e}",
        "warn_no_properties": "Nenhuma propriedade encontrada em types.json.",
        "warn_vault_missing": "Vault não configurado ou não encontrado.\nClique em Browse para selecionar o vault.",
        "warn_mkdir_failed": "Não foi possível criar a pasta:\n{path}\n\n{e}",
        "confirm_overwrite_title": "Ficheiro já existe",
        "confirm_overwrite_body": "'{filename}' já existe na pasta de destino.\nSobrescrever?",
        "warn_write_failed": "Não foi possível escrever o ficheiro:\n{path}\n\n{e}",
        "success_export": "Exportado para Obsidian:\n{path}",
    },
    "en": {
        "tag_placeholder": "add tag…",
        # ImporterDialog
        "importer_title": "Import from NotebookLM",
        "btn_prompt_mc": "MC Prompt  📋",
        "btn_prompt_mc_copied": "Copied! ✓",
        "btn_prompt_cloze": "Cloze Prompt  📋",
        "btn_prompt_cloze_copied": "Copied! ✓",
        "tooltip_prompt_mc": "Copy the multiple choice prompt to clipboard",
        "tooltip_prompt_cloze": "Copy the Cloze prompt to clipboard",
        "tab_mc": "Multiple Choice",
        "tab_cloze": "Cloze",
        "lbl_deck": "Destination deck:",
        "lbl_tags": "Tags:",
        "btn_cancel": "Cancel",
        "btn_import": "Import →",
        "mc_instructions": (
            "Paste the quiz text generated by NotebookLM below.\n"
            "Each question must follow the format:\n"
            "  1. Question text\n"
            "  A) Choice A   B) Choice B\n"
            "  Resposta: A\n"
            "  Explicação: Explanation text"
        ),
        "mc_placeholder": "Paste your NotebookLM quiz text here...",
        "cloze_instructions": (
            "Paste the Cloze text generated by NotebookLM below.\n"
            "One card per line. Format:\n"
            "  {{c1::term}} is/are [context]."
        ),
        "cloze_placeholder": "Paste your NotebookLM Cloze text here...",
        "lbl_preview": "Preview:",
        "preview_bad_format": "Unrecognized format — use the MC Prompt 📋 in NotebookLM",
        "preview_no_questions": "No questions detected — check the format",
        "preview_no_cloze": "No Cloze cards detected — check the format",
        "warn_no_text": "Please paste some text before importing.",
        "warn_no_questions": (
            "No questions found.\n\n"
            "Make sure the text follows the expected format:\n"
            "1. Question text\n"
            "A) Choice A\n"
            "Resposta: A\n"
            "Explicação: Explanation"
        ),
        "warn_no_cloze": "No Cloze cards found.\n\nEach line must contain {{c1::term}}.",
        "warn_no_note_type": "Multiple Choice Quiz note type not found. Please restart Anki.",
        "warn_no_cloze_type": "Native Cloze note type not found in your collection.",
        "confirm_import_title": "Confirm import",
        "confirm_mc_body": "<b>{n}</b> card(s) will be added",
        "confirm_cloze_body": "<b>{n}</b> Cloze card(s) found",
        "confirm_deck_lbl": "Deck:",
        "confirm_tags_lbl": "Tags:",
        "confirm_none": "(none)",
        "confirm_proceed": "Proceed with import?",
        "success_mc": "{created} card(s) added to '{deck}'.",
        "success_skipped": " {skipped} duplicate(s) skipped.",
        "success_cloze": "{created} Cloze card(s) added to '{deck}'.",
        # ObsidianExporterDialog
        "exporter_title": "Export to Obsidian",
        "tab_export": "Export",
        "tab_model": "Template",
        "lbl_template": "Template:",
        "lbl_source_deck": "Source deck:",
        "lbl_cards": "Cards:",
        "lbl_vault": "Vault:",
        "vault_hint": "Click Browse to select the vault",
        "btn_browse": "Browse...",
        "lbl_output": "Output folder:",
        "output_hint": "Relative folder inside the vault (optional)",
        "lbl_note_title": "Note title:",
        "title_hint": "e.g.: COM130 Week 3 — Anki Review",
        "btn_cancel_exp": "Cancel",
        "btn_export": "Export →",
        "cards_summary": "{total} total ({mc} MC, {cloze} Cloze)",
        "no_cards": "No cards found",
        "btn_new": "New",
        "btn_duplicate": "Duplicate",
        "btn_delete": "Delete",
        "btn_save": "Save",
        "lbl_filename": "File name:",
        "lbl_vars": (
            "Variables: {{title}}  {{date}}  {{deck}}  {{tags}}\n"
            "{{cards}}  {{mc_cards}}  {{cloze_cards}}\n"
            "{{cards_callouts}}  {{mc_cards_callouts}}  {{cloze_cards_callouts}}"
        ),
        "col_type": "Type",
        "col_property": "Property",
        "col_value": "Value",
        "btn_add_prop": "+ Add property",
        "btn_import_obs": "Import from Obsidian",
        "lbl_content": "Note content:",
        "btn_reset": "Reset defaults",
        "prop_key_hint": "Property",
        "prop_val_hint": "Value or {{variable}}",
        "dlg_vault_title": "Select Obsidian Vault",
        "dlg_folder_title": "Select output folder",
        "obs_props_imported": "{n} property(ies) available.\nClick '+ Add property' and choose from the list.",
        "template_saved": "Template '{name}' saved.",
        "dlg_new_tmpl_title": "New template",
        "dlg_new_tmpl_label": "New template name:",
        "warn_tmpl_exists": "A template named '{name}' already exists.",
        "dlg_dup_tmpl_title": "Duplicate template",
        "dlg_dup_tmpl_label": "Duplicated template name:",
        "dlg_del_tmpl_title": "Delete template",
        "dlg_del_tmpl_body": "Delete template '{name}'?",
        "warn_last_tmpl": "Cannot delete the only template.",
        "warn_config_save": "Error saving configuration:\n{e}",
        "warn_no_vault_props": "Vault not configured.\nSet the vault in the Export tab before importing properties.",
        "warn_types_not_found": "File not found:\n{path}\n\nMake sure the vault is correct and has properties defined.",
        "warn_types_error": "Error reading types.json:\n{e}",
        "warn_no_properties": "No properties found in types.json.",
        "warn_vault_missing": "Vault not configured or not found.\nClick Browse to select the vault.",
        "warn_mkdir_failed": "Could not create folder:\n{path}\n\n{e}",
        "confirm_overwrite_title": "File already exists",
        "confirm_overwrite_body": "'{filename}' already exists in the destination folder.\nOverwrite?",
        "warn_write_failed": "Could not write file:\n{path}\n\n{e}",
        "success_export": "Exported to Obsidian:\n{path}",
    },
}


def _get_lang() -> str:
    import json, os
    meta = os.path.join(os.path.dirname(os.path.abspath(__file__)), "meta.json")
    if os.path.isfile(meta):
        try:
            return json.loads(open(meta, encoding="utf-8-sig").read()).get(
                "config", {}).get("language", "pt")
        except Exception:
            pass
    return "pt"


_lang: str = _get_lang()


def _t(key: str, **kw) -> str:
    s = _STRINGS.get(_lang, _STRINGS["pt"]).get(key, _STRINGS["pt"].get(key, key))
    return s.format(**kw) if kw else s


def _set_lang(lang: str) -> None:
    global _lang
    import json, os
    _lang = lang
    meta = os.path.join(os.path.dirname(os.path.abspath(__file__)), "meta.json")
    try:
        data: dict = {}
        if os.path.isfile(meta):
            data = json.loads(open(meta, encoding="utf-8").read())
        data.setdefault("config", {})["language"] = lang
        with open(meta, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
    except Exception:
        pass


# ---------------------------------------------------------------------------
# Note type definition
# ---------------------------------------------------------------------------

# This is the name that will appear in Anki's note type list.
NOTE_TYPE_NAME = "Multiple Choice Quiz"

PROMPT_MC = (
    "Crie um Relatório Personalizado transformando todas as atividades avaliativas "
    "das fontes em questões de múltipla escolha. Siga exatamente este formato para cada questão:\n"
    "1. [Enunciado]\n"
    "A) [Alternativa A]\n"
    "B) [Alternativa B]\n"
    "C) [Alternativa C]\n"
    "D) [Alternativa D]\n"
    "E) [Alternativa E]\n"
    "Resposta: A\n"
    "Explicação: [Uma frase]\n"
    "Regras: numeração sequencial, letras maiúsculas, uma linha em branco entre questões, "
    "sem títulos ou gabarito separado."
)

PROMPT_CLOZE = (
    "Crie um Relatório Personalizado transformando todos os conceitos das fontes "
    "em flashcards no formato Cloze.\n\n"
    "Formato obrigatório — cada card deve ocupar exatamente UMA linha isolada:\n"
    "{{c1::termo ou conceito}} é/são [definição ou contexto em uma frase].\n\n"
    "Regras:\n"
    "- Uma linha por card, seguida de uma linha em branco\n"
    "- Nunca agrupe vários cards no mesmo parágrafo\n"
    "- Use apenas {{c1::}}, sem {{c2::}} ou outras numerações\n"
    "- Sem numeração, títulos, subtítulos ou texto introdutório\n"
    "- Sem duplicatas\n\n"
    "Exemplo correto:\n"
    "{{c1::TCP/IP}} é o conjunto de protocolos que governa a transmissão de dados na internet.\n\n"
    "{{c1::DNS}} é o sistema responsável por traduzir nomes de domínio em endereços IP."
)

# These are the fields the user will fill in when creating a card.
# "Explanation" is optional — the card will work without it.
FIELDS = [
    "Question",   # The question text
    "A",          # Choice A
    "B",          # Choice B
    "C",          # Choice C (optional — leave blank to hide)
    "D",          # Choice D (optional — leave blank to hide)
    "E",          # Choice E (optional — leave blank to hide)
    "Answer",     # The correct letter: A, B, C, D, or E
    "Explanation"  # Optional explanation shown after answering
]

# Front template: what the user sees BEFORE answering.
# Uses HTML + CSS + JavaScript.
# Anki replaces {{FieldName}} with the actual field content at display time.
#
# HOW SHUFFLING WORKS:
#   1. Anki renders all filled choices as hidden <span> tags with their data
#   2. JavaScript reads those spans, builds an array of {letter, text} objects
#   3. Fisher-Yates shuffle randomizes the array order
#   4. JS dynamically creates the visible buttons in the new shuffled order
#   5. Each button keeps data-letter pointing to the ORIGINAL letter (A, B, etc.)
#      so the Answer field comparison always works correctly
FRONT_TEMPLATE = """
<div class="quiz-card">

  <!-- Question -->
  <div class="question">{{Question}}</div>

  <!-- Hidden data sources — Anki fills these in, JS reads them.
       The {{#X}}...{{/X}} syntax means: only render if field X is not empty. -->
  <div id="raw-choices" style="display:none">
    {{#A}}<span data-letter="A">{{A}}</span>{{/A}}
    {{#B}}<span data-letter="B">{{B}}</span>{{/B}}
    {{#C}}<span data-letter="C">{{C}}</span>{{/C}}
    {{#D}}<span data-letter="D">{{D}}</span>{{/D}}
    {{#E}}<span data-letter="E">{{E}}</span>{{/E}}
  </div>

  <!-- Buttons will be injected here by JavaScript after shuffling -->
  <div class="choices" id="choices"></div>

  <!-- Feedback message shown after the user picks an answer -->
  <div class="feedback" id="feedback"></div>

</div>

<script>
  // IIFE — Immediately Invoked Function Expression.
  // Wrapping everything in (() => { ... })() creates a brand new isolated scope
  // every time the card loads. Without this, Anki reuses the same JS context
  // across cards, causing variable conflicts (answered, correctAnswer, etc.)
  // that break the second card onward.
  (() => {

    const correctAnswer = "{{Answer}}".trim().toUpperCase();

    // Tracks whether the user has already answered (prevents double-clicking).
    let answered = false;

    // ── Step 1: Collect choices from the hidden spans ────────────────────
    // querySelectorAll returns all <span> elements inside #raw-choices.
    const rawSpans = document.querySelectorAll("#raw-choices span");

    // Convert the NodeList into a plain JS array of objects: { letter, text }
    const choices = Array.from(rawSpans).map(span => ({
      letter: span.dataset.letter,        // "A", "B", "C", etc.
      text:   span.innerHTML.trim()       // The actual choice text (may contain HTML)
    }));

    // ── Step 2: Shuffle using Fisher-Yates algorithm ─────────────────────
    // Standard unbiased shuffle — every permutation is equally likely.
    // Iterates backwards, swapping each element with a random earlier one.
    for (let i = choices.length - 1; i > 0; i--) {
      const j = Math.floor(Math.random() * (i + 1));
      [choices[i], choices[j]] = [choices[j], choices[i]];
    }

    // ── Step 3: Render shuffled buttons into the DOM ─────────────────────
    // Visual labels are always shown as A, B, C, D in order.
    // The original letter (data-letter) is kept hidden for answer checking.
    const visualLabels = ["A", "B", "C", "D", "E"];
    const container = document.getElementById("choices");

    choices.forEach((choice, index) => {
      const btn = document.createElement("button");
      btn.className = "choice";
      btn.dataset.letter = choice.letter;          // original letter — used to check Answer
      btn.dataset.visual  = visualLabels[index];   // visual label — always A, B, C, D in order
      btn.onclick = () => selectChoice(btn);

      btn.innerHTML =
        '<span class="letter">' + visualLabels[index] + '</span>' +
        '<span class="text">'   + choice.text         + '</span>';

      container.appendChild(btn);
    });

    // ── Step 4: Handle user click ─────────────────────────────────────────
    function selectChoice(button) {
      if (answered) return;
      answered = true;

      // Compare the ORIGINAL letter against the Answer field
      const chosen = button.dataset.letter.toUpperCase();
      const allButtons = document.querySelectorAll(".choice");
      allButtons.forEach(btn => btn.disabled = true);

      const feedback = document.getElementById("feedback");

      if (chosen === correctAnswer) {
        button.classList.add("correct");
        feedback.textContent = "✓ Correct!";
        feedback.className = "feedback correct-msg";
      } else {
        button.classList.add("wrong");
        // Show the visual label (A/B/C/D) of the correct answer in the feedback
        let correctVisual = "";
        allButtons.forEach(btn => {
          if (btn.dataset.letter.toUpperCase() === correctAnswer) {
            btn.classList.add("correct");
            correctVisual = btn.dataset.visual;
          }
        });
        feedback.textContent = "✗ Wrong. The correct answer is " + correctVisual + ".";
        feedback.className = "feedback wrong-msg";
      }
    }

  })(); // End of IIFE — executes immediately, scope is discarded after
</script>
"""

# Back template: what the user sees AFTER flipping the card.
# The front already showed the interactive quiz — the back confirms the answer
# and shows the explanation. Choices are rendered in original order (A, B, C, D)
# with the correct one highlighted in green.
BACK_TEMPLATE = """
<div class="quiz-card">

  <!-- Question repeated for context -->
  <div class="question">{{Question}}</div>

  <!-- Hidden data — JS reads these to render the choices -->
  <div id="raw-choices-back" style="display:none">
    {{#A}}<span data-letter="A">{{A}}</span>{{/A}}
    {{#B}}<span data-letter="B">{{B}}</span>{{/B}}
    {{#C}}<span data-letter="C">{{C}}</span>{{/C}}
    {{#D}}<span data-letter="D">{{D}}</span>{{/D}}
    {{#E}}<span data-letter="E">{{E}}</span>{{/E}}
  </div>

  <!-- Choices rendered by JS -->
  <div class="choices" id="choices-back"></div>

  <!-- Correct answer banner -->
  <div class="correct-banner" id="correct-banner"></div>

  <!-- Optional explanation — only shown if the field is filled -->
  {{#Explanation}}
  <div class="explanation">
    <span class="explanation-label">Explanation</span>
    {{Explanation}}
  </div>
  {{/Explanation}}

</div>

<script>
  (() => {
    const correctAnswer = "{{Answer}}".trim().toUpperCase();
    const visualLabels  = ["A", "B", "C", "D", "E"];

    // Collect choices in original order (no shuffle on the back)
    const rawSpans = document.querySelectorAll("#raw-choices-back span");
    const choices  = Array.from(rawSpans).map(span => ({
      letter: span.dataset.letter,
      text:   span.innerHTML.trim()
    }));

    // Render choices as non-interactive divs, highlighting the correct one
    const container = document.getElementById("choices-back");

    choices.forEach((choice, index) => {
      const div = document.createElement("div");
      div.className = "choice";
      div.dataset.letter = choice.letter;

      // Highlight the correct answer in green
      if (choice.letter === correctAnswer) {
        div.classList.add("correct");
      }

      div.innerHTML =
        '<span class="letter">' + visualLabels[index] + '</span>' +
        '<span class="text">'   + choice.text         + '</span>';

      container.appendChild(div);
    });

    // Show a banner with the correct answer label
    const correctIndex = choices.findIndex(c => c.letter === correctAnswer);
    const correctVisual = correctIndex >= 0 ? visualLabels[correctIndex] : correctAnswer;
    const banner = document.getElementById("correct-banner");
    banner.textContent = "✓ Correct answer: " + correctVisual;
  })();
</script>
"""

# CSS styles shared between front and back templates.
# Anki applies this to both sides of the card automatically.
CARD_CSS = """
/* ── Base card layout ─────────────────────────────────────── */
.card {
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
  font-size: 16px;
  line-height: 1.6;
  background-color: #1a1a2e;
  color: #e0e0e0;
  margin: 0;
  padding: 0;
}

.quiz-card {
  max-width: 680px;
  margin: 0 auto;
  padding: 24px 20px;
}

/* ── Question ─────────────────────────────────────────────── */
.question {
  font-size: 17px;
  font-weight: 500;
  color: #ffffff;
  margin-bottom: 20px;
  line-height: 1.5;
}

/* ── Choice buttons (front side) ──────────────────────────── */
.choices {
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin-bottom: 16px;
}

.choice {
  display: flex;
  align-items: center;
  gap: 12px;
  background: #16213e;
  border: 1px solid #0f3460;
  border-radius: 8px;
  padding: 12px 16px;
  cursor: pointer;
  text-align: left;
  color: #e0e0e0;
  font-size: 15px;
  transition: background 0.15s, border-color 0.15s;
  width: 100%;
}

/* Hover effect — only when the button is still enabled */
.choice:not(:disabled):hover {
  background: #0f3460;
  border-color: #e94560;
}

.choice:disabled {
  cursor: default;
}

/* Letter badge (A, B, C...) */
.choice .letter {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  border-radius: 50%;
  background: #0f3460;
  color: #a0c4ff;
  font-weight: 600;
  font-size: 13px;
  flex-shrink: 0;
}

/* ── Feedback states ──────────────────────────────────────── */

/* Correct answer highlight */
.choice.correct {
  background: #0d3b2e;
  border-color: #2ecc71;
}

.choice.correct .letter {
  background: #2ecc71;
  color: #0d3b2e;
}

/* Wrong answer highlight */
.choice.wrong {
  background: #3b0d0d;
  border-color: #e74c3c;
}

.choice.wrong .letter {
  background: #e74c3c;
  color: #fff;
}

/* Feedback text below choices */
.feedback {
  font-size: 15px;
  font-weight: 500;
  min-height: 24px;
  margin-top: 8px;
}

.feedback.correct-msg { color: #2ecc71; }
.feedback.wrong-msg   { color: #e74c3c; }

/* ── Explanation (back side) ──────────────────────────────── */
.explanation {
  margin-top: 20px;
  padding: 14px 16px;
  background: #16213e;
  border-left: 3px solid #a0c4ff;
  border-radius: 4px;
  font-size: 14px;
  color: #c0c0d0;
  line-height: 1.6;
}

.explanation-label {
  display: block;
  font-size: 11px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: #a0c4ff;
  margin-bottom: 6px;
}

/* ── Correct answer banner (back side) ───────────────────── */
.correct-banner {
  margin-top: 12px;
  padding: 10px 16px;
  background: #0d3b2e;
  border: 1px solid #2ecc71;
  border-radius: 8px;
  font-size: 15px;
  font-weight: 500;
  color: #2ecc71;
}
"""


# ---------------------------------------------------------------------------
# Note type creation and sync
# ---------------------------------------------------------------------------

# Template version — bump this number whenever you change FRONT_TEMPLATE,
# BACK_TEMPLATE, or CARD_CSS. The addon compares this against the version
# stored in the note type, and re-syncs the templates if they differ.
# This ensures users who already have the addon always get the latest templates
# after updating, without losing any of their cards.
TEMPLATE_VERSION = "1.1.0"


def create_note_type():
    """
    Creates or updates the Multiple Choice Quiz note type.

    First install  → creates the note type from scratch with all fields and templates.
    Existing install → checks the stored template version. If the code has a newer
                       version, updates the front template, back template, and CSS
                       in place. Cards and their reviews are never affected.
    """

    col = mw.col

    existing = col.models.by_name(NOTE_TYPE_NAME)

    if not existing:
        # ── First install: build the note type from scratch ──────────────
        model = col.models.new(NOTE_TYPE_NAME)

        for field_name in FIELDS:
            field = col.models.new_field(field_name)
            col.models.add_field(model, field)

        template = col.models.new_template("Card 1")
        template["qfmt"] = FRONT_TEMPLATE
        template["afmt"] = BACK_TEMPLATE
        model["css"] = CARD_CSS

        # Store the current template version inside the note type so future
        # runs can detect whether an update is needed.
        model["vers"] = [TEMPLATE_VERSION]

        col.models.add_template(model, template)
        col.models.add(model)
        col.models.save(model)

    else:
        # ── Existing install: sync templates if version changed ───────────
        stored_version = (existing.get("vers") or ["0"])[0]

        if stored_version == TEMPLATE_VERSION:
            return  # Already up to date — nothing to do

        # Update the front template, back template, and CSS.
        # The "tmpls" key holds the list of card templates inside the model.
        # We only have one template ("Card 1"), so we update index 0.
        existing["tmpls"][0]["qfmt"] = FRONT_TEMPLATE
        existing["tmpls"][0]["afmt"] = BACK_TEMPLATE
        existing["css"] = CARD_CSS
        existing["vers"] = [TEMPLATE_VERSION]

        col.models.save(existing)


# ---------------------------------------------------------------------------
# Question parser
# ---------------------------------------------------------------------------


def parse_questions(text: str) -> list:
    """
    Parses NotebookLM quiz text into a list of question dicts.

    Handles both formats:
    - Numbered:   "1. Question A) Choice Resposta: A Explicação: text."
    - Unnumbered: "Question A) Choice Resposta: A Explicação: text."

    Returns list of dicts with keys: question, A, B, C, D, E, answer, explanation
    """

    text = text.replace('\r\n', '\n').replace('\r', '\n').strip()
    # Strip preamble before the first question.
    # Numbered format (multiline): "^1." at start of line.
    # Numbered format (single-line block): "\b1." at word boundary.
    # Unnumbered format: drop leading lines that contain neither choices (A))
    # nor an answer marker, since those lines are titles/headings.
    numbered = re.search(r'(?m)^1[\.\)]', text)
    if not numbered:
        numbered = re.search(r'\b1[\.\)]\s', text)
    if numbered:
        text = text[numbered.start():]
    else:
        lines = text.split('\n')
        while lines and 'A)' not in lines[0] and 'Resposta:' not in lines[0]:
            lines.pop(0)
        text = '\n'.join(lines)

    questions = []

    # Match the full tail of each question as a single unit.
    # Lookahead alternatives handle:
    #   \n\s*\n         — blank line between questions
    #   \n\d+[\.\)]     — numbered question on next line
    #   \s+\d+[\.\)]\s  — numbered question on same line (single-line paste)
    #   \n              — unnumbered questions, one per line
    #   \Z              — end of string
    tail_re = re.compile(
        r'Resposta:\s*([A-Ea-e])\s*\n?\s*Explica[çc][aã]o:\s*(.+?)(?=\n\s*\n|\n\d+[\.\)]|\s+\d+[\.\)]\s|\n|\Z)',
        re.IGNORECASE | re.DOTALL
    )
    choice_re = re.compile(
        r'\b([A-E])\)\s*(.+?)(?=\s+[A-E]\)|\s*Resposta:|$)', re.DOTALL)

    tail_matches = list(tail_re.finditer(text))
    if not tail_matches:
        return []

    def last_a_before(pos):
        matches = list(re.finditer(r'\bA\)', text[:pos]))
        return matches[-1].start() if matches else None

    for i, tail in enumerate(tail_matches):
        answer = tail.group(1).upper()
        explanation = tail.group(2).strip()

        # ── Choices ────────────────────────────────────────────────────────
        choices_start = last_a_before(tail.start())
        if choices_start is None:
            continue

        choices_block = text[choices_start:tail.start()]
        choices = {}
        for cm in choice_re.finditer(choices_block):
            choices[cm.group(1).upper()] = cm.group(2).strip().rstrip('.')

        # ── Question text ──────────────────────────────────────────────────
        if i == 0:
            raw_question = text[:choices_start].strip()
        else:
            raw_question = text[tail_matches[i - 1].end()                                :choices_start].strip()

        # Strip leading question numbers like "1. " or "1) "
        raw_question = re.sub(r'^\d+[\.\)]\s*', '', raw_question)

        if raw_question and answer:
            q = {"question": raw_question, "answer": answer,
                 "explanation": explanation}
            q.update(choices)
            questions.append(q)

    return questions


def parse_cloze(text: str) -> list:
    """Returns individual cloze sentences containing at least one {{cN::}} marker.

    Handles two layouts:
    - One card per line (standard NotebookLM output)
    - Multiple sentences concatenated in a paragraph (split on '. {{c' boundaries)
    """
    results = []
    for line in text.splitlines():
        line = line.strip()
        if not line or "{{c" not in line:
            continue
        if line.count("{{c") > 1:
            # Split paragraph into individual sentences at '. {{c' boundaries
            parts = re.split(r'(?<=\.)\s+(?=\{\{c)', line)
            results.extend(p.strip() for p in parts if "{{c" in p)
        else:
            results.append(line)
    return results


# ---------------------------------------------------------------------------
# Obsidian export helpers
# ---------------------------------------------------------------------------

def _anki_tags_to_obsidian(tags_list: list) -> list:
    """Convert Anki tags to Obsidian format, preserving :: hierarchy as /."""
    result = []
    for tag in tags_list:
        obs_tag = tag.replace("::", "/")
        if obs_tag and obs_tag not in result:
            result.append(obs_tag)
    return result


def _format_mc_cards(mc_notes: list) -> str:
    body = "## Questões (Múltipla Escolha)\n\n"
    for i, q in enumerate(mc_notes, 1):
        body += f"{i}. {q.get('question', '')}\n"
        for letter in "ABCDE":
            if q.get(letter):
                body += f"   {letter}) {q[letter]}\n"
        ans = q.get("answer", "")
        expl = q.get("explanation", "")
        body += f"   **Resposta: {ans}**"
        body += f" — {expl}\n\n" if expl else "\n\n"
    return body


def _format_cloze_cards(cloze_notes: list) -> str:
    body = "## Cloze\n\n"
    for c in cloze_notes:
        body += f"- {c}\n"
    return body


def _format_mc_callouts(mc_notes: list) -> str:
    body = "## Questões (Múltipla Escolha)\n\n"
    for i, q in enumerate(mc_notes, 1):
        body += f"> [!question] {i}. {q.get('question', '')}\n"
        for letter in "ABCDE":
            if q.get(letter):
                body += f"> {letter}) {q[letter]}\n"
        ans = q.get("answer", "")
        expl = q.get("explanation", "")
        body += f">\n> **Resposta: {ans}**"
        body += f" — {expl}\n\n" if expl else "\n\n"
    return body


def _format_cloze_callouts(cloze_notes: list) -> str:
    body = "## Cloze\n\n"
    for c in cloze_notes:
        body += f"> [!info]\n> {c}\n\n"
    return body


def _render_template(template: str, variables: dict) -> str:
    for key, value in variables.items():
        template = template.replace("{{" + key + "}}", value)
    return template


def _yaml_quote(value: str) -> str:
    """Wrap YAML value in double quotes when needed to preserve string type."""
    special = set('[]{}|>#!:,\\')
    stripped = value.strip()
    needs_quotes = (
        any(c in value for c in special)
        or stripped.lstrip('-').replace('.', '', 1).isdigit()
        or stripped.lower() in ('true', 'false', 'null', 'yes', 'no', '')
    )
    if needs_quotes:
        return '"' + value.replace('\\', '\\\\').replace('"', '\\"') + '"'
    return value


def _build_obsidian_note(title: str, deck_name: str, obs_tags: list,
                         mc_notes: list, cloze_notes: list,
                         tmpl_properties: str, tmpl_content: str) -> str:
    from datetime import date
    tags_yaml = "\n".join(f"  - {t}" for t in obs_tags)
    mc_str = _format_mc_cards(mc_notes) if mc_notes else ""
    cloze_str = _format_cloze_cards(cloze_notes) if cloze_notes else ""
    mc_callouts = _format_mc_callouts(mc_notes) if mc_notes else ""
    cloze_callouts = _format_cloze_callouts(cloze_notes) if cloze_notes else ""
    sep = "\n" if mc_str and cloze_str else ""
    cards_str = (mc_str + sep + cloze_str).strip()
    sep_c = "\n" if mc_callouts and cloze_callouts else ""
    cards_callouts_str = (mc_callouts + sep_c + cloze_callouts).strip()
    variables = {
        "title": title,
        "date": date.today().isoformat(),
        "deck": deck_name,
        "tags": tags_yaml,
        "cards": cards_str,
        "mc_cards": mc_str.strip(),
        "cloze_cards": cloze_str.strip(),
        "cards_callouts": cards_callouts_str,
        "mc_cards_callouts": mc_callouts.strip(),
        "cloze_cards_callouts": cloze_callouts.strip(),
    }
    props = _render_template(tmpl_properties, variables)
    content = _render_template(tmpl_content, variables)
    return f"---\n{props}\n---\n\n{content}\n"


# ---------------------------------------------------------------------------
# Tag chip editor
# ---------------------------------------------------------------------------


class _TagChipEditor(QWidget):
    """Chip-style tag editor matching Anki's native Add dialog behaviour."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._tags: list = []

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(3)

        # chips row (horizontally scrollable, fixed height)
        self._chip_container = QWidget()
        self._chip_layout = QHBoxLayout(self._chip_container)
        self._chip_layout.setContentsMargins(2, 2, 2, 2)
        self._chip_layout.setSpacing(4)
        self._chip_layout.addStretch()

        chip_scroll = QScrollArea()
        chip_scroll.setWidget(self._chip_container)
        chip_scroll.setWidgetResizable(True)
        chip_scroll.setFixedHeight(36)
        chip_scroll.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        chip_scroll.setVerticalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        chip_scroll.setFrameShape(QFrame.Shape.NoFrame)

        self._input = TagEdit(self)
        self._input.setPlaceholderText(_t("tag_placeholder"))
        self._input.editingFinished.connect(self._commit_input)
        self._input.installEventFilter(self)

        outer.addWidget(chip_scroll)
        outer.addWidget(self._input)

    def eventFilter(self, obj, event) -> bool:
        if obj is self._input and event.type() == QEvent.Type.KeyPress:
            if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
                self._commit_input()
                return True  # consume — don't let Enter trigger the Import button
        return super().eventFilter(obj, event)

    def setCol(self, col) -> None:
        self._input.setCol(col)

    def _commit_input(self) -> None:
        text = self._input.text().strip()
        if not text:
            return
        for tag in mw.col.tags.split(text):
            if tag and tag not in self._tags:
                self._tags.append(tag)
        self._input.clear()
        self._rebuild()

    def _rebuild(self) -> None:
        while self._chip_layout.count() > 1:
            item = self._chip_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        for tag in self._tags:
            frame = QFrame()
            frame.setStyleSheet(
                "QFrame { background: #3a6bc4; border-radius: 4px; }"
            )
            row = QHBoxLayout(frame)
            row.setContentsMargins(7, 2, 3, 2)
            row.setSpacing(3)
            lbl = QLabel(tag)
            lbl.setStyleSheet(
                "color: white; font-size: 12px; background: transparent;"
            )
            del_btn = QPushButton()
            del_btn.setIcon(
                QApplication.style().standardIcon(
                    QStyle.StandardPixmap.SP_TitleBarCloseButton
                )
            )
            del_btn.setFixedSize(16, 16)
            del_btn.setStyleSheet("background: transparent; border: none;")
            del_btn.clicked.connect(lambda _, t=tag: self._remove(t))
            row.addWidget(lbl)
            row.addWidget(del_btn)
            self._chip_layout.insertWidget(
                self._chip_layout.count() - 1, frame)

    def _remove(self, tag: str) -> None:
        self._tags = [t for t in self._tags if t != tag]
        self._rebuild()

    def set_tags(self, tags: list) -> None:
        self._tags = list(tags)
        self._rebuild()

    def get_tags(self) -> list:
        result = list(self._tags)
        text = self._input.text().strip()
        if text:
            for tag in mw.col.tags.split(text):
                if tag and tag not in result:
                    result.append(tag)
        return result


# ---------------------------------------------------------------------------
# Importer UI
# ---------------------------------------------------------------------------


class ImporterDialog(QDialog):
    """
    Dialog with two tabs — Multiple Choice and Cloze — for importing
    NotebookLM text into Anki.
    """

    _INSTRUCTION_STYLE = (
        "background: palette(mid);"
        "border-radius: 6px;"
        "padding: 10px;"
        "font-size: 12px;"
    )

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(_t("importer_title"))
        self.setMinimumWidth(560)
        self.setMinimumHeight(620)
        self._build_ui()
        self.tags_input.set_tags(self._load_tags())

    # ── Tag persistence ───────────────────────────────────────────────────

    def _meta_path(self) -> str:
        import os
        return os.path.join(os.path.dirname(os.path.abspath(__file__)), "meta.json")

    def _load_tags(self) -> list:
        import json
        import os
        path = self._meta_path()
        if os.path.isfile(path):
            try:
                data = json.loads(open(path, encoding="utf-8-sig").read())
                return data.get("config", {}).get("importer_tags", [])
            except Exception:
                pass
        return []

    def _save_tags(self) -> None:
        import json
        import os
        path = self._meta_path()
        try:
            data: dict = {}
            if os.path.isfile(path):
                data = json.loads(open(path, encoding="utf-8").read())
            data.setdefault("config", {})[
                "importer_tags"] = self.tags_input.get_tags()
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
        except Exception:
            pass

    def closeEvent(self, event) -> None:
        self._save_tags()
        super().closeEvent(event)

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(20, 20, 20, 20)

        # ── Language toggle ───────────────────────────────────────────────
        lang_row = QHBoxLayout()
        lang_row.addStretch()
        for code, label in [("pt", "PT"), ("en", "EN")]:
            lb = QPushButton(label)
            lb.setFixedWidth(34)
            lb.setFlat(True)
            if _lang == code:
                lb.setStyleSheet("color: white; font-weight: bold; text-decoration: underline; border: none;")
            else:
                lb.setStyleSheet("color: #888; border: none;")
            lb.clicked.connect(lambda _, c=code: self._switch_lang(c))
            lang_row.addWidget(lb)
        layout.addLayout(lang_row)

        # ── Prompt copy buttons ───────────────────────────────────────────
        prompt_row = QHBoxLayout()
        btn_copy_mc = QPushButton(_t("btn_prompt_mc"))
        btn_copy_mc.setToolTip(_t("tooltip_prompt_mc"))
        btn_copy_mc.clicked.connect(
            lambda: self._copy_to_clipboard(
                PROMPT_MC, btn_copy_mc, "btn_prompt_mc", "btn_prompt_mc_copied")
        )
        btn_copy_cloze = QPushButton(_t("btn_prompt_cloze"))
        btn_copy_cloze.setToolTip(_t("tooltip_prompt_cloze"))
        btn_copy_cloze.clicked.connect(
            lambda: self._copy_to_clipboard(
                PROMPT_CLOZE, btn_copy_cloze, "btn_prompt_cloze", "btn_prompt_cloze_copied")
        )
        prompt_row.addWidget(btn_copy_mc)
        prompt_row.addWidget(btn_copy_cloze)
        layout.addLayout(prompt_row)

        # ── Tabs ──────────────────────────────────────────────────────────
        self.tabs = QTabWidget()
        self.tabs.addTab(self._build_mc_tab(), _t("tab_mc"))
        self.tabs.addTab(self._build_cloze_tab(), _t("tab_cloze"))
        layout.addWidget(self.tabs)

        # ── Deck selector (shared) ────────────────────────────────────────
        deck_row = QHBoxLayout()
        deck_label = QLabel(_t("lbl_deck"))
        deck_label.setFixedWidth(120)
        self.deck_combo = QComboBox()
        for name in sorted(mw.col.decks.all_names()):
            self.deck_combo.addItem(name)
        deck_row.addWidget(deck_label)
        deck_row.addWidget(self.deck_combo, stretch=1)
        layout.addLayout(deck_row)

        # ── Tags input (shared) ───────────────────────────────────────────
        tags_row = QHBoxLayout()
        tags_label = QLabel(_t("lbl_tags"))
        tags_label.setFixedWidth(120)
        self.tags_input = _TagChipEditor(self)
        self.tags_input.setCol(mw.col)
        tags_row.addWidget(tags_label)
        tags_row.addWidget(self.tags_input, stretch=1)
        layout.addLayout(tags_row)

        # ── Buttons (shared) ──────────────────────────────────────────────
        btn_row = QHBoxLayout()
        btn_row.addStretch()
        cancel_btn = QPushButton(_t("btn_cancel"))
        cancel_btn.clicked.connect(self.reject)
        import_btn = QPushButton(_t("btn_import"))
        import_btn.setDefault(True)
        import_btn.clicked.connect(self._on_import)
        btn_row.addWidget(cancel_btn)
        btn_row.addWidget(import_btn)
        layout.addLayout(btn_row)

    def _build_mc_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(10)
        layout.setContentsMargins(0, 12, 0, 0)
        instructions = QLabel(_t("mc_instructions"))
        instructions.setWordWrap(True)
        instructions.setStyleSheet(self._INSTRUCTION_STYLE)
        layout.addWidget(instructions)
        self.mc_input = QTextEdit()
        self.mc_input.setPlaceholderText(_t("mc_placeholder"))
        layout.addWidget(self.mc_input)

        layout.addWidget(QLabel(_t("lbl_preview")))
        self.mc_preview = QListWidget()
        self.mc_preview.setEditTriggers(
            QAbstractItemView.EditTrigger.NoEditTriggers)
        self.mc_preview.setFixedHeight(110)
        self.mc_input.textChanged.connect(self._update_mc_preview)
        layout.addWidget(self.mc_preview)
        return tab

    def _build_cloze_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(10)
        layout.setContentsMargins(0, 12, 0, 0)
        instructions = QLabel(_t("cloze_instructions"))
        instructions.setWordWrap(True)
        instructions.setStyleSheet(self._INSTRUCTION_STYLE)
        layout.addWidget(instructions)
        self.cloze_input = QTextEdit()
        self.cloze_input.setPlaceholderText(_t("cloze_placeholder"))
        layout.addWidget(self.cloze_input)

        layout.addWidget(QLabel(_t("lbl_preview")))
        self.cloze_preview = QListWidget()
        self.cloze_preview.setEditTriggers(
            QAbstractItemView.EditTrigger.NoEditTriggers)
        self.cloze_preview.setFixedHeight(110)
        self.cloze_input.textChanged.connect(self._update_cloze_preview)
        layout.addWidget(self.cloze_preview)
        return tab

    def _update_mc_preview(self):
        self.mc_preview.clear()
        questions = parse_questions(self.mc_input.toPlainText())
        for i, q in enumerate(questions, 1):
            snippet = q.get("question", "")[:70]
            self.mc_preview.addItem(
                f"Q{i}: {snippet}  →  {q.get('answer', '?')}")
        if not questions and self.mc_input.toPlainText().strip():
            text = self.mc_input.toPlainText()
            if "Resposta:" not in text and "Explicação:" not in text:
                msg = _t("preview_bad_format")
            else:
                msg = _t("preview_no_questions")
            item = QListWidgetItem(msg)
            item.setForeground(Qt.GlobalColor.red)
            self.mc_preview.addItem(item)

    def _update_cloze_preview(self):
        self.cloze_preview.clear()
        cards = parse_cloze(self.cloze_input.toPlainText())
        for card in cards:
            self.cloze_preview.addItem(card[:80])
        if not cards and self.cloze_input.toPlainText().strip():
            item = QListWidgetItem(_t("preview_no_cloze"))
            item.setForeground(Qt.GlobalColor.red)
            self.cloze_preview.addItem(item)

    def _get_tags(self) -> list:
        return self.tags_input.get_tags()

    def _is_duplicate_mc(self, question: str) -> bool:
        query = f'"note:{NOTE_TYPE_NAME}" "Question:{question}"'
        return bool(mw.col.find_notes(query))

    def _is_duplicate_cloze(self, card_text: str) -> bool:
        query = f'"note:Cloze" "Text:{card_text}"'
        return bool(mw.col.find_notes(query))

    def _copy_to_clipboard(self, text, btn, original_key, copied_key):
        QApplication.clipboard().setText(text)
        btn.setText(_t(copied_key))
        from aqt.qt import QTimer
        QTimer.singleShot(1500, lambda: btn.setText(_t(original_key)))

    def _switch_lang(self, lang: str) -> None:
        _set_lang(lang)
        self._save_tags()
        self.close()
        _open_importer()

    def _on_import(self):
        if self.tabs.currentIndex() == 0:
            self._import_mc()
        else:
            self._import_cloze()

    def _import_mc(self):
        from aqt.utils import showWarning, showInfo
        raw_text = self.mc_input.toPlainText().strip()
        if not raw_text:
            showWarning(_t("warn_no_text"))
            return

        questions = parse_questions(raw_text)
        if not questions:
            showWarning(_t("warn_no_questions"))
            return

        deck_name = self.deck_combo.currentText()
        tags = self._get_tags()
        tags_str = ", ".join(tags) if tags else _t("confirm_none")
        reply = QMessageBox.question(
            self, _t("confirm_import_title"),
            f"{_t('confirm_mc_body', n=len(questions))}<br>"
            f"{_t('confirm_deck_lbl')} <b>{deck_name}</b><br>"
            f"{_t('confirm_tags_lbl')} <b>{tags_str}</b><br><br>"
            f"{_t('confirm_proceed')}",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply != QMessageBox.StandardButton.Yes:
            return

        deck_id = mw.col.decks.id(deck_name)
        mw.col.decks.select(deck_id)

        model = mw.col.models.by_name(NOTE_TYPE_NAME)
        if not model:
            showWarning(_t("warn_no_note_type"))
            return

        created = 0
        skipped = 0
        for q in questions:
            if self._is_duplicate_mc(q.get("question", "")):
                skipped += 1
                continue
            note = mw.col.new_note(model)
            note["Question"] = q.get("question", "")
            note["A"] = q.get("A", "")
            note["B"] = q.get("B", "")
            note["C"] = q.get("C", "")
            note["D"] = q.get("D", "")
            note["E"] = q.get("E", "")
            note["Answer"] = q.get("answer", "")
            note["Explanation"] = q.get("explanation", "")
            note.note_type()["did"] = deck_id
            note.tags = self._get_tags()
            mw.col.add_note(note, deck_id)
            created += 1

        mw.reset()
        msg = _t("success_mc", created=created, deck=deck_name)
        if skipped:
            msg += _t("success_skipped", skipped=skipped)
        showInfo(msg)
        self.accept()

    def _import_cloze(self):
        from aqt.utils import showWarning, showInfo
        raw_text = self.cloze_input.toPlainText().strip()
        if not raw_text:
            showWarning(_t("warn_no_text"))
            return

        cards = parse_cloze(raw_text)
        if not cards:
            showWarning(_t("warn_no_cloze"))
            return

        # Find the native Cloze note type (model type == 1)
        cloze_model = next(
            (m for m in mw.col.models.all() if m["type"] == 1), None
        )
        if not cloze_model:
            showWarning(_t("warn_no_cloze_type"))
            return

        deck_name = self.deck_combo.currentText()
        tags = self._get_tags()
        tags_str = ", ".join(tags) if tags else _t("confirm_none")
        reply = QMessageBox.question(
            self, _t("confirm_import_title"),
            f"{_t('confirm_cloze_body', n=len(cards))}<br>"
            f"{_t('confirm_deck_lbl')} <b>{deck_name}</b><br>"
            f"{_t('confirm_tags_lbl')} <b>{tags_str}</b><br><br>"
            f"{_t('confirm_proceed')}",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply != QMessageBox.StandardButton.Yes:
            return

        deck_id = mw.col.decks.id(deck_name)
        mw.col.decks.select(deck_id)

        created = 0
        skipped = 0
        for card_text in cards:
            if self._is_duplicate_cloze(card_text):
                skipped += 1
                continue
            note = mw.col.new_note(cloze_model)
            # Escape HTML so tags like <tr> are displayed literally, not stripped
            safe_text = card_text.replace("&", "&amp;").replace(
                "<", "&lt;").replace(">", "&gt;")
            note.fields[0] = safe_text
            note.note_type()["did"] = deck_id
            note.tags = self._get_tags()
            mw.col.add_note(note, deck_id)
            created += 1

        mw.reset()
        msg = _t("success_cloze", created=created, deck=deck_name)
        if skipped:
            msg += _t("success_skipped", skipped=skipped)
        showInfo(msg)
        self.accept()


# ---------------------------------------------------------------------------
# Obsidian Exporter UI
# ---------------------------------------------------------------------------

_OBS_DEFAULT_FILENAME = "{{title}}.md"
_OBS_DEFAULT_CONTENT = "{{cards}}"

# (label, internal key) — order matches Obsidian's property type list
_PROP_TYPES = [
    ("Ab  Text",      "text"),
    ("≡   List",      "list"),
    ("#   Number",    "number"),
    ("☑   Checkbox",  "checkbox"),
    ("📅  Date",      "date"),
    ("⏰  Datetime",  "datetime"),
]

_OBS_DEFAULT_PROP_ROWS = [
    ["tags",      "{{tags}}",  "list"],
    ["created",   "{{date}}",  "date"],
    ["anki-deck", "{{deck}}",  "text"],
]

_OBS_DEFAULT_TEMPLATES = [
    {
        "name": "Default",
        "filename": _OBS_DEFAULT_FILENAME,
        "prop_rows": _OBS_DEFAULT_PROP_ROWS,
        "content": _OBS_DEFAULT_CONTENT,
    }
]


class _PropertyRow(QWidget):
    """A single key/value row in the properties editor."""

    def __init__(self, key: str = "", value: str = "", ptype: str = "text",
                 known_props: dict | None = None, parent=None):
        super().__init__(parent)
        self._known_props: dict = known_props or {}
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 2, 0, 2)
        layout.setSpacing(6)

        self.type_combo = QComboBox()
        self.type_combo.setFixedWidth(110)
        for label, data in _PROP_TYPES:
            self.type_combo.addItem(label, userData=data)
        for i, (_, data) in enumerate(_PROP_TYPES):
            if data == ptype:
                self.type_combo.setCurrentIndex(i)
                break

        self.key_combo = QComboBox()
        self.key_combo.setEditable(True)
        self.key_combo.setFixedWidth(140)
        self.key_combo.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)
        self.key_combo.lineEdit().setPlaceholderText(_t("prop_key_hint"))
        if self._known_props:
            self.key_combo.addItem("")
            for name in sorted(self._known_props.keys()):
                self.key_combo.addItem(name)
        self.key_combo.setCurrentText(key)
        self.key_combo.currentTextChanged.connect(self._on_key_changed)

        self.val_edit = QLineEdit(value)
        self.val_edit.setPlaceholderText(_t("prop_val_hint"))

        self.del_btn = QPushButton()
        self.del_btn.setFixedSize(26, 26)
        self.del_btn.setIcon(
            QApplication.style().standardIcon(QStyle.StandardPixmap.SP_TrashIcon)
        )
        self.del_btn.setStyleSheet("background: transparent; border: none;")
        self.del_btn.setToolTip("Remover propriedade")

        layout.addWidget(self.type_combo)
        layout.addWidget(self.key_combo)
        layout.addWidget(self.val_edit, stretch=1)
        layout.addWidget(self.del_btn)

    def _on_key_changed(self, text: str) -> None:
        if text in self._known_props:
            ptype = self._known_props[text]
            for i, (_, data) in enumerate(_PROP_TYPES):
                if data == ptype:
                    self.type_combo.setCurrentIndex(i)
                    return

    def ptype(self) -> str:
        return self.type_combo.currentData()

    def key(self) -> str:
        return self.key_combo.currentText().strip()


class ObsidianExporterDialog(QDialog):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(_t("exporter_title"))
        self.setMinimumWidth(580)
        self.setMinimumHeight(600)
        self._mc_notes: list = []
        self._cloze_notes: list = []
        self._all_tags: list = []
        self._cfg = self._load_config()
        self._build_ui()

    # ── Config ───────────────────────────────────────────────────────────────

    def _meta_path(self) -> str:
        import os
        return os.path.join(os.path.dirname(os.path.abspath(__file__)), "meta.json")

    def _load_config(self) -> dict:
        import json
        import os
        raw: dict = {}
        path = self._meta_path()
        if os.path.isfile(path):
            try:
                raw = json.loads(
                    open(path, encoding="utf-8-sig").read()).get("config", {})
            except Exception:
                pass
        # Migrate old single-template format to the new templates list
        if "obs_prop_rows" in raw and "obs_templates" not in raw:
            raw["obs_templates"] = [{
                "name": "Default",
                "filename": raw.pop("obs_template_filename", _OBS_DEFAULT_FILENAME),
                "prop_rows": raw.pop("obs_prop_rows", _OBS_DEFAULT_PROP_ROWS),
                "content": raw.pop("obs_template_content", _OBS_DEFAULT_CONTENT),
            }]
            raw.setdefault("obs_active_template", "Default")
        defaults = {
            "obsidian_vault_path": "",
            "obsidian_last_folder": "",
            "obs_templates": list(_OBS_DEFAULT_TEMPLATES),
            "obs_active_template": _OBS_DEFAULT_TEMPLATES[0]["name"],
            "obs_tmpl_deck_link": {},
            "obs_known_properties": {},
        }
        return {**defaults, **raw}

    def _save_config(self) -> None:
        import json
        import os
        from aqt.utils import showWarning
        path = self._meta_path()
        try:
            data: dict = {}
            if os.path.isfile(path):
                data = json.loads(open(path, encoding="utf-8").read())
            data["config"] = self._cfg
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
        except Exception as e:
            showWarning(_t("warn_config_save", e=e))

    # ── UI build ─────────────────────────────────────────────────────────────

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(20, 20, 20, 20)

        # ── Language toggle ───────────────────────────────────────────────
        lang_row = QHBoxLayout()
        lang_row.addStretch()
        for code, label in [("pt", "PT"), ("en", "EN")]:
            lb = QPushButton(label)
            lb.setFixedWidth(34)
            lb.setFlat(True)
            if _lang == code:
                lb.setStyleSheet("color: white; font-weight: bold; text-decoration: underline; border: none;")
            else:
                lb.setStyleSheet("color: #888; border: none;")
            lb.clicked.connect(lambda _, c=code: self._switch_lang(c))
            lang_row.addWidget(lb)
        layout.addLayout(lang_row)

        tabs = QTabWidget()
        tabs.addTab(self._build_export_tab(), _t("tab_export"))
        tabs.addTab(self._build_template_tab(), _t("tab_model"))
        layout.addWidget(tabs)

    def _switch_lang(self, lang: str) -> None:
        _set_lang(lang)
        self._save_active_to_config()
        self._save_config()
        self.close()
        _open_obsidian_exporter()

    def _build_export_tab(self) -> QWidget:
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(12)
        layout.setContentsMargins(16, 16, 16, 16)

        # Template selector (mirrors Modelo tab)
        tmpl_row = QHBoxLayout()
        tmpl_label = QLabel(_t("lbl_template"))
        tmpl_label.setFixedWidth(120)
        self.export_tmpl_combo = QComboBox()
        for t in self._cfg.get("obs_templates", _OBS_DEFAULT_TEMPLATES):
            self.export_tmpl_combo.addItem(t["name"])
        active = self._cfg.get("obs_active_template",
                               _OBS_DEFAULT_TEMPLATES[0]["name"])
        idx = self.export_tmpl_combo.findText(active)
        self.export_tmpl_combo.setCurrentIndex(max(0, idx))
        self.export_tmpl_combo.currentIndexChanged.connect(
            self._on_export_tmpl_selected)
        tmpl_row.addWidget(tmpl_label)
        tmpl_row.addWidget(self.export_tmpl_combo, stretch=1)
        layout.addLayout(tmpl_row)

        # Deck selector
        deck_row = QHBoxLayout()
        deck_label = QLabel(_t("lbl_source_deck"))
        deck_label.setFixedWidth(120)
        self.deck_combo = QComboBox()
        for name in sorted(mw.col.decks.all_names()):
            self.deck_combo.addItem(name)
        self.deck_combo.currentTextChanged.connect(self._load_deck_cards)
        self.deck_combo.currentTextChanged.connect(self._on_deck_changed)
        deck_row.addWidget(deck_label)
        deck_row.addWidget(self.deck_combo, stretch=1)
        layout.addLayout(deck_row)

        # Card preview list
        self.cards_label = QLabel(_t("lbl_cards"))
        layout.addWidget(self.cards_label)
        self.card_list = QListWidget()
        self.card_list.setEditTriggers(
            QAbstractItemView.EditTrigger.NoEditTriggers)
        self.card_list.setFixedHeight(120)
        layout.addWidget(self.card_list)

        # Vault path
        vault_row = QHBoxLayout()
        vault_label = QLabel(_t("lbl_vault"))
        vault_label.setFixedWidth(120)
        self.vault_edit = QLineEdit()
        self.vault_edit.setReadOnly(True)
        self.vault_edit.setPlaceholderText(_t("vault_hint"))
        self.vault_edit.setText(self._cfg.get("obsidian_vault_path", ""))
        btn_vault = QPushButton(_t("btn_browse"))
        btn_vault.clicked.connect(self._on_browse_vault)
        vault_row.addWidget(vault_label)
        vault_row.addWidget(self.vault_edit, stretch=1)
        vault_row.addWidget(btn_vault)
        layout.addLayout(vault_row)

        # Output folder
        folder_row = QHBoxLayout()
        folder_label = QLabel(_t("lbl_output"))
        folder_label.setFixedWidth(120)
        self.folder_edit = QLineEdit()
        self.folder_edit.setPlaceholderText(_t("output_hint"))
        self.folder_edit.setText(self._cfg.get("obsidian_last_folder", ""))
        btn_folder = QPushButton(_t("btn_browse"))
        btn_folder.clicked.connect(self._on_browse_output_folder)
        folder_row.addWidget(folder_label)
        folder_row.addWidget(self.folder_edit, stretch=1)
        folder_row.addWidget(btn_folder)
        layout.addLayout(folder_row)

        # Note title
        title_row = QHBoxLayout()
        title_label = QLabel(_t("lbl_note_title"))
        title_label.setFixedWidth(120)
        self.title_edit = QLineEdit()
        self.title_edit.setPlaceholderText(_t("title_hint"))
        title_row.addWidget(title_label)
        title_row.addWidget(self.title_edit, stretch=1)
        layout.addLayout(title_row)

        layout.addStretch()

        # Buttons
        btn_row = QHBoxLayout()
        btn_row.addStretch()
        cancel_btn = QPushButton(_t("btn_cancel_exp"))
        cancel_btn.clicked.connect(self.reject)
        export_btn = QPushButton(_t("btn_export"))
        export_btn.setDefault(True)
        export_btn.clicked.connect(self._on_export)
        btn_row.addWidget(cancel_btn)
        btn_row.addWidget(export_btn)
        layout.addLayout(btn_row)

        self._load_deck_cards(self.deck_combo.currentText())
        return tab

    def _build_template_tab(self) -> QWidget:
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(10)
        layout.setContentsMargins(16, 16, 16, 16)

        # ── Template selector row ─────────────────────────────────────────────
        tmpl_row = QHBoxLayout()
        tmpl_row.addWidget(QLabel(_t("lbl_template")))
        self.tmpl_combo = QComboBox()
        self.tmpl_combo.setMinimumWidth(140)
        for t in self._cfg.get("obs_templates", _OBS_DEFAULT_TEMPLATES):
            self.tmpl_combo.addItem(t["name"])
        active = self._cfg.get("obs_active_template",
                               _OBS_DEFAULT_TEMPLATES[0]["name"])
        idx = self.tmpl_combo.findText(active)
        self.tmpl_combo.setCurrentIndex(max(0, idx))

        btn_new = QPushButton(_t("btn_new"))
        btn_dup = QPushButton(_t("btn_duplicate"))
        btn_del = QPushButton(_t("btn_delete"))
        btn_save = QPushButton(_t("btn_save"))

        tmpl_row.addWidget(self.tmpl_combo, stretch=1)
        tmpl_row.addWidget(btn_new)
        tmpl_row.addWidget(btn_dup)
        tmpl_row.addWidget(btn_del)
        tmpl_row.addWidget(btn_save)
        layout.addLayout(tmpl_row)

        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet("color: #444;")
        layout.addWidget(sep)

        # ── Filename ──────────────────────────────────────────────────────────
        fn_row = QHBoxLayout()
        fn_label = QLabel(_t("lbl_filename"))
        fn_label.setFixedWidth(140)
        self.filename_edit = QLineEdit()
        fn_row.addWidget(fn_label)
        fn_row.addWidget(self.filename_edit, stretch=1)
        layout.addLayout(fn_row)

        vars_hint = QLabel(_t("lbl_vars"))
        vars_hint.setStyleSheet("color: gray; font-size: 11px;")
        vars_hint.setWordWrap(True)
        layout.addWidget(vars_hint)

        # ── Properties ────────────────────────────────────────────────────────
        # Column headers
        col_header = QHBoxLayout()
        col_header.setContentsMargins(0, 0, 0, 0)
        col_header.setSpacing(6)
        lbl_type = QLabel(_t("col_type"))
        lbl_type.setFixedWidth(110)
        lbl_type.setStyleSheet("color: #888; font-size: 11px;")
        lbl_key = QLabel(_t("col_property"))
        lbl_key.setFixedWidth(120)
        lbl_key.setStyleSheet("color: #888; font-size: 11px;")
        lbl_val = QLabel(_t("col_value"))
        lbl_val.setStyleSheet("color: #888; font-size: 11px;")
        lbl_del_spacer = QLabel()
        lbl_del_spacer.setFixedWidth(26)
        col_header.addWidget(lbl_type)
        col_header.addWidget(lbl_key)
        col_header.addWidget(lbl_val, stretch=1)
        col_header.addWidget(lbl_del_spacer)
        layout.addLayout(col_header)

        self._props_container = QWidget()
        self._props_layout = QVBoxLayout(self._props_container)
        self._props_layout.setContentsMargins(0, 0, 0, 0)
        self._props_layout.setSpacing(2)
        self._prop_rows: list = []

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(self._props_container)
        scroll.setFixedHeight(130)
        scroll.setFrameShape(scroll.Shape.StyledPanel)
        layout.addWidget(scroll)

        prop_actions = QHBoxLayout()
        add_prop_btn = QPushButton(_t("btn_add_prop"))
        add_prop_btn.setFlat(True)
        add_prop_btn.setStyleSheet(
            "color: #6c9; text-align: left; padding: 2px 0;")
        add_prop_btn.clicked.connect(lambda: self._add_property_row())
        import_prop_btn = QPushButton(_t("btn_import_obs"))
        import_prop_btn.setFlat(True)
        import_prop_btn.setStyleSheet(
            "color: #69c; text-align: left; padding: 2px 0;")
        import_prop_btn.clicked.connect(self._on_import_obsidian_properties)
        prop_actions.addWidget(add_prop_btn)
        prop_actions.addStretch()
        prop_actions.addWidget(import_prop_btn)
        layout.addLayout(prop_actions)

        # ── Content ───────────────────────────────────────────────────────────
        layout.addWidget(QLabel(_t("lbl_content")))
        self.content_edit = QTextEdit()
        layout.addWidget(self.content_edit, stretch=1)

        # ── Bottom row ────────────────────────────────────────────────────────
        bottom_row = QHBoxLayout()
        bottom_row.addStretch()
        reset_btn = QPushButton(_t("btn_reset"))
        bottom_row.addWidget(reset_btn)
        layout.addLayout(bottom_row)

        # ── Load active template & wire signals ───────────────────────────────
        self._load_template_into_ui(self._get_active_template())
        self.tmpl_combo.currentIndexChanged.connect(self._on_template_selected)
        btn_new.clicked.connect(self._on_new_template)
        btn_dup.clicked.connect(self._on_duplicate_template)
        btn_del.clicked.connect(self._on_delete_template)
        btn_save.clicked.connect(self._on_save_template)
        reset_btn.clicked.connect(self._on_reset_template)

        return tab

    # ── Deck loading ─────────────────────────────────────────────────────────

    def _load_deck_cards(self, deck_name: str = "") -> None:
        if not deck_name:
            deck_name = self.deck_combo.currentText()
        self.card_list.clear()
        self._mc_notes = []
        self._cloze_notes = []
        tag_set: set = set()

        note_ids = mw.col.find_notes(f'"deck:{deck_name}"')
        counter = 0
        for nid in note_ids:
            note = mw.col.get_note(nid)
            for tag in note.tags:
                tag_set.add(tag)
            field_names = [f["name"] for f in note.note_type()["flds"]]
            counter += 1
            if "Question" in field_names:
                q = {
                    "question": note["Question"],
                    "A": note["A"], "B": note["B"],
                    "C": note["C"], "D": note["D"],
                    "E": note["E"],
                    "answer": note["Answer"],
                    "explanation": note["Explanation"],
                }
                self._mc_notes.append(q)
                self.card_list.addItem(
                    f"{counter}) MC: {note['Question'][:60]}  → {note['Answer']}")
            else:
                text = note.fields[0]
                self._cloze_notes.append(text)
                self.card_list.addItem(f"{counter}) Cloze: {text[:65]}")

        self._all_tags = list(tag_set)
        mc_count = len(self._mc_notes)
        cloze_count = len(self._cloze_notes)
        total = mc_count + cloze_count
        if total:
            summary = _t("cards_summary", total=total, mc=mc_count, cloze=cloze_count)
        else:
            summary = _t("no_cards")
        self.cards_label.setText(f"{_t('lbl_cards')} {summary}")

    # ── Browse handlers ──────────────────────────────────────────────────────

    def _on_browse_vault(self) -> None:
        path = QFileDialog.getExistingDirectory(
            self, _t("dlg_vault_title"),
            self._cfg.get("obsidian_vault_path", ""))
        if path:
            self.vault_edit.setText(path)
            self._cfg["obsidian_vault_path"] = path
            self._save_config()

    def _on_browse_output_folder(self) -> None:
        start = self._cfg.get("obsidian_vault_path", "") or ""
        path = QFileDialog.getExistingDirectory(
            self, _t("dlg_folder_title"), start)
        if path:
            import os
            vault = self._cfg.get("obsidian_vault_path", "")
            try:
                rel = os.path.relpath(path, vault) if vault else path
            except ValueError:
                rel = path
            self.folder_edit.setText(rel)

    # ── Quick fields ─────────────────────────────────────────────────────────

    def _on_export_tmpl_selected(self, index: int) -> None:
        templates = self._get_templates()
        if not (0 <= index < len(templates)):
            return
        new_tmpl = templates[index]
        new_name = new_tmpl["name"]
        self._cfg["obs_active_template"] = new_name
        # Sync Modelo tab combo without triggering its signal
        if hasattr(self, "tmpl_combo"):
            self.tmpl_combo.blockSignals(True)
            self.tmpl_combo.setCurrentIndex(index)
            self.tmpl_combo.blockSignals(False)
        # Auto-link: restore saved deck for this template
        saved_deck = self._cfg.get("obs_tmpl_deck_link", {}).get(new_name)
        if saved_deck and hasattr(self, "deck_combo"):
            deck_idx = self.deck_combo.findText(saved_deck)
            if deck_idx >= 0:
                self.deck_combo.setCurrentIndex(deck_idx)
        self._save_config()

    def _on_deck_changed(self, deck_name: str) -> None:
        tmpl_name = self._cfg.get("obs_active_template", "")
        if tmpl_name:
            self._cfg.setdefault("obs_tmpl_deck_link", {})[
                tmpl_name] = deck_name

    # ── Obsidian property import ─────────────────────────────────────────────

    _OBS_TYPE_MAP = {
        "text":      "text",
        "multitext": "list",
        "tags":      "list",
        "number":    "number",
        "checkbox":  "checkbox",
        "date":      "date",
        "datetime":  "datetime",
    }

    def _on_import_obsidian_properties(self) -> None:
        import json
        import os
        from aqt.utils import showWarning, showInfo

        vault = self._cfg.get("obsidian_vault_path", "").strip()
        if not vault or not os.path.isdir(vault):
            showWarning(_t("warn_no_vault_props"))
            return

        types_path = os.path.join(vault, ".obsidian", "types.json")
        if not os.path.isfile(types_path):
            showWarning(_t("warn_types_not_found", path=types_path))
            return

        try:
            with open(types_path, encoding="utf-8") as f:
                data = json.load(f)
        except Exception as e:
            showWarning(_t("warn_types_error", e=e))
            return

        types_dict: dict = data.get("types", {})
        if not types_dict:
            showWarning(_t("warn_no_properties"))
            return

        # Save to config as {name: mapped_ptype} — not added as rows
        known: dict = {}
        for name, obs_type in types_dict.items():
            known[name] = self._OBS_TYPE_MAP.get(obs_type, "text")
        self._cfg["obs_known_properties"] = known
        self._save_config()

        # Reload existing rows so their dropdowns include the new options
        current = self._read_ui_as_template()
        self._load_template_into_ui(current)

        showInfo(_t("obs_props_imported", n=len(known)))

    # ── Property row helpers ─────────────────────────────────────────────────

    def _add_property_row(self, key: str = "", value: str = "", ptype: str = "text") -> None:
        known = self._cfg.get("obs_known_properties", {})
        row = _PropertyRow(key, value, ptype, known_props=known,
                           parent=self._props_container)
        row.del_btn.clicked.connect(lambda: self._remove_property_row(row))
        self._prop_rows.append(row)
        self._props_layout.addWidget(row)

    def _remove_property_row(self, row: "_PropertyRow") -> None:
        if row in self._prop_rows:
            self._prop_rows.remove(row)
        row.setParent(None)
        row.deleteLater()

    def _get_prop_rows_data(self) -> list:
        return [
            [r.key(), r.val_edit.text().strip(), r.ptype()]
            for r in self._prop_rows
            if r.key()
        ]

    # ── Template management ──────────────────────────────────────────────────

    def _get_templates(self) -> list:
        return self._cfg.setdefault("obs_templates", list(_OBS_DEFAULT_TEMPLATES))

    def _get_active_template(self) -> dict:
        templates = self._get_templates()
        name = self._cfg.get("obs_active_template", templates[0]["name"])
        for t in templates:
            if t["name"] == name:
                return t
        return templates[0]

    def _load_template_into_ui(self, tmpl: dict) -> None:
        self.filename_edit.setText(tmpl.get("filename", _OBS_DEFAULT_FILENAME))
        for row in list(self._prop_rows):
            self._remove_property_row(row)
        for row_data in tmpl.get("prop_rows", _OBS_DEFAULT_PROP_ROWS):
            key, val, *rest = row_data
            ptype = rest[0] if rest else "text"
            self._add_property_row(key, val, ptype)
        self.content_edit.setPlainText(
            tmpl.get("content", _OBS_DEFAULT_CONTENT))

    def _read_ui_as_template(self) -> dict:
        # Use obs_active_template as the name source — tmpl_combo.currentText() may
        # already reflect the NEW selection when this is called during a switch.
        name = self._cfg.get("obs_active_template",
                             self.tmpl_combo.currentText())
        return {
            "name": name,
            "filename": self.filename_edit.text().strip() or _OBS_DEFAULT_FILENAME,
            "prop_rows": self._get_prop_rows_data(),
            "content": self.content_edit.toPlainText(),
        }

    def _save_active_to_config(self) -> None:
        current = self._read_ui_as_template()
        templates = self._get_templates()
        name = self._cfg.get("obs_active_template", "")
        for i, t in enumerate(templates):
            if t["name"] == name:
                templates[i] = current
                break
        self._cfg["obs_templates"] = templates

    def _on_save_template(self) -> None:
        self._save_active_to_config()
        self._save_config()
        from aqt.utils import showInfo
        name = self._cfg.get("obs_active_template", "")
        showInfo(_t("template_saved", name=name))

    def _on_template_selected(self, index: int) -> None:
        self._save_active_to_config()
        templates = self._get_templates()
        if 0 <= index < len(templates):
            self._cfg["obs_active_template"] = templates[index]["name"]
            self._load_template_into_ui(templates[index])
            # Sync export combo
            self.export_tmpl_combo.blockSignals(True)
            self.export_tmpl_combo.setCurrentIndex(index)
            self.export_tmpl_combo.blockSignals(False)

            self._save_config()

    def _on_new_template(self) -> None:
        from aqt.utils import getText
        name, ok = getText(_t("dlg_new_tmpl_label"), title=_t("dlg_new_tmpl_title"))
        if not ok or not name.strip():
            return
        name = name.strip()
        if any(t["name"] == name for t in self._get_templates()):
            from aqt.utils import showWarning
            showWarning(_t("warn_tmpl_exists", name=name))
            return
        new_tmpl = {
            "name": name,
            "filename": _OBS_DEFAULT_FILENAME,
            "prop_rows": [list(r) for r in _OBS_DEFAULT_PROP_ROWS],
            "content": _OBS_DEFAULT_CONTENT,
        }
        self._get_templates().append(new_tmpl)
        self._cfg["obs_active_template"] = name
        for combo in (self.tmpl_combo, self.export_tmpl_combo):
            combo.blockSignals(True)
            combo.addItem(name)
            combo.setCurrentIndex(combo.count() - 1)
            combo.blockSignals(False)
        self._load_template_into_ui(new_tmpl)
        self._save_config()

    def _on_duplicate_template(self) -> None:
        from aqt.utils import getText
        current = self._read_ui_as_template()
        suggested = f"Cópia de {current['name']}"
        name, ok = getText(_t("dlg_dup_tmpl_label"),
                           default=suggested, title=_t("dlg_dup_tmpl_title"))
        if not ok or not name.strip():
            return
        name = name.strip()
        if any(t["name"] == name for t in self._get_templates()):
            from aqt.utils import showWarning
            showWarning(_t("warn_tmpl_exists", name=name))
            return
        dup = {**current, "name": name}
        self._get_templates().append(dup)
        self._cfg["obs_active_template"] = name
        for combo in (self.tmpl_combo, self.export_tmpl_combo):
            combo.blockSignals(True)
            combo.addItem(name)
            combo.setCurrentIndex(combo.count() - 1)
            combo.blockSignals(False)
        self._load_template_into_ui(dup)
        self._save_config()

    def _on_delete_template(self) -> None:
        templates = self._get_templates()
        if len(templates) <= 1:
            from aqt.utils import showWarning
            showWarning(_t("warn_last_tmpl"))
            return
        name = self.tmpl_combo.currentText()
        reply = QMessageBox.question(
            self, _t("dlg_del_tmpl_title"),
            _t("dlg_del_tmpl_body", name=name),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply != QMessageBox.StandardButton.Yes:
            return
        idx = self.tmpl_combo.currentIndex()
        self._cfg["obs_templates"] = [
            t for t in templates if t["name"] != name]
        new_idx = max(0, idx - 1)
        self._cfg["obs_active_template"] = self._get_templates()[
            new_idx]["name"]
        for combo in (self.tmpl_combo, self.export_tmpl_combo):
            combo.blockSignals(True)
            combo.removeItem(idx)
            combo.setCurrentIndex(new_idx)
            combo.blockSignals(False)
        self._load_template_into_ui(self._get_templates()[new_idx])
        self._save_config()

    def _on_reset_template(self) -> None:
        self._load_template_into_ui({
            "filename": _OBS_DEFAULT_FILENAME,
            "prop_rows": _OBS_DEFAULT_PROP_ROWS,
            "content": _OBS_DEFAULT_CONTENT,
        })

    # ── Export ───────────────────────────────────────────────────────────────

    def closeEvent(self, event) -> None:
        self._save_active_to_config()
        self._save_config()
        super().closeEvent(event)

    def _on_export(self) -> None:
        import os
        from aqt.utils import showWarning, showInfo

        vault = self._cfg.get("obsidian_vault_path", "").strip()
        if not vault or not os.path.isdir(vault):
            showWarning(_t("warn_vault_missing"))
            return

        folder_rel = self.folder_edit.text().strip()
        output_dir = os.path.join(vault, folder_rel) if folder_rel else vault
        try:
            os.makedirs(output_dir, exist_ok=True)
        except OSError as e:
            showWarning(_t("warn_mkdir_failed", path=output_dir, e=e))
            return

        deck_name = self.deck_combo.currentText()
        title = self.title_edit.text().strip() or deck_name
        tmpl_fn = self.filename_edit.text().strip() or _OBS_DEFAULT_FILENAME
        tmpl_content = self.content_edit.toPlainText()

        # Render filename
        from datetime import date
        fn_vars = {
            "title": title, "date": date.today().isoformat(), "deck": deck_name
        }
        filename = _render_template(tmpl_fn, fn_vars)
        if not filename.endswith(".md"):
            filename += ".md"
        filepath = os.path.join(output_dir, filename)

        if os.path.exists(filepath):
            reply = QMessageBox.question(
                self, _t("confirm_overwrite_title"),
                _t("confirm_overwrite_body", filename=filename),
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            )
            if reply != QMessageBox.StandardButton.Yes:
                return

        obs_tags = _anki_tags_to_obsidian(self._all_tags)

        # Build properties YAML from structured rows
        from datetime import date as _date
        all_vars = {
            "title": title, "date": _date.today().isoformat(),
            "deck": deck_name,
            "tags": "\n".join(f"  - {t}" for t in obs_tags),
        }
        yaml_lines = []
        for key, val_tmpl, ptype in self._get_prop_rows_data():
            rendered = _render_template(val_tmpl, all_vars)
            if ptype == "list":
                yaml_lines.append(f"{key}:")
                if "\n" in rendered:
                    yaml_lines.append(rendered)
                else:
                    for item in (v.strip() for v in rendered.split(",") if v.strip()):
                        yaml_lines.append(f"  - {_yaml_quote(item)}")
            elif ptype == "checkbox":
                yaml_lines.append(
                    f"{key}: {'true' if rendered.lower() in ('true', 'yes', '1') else 'false'}")
            elif ptype in ("number", "date", "datetime"):
                yaml_lines.append(f"{key}: {rendered.strip().strip('\"\'')}")
            else:
                yaml_lines.append(f"{key}: {_yaml_quote(rendered)}")
        tmpl_props = "\n".join(yaml_lines)

        content = _build_obsidian_note(
            title=title, deck_name=deck_name, obs_tags=obs_tags,
            mc_notes=self._mc_notes, cloze_notes=self._cloze_notes,
            tmpl_properties=tmpl_props, tmpl_content=tmpl_content,
        )

        try:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(content)
        except OSError as e:
            showWarning(_t("warn_write_failed", path=filepath, e=e))
            return

        self._cfg["obsidian_last_folder"] = folder_rel
        self._save_active_to_config()
        self._save_config()

        showInfo(_t("success_export", path=filepath))
        self.accept()


# ---------------------------------------------------------------------------
# Addon startup hook
# ---------------------------------------------------------------------------

def on_main_window_ready():
    """
    Called by Anki once the main window and collection are fully loaded.
    Safe to access mw.col here.
    """
    create_note_type()
    _register_menu()


def _register_menu():
    mw.form.menuTools.addAction("Import from NotebookLM").triggered.connect(
        _open_importer)
    mw.form.menuTools.addAction("Export to Obsidian").triggered.connect(
        _open_obsidian_exporter)


def _open_importer():
    ImporterDialog(parent=mw).exec()


def _open_obsidian_exporter():
    ObsidianExporterDialog(parent=mw).exec()


# Register our function to run after Anki finishes loading.
# gui_hooks.main_window_did_init fires once per session, after mw.col is ready.
gui_hooks.main_window_did_init.append(on_main_window_ready)
