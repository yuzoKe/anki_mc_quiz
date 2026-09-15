"""Parsers e formatadores — o núcleo puro do addon.

Converte a saída do NotebookLM em cards (`parse_questions`, `parse_cloze`) e
os cards de volta em Markdown para o Obsidian (`_format_*`, `_build_obsidian_note`).

Módulo puro: só depende de `re` e das strings de `i18n`. Não importa aqt nem Qt,
para poder ser exercitado por testes fora do Anki.
"""

import re
import unicodedata

from .i18n import (
    _t, ALL_ANSWER_MARKERS, ALL_EXPLANATION_MARKERS,
)


# ---------------------------------------------------------------------------
# Question parser
# ---------------------------------------------------------------------------
# O texto que chega é escrito por um LLM, por isso o formato varia: numeração
# presente ou ausente, alternativas em "A)" / "A." / "(A)", marcadores a negrito
# ("**Resposta:**"), explicação opcional e em qualquer língua. Em vez de uma
# regex que tente descrever tudo isso de uma vez, o parser ancora-se na única
# estrutura que nunca falha — o BLOCO DE ALTERNATIVAS — e lê o resto à volta:
#
#     ### 1. <enunciado>       ← o parágrafo imediatamente antes do bloco
#     A) ...  B) ...           ← o bloco (letras em sequência, estilo homogéneo)
#     **Resposta:** B          ← a cauda, até ao enunciado seguinte
#     Explicação: ...
#
# Um bloco só é aceite se começar em A e cada letra seguinte for a sucessora
# exata, com o mesmo delimitador e a mesma caixa. É isso que impede uma linha
# de prosa como "A. Turing provou que…" de ser lida como alternativa: sem um
# "B." a seguir no mesmo estilo, a linha é devolvida ao enunciado.

_MAX_CHOICES = 10
_CHOICE_LETTERS = "ABCDEFGHIJ"

_CHOICE_RE = re.compile(
    r"^[ \t]*(?:([-*+])[ \t]+)?(\()?([A-Za-z])[ \t]*([\)\.\:\-–—])[ \t]+"
    r"(\S.*?)[ \t]*$")
_QNUM_RE = re.compile(r"^[ \t]*(?:#{1,6}[ \t]*)?(?:\*\*)?\d{1,3}[\.\)][ \t]+")
_MARKER_RE = re.compile(r"^[ \t]*([^\s:][^:]{0,29}?)[ \t]*:[ \t]*(.*?)[ \t]*$")
_HEADING_RE = re.compile(r"^[ \t]*#{1,6}[ \t]+")    # "### x", nunca "#include"
_MD_EDGE_RE = re.compile(r"^[\s>*_#\-]+|[\s*_]+$")
_BOLD_WRAP_RE = re.compile(r"^\*\*(.+?)\*\*$")


def _normalize(text: str) -> str:
    """Minúsculas e sem acentos, para comparar marcadores entre línguas."""
    decomposed = unicodedata.normalize("NFD", text)
    return "".join(c for c in decomposed
                   if unicodedata.category(c) != "Mn").lower().strip()


def _marker_word(raw: str) -> str:
    """Normaliza a etiqueta antes dos ':', descartando o markdown à volta.

    LLMs escrevem tanto `Resposta:` como `**Resposta correta:**` ou
    `> **Answer:**` — todas têm de chegar à tabela como a mesma palavra.
    """
    return _normalize(_MD_EDGE_RE.sub("", raw))


def _marker_value(raw: str) -> str:
    return _MD_EDGE_RE.sub("", raw).strip()


def _choice_style(m) -> tuple:
    """(bullet, parênteses, delimitador, caixa) — igual em todo o bloco."""
    return (m.group(1) is not None, bool(m.group(2)),
            m.group(4), m.group(3).isupper())


def _find_choice_runs(lines: list) -> list:
    """Blocos de alternativas válidos, cada um como [(idx, letra, texto), ...].

    Válido = começa em A/a, letras consecutivas sem saltos, estilo homogéneo e
    pelo menos duas alternativas.
    """
    runs = []
    i = 0
    while i < len(lines):
        m = _CHOICE_RE.match(lines[i])
        if not m or m.group(3).upper() != "A":
            i += 1
            continue
        style = _choice_style(m)
        run = [(i, "A", m.group(5))]
        j = i + 1
        while j < len(lines) and len(run) < _MAX_CHOICES:
            m2 = _CHOICE_RE.match(lines[j])
            if (not m2
                    or _choice_style(m2) != style
                    or m2.group(3).upper() != _CHOICE_LETTERS[len(run)]):
                break
            run.append((j, m2.group(3).upper(), m2.group(5)))
            j += 1
        if len(run) >= 2:
            runs.append(run)
            i = j
        else:
            i += 1          # "A. Turing…" sem "B." a seguir: era prosa
    return runs


def _known_marker(line: str):
    """('answer'|'explanation', valor) se a linha abre com marcador conhecido."""
    m = _MARKER_RE.match(line)
    if not m:
        return None
    word = _marker_word(m.group(1))
    if word in ALL_ANSWER_MARKERS:
        return ("answer", _marker_value(m.group(2)))
    if word in ALL_EXPLANATION_MARKERS:
        return ("explanation", _marker_value(m.group(2)))
    return None


def _generic_marker(line: str):
    """Marcador desconhecido mas plausível: uma palavra curta antes de ':'.

    Só é usado na cauda (depois das alternativas) e, no caso da resposta, só se
    o valor corresponder mesmo a uma alternativa do bloco — sem isso, um
    enunciado com 'Vitamina: D' ou 'Drive: C' viraria resposta.
    """
    m = _MARKER_RE.match(line)
    if not m:
        return None
    word = _marker_word(m.group(1))
    if not word or len(word) > 20 or not word.replace(" ", "").isalpha():
        return None
    return _marker_value(m.group(2))


def _answer_to_letter(value: str, run: list):
    """'B' → 'B'; '2' → 'B'; 'Mitocôndria' → a letra dessa alternativa."""
    letters = "".join(letter for _, letter, _ in run)
    v = value.strip().strip("().-–—").strip()
    if len(v) == 1 and v.isalpha() and v.upper() in letters:
        return v.upper()
    if v.isdigit():
        idx = int(v) - 1
        if 0 <= idx < len(letters):
            return letters[idx]
    # "B) Um ponteiro é…" — a letra seguida do texto da alternativa.
    lettered = re.match(r"^([A-Ja-j])[\).]\s", v)
    if lettered and lettered.group(1).upper() in letters:
        return lettered.group(1).upper()
    # Alguns modelos respondem com o texto completo da alternativa.
    target = _normalize(v)
    if target:
        for _, letter, choice_text in run:
            if _normalize(choice_text) == target:
                return letter
    return None


# ---------------------------------------------------------------------------
# Questões escritas numa só linha
# ---------------------------------------------------------------------------
# Os relatórios do NotebookLM (sobretudo o formato "Interativo") ignoram o
# "uma linha por campo" do prompt e colam tudo:
#
#     Enunciado… A) … B) … C) … Resposta: B Explicação: …
#
# `_explode_inline` devolve essa linha no formato multi-linha que o resto do
# parser já lê, terminada por `_INLINE_END`: numa linha única a explicação
# acaba no fim da linha, e o que vem depois já é outra coisa.
#
# A cadeia de alternativas é montada de trás para a frente a partir do marcador
# de resposta, e a resposta tem de apontar para uma alternativa dessa cadeia.
# É o que impede "I. … II. …", "V - F - V" ou "A) 15 A B) 10 B" de a partirem.

_INLINE_END = "\x00QEND\x00"
_INLINE_CHOICE_RE = re.compile(r"(?:(?<=\s)|^)(\()?([A-Ja-j])([\).])(?=\s)")
_INLINE_QNUM_RE = re.compile(r"(?:(?<=\s)|^)(\d{1,3})[\.\)]\s+(?=\S)")
_LEADING_NUMBER_RE = re.compile(r"^\s*(?:#{1,6}\s*)?(?:\*\*)?(\d{1,3})[\.\)]\s")
_ACCENT_CLASSES = {"a": "aáàâãä", "e": "eéèêë", "i": "iíìîï",
                   "o": "oóòôõö", "u": "uúùûü", "c": "cç", "n": "nñ"}


def _accent_insensitive(word: str) -> str:
    """'explicacao' → padrão que casa também 'Explicação'."""
    parts = []
    for ch in word:
        if ch == " ":
            parts.append(r"\s+")
        elif ch in _ACCENT_CLASSES:
            parts.append("[%s]" % _ACCENT_CLASSES[ch])
        else:
            parts.append(re.escape(ch))
    return "".join(parts)


def _inline_marker_re(markers):
    alternatives = "|".join(_accent_insensitive(m)
                            for m in sorted(markers, key=len, reverse=True))
    return re.compile(
        r"(?:(?<=\s)|^)(?:\*\*)?(?:%s)[ \t]*(?:\*\*)?[ \t]*:(?:\*\*)?"
        % alternatives, re.IGNORECASE)


_INLINE_ANSWER_RE = _inline_marker_re(ALL_ANSWER_MARKERS)
_INLINE_EXPL_RE = _inline_marker_re(ALL_EXPLANATION_MARKERS)


def _inline_style(m) -> tuple:
    return (bool(m.group(1)), m.group(3), m.group(2).isupper())


def _inline_chain(cands: list, end: int):
    """Cadeia A, B, C… que termina em `cands[end]`, ou None.

    Candidatos de outro estilo são texto (o "I." de "I. … II. …" no meio de
    alternativas "A)"); um do mesmo estilo com a letra errada parte a cadeia.
    """
    last = cands[end]
    style = _inline_style(last)
    idx = _CHOICE_LETTERS.find(last.group(2).upper())
    if idx < 1:
        return None
    chain = [last]
    for c in reversed(cands[:end]):
        if _inline_style(c) != style:
            continue
        if c.group(2).upper() != _CHOICE_LETTERS[idx - 1]:
            return None
        chain.append(c)
        idx -= 1
        if idx == 0:
            break
    if idx:
        return None
    chain.reverse()
    return chain


def _explode_at(line: str, cands: list, end: int, marker):
    chain = _inline_chain(cands, end)
    if not chain:
        return None
    bounds = [c.start() for c in chain[1:]] + [marker.start()]
    texts = [line[c.end():b].strip() for c, b in zip(chain, bounds)]
    if not all(texts):
        return None

    rest = line[marker.start():]
    size = marker.end() - marker.start()
    expl = _INLINE_EXPL_RE.search(rest, size)
    value = _marker_value(rest[size:(expl.start() if expl else None)])
    run = [(0, c.group(2).upper(), t) for c, t in zip(chain, texts)]
    if not _answer_to_letter(value, run):
        return None

    prefix = line[:chain[0].start()].strip()
    exploded = [prefix] if prefix else []
    exploded += [line[c.start():b].strip() for c, b in zip(chain, bounds)]
    exploded.append((rest[:expl.start()] if expl else rest).strip())
    following = None
    if expl:
        explanation = rest[expl.start():].strip()
        number = _LEADING_NUMBER_RE.match(prefix)
        if number:
            explanation, following = _split_next_numbered(
                explanation, int(number.group(1)) + 1)
        exploded.append(explanation)
    exploded.append(_INLINE_END)
    return exploded + (following or [])


def _split_next_numbered(text: str, expected: int) -> tuple:
    """Separa a questão N+1 colada no fim da explicação da questão N.

    Só para questões numeradas, e só com o número seguinte exato — é o que
    distingue "2. Qual…" do "*(p - 1) aponta" que vive dentro de uma explicação.
    """
    for m in _INLINE_QNUM_RE.finditer(text):
        if m.start() == 0 or int(m.group(1)) != expected:
            continue
        following = _explode_inline(text[m.start():].strip())
        if following:
            return text[:m.start()].strip(), following
    return text, None


