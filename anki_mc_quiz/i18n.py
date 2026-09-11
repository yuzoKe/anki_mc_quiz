"""Strings de interface e seleção de idioma.

Módulo puro: não importa aqt nem Qt, para poder ser testado fora do Anki.
O `_lang` vive aqui e é lido via `get_lang()` — importar o valor congelaria-o
no momento do import, e a troca de idioma em runtime deixaria de ter efeito.
"""

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
        "lbl_preview_count": "Preview: {n}",
        "preview_ignored": "{n} ignorada(s) — {reason}:",
        "reason_no_choices": "não encontrei alternativas (A, B, C…)",
        "reason_no_answer": "falta a linha de resposta",
        "reason_no_question": "falta o enunciado",
        "success_oversized": (
            "\n{n} questão(ões) ignorada(s) por terem mais de 5 alternativas — "
            "o tipo de nota só tem campos A a E."),
        # Texto que aparece no próprio card, durante a revisão.
        "card_correct": "✓ Correto!",
        "card_wrong": "✗ Errado. A resposta certa é ",
        "card_banner": "✓ Resposta correta: ",
        "card_explanation_label": "Explicação",
        "warn_no_text": "Cole algum texto antes de importar.",
        "warn_notetype_failed": (
            "O addon Multiple Choice Quiz não conseguiu criar ou atualizar o "
            "seu tipo de nota:\n\n{e}\n\n"
            "O resto do Anki continua a funcionar normalmente."),
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
        "success_errors": " {errors} card(s) ignorado(s) por erro (conteúdo inválido).",
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
        # Obsidian export formatting
        "fmt_mc_heading": "## Questões (Múltipla Escolha)",
        "fmt_cloze_heading": "## Cloze",
        "fmt_answer": "Resposta",
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
            "  Answer: A\n"
            "  Explanation: Explanation text"
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
        "lbl_preview_count": "Preview: {n}",
        "preview_ignored": "{n} skipped — {reason}:",
        "reason_no_choices": "no choices found (A, B, C…)",
        "reason_no_answer": "the answer line is missing",
        "reason_no_question": "the question text is missing",
        "success_oversized": (
            "\n{n} question(s) skipped for having more than 5 choices — "
            "the note type only has fields A to E."),
        # Text shown on the card itself, during review.
        "card_correct": "✓ Correct!",
        "card_wrong": "✗ Wrong. The correct answer is ",
        "card_banner": "✓ Correct answer: ",
        "card_explanation_label": "Explanation",
        "warn_no_text": "Please paste some text before importing.",
        "warn_notetype_failed": (
            "The Multiple Choice Quiz addon could not create or update its "
            "note type:\n\n{e}\n\n"
            "The rest of Anki keeps working normally."),
        "warn_no_questions": (
            "No questions found.\n\n"
            "Make sure the text follows the expected format:\n"
            "1. Question text\n"
            "A) Choice A\n"
            "Answer: A\n"
            "Explanation: Explanation"
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
        "success_errors": " {errors} card(s) skipped due to errors (invalid content).",
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
        # Obsidian export formatting
        "fmt_mc_heading": "## Multiple Choice Questions",
        "fmt_cloze_heading": "## Cloze",
        "fmt_answer": "Answer",
    },
}


def _stored_lang():
    """Idioma que o utilizador escolheu no toggle, se já escolheu algum."""
    import json, os
    meta = os.path.join(os.path.dirname(os.path.abspath(__file__)), "meta.json")
    if os.path.isfile(meta):
        try:
            stored = json.loads(open(meta, encoding="utf-8-sig").read()).get(
                "config", {}).get("language")
            if stored in _STRINGS:
                return stored
        except Exception:
            pass
    return None


def _anki_lang():
    """Idioma do próprio Anki, quando corremos lá dentro.

    Import tardio de propósito: este módulo tem de continuar a carregar fora do
    Anki, e é isso que permite testá-lo. Um Anki em espanhol devolve None e cai
    no inglês — melhor omissão do que abrir em português para toda a gente.
    """
    candidates = []
    try:
        from anki.lang import current_lang
        candidates.append(current_lang)
    except Exception:
        pass
    try:
        from aqt import mw
        candidates.append(mw.pm.meta.get("defaultLang"))
    except Exception:
        pass
    # Corre no import do addon: nada aqui pode levantar, ou o Anki arranca sem
    # o addon. Daí não assumir sequer que o locale veio como string.
    for raw in candidates:
        try:
            code = str(raw or "").replace("-", "_").split("_")[0].lower()
        except Exception:
            continue
        if code in _STRINGS:
            return code
    return None


def _get_lang() -> str:
    return _stored_lang() or _anki_lang() or "en"


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


def get_lang() -> str:
    """Idioma ativo. Use isto em vez de importar `_lang` diretamente."""
    return _lang


# ---------------------------------------------------------------------------
# Marcadores de resposta/explicação — dados de língua usados pelo parser
# ---------------------------------------------------------------------------
# Escritos já normalizados: minúsculas e sem acentos, porque o parser compara
# contra `_normalize()`. Assim "Explicação", "Explicacao" e "EXPLICAÇÃO" casam
# todos com a mesma entrada, sem listar variantes.
#
# O parser NÃO depende desta tabela para funcionar: quando o marcador é
# desconhecido há um fallback genérico. A tabela é o caminho rápido e seguro.

ANSWER_MARKERS = {
    "pt": ("resposta", "gabarito", "alternativa correta"),
    "en": ("answer", "correct answer", "ans", "key", "solution", "correct"),
    "es": ("respuesta", "solucion"),
    "fr": ("reponse", "solution"),
    "de": ("antwort", "losung"),
    "it": ("risposta", "soluzione"),
}

EXPLANATION_MARKERS = {
    "pt": ("explicacao", "justificativa", "comentario"),
    "en": ("explanation", "rationale", "why", "feedback"),
    "es": ("explicacion", "justificacion"),
    "fr": ("explication", "justification"),
    "de": ("erklarung", "begrundung"),
    "it": ("spiegazione", "motivazione"),
}


def _flatten(table: dict) -> frozenset:
    return frozenset(m for variants in table.values() for m in variants)


ALL_ANSWER_MARKERS = _flatten(ANSWER_MARKERS)
ALL_EXPLANATION_MARKERS = _flatten(EXPLANATION_MARKERS)
