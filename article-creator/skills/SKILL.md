---
name: article-creator
description: Cria artigos didáticos ricos em markdown a partir de um material de referência. O artigo será estruturado em seções, com tabelas, notas, diagramas, glossário e será compilado para HTML posteriormente.
---

# Article Creator Skill

Esta skill orienta a IA na criação de artigos didáticos e progressivos baseados em materiais de referência brutos (páginas web, artigos, documentações).

## Diretrizes Principais

1. **Estudo Profundo**: Leia as referências e extraia o conhecimento real. NUNCA invente fatos, jargões ou dados. Use EXCLUSIVAMENTE o conteúdo das referências.
2. **Didática e Progressão**: Organize o conteúdo de forma progressiva (do básico ao avançado). Se o conteúdo for extenso, divida-o em múltiplos artigos lógicos.
3. **Formatação Rica em Markdown**: O conteúdo será transformado em um HTML rico. Portanto, utilize os seguintes elementos markdown para estruturação:
   - `> [!NOTE]`, `> [!TIP]`, `> [!IMPORTANT]`, `> [!WARNING]`: Para notas de destaque.
   - blocos de código (` ```language `) com comentários explicativos.
   - Tabelas (quando houver comparativos ou dados estruturados).
   - Diagramas usando Mermaid (` ```mermaid `) para explicar arquiteturas ou fluxos.
   - Glossários no final do artigo, se o texto tiver jargões complexos.
4. **Seções Claras**: Use Header 2 (`##`) para grandes blocos e Header 3 (`###`) para subseções.
5. **Consolidação**: Encerre cada artigo com um resumo ou conclusão consolidada do que foi aprendido.
6. **Tom de Voz e Diretrizes de Escrita**:
   - **Tom Técnico-Didático de Alta Performance**: Focado em clareza, objetividade e pragmatismo. Sem termos de autoajuda corporativa ou jargões vazios de marketing.
   - **Foco no Contexto do Porquê**: Antes de propor uma ferramenta ou código, explique claramente o problema real que aquela solução resolve.
   - **Sem Emojis nos Títulos ou Corpo**: Emojis degradam a sensação "premium" e profissional de um material técnico corporativo. Remova emojis de cabeçalhos (`#`, `##`, `###`) e de notas.
   - **Estruturação de Lição Padrão**:
     - **Introdução Curta**: Contextualização concisa.
     - **Seção "O que você vai aprender"**: Lista em tópicos limpos dos objetivos práticos do módulo.
     - **Explicação Teórica/Arquitetural**: Uso de diagramas Mermaid claros ou tabelas comparativas.
     - **Passos de Implementação Prática**: Estruturados como "Passo 1 — [Título]", "Passo 2 — [Título]" com comandos reais e exemplos práticos.
   - **Linguagem Direta e Elegante**: Em vez de gírias ("IA policial", "conversinha de chat"), use termos precisos de engenharia ("mecanismo de validação determinística", "orquestração baseada em especificações").


## Workflow

1. Ao receber as URLs ou referências, use `search_web` ou ferramentas de busca para ler o conteúdo.
2. Crie na Base de Conhecimento resumos brutos e precisos sobre o que cada referência quer passar.
3. Valide interpretações em busca de "gaps".
4. Trace uma "linha de raciocínio" conectando os pontos de forma didática.
5. Gere os artigos sequenciais aplicando as diretrizes desta skill.