def _explode_inline(line: str):
    """Linhas multi-linha equivalentes a uma questão inline, ou None."""
    cands = list(_INLINE_CHOICE_RE.finditer(line))
    if len(cands) < 2:
        return None
    for marker in _INLINE_ANSWER_RE.finditer(line):
        for end in range(len(cands) - 1, 0, -1):
            if cands[end].end() > marker.start():
                continue
            exploded = _explode_at(line, cands, end, marker)
            if exploded:
                return exploded
    return None


def _explode_inline_questions(lines: list) -> list:
    out = []
    for line in lines:
        out.extend(_explode_inline(line) or [line])
    return out


def _join_paragraphs(lines: list) -> str:
    """Linhas soltas viram um parágrafo; linhas em branco separam parágrafos."""
    paragraphs, current = [], []
    for ln in lines:
        if ln.strip():
            current.append(ln.strip())
        elif current:
            paragraphs.append(" ".join(current))
            current = []
    if current:
        paragraphs.append(" ".join(current))
    return "\n".join(paragraphs).strip()


def _clean_stem(text: str) -> str:
    """Tira do enunciado o que é notação e não conteúdo: '### ', '1. ', '**'."""
    text = _HEADING_RE.sub("", text.strip())
    text = _QNUM_RE.sub("", text)
    return _BOLD_WRAP_RE.sub(r"\1", text.strip()).strip()


_CODE_LINE_RE = re.compile(
    r"^[ \t]{2,}\S"
    r"|^\s*#\s*(?:include|define|import|pragma|ifn?def|if|endif)\b"
    r"|^\s*(?://|/\*|\*/)"
    r"|[;{}]\s*$"
    r"|^\s*[{}]"
    r"|\w\(.*\)"
    r"|^\s*(?:if|for|while|def|class|return|import|switch|case|else|elif)\b")
_CODE_BLOCK_OPENER_RE = re.compile(
    r"^\s+\S|^\s*(?:if|for|while|def|class|else|elif|try|except|with|case|"
    r"default)\b")


def _looks_like_code(line: str) -> bool:
    return bool(_PLACEHOLDER_RE.search(line) or _CODE_LINE_RE.search(line))


def _is_code_body(line: str) -> bool:
    """Linha de código solto que merece ir para dentro de um bloco ```.

    Mais estrita que `_looks_like_code`: uma frase que menciona `f(x)` e acaba
    em '.' ou '?' continua a ser prosa do enunciado.
    """
    if _PLACEHOLDER_RE.search(line) or not _CODE_LINE_RE.search(line):
        return False
    stripped = line.rstrip()
    if stripped.endswith((".", "?", "!")):
        return False
    if stripped.endswith(":"):
        return bool(_CODE_BLOCK_OPENER_RE.match(line))
    return True


def _is_boundary(line: str) -> bool:
    """Linha que já pertence à questão anterior."""
    return line == _INLINE_END or bool(_known_marker(line))


def _bridges_code(lines: list, i: int, floor: int) -> bool:
    """Linha em branco no meio de código colado sem ``` (depois do #include,
    entre duas funções) — não separa questões."""
    below = next((lines[k] for k in range(i + 1, len(lines))
                  if lines[k].strip()), "")
    above = next((lines[k] for k in range(i - 1, floor, -1)
                  if lines[k].strip()), "")
    if not above or _is_boundary(above) or not _looks_like_code(below):
        return False
    return _looks_like_code(above) or above.rstrip().endswith(":")


def _is_dense(lines: list, run_start: int, floor: int) -> bool:
    """Questões coladas umas às outras, sem linha em branco a separá-las.

    É o que os relatórios "Interativos" do NotebookLM produzem. Aí nenhuma linha
    em branco marca o início do enunciado, e é preciso outro critério para não
    arrastar títulos de secção ou o preâmbulo do relatório.
    """
    s = run_start - 1
    while s > floor and not _is_boundary(lines[s]):
        if not lines[s].strip() and not _bridges_code(lines, s, floor):
            return False
        s -= 1
    return True


def _stem_start(lines: list, run: list, floor: int) -> int:
    """Primeira linha do enunciado que precede um bloco de alternativas.

    Anda para trás até um marcador da questão anterior ou uma linha numerada
    (incluída: é onde o enunciado começa). Uma linha em branco também para,
    exceto no meio de código.

    Numa questão que veio de uma linha única e está colada às outras (texto
    denso), só continua a subir por código e por introduções terminadas em ':'
    ("Considere o trecho em C:") — é isso que deixa de fora "Atividades
    Avaliativas - Parte II" e o preâmbulo do relatório. Numa questão multi-linha
    vale o parágrafo inteiro: "1. Quem formulou…" / "A. Turing provou…" / "Esta
    ideia…" é um enunciado só.
    """
    run_start, run_end = run[0][0], run[-1][0]
    inline = _INLINE_END in lines[run_end + 1:run_end + 4]
    dense = inline and _is_dense(lines, run_start, floor)
    start = run_start
    s = run_start - 1
    while s > floor:
        line = lines[s]
        if _is_boundary(line):
            break
        if not line.strip():
            if not _bridges_code(lines, s, floor):
                break
            s -= 1
            continue
        numbered = bool(_QNUM_RE.match(line) or _HEADING_RE.match(line))
        if (dense and start != run_start and not numbered
                and not _looks_like_code(line)
                and not line.rstrip().endswith(":")):
            break
        start = s
        if numbered:
            break
        s -= 1
    return start


def _fence_loose_code(lines: list) -> list:
    """Envolve em ``` o código que o LLM colou solto no enunciado.

    Sem isto as linhas colapsam num parágrafo só no card (o HTML junta o
    espaço em branco) e o highlight.js nunca as vê.
    """
    out, block = [], []

    def flush():
        while block and not block[-1].strip():
            block.pop()
        if block:
            out.append("```\n" + "\n".join(block) + "\n```")
            block.clear()

    for line in lines:
        if _is_code_body(line):
            block.append(line.rstrip())
        elif block and not line.strip():
            block.append("")
        else:
            flush()
            out.append(line)
    flush()
    return out


def _read_tail(tail: list, run: list) -> tuple:
    """Extrai (resposta, explicação) da região entre o bloco e o enunciado
    seguinte. A explicação acumula parágrafos até dois brancos seguidos ou um
    novo marcador conhecido."""
    answer, explanation, blanks, collecting = None, [], 0, False
    for line in tail:
        if line == _INLINE_END:
            break
        if answer is None:
            hit = _known_marker(line)
            value = hit[1] if hit and hit[0] == "answer" else None
            if value is None:
                value = _generic_marker(line)
            letter = _answer_to_letter(value, run) if value else None
            if letter:
                answer = letter
            continue
        if not line.strip():
            blanks += 1
            if collecting and blanks >= 2:
                break
            if collecting:
                explanation.append("")
            continue
        blanks = 0
        if not collecting:
            hit = _known_marker(line)
            if hit and hit[0] == "explanation":
                collecting = True
                explanation.append(hit[1])
                continue
            generic = _generic_marker(line)
            if generic is not None:
                collecting = True
                explanation.append(generic)
            continue
        if _known_marker(line):
            break
        explanation.append(line)
    return answer, explanation


def _parse_structured(lines: list, blocks: list) -> tuple:
    """Devolve (questões, rejeitados) a partir das linhas já protegidas."""
    runs = _find_choice_runs(lines)
    if not runs:
        return [], [{"reason": "no_choices",
                     "excerpt": _join_paragraphs(lines)[:200]}]

    starts = []
    for k, run in enumerate(runs):
        floor = runs[k - 1][-1][0] if k else -1
        starts.append(_stem_start(lines, run, floor))

    questions, rejected = [], []
    for k, run in enumerate(runs):
        stem_lines = lines[starts[k]:run[0][0]]
        tail_end = starts[k + 1] if k + 1 < len(runs) else len(lines)
        tail = lines[run[-1][0] + 1:tail_end]
        answer, explanation = _read_tail(tail, run)

        question = _clean_stem("\n".join(_fence_loose_code(stem_lines)))
        question = _restore_code_blocks(question, blocks)
        if not question or not answer:
            shown = [l for l in stem_lines + tail if l != _INLINE_END]
            rejected.append({
                "reason": "no_answer" if question else "no_question",
                "excerpt": _restore_code_blocks(
                    "\n".join(shown).strip()[:200], blocks),
            })
            continue

        entry = {"question": question, "answer": answer,
                 "explanation": _restore_code_blocks(
                     _join_paragraphs(explanation), blocks)}
        for _, letter, choice_text in run:
            entry[letter] = _restore_code_blocks(choice_text.strip(), blocks)
        questions.append(entry)

    return questions, rejected


