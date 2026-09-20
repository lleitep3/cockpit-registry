# Decisão de plataforma mobile

## Perguntas de decisão

| Dimensão | Pergunta | Sinal de Flutter | Sinal de nativo |
| --- | --- | --- | --- |
| UI | A experiência precisa ser visualmente muito consistente? | forte | fraco |
| APIs | Recursos específicos de uma plataforma são centrais? | bridge delimitada | forte |
| Time | A equipe domina Dart e quer compartilhar código? | forte | depende |
| Distribuição | Há widgets, extensões, watch ou Live Activities? | possível, mas validar | forte |
| Performance | Há gráficos, câmera ou áudio com baixa latência? | validar cedo | pode favorecer nativo |
| Prazo | É necessário entregar dois sistemas rapidamente? | forte | menor |
| UX | Padrões nativos divergentes são parte do produto? | cuidado | forte |

Não usar a tabela como pontuação automática. Ela organiza perguntas; a decisão precisa de evidência do produto.

## Híbrido saudável

Compartilhe contratos e domínio quando fizer sentido. Isole platform adapters, permissões, lifecycle e UI específica. Defina observabilidade e testes por fronteira. Híbrido mal delimitado apenas espalha complexidade entre três runtimes.
