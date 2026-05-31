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
    QTextEdit, QComboBox, QPushButton, QTabWidget, QWidget, Qt
)
import re
from aqt import mw, gui_hooks


# ---------------------------------------------------------------------------
# Note type definition
# ---------------------------------------------------------------------------

# This is the name that will appear in Anki's note type list.
NOTE_TYPE_NAME = "Multiple Choice Quiz"

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

    # Strip leading all-caps report title (lines with no ASCII lowercase letters)
    text = re.sub(r'^(?:[^\na-z]*\n)+\s*', '', text.strip())

    questions = []

    # Match the full tail of each question as a single unit so the explanation
    # boundary is captured by the regex rather than a fragile period heuristic.
    tail_re = re.compile(
        r'Resposta:\s*([A-Ea-e])\s+Explica[çc][aã]o:\s*([^.]+\.)',
        re.IGNORECASE
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
            raw_question = text[tail_matches[i - 1].end():choices_start].strip()

        # Strip leading question numbers like "1. " or "1) "
        raw_question = re.sub(r'^\d+[\.\)]\s*', '', raw_question)

        if raw_question and answer:
            q = {"question": raw_question, "answer": answer,
                 "explanation": explanation}
            q.update(choices)
            questions.append(q)

    return questions


def parse_cloze(text: str) -> list:
    """Returns non-empty lines that contain at least one {{cN::}} cloze marker."""
    return [
        line.strip()
        for line in text.splitlines()
        if line.strip() and "{{c" in line
    ]


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
        self.setWindowTitle("Import from NotebookLM")
        self.setMinimumWidth(560)
        self.setMinimumHeight(480)
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(20, 20, 20, 20)

        # ── Tabs ──────────────────────────────────────────────────────────
        self.tabs = QTabWidget()
        self.tabs.addTab(self._build_mc_tab(), "Multiple Choice")
        self.tabs.addTab(self._build_cloze_tab(), "Cloze")
        layout.addWidget(self.tabs)

        # ── Deck selector (shared) ────────────────────────────────────────
        deck_row = QHBoxLayout()
        deck_label = QLabel("Destination deck:")
        deck_label.setFixedWidth(120)
        self.deck_combo = QComboBox()
        for name in sorted(mw.col.decks.all_names()):
            self.deck_combo.addItem(name)
        deck_row.addWidget(deck_label)
        deck_row.addWidget(self.deck_combo, stretch=1)
        layout.addLayout(deck_row)

        # ── Buttons (shared) ──────────────────────────────────────────────
        btn_row = QHBoxLayout()
        btn_row.addStretch()
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setFixedWidth(100)
        cancel_btn.clicked.connect(self.reject)
        import_btn = QPushButton("Import →")
        import_btn.setFixedWidth(100)
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
        instructions = QLabel(
            "Paste the quiz text generated by NotebookLM below.\n"
            "Each question must follow the format:\n"
            "  1. Question text\n"
            "  A) Choice A   B) Choice B\n"
            "  Resposta: A\n"
            "  Explicação: Explanation text"
        )
        instructions.setWordWrap(True)
        instructions.setStyleSheet(self._INSTRUCTION_STYLE)
        layout.addWidget(instructions)
        self.mc_input = QTextEdit()
        self.mc_input.setPlaceholderText("Paste your NotebookLM quiz text here...")
        layout.addWidget(self.mc_input)
        return tab

    def _build_cloze_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(10)
        layout.setContentsMargins(0, 12, 0, 0)
        instructions = QLabel(
            "Paste the Cloze text generated by NotebookLM below.\n"
            "One card per line. Format:\n"
            "  {{c1::term}} is/are [context]."
        )
        instructions.setWordWrap(True)
        instructions.setStyleSheet(self._INSTRUCTION_STYLE)
        layout.addWidget(instructions)
        self.cloze_input = QTextEdit()
        self.cloze_input.setPlaceholderText("Paste your NotebookLM Cloze text here...")
        layout.addWidget(self.cloze_input)
        return tab

    def _on_import(self):
        if self.tabs.currentIndex() == 0:
            self._import_mc()
        else:
            self._import_cloze()

    def _import_mc(self):
        from aqt.utils import showWarning, showInfo
        raw_text = self.mc_input.toPlainText().strip()
        if not raw_text:
            showWarning("Please paste some text before importing.")
            return

        questions = parse_questions(raw_text)
        if not questions:
            showWarning(
                "No questions found.\n\n"
                "Make sure the text follows the expected format:\n"
                "1. Question text\n"
                "A) Choice A\n"
                "Resposta: A\n"
                "Explicação: Explanation"
            )
            return

        deck_name = self.deck_combo.currentText()
        deck_id = mw.col.decks.id(deck_name)
        mw.col.decks.select(deck_id)

        model = mw.col.models.by_name(NOTE_TYPE_NAME)
        if not model:
            showWarning("Multiple Choice Quiz note type not found. Please restart Anki.")
            return

        created = 0
        for q in questions:
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
            mw.col.add_note(note, deck_id)
            created += 1

        mw.reset()
        showInfo(f"{created} card(s) added to '{deck_name}'.")
        self.accept()

    def _import_cloze(self):
        from aqt.utils import showWarning, showInfo
        raw_text = self.cloze_input.toPlainText().strip()
        if not raw_text:
            showWarning("Please paste some text before importing.")
            return

        cards = parse_cloze(raw_text)
        if not cards:
            showWarning(
                "No Cloze cards found.\n\n"
                "Each line must contain {{c1::term}}."
            )
            return

        # Find the native Cloze note type (model type == 1)
        cloze_model = next(
            (m for m in mw.col.models.all() if m["type"] == 1), None
        )
        if not cloze_model:
            showWarning("Native Cloze note type not found in your collection.")
            return

        deck_name = self.deck_combo.currentText()
        deck_id = mw.col.decks.id(deck_name)
        mw.col.decks.select(deck_id)

        created = 0
        for card_text in cards:
            note = mw.col.new_note(cloze_model)
            note.fields[0] = card_text
            note.note_type()["did"] = deck_id
            mw.col.add_note(note, deck_id)
            created += 1

        mw.reset()
        showInfo(f"{created} Cloze card(s) added to '{deck_name}'.")
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
    """
    Adds 'Import from NotebookLM' under Anki's Tools menu.
    Clicking it opens the ImporterDialog.
    """
    action = mw.form.menuTools.addAction("Import from NotebookLM")
    action.triggered.connect(_open_importer)


def _open_importer():
    """Opens the importer dialog."""
    dialog = ImporterDialog(parent=mw)
    dialog.exec()


# Register our function to run after Anki finishes loading.
# gui_hooks.main_window_did_init fires once per session, after mw.col is ready.
gui_hooks.main_window_did_init.append(on_main_window_ready)
