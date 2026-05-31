- Addon para o Anki chamado anki_mc_quiz
- Linguagem: Python, com templates em HTML/CSS/JS embutidos como strings
- O arquivo principal é anki_mc_quiz/__init__.py
- Não usar pip install — o Anki tem Python embutido
- Avisos do Pylance sobre aqt, aqt.qt, aqt.utils são esperados e podem ser ignorados
- Para testar: copiar __init__.py para %APPDATA%\Anki2\addons21\anki_mc_quiz\ e reiniciar o Anki

Funcionalidades já implementadas:
1. Note type "Multiple Choice Quiz" criado automaticamente no primeiro uso
2. Campos: Question, A, B, C, D, E, Answer, Explanation
3. Template front: múltipla escolha interativa com Fisher-Yates shuffle, IIFE para isolamento de escopo, visual labels A/B/C/D em ordem
4. Template back: mostra alternativas com a correta destacada + banner verde + explicação
5. TEMPLATE_VERSION para sync automático quando o usuário atualiza o addon
6. Menu Tools > Import from NotebookLM: janela Qt com textarea, deck selector, botão importar
7. parse_questions: parser que extrai questões do texto gerado pelo NotebookLM

Problema atual na parse_questions:
- O NotebookLM gera texto sem numeração, tudo numa linha só
- Formato: "Enunciado A) op1 B) op2 Resposta: A Explicação: texto. Enunciado A) op1..."
- O parser atual não separa corretamente as questões nesse formato
- Precisa usar "Resposta:" como âncora e "A)" como início das alternativas

Contexto do projeto:
- Desenvolvido durante o Clube da Programação da Laura Dubugras (4 semanas)
- Projeto nasceu do zero durante o clube
- Objetivo: automatizar o fluxo de estudo da faculdade (UNIVESP - Engenharia de Computação)

Fluxo de estudo planejado:
- Semanas 1-7 (aprender): Material da aula → NotebookLM (prompt Cloze) → importar pro Anki → revisar com Cloze
- Semana 8/9 (testar): Material acumulado → NotebookLM (prompt MC) → importar pro Anki → revisar com múltipla escolha

Próximas funcionalidades a implementar:
1. Importador Cloze: segunda aba na janela de importação, cola texto no formato {{c1::termo}} e cria cards no note type Cloze nativo do Anki
2. A janela de importação deve ter duas abas: "Multiple Choice" e "Cloze"

Prompts do NotebookLM já definidos:

PROMPT MÚLTIPLA ESCOLHA:
Crie um Relatório Personalizado transformando todas as atividades avaliativas das fontes em questões de múltipla escolha. Siga exatamente este formato para cada questão:
1. [Enunciado]
A) [Alternativa A]
...
Resposta: A
Explicação: [Uma frase]
Regras: numeração sequencial, letras maiúsculas, uma linha em branco entre questões, sem títulos ou gabarito separado.

PROMPT CLOZE:
Crie um Relatório Personalizado transformando todos os conceitos das fontes em flashcards no formato Cloze.
Formato: {{c1::termo}} é/são [contexto].
Regras: uma linha por card, apenas {{c1::}}, sem numeração, sem duplicatas.

Repositório: https://github.com/yuzoKe/anki_mc_quiz