# -*- coding: utf-8 -*-
"""Corpus dourado do parser.

Corre sem o Anki instalado:  python -m unittest discover -s tests

Os testes descrevem o comportamento CORRETO, não o atual. Os que falham marcam
exatamente o que a reescrita do parser tem de resolver; os que passam são a rede
de segurança que ela não pode partir.
"""

import re
import unittest

from _addon import ROOT, fixture, i18n, parsers


def parse(name):
    return parsers.parse_questions(fixture(name))


class FormatosEstabelecidos(unittest.TestCase):
    """Já funcionam hoje. Se algum destes ficar vermelho, houve regressão."""

    def test_pt_numerado(self):
        qs = parse("mc_pt_numerado")
        self.assertEqual(len(qs), 3)
        self.assertEqual(qs[0]["question"],
                         "Qual protocolo traduz nomes de domínio em endereços IP?")
        self.assertEqual(qs[0]["B"], "DNS")
        self.assertEqual(qs[0]["answer"], "B")
        self.assertIn("endereços IP numéricos", qs[0]["explanation"])

    def test_en_numbered(self):
        qs = parse("mc_en_numbered")
        self.assertEqual(len(qs), 2)
        self.assertEqual(qs[1]["answer"], "C")
        self.assertEqual(qs[1]["C"], "O(log n)")

    def test_preambulo_do_relatorio_e_descartado(self):
        qs = parse("mc_pt_preambulo")
        self.assertEqual(len(qs), 2)
        self.assertNotIn("Relatório Personalizado", qs[0]["question"])
        self.assertNotIn("Fontes:", qs[0]["question"])

    def test_duas_alternativas(self):
        qs = parse("mc_pt_duas_alternativas")
        self.assertEqual(len(qs), 1)
        self.assertEqual(qs[0]["A"], "Verdadeiro")
        self.assertEqual(qs[0]["B"], "Falso")
        self.assertNotIn("C", qs[0])

    def test_bloco_de_codigo_sobrevive_ao_parse(self):
        qs = parse("mc_pt_codigo")
        self.assertEqual(len(qs), 1)
        self.assertIn("```", qs[0]["question"])
        self.assertIn("sum(xs) / len(xs)", qs[0]["question"])

    def test_a_dentro_do_enunciado_nao_desalinha(self):
        qs = parse("mc_pt_a_no_enunciado")
        self.assertEqual(len(qs), 1)
        self.assertIn("rótulo num formulário", qs[0]["question"])
        self.assertEqual(qs[0]["A"], "Rótulos não podem conter parênteses")
        self.assertEqual(qs[0]["D"], "Rótulos são opcionais")


class Idiomas(unittest.TestCase):
    """O parser tem de reconhecer os marcadores naturais de cada língua."""

    def _verifica(self, nome, resposta_q1):
        qs = parse(nome)
        self.assertEqual(len(qs), 5, "esperadas 5 questões em %s" % nome)
        self.assertEqual(qs[0]["answer"], resposta_q1)
        for i, q in enumerate(qs, 1):
            self.assertTrue(q["question"].strip(), "q%d sem enunciado" % i)
            self.assertTrue(q["explanation"].strip(), "q%d sem explicação" % i)
            self.assertIn(q["answer"], "ABCDE")

    def test_espanhol(self):   # Respuesta / Explicación
        self._verifica("mc_es", "B")

    def test_frances(self):    # Réponse / Explication
        self._verifica("mc_fr", "B")

    def test_alemao(self):     # Antwort / Erklärung
        self._verifica("mc_de", "C")

    def test_italiano(self):   # Risposta / Spiegazione
        self._verifica("mc_it", "B")


class CasosLimite(unittest.TestCase):

    def test_explicacao_ausente_nao_descarta_a_questao(self):
        qs = parse("mc_pt_sem_explicacao")
        self.assertEqual(len(qs), 2)
        self.assertEqual(qs[0]["answer"], "B")
        self.assertEqual(qs[0]["explanation"], "")
        self.assertEqual(qs[1]["answer"], "A")

    def test_explicacao_multilinha_nao_e_truncada(self):
        qs = parse("mc_pt_explicacao_multilinha")
        self.assertEqual(len(qs), 2)
        expl = qs[0]["explanation"]
        self.assertIn("Atomicidade", expl)
        self.assertIn("Durabilidade", expl)
        self.assertIn("não deixa qualquer efeito", expl)

    def test_alternativas_com_ponto(self):
        qs = parse("mc_pt_alt_pontos")
        self.assertEqual(len(qs), 1)
        self.assertEqual(qs[0]["A"], "Byte")
        self.assertEqual(qs[0]["B"], "Bit")
        self.assertEqual(qs[0]["D"], "Nibble")
        self.assertEqual(qs[0]["answer"], "B")

    def test_alternativas_entre_parenteses(self):
        qs = parse("mc_pt_alt_parenteses")
        self.assertEqual(len(qs), 1)
        self.assertEqual(qs[0]["A"], "Quicksort")
        self.assertEqual(qs[0]["B"], "Bubble sort otimizado")
        self.assertEqual(qs[0]["C"], "Merge sort")
        self.assertEqual(qs[0]["D"], "Heapsort")

    def test_mais_de_cinco_alternativas_nao_sao_engolidas(self):
        qs = parse("mc_pt_oito_alternativas")
        self.assertEqual(len(qs), 1)
        self.assertEqual(qs[0]["E"], "Oracle")
        self.assertEqual(qs[0]["F"], "SQL Server")
        self.assertEqual(qs[0]["H"], "DB2")
        self.assertEqual(qs[0]["answer"], "C")

    def test_texto_sem_questoes_devolve_lista_vazia(self):
        self.assertEqual(parsers.parse_questions(""), [])
        self.assertEqual(parsers.parse_questions("Só um parágrafo solto."), [])


class FormatosDoEcossistema(unittest.TestCase):
    """Formatos que o estudante pode trazer de fora do NotebookLM."""

    def test_aiken_do_moodle(self):
        qs = parse("mc_aiken")
        self.assertEqual(len(qs), 2)
        self.assertEqual(qs[0]["question"],
                         "Qual organela é responsável pela respiração celular?")
        self.assertEqual(qs[0]["answer"], "B")
        self.assertEqual(qs[0]["explanation"], "")
        self.assertEqual(qs[1]["answer"], "C")

    def test_markdown_de_llm_com_marcador_a_negrito(self):
        qs = parse("mc_llm_markdown")
        self.assertEqual(len(qs), 2)
        self.assertEqual(qs[0]["question"], "Qual é a capital da França?")
        self.assertEqual(qs[0]["answer"], "C")
        self.assertIn("maior cidade da França", qs[0]["explanation"])
        self.assertEqual(qs[1]["answer"], "B")

    def test_resposta_dada_pelo_texto_da_alternativa(self):
        qs = parse("mc_resposta_por_texto")
        self.assertEqual(len(qs), 1)
        self.assertEqual(qs[0]["answer"], "B")


class ArmadilhasDeFormato(unittest.TestCase):

    def test_prosa_iniciada_por_letra_nao_vira_alternativa(self):
        """'A. Turing provou…' sem um 'B.' a seguir é prosa, não alternativa."""
        qs = parse("mc_prosa_com_inicial")
        self.assertEqual(len(qs), 1)
        self.assertIn("A. Turing provou", qs[0]["question"])
        self.assertEqual(qs[0]["A"], "Alan Turing")
        self.assertEqual(qs[0]["D"], "Kurt Gödel")

    def test_explicacao_de_dois_paragrafos_fica_inteira(self):
        qs = parse("mc_explicacao_dois_paragrafos")
        self.assertEqual(len(qs), 2)
        expl = qs[0]["explanation"]
        self.assertIn("retransmite o que se perde", expl)
        self.assertIn("envia e esquece", expl)
        self.assertEqual(qs[1]["question"], "Que porta o HTTPS usa por omissão?")
        self.assertEqual(qs[1]["explanation"], "O HTTPS atende na porta 443.")