def parse_questions_report(text: str) -> tuple:
    """Como `parse_questions`, mas devolve também os blocos que ficaram de fora.

    Cada rejeitado é {'reason': str, 'excerpt': str} — é isto que permite ao
    importador dizer *o que* correu mal em vez de mostrar uma preview vazia.
    """
    text = text.replace("\r\n", "\n").replace("\r", "\n").strip()
    if not text:
        return [], []
    protected, blocks = _protect_code_blocks(text)
    return _parse_structured(
        _explode_inline_questions(protected.split("\n")), blocks)


def parse_questions(text: str) -> list:
    """Converte a saída do NotebookLM numa lista de questões.

    Cada questão é um dict com `question`, `answer`, `explanation` e uma chave
    por alternativa (`A`, `B`, … até `J`).
    """
    return parse_questions_report(text)[0]


_CLOZE_MARKER_FIX_RE = re.compile(r"\{\{[ \t]*(c\d+)[ \t]*::[ \t]*")


def _normalize_cloze_markers(text: str) -> str:
    """`{{c1 :: x}}` → `{{c1::x}}`. O Anki só reconhece a lacuna com o `::`
    colado ao `cN` (sem espaço antes); com espaço, a nota entrava sem cloze."""
    return _CLOZE_MARKER_FIX_RE.sub(r"{{\1::", text)


def _cloze_bridges_code(lines: list, i: int) -> bool:
    """A próxima linha não vazia ainda é código (e não um card novo)?

    Cobre os dois brancos que aparecem no relatório do NotebookLM: o que separa
    o `{{c}}` do bloco de código colado logo a seguir, e os que o próprio código
    traz (depois do `#include`, dentro de um struct). Um `{{c}}` novo ou uma
    linha de prosa/título não são código — aí o branco fecha o card à mesma.
    """
    below = next((lines[k] for k in range(i + 1, len(lines))
                  if lines[k].strip()), "")
    return "{{c" not in below and _looks_like_code(below)


def _is_cloze_continuation(current: str) -> bool:
    """A frase do card atual foi cortada a meio e a próxima linha continua-a?

    Só quando o card ainda não terminou em pontuação final e ainda não começou
    código. É o que reconstitui `...de um de seus` + `membros.` sem arrastar um
    título — títulos vêm depois de um card que já fechou (ponto final) ou de uma
    linha em branco, e a linha em branco fecha o card por `_cloze_bridges_code`.
    """
    return not current.rstrip().endswith((".", "!", "?", ":", ";"))


def _parse_cloze_lines(lines: list) -> list:
    """Uma frase `{{c}}` por card, robusto ao relatório real do NotebookLM:

    - o código colado SEM ``` a seguir a um card vai para dentro dele, entre ```,
      mesmo separado por uma linha em branco e mesmo que o código traga os seus
      próprios brancos (`_cloze_bridges_code`);
    - uma frase de card quebrada em várias linhas volta a juntar-se
      (`_is_cloze_continuation`);
    - um `{{c}}` novo, ou prosa/título, fecham o card — assim títulos e preâmbulo
      não entram;
    - um bloco ```...``` já protegido chega como placeholder de 1 linha:
      restaura-se sozinho como fence, por isso entra no card sem ``` extra.
    """
    cards, current, code = [], None, []

    def close_code():
        """Solda o código solto pendente ao card em curso, entre ```."""
        nonlocal current, code
        while code and not code[-1].strip():
            code.pop()
        if code:
            current += "\n```\n" + "\n".join(code) + "\n```"
        code = []

    def flush():
        nonlocal current
        close_code()
        if current is not None:
            cards.append(current)
        current = None

    for i, line in enumerate(lines):
        stripped = line.strip()
        if "{{c" in stripped:
            flush()
            if stripped.count("{{c") > 1:
                parts = re.split(r"(?<=\.)\s+(?=\{\{c)", stripped)
                cards.extend(p.strip() for p in parts[:-1] if "{{c" in p)
                stripped = parts[-1].strip()
            current = stripped
        elif current is None:
            continue                       # preâmbulo/título antes do 1.º card
        elif _PLACEHOLDER_RE.search(stripped):
            close_code()
            current += "\n" + stripped     # ``` já protegido: entra tal e qual
        elif _is_code_body(line):
            code.append(line.rstrip())
        elif not stripped:
            if _cloze_bridges_code(lines, i):
                if code:
                    code.append("")        # branco no meio do código: não fecha
                # branco antes do código: não fecha nem abre com linha vazia
            else:
                flush()
        elif not code and _is_cloze_continuation(current):
            current += " " + stripped      # cauda de frase quebrada em 2 linhas
        else:
            flush()
    flush()
    return cards


def parse_cloze(text: str) -> list:
    """Returns individual cloze sentences containing at least one {{cN::}} marker.

    Handles these layouts:
    - One card per line (standard NotebookLM output)
    - Multiple sentences concatenated in a paragraph (split on '. {{c' boundaries)
    - A card followed by loose (unfenced) code lines, which get attached to it —
      even when a blank line sits between them and even when the code carries its
      own blank lines (#include then a struct)
    - A card whose sentence is hard-wrapped across two lines
    - A card followed by a fenced ```...``` block
    - Markers written with spaces (``{{c1 :: x}}``), normalized to ``{{c1::x}}``
    """
    # Shield fenced code blocks so a multi-line block stays on one logical card.
    text, blocks = _protect_code_blocks(text)
    text = _normalize_cloze_markers(text)
    results = _parse_cloze_lines(text.split("\n"))
    return [_restore_code_blocks(r, blocks) for r in results]


def _escape_search(text: str) -> str:
    """Escape characters that are special to Anki's search syntax.

    Without this, a question/card containing a double quote (common in
    NotebookLM output, e.g. Qual o significado de "API"?) breaks the quoted
    search term and raises anki.errors.SearchError. Backslash must be escaped
    first so the escapes we add are not doubled.
    """
    return (
        text.replace("\\", "\\\\")
        .replace('"', '\\"')
        .replace("*", "\\*")
        .replace("_", "\\_")
    )


def _html_escape(text: str) -> str:
    """Escape HTML-special characters so code snippets survive intact.

    Java/C++ answers contain characters like <, > and & (e.g. vector<int>,
    a < b, System&). Anki renders card fields as HTML, so unescaped angle
    brackets are swallowed as unknown tags. Ampersand must be escaped first.
    """
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


# ---------------------------------------------------------------------------
# Code blocks (Markdown fenced ``` / inline `code`) → highlighted HTML
# ---------------------------------------------------------------------------
# The parsers below work line-by-line, so a multi-line fenced code block would
# be torn apart (its inner newlines look like question/card boundaries). To
# avoid that, _protect_code_blocks() replaces every ```...``` block with a
# single-line, regex-inert placeholder (NUL-delimited, no A)/Resposta:/digit.
# patterns) before parsing, and _restore_code_blocks() puts them back on the
# extracted field text afterwards. _render_content() then turns the restored
# fences into <pre><code> markup that highlight.js colors on the card.

_FENCE_RE = re.compile(r"```([A-Za-z0-9+#._-]*)[ \t]*\n?(.*?)```", re.DOTALL)
_INLINE_CODE_RE = re.compile(r"`([^`\n]+)`")
_PLACEHOLDER_RE = re.compile("\x00CB(\\d+)\x00")

# Inline base styling so a code block still looks like a dark code box even on
# note types whose template does NOT load highlight.js (e.g. the native Cloze
# type). On the Multiple Choice cards, highlight.js + CARD_CSS layer colors and
# line numbers on top of this.
_CODE_PRE_STYLE = (
    "background:#282c34;color:#abb2bf;padding:12px 14px;border-radius:8px;"
    "overflow-x:auto;font-family:'JetBrains Mono',Consolas,'Courier New',monospace;"
    "font-size:13.5px;line-height:1.5;white-space:pre;tab-size:4;margin:12px 0;"
    "text-align:left"
)


def _protect_code_blocks(text: str):
    """Replace ```...``` blocks with inert single-line placeholders.

    Returns (protected_text, blocks) where blocks[i] is the original fenced
    block (including its backticks). An unclosed fence is left untouched.
    """
    blocks = []

    def _stash(m):
        blocks.append(m.group(0))
        return "\x00CB%d\x00" % (len(blocks) - 1)

    return _FENCE_RE.sub(_stash, text), blocks


def _restore_code_blocks(text: str, blocks: list) -> str:
    """Reverse _protect_code_blocks() on a (possibly sliced) piece of text."""
    if not blocks:
        return text

    def _unstash(m):
        idx = int(m.group(1))
        return blocks[idx] if 0 <= idx < len(blocks) else m.group(0)

    return _PLACEHOLDER_RE.sub(_unstash, text)


def _render_inline(text: str) -> str:
    """HTML-escape text, turning `inline code` spans into <code> elements."""
    parts = []
    last = 0
    for m in _INLINE_CODE_RE.finditer(text):
        parts.append(_html_escape(text[last:m.start()]))
        parts.append(
            '<code class="amcq-inline">%s</code>' % _html_escape(m.group(1))
        )
        last = m.end()
    parts.append(_html_escape(text[last:]))
    return "".join(parts)


def _render_content(text: str) -> str:
    """Convert a field's text to Anki-ready HTML.

    Fenced ```lang code``` blocks become <pre><code class="language-lang"> so
    highlight.js can color them; inline `code` becomes <code>; everything else
    is HTML-escaped exactly as _html_escape would do. Safe to call on plain
    text with no code (it just escapes).
    """
    out = []
    last = 0
    for m in _FENCE_RE.finditer(text):
        out.append(_render_inline(text[last:m.start()]))
        lang = m.group(1).strip().lower()
        code = m.group(2).strip("\n")
        cls = ' class="language-%s"' % lang if lang else ""
        out.append(
            '<pre class="amcq-code" style="%s"><code%s>%s</code></pre>'
            % (_CODE_PRE_STYLE, cls, _html_escape(code))
        )
        last = m.end()
    out.append(_render_inline(text[last:]))
    return "".join(out)


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
    body = f"{_t('fmt_mc_heading')}\n\n"
    for i, q in enumerate(mc_notes, 1):
        body += f"{i}. {q.get('question', '')}\n"
        for letter in "ABCDE":
            if q.get(letter):
                body += f"   {letter}) {q[letter]}\n"
        ans = q.get("answer", "")
        expl = q.get("explanation", "")
        body += f"   **{_t('fmt_answer')}: {ans}**"
        body += f" — {expl}\n\n" if expl else "\n\n"
    return body


def _format_cloze_cards(cloze_notes: list) -> str:
    body = f"{_t('fmt_cloze_heading')}\n\n"
    for c in cloze_notes:
        body += f"- {c}\n"
    return body


def _format_mc_callouts(mc_notes: list) -> str:
    body = f"{_t('fmt_mc_heading')}\n\n"
    for i, q in enumerate(mc_notes, 1):
        body += f"> [!question] {i}. {q.get('question', '')}\n"
        for letter in "ABCDE":
            if q.get(letter):
                body += f"> {letter}) {q[letter]}\n"
        ans = q.get("answer", "")
        expl = q.get("explanation", "")
        body += f">\n> **{_t('fmt_answer')}: {ans}**"
        body += f" — {expl}\n\n" if expl else "\n\n"
    return body


def _format_cloze_callouts(cloze_notes: list) -> str:
    body = f"{_t('fmt_cloze_heading')}\n\n"
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