class Diagnostico(unittest.TestCase):
    """O relatório é o que substitui a preview vazia por uma explicação."""

    def test_texto_sem_alternativas_e_reportado(self):
        qs, rejeitados = parsers.parse_questions_report(
            "Um parágrafo qualquer sem questões nenhumas.")
        self.assertEqual(qs, [])
        self.assertEqual(len(rejeitados), 1)
        self.assertEqual(rejeitados[0]["reason"], "no_choices")

    def test_questao_sem_resposta_e_reportada(self):
        texto = ("1. Questão completa?\nA) Um\nB) Dois\nResposta: A\n"
                 "Explicação: porque sim.\n\n"
                 "2. Questão a que falta a linha de resposta?\nA) Um\nB) Dois\n")
        qs, rejeitados = parsers.parse_questions_report(texto)
        self.assertEqual(len(qs), 1)
        self.assertEqual(len(rejeitados), 1)
        self.assertEqual(rejeitados[0]["reason"], "no_answer")
        self.assertIn("falta a linha de resposta", rejeitados[0]["excerpt"])

    def test_sem_rejeitados_quando_corre_tudo_bem(self):
        qs, rejeitados = parsers.parse_questions_report(fixture("mc_pt_numerado"))
        self.assertEqual(len(qs), 3)
        self.assertEqual(rejeitados, [])


class RelatorioInterativoDoNotebookLM(unittest.TestCase):
    """Formato "Interativo": preâmbulo, títulos de secção, cada questão numa só
    linha e código colado sem ```. Réplica estrutural de um relatório real."""

    @classmethod
    def setUpClass(cls):
        cls.qs, cls.rejeitados = parsers.parse_questions_report(
            fixture("mc_pt_notebooklm_interativo"))

    def test_todas_as_questoes_com_o_gabarito_certo(self):
        self.assertEqual(self.rejeitados, [])
        self.assertEqual([q["answer"] for q in self.qs], list("BCCAAAACA"))

    def test_preambulo_e_titulos_de_secao_ficam_de_fora(self):
        for q in self.qs:
            for lixo in ("Introdução", "Objetivos de Aprendizagem",
                         "Atividades Avaliativas", "Neste relatório"):
                self.assertNotIn(lixo, q["question"])
        self.assertTrue(self.qs[0]["question"].startswith("Selecione"))
        self.assertTrue(self.qs[7]["question"].startswith("Em C, na declaração:"))

    def test_explicacao_acaba_no_fim_da_linha(self):
        self.assertEqual(
            self.qs[0]["explanation"],
            "Uma função recursiva resolve o problema chamando-se a si mesma "
            "com uma entrada menor.")
        for q in self.qs:
            self.assertNotIn("Considere", q["explanation"])
            self.assertNotIn("Atividades", q["explanation"])

    def test_codigo_solto_vai_para_um_bloco(self):
        q = self.qs[1]["question"]
        self.assertTrue(q.startswith("Considere as seguintes declarações em C:\n```\n"))
        self.assertIn("int *q = &a;", q)
        self.assertTrue(q.endswith("\n```\nApós a execução, qual o valor de a?"))

    def test_linhas_em_branco_dentro_do_codigo_nao_partem_o_enunciado(self):
        q = self.qs[4]["question"]
        self.assertTrue(q.startswith("Considere o seguinte trecho de código em C:"))
        for trecho in ("#include <stdio.h>", "int dobra(int x) {", "return 0;"):
            self.assertIn(trecho, q)
        self.assertEqual(q.count("```"), 2)

    def test_assinatura_de_funcao_no_meio_do_enunciado(self):
        self.assertIn(
            "II. Na função:\n```\nint fputs(const char *s, FILE *arq)\n```\n"
            "o parâmetro s indica", self.qs[3]["question"])
        self.assertEqual(
            self.qs[3]["explanation"],
            "A afirmativa II é falsa porque s é a cadeia de caracteres a "
            "escrever, e não uma contagem de bytes.")

    def test_alternativas_que_parecem_marcadores(self):
        self.assertEqual(self.qs[2]["E"], "I, II e III.")
        self.assertEqual(self.qs[3]["A"], "V - F - V.")
        self.assertEqual(self.qs[4]["A"], "3 4")
        self.assertEqual(self.qs[6]["A"], "1 obter o endereço; 2 acessar o valor")
        self.assertEqual((self.qs[8]["A"], self.qs[8]["B"], self.qs[8]["D"]),
                         ("7 B", "7 A", "B 7"))

    def test_frase_que_cita_codigo_continua_prosa(self):
        q = self.qs[8]["question"]
        self.assertTrue(q.endswith("para Par x = {7, 'B'}?"))
        self.assertEqual(q.count("```"), 2)


class NumeradasNumaSoLinha(unittest.TestCase):

    def test_varias_questoes_coladas_na_mesma_linha(self):
        qs = parse("mc_pt_numerado_linha_unica")
        self.assertEqual([q["answer"] for q in qs], ["B", "C", "B"])
        self.assertEqual(qs[0]["question"],
                         "Qual protocolo traduz nomes em endereços IP?")
        self.assertEqual(qs[0]["D"], "FTP")
        self.assertEqual(qs[0]["explanation"], "O DNS resolve nomes de domínio.")
        self.assertEqual(qs[2]["question"],
                         "Que camada do modelo OSI faz o roteamento?")

    def test_parenteses_numerados_dentro_da_explicacao_nao_partem_a_questao(self):
        qs = parse("mc_pt_numerado_linha_unica")
        self.assertEqual(
            qs[1]["explanation"],
            "O HTTPS usa a porta 443, e a expressão *(p - 1) aqui é só texto.")


class NadaVazaParaOsCampos(unittest.TestCase):

    def test_nenhum_token_interno_chega_a_um_card(self):
        for path in sorted((ROOT / "tests" / "fixtures").glob("mc_*.txt")):
            for q in parsers.parse_questions(path.read_text(encoding="utf-8")):
                for chave, valor in q.items():
                    self.assertNotIn("\x00", valor, "%s: %s" % (path.name, chave))


class Cloze(unittest.TestCase):

    def test_um_card_por_linha(self):
        cards = parsers.parse_cloze(fixture("cloze_pt"))
        self.assertEqual(len(cards), 3)
        self.assertTrue(all("{{c1::" in c for c in cards))
        self.assertIn("TCP/IP", cards[0])

    def test_linhas_sem_marcador_sao_ignoradas(self):
        texto = "Introdução ao tema\n\n{{c1::HTTP}} é um protocolo.\n\nFim."
        self.assertEqual(parsers.parse_cloze(texto), ["{{c1::HTTP}} é um protocolo."])


class ClozeComCodigoSolto(unittest.TestCase):
    """Formato do NotebookLM em que cada card é uma linha e o código vem colado
    a seguir, sem ``` e sem linhas em branco a separar os cards."""

    @classmethod
    def setUpClass(cls):
        cls.cards = parsers.parse_cloze(fixture("cloze_pt_codigo_solto"))

    def test_um_card_por_marcador(self):
        self.assertEqual(len(self.cards), 6)
        self.assertTrue(all("{{c1::" in c for c in self.cards))

    def test_preambulo_e_titulos_ficam_de_fora(self):
        junto = "\n".join(self.cards)
        for lixo in ("Introduction", "Você sabia", "Objetivos de Aprendizagem",
                     "Flashcards - Laços", "Flashcards - Ponteiros"):
            self.assertNotIn(lixo, junto)

    def test_cards_sem_codigo_nao_ganham_bloco(self):
        for i in (0, 1, 3, 5):
            self.assertNotIn("```", self.cards[i])
        self.assertEqual(self.cards[0],
                         "{{c1::while}} é o laço que testa a condição antes de "
                         "cada iteração.")

    def test_codigo_solto_vai_para_o_card_anterior(self):
        c = self.cards[2]
        self.assertTrue(c.startswith("{{c1::Pós-incremento}}"))
        self.assertIn("```\nint i = 0;\nwhile (i < 3) {\n    i++;\n}\n```", c)

    def test_bloco_de_codigo_vira_caixa_no_import(self):
        html = parsers._render_content(self.cards[4])
        self.assertIn("<pre", html)
        self.assertIn("int arr[] = {1, 2, 3};", html)
        self.assertEqual(html.count("<pre"), 1)

    def test_o_card_a_seguir_ao_codigo_nao_arrasta_o_bloco(self):
        self.assertEqual(
            self.cards[5],
            "{{c1::Desreferência}} acessa o valor no endereço apontado com o "
            "operador asterisco.")

    def test_nenhum_card_perde_o_marcador_cloze(self):
        for c in self.cards:
            self.assertRegex(c, r"\{\{c\d+::")
            self.assertNotIn("\x00", c)


class ClozeComCodigoComLinhasEmBranco(unittest.TestCase):
    """O código colado sem ``` pode trazer as suas próprias linhas em branco
    (depois do #include, dentro de um struct). Essas linhas não podem fechar o
    card nem descartar o resto do trecho — era o que fazia o card só guardar a
    primeira linha (#include) e perder o corpo todo."""

    @classmethod
    def setUpClass(cls):
        cls.cards = parsers.parse_cloze(fixture("cloze_pt_codigo_com_brancos"))

    def test_um_card_por_marcador(self):
        self.assertEqual(len(self.cards), 3)
        self.assertTrue(all("{{c1::" in c for c in self.cards))

    def test_o_bloco_de_codigo_nao_e_truncado_na_primeira_linha_em_branco(self):
        c = self.cards[1]
        self.assertTrue(c.startswith("{{c1::20 A}}"))
        for trecho in ("#include <stdio.h>", "typedef struct {", "int x;",
                       "char y;", "} MyStruct;", "MyStruct b = a;",
                       "return 0;"):
            self.assertIn(trecho, c)
        self.assertEqual(c.count("```"), 2)

    def test_linhas_em_branco_dentro_do_codigo_sao_preservadas(self):
        self.assertIn("int x;\n\nchar y;", self.cards[1])

    def test_o_card_seguinte_nao_arrasta_o_bloco(self):
        self.assertEqual(
            self.cards[2],
            "{{c1::Cópia por valor}} é o que acontece quando uma estrutura é "
            "atribuída a outra.")

    def test_o_card_sem_codigo_nao_ganha_bloco(self):
        self.assertNotIn("```", self.cards[0])

    def test_titulo_e_marcador_interno_ficam_de_fora(self):
        junto = "\n".join(self.cards)
        self.assertNotIn("Flashcards - Estruturas", junto)
        for c in self.cards:
            self.assertNotIn("\x00", c)

    def test_bloco_vira_uma_unica_caixa_no_import(self):
        html = parsers._render_content(self.cards[1])
        self.assertEqual(html.count("<pre"), 1)
        self.assertIn("typedef struct", html)
        self.assertIn("&lt;stdio.h&gt;", html)


class ClozeComWidgetDoNotebookLM(unittest.TestCase):
    """O relatório "Interativo" intercala widgets sugeridos (mapa mental, com um
    botão "Adicionar"). Como nenhuma dessas linhas tem `{{c}}` nem é código, o
    filtro deixa-as de fora — este teste tranca esse comportamento."""

    @classmethod
    def setUpClass(cls):
        cls.cards = parsers.parse_cloze(fixture("cloze_pt_widget_notebooklm"))

    def test_widget_nao_vira_card_nem_polui_outro(self):
        self.assertEqual(len(self.cards), 4)
        junto = "\n".join(self.cards)
        for lixo in ("Opção recomendada", "Mapa mental", "Fluxo de Controlo",
                     "Adicionar", "Flashcards - Laços", "Flashcards - Funções"):
            self.assertNotIn(lixo, junto)

    def test_card_antes_do_widget_mantem_o_codigo(self):
        c = self.cards[1]
        self.assertTrue(c.startswith("{{c1::Pós-incremento}}"))
        self.assertIn("```\nint i = 0;\nwhile (i < 3) {\n    i++;\n}\n```", c)
        self.assertNotIn("Opção recomendada", c)

    def test_cards_depois_do_widget_sao_lidos(self):
        self.assertTrue(self.cards[2].startswith("{{c1::return}}"))
        self.assertTrue(self.cards[3].startswith("{{c1::Recursão}}"))


class ClozeRelatorioRealDoNotebookLM(unittest.TestCase):
    """Saída canónica do NotebookLM para Cloze (cópia real do relatório): 25
    cards separados por linha em branco, e quatro deles seguidos de um bloco de
    código colado SEM ``` — sempre com uma linha em branco entre a frase e o
    código, e mais brancos entre o código e o card seguinte."""

    @classmethod
    def setUpClass(cls):
        cls.cards = parsers.parse_cloze(fixture("cloze_pt_notebooklm_real"))

    def test_todos_os_cards_sao_lidos(self):
        self.assertEqual(len(self.cards), 25)
        for i, c in enumerate(self.cards):
            self.assertRegex(c, r"\{\{c\d+::", "card %d sem marcador" % i)
            self.assertNotIn("\x00", c)

    def test_o_branco_entre_a_frase_e_o_codigo_nao_descarta_o_bloco(self):
        c = self.cards[19]
        self.assertTrue(c.startswith("{{c1::20}} é o valor final"))
        self.assertIn("```\nint x = 10;\nint *p;\np = &x;\n*p = 20;\n```", c)

    def test_apenas_os_quatro_cards_com_codigo_ganham_bloco(self):
        com_codigo = [i for i, c in enumerate(self.cards) if "```" in c]
        self.assertEqual(com_codigo, [19, 20, 21, 22])
        for i in com_codigo:
            self.assertEqual(self.cards[i].count("```"), 2)

    def test_a_indentacao_do_codigo_e_preservada(self):
        self.assertIn("\n    int x;\n    char y;", self.cards[20])
        self.assertIn("\n    int *p = arr;\n", self.cards[21])

    def test_o_card_seguinte_ao_codigo_fica_limpo(self):
        # depois de cada bloco há 2 brancos e o card seguinte não herda código
        self.assertTrue(self.cards[20].startswith("{{c1::20 A}}"))
        self.assertNotIn("```", self.cards[23])
        self.assertTrue(self.cards[24].startswith("{{c1::Ponteiro para a estr"))

    def test_cada_bloco_vira_uma_unica_caixa_no_import(self):
        for i in (19, 20, 21, 22):
            html = parsers._render_content(self.cards[i])
            self.assertEqual(html.count("<pre"), 1, "card %d" % i)
        self.assertIn("&amp;x", parsers._render_content(self.cards[19]))


class ClozeFormatosDesalinhados(unittest.TestCase):
    """Desvios que aparecem quando o texto é colado à mão ou sofre quebra dura:
    branco antes do código, frase quebrada em duas linhas e `::` com espaços."""

    CODE = ("#include <stdio.h>\ntypedef struct {\nint x;\nchar y;\n"
            "} MyStruct;\nint main() {\nreturn 0;\n}")

    def test_branco_entre_a_frase_e_o_codigo_nao_orfana_o_bloco(self):
        cards = parsers.parse_cloze(
            "{{c1::20 A}} são os valores impressos.\n\n" + self.CODE)
        self.assertEqual(len(cards), 1)
        self.assertIn("#include <stdio.h>", cards[0])
        self.assertEqual(cards[0].count("```"), 2)

    def test_frase_quebrada_em_duas_linhas_volta_a_juntar_se(self):
        cards = parsers.parse_cloze(
            "{{c1::20 A}} são os valores impressos de um de seus\nmembros.\n"
            + self.CODE)
        self.assertEqual(len(cards), 1)
        self.assertTrue(cards[0].startswith(
            "{{c1::20 A}} são os valores impressos de um de seus membros."))
        self.assertIn("#include <stdio.h>", cards[0])

    def test_marcador_com_espacos_e_normalizado(self):
        cards = parsers.parse_cloze("{{c1 :: 20 A}} é a resposta.")
        self.assertEqual(cards, ["{{c1::20 A}} é a resposta."])

    def test_titulo_colado_a_um_card_terminado_nao_e_absorvido(self):
        # frase terminada em ponto + título logo abaixo: o título fica de fora
        cards = parsers.parse_cloze(
            "{{c1::HTTP}} é um protocolo.\nFlashcards - Redes\n"
            "{{c1::DNS}} traduz nomes.")
        self.assertEqual(cards, ["{{c1::HTTP}} é um protocolo.",
                                 "{{c1::DNS}} traduz nomes."])


class Helpers(unittest.TestCase):

    def test_tags_anki_viram_hierarquia_obsidian(self):
        self.assertEqual(
            parsers._anki_tags_to_obsidian(["UNIVESP::COM130", "solta"]),
            ["UNIVESP/COM130", "solta"])

    def test_tags_duplicadas_sao_removidas(self):
        self.assertEqual(
            parsers._anki_tags_to_obsidian(["a::b", "a::b"]), ["a/b"])

    def test_yaml_cita_valores_ambiguos(self):
        self.assertEqual(parsers._yaml_quote("[[nota]]"), '"[[nota]]"')
        self.assertEqual(parsers._yaml_quote("4"), '"4"')
        self.assertEqual(parsers._yaml_quote("true"), '"true"')
        self.assertEqual(parsers._yaml_quote("texto simples"), "texto simples")

    def test_render_content_escapa_html_e_marca_codigo(self):
        out = parsers._render_content("a < b e `x` e ```py\nprint(1)\n```")
        self.assertIn("&lt;", out)
        self.assertIn('<code class="amcq-inline">x</code>', out)
        self.assertIn('class="language-py"', out)
        self.assertIn("print(1)", out)


class Idioma(unittest.TestCase):

    def test_locales_tem_as_mesmas_chaves(self):
        """Uma chave a faltar em EN faz o inglês cair em português em silêncio."""
        pt = set(i18n._STRINGS["pt"])
        en = set(i18n._STRINGS["en"])
        self.assertEqual(pt - en, set(), "chaves sem tradução EN")
        self.assertEqual(en - pt, set(), "chaves sem original PT")

    def test_marcadores_de_resposta_cobrem_os_idiomas_do_corpus(self):
        for lingua in ("pt", "en", "es", "fr", "de", "it"):
            self.assertIn(lingua, i18n.ANSWER_MARKERS)
            self.assertIn(lingua, i18n.EXPLANATION_MARKERS)

    def test_marcadores_estao_normalizados(self):
        """A tabela é comparada contra texto sem acentos e em minúsculas."""
        todos = i18n.ALL_ANSWER_MARKERS | i18n.ALL_EXPLANATION_MARKERS
        for marcador in todos:
            self.assertEqual(marcador, parsers._normalize(marcador),
                             "marcador não normalizado: %r" % marcador)

    def test_sem_escolha_guardada_nem_anki_cai_no_ingles(self):
        """O default antigo era 'pt' — abria em português para toda a gente."""
        stored, anki = i18n._stored_lang, i18n._anki_lang
        try:
            i18n._stored_lang = lambda: None
            i18n._anki_lang = lambda: None
            self.assertEqual(i18n._get_lang(), "en")
            i18n._anki_lang = lambda: "pt"
            self.assertEqual(i18n._get_lang(), "pt")
            i18n._stored_lang = lambda: "en"
            self.assertEqual(i18n._get_lang(), "en",
                             "a escolha do utilizador manda sobre o locale")
        finally:
            i18n._stored_lang, i18n._anki_lang = stored, anki


class TemplatesDoCard(unittest.TestCase):
    """`__init__.py` importa aqt e não carrega aqui, por isso estas verificações
    leem-no como texto. Cobrem dois enganos que só apareceriam no card do
    estudante: um marcador por resolver e uma cor sem valor num dos temas."""

    @classmethod
    def setUpClass(cls):
        cls.src = (ROOT / "anki_mc_quiz" / "__init__.py").read_text(
            encoding="utf-8")
        inicio = cls.src.index("CARD_CSS = ")
        cls.css = cls.src[inicio:cls.src.index(".hljs{color")]

    def test_todo_marcador_tem_substituicao(self):
        usados = set(re.findall(r"%%AMCQ_[A-Z]+%%", self.src))
        dicionario = self.src[self.src.index("replacements = {"):]
        resolvidos = set(re.findall(r'"(%%AMCQ_[A-Z]+%%)":',
                                    dicionario[:dicionario.index("}")]))
        self.assertTrue(usados)
        self.assertEqual(usados, resolvidos)

    def test_toda_variavel_de_cor_existe_nos_dois_temas(self):
        usadas = set(re.findall(r"var\((--amcq-[a-z-]+)\)", self.css))
        escuro, claro = self.css.split(":not(.nightMode)")
        definidas_escuro = set(re.findall(r"(--amcq-[a-z-]+):", escuro))
        definidas_claro = set(re.findall(r"(--amcq-[a-z-]+):", claro))
        self.assertTrue(usadas)
        self.assertEqual(usadas - definidas_escuro, set())
        self.assertEqual(usadas - definidas_claro, set())

    def test_nenhuma_cor_fixa_fora_da_paleta(self):
        corpo = self.css[self.css.index("/* ── Base card layout"):]
        self.assertEqual(re.findall(r"#[0-9a-fA-F]{3,6}", corpo), [])


if __name__ == "__main__":
    unittest.main(verbosity=2)
