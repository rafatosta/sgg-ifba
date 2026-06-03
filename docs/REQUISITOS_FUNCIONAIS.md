# Requisitos Funcionais Atuais — SGG IFBA

Este documento consolida os requisitos funcionais atualmente implementados no SGG IFBA, com base nas rotas, modelos, views, serviços e telas existentes do software. O objetivo é servir como referência para manutenção, priorização de melhorias e implementação de um frontend separado.

## 1. Escopo atual do sistema

O SGG IFBA é um sistema de gestão de grades horárias que permite:

- cadastrar e manter professores, disciplinas, horários, turmas, grades e solicitações;
- visualizar grade pessoal do professor e grade por turma;
- solicitar permuta, substituição, liberação/ausência e assunção de horários;
- aprovar ou rejeitar solicitações pendentes;
- controlar pendências de devolução/pagamento de aulas;
- gerar relatórios e PDFs para fluxos administrativos;
- simular alterações de grade antes de oficializá-las.

## 2. Atores e perfis

| Ator/perfil | Descrição | Critério atual de identificação |
| --- | --- | --- |
| Usuário autenticado | Pessoa com conta Django válida no sistema. | Sessão autenticada do Django. |
| Professor | Usuário vinculado a um registro de professor. | `User` relacionado a `Professor`. |
| Coordenador | Professor com permissão de coordenação. | `Professor.is_coordenador = true` ou superusuário em rotas de coordenação. |
| Diretor | Professor com permissão de direção. | `Professor.is_diretor = true` ou superusuário em rotas de direção. |
| Gestor | Usuário em grupos administrativos específicos ou superusuário. | Superusuário ou grupos `Coordenador`/`Diretor`, conforme decorator existente. |
| Administrador Django | Usuário com acesso ao painel administrativo. | Permissões padrão do Django Admin. |

## 3. Cadastros e administração

| ID | Requisito funcional | Ator principal | Situação atual |
| --- | --- | --- | --- |
| RF-001 | O sistema deve permitir cadastrar, editar e excluir professores. | Administrador Django | Implementado via Django Admin. |
| RF-002 | O sistema deve permitir vincular um professor a uma conta de usuário Django. | Administrador Django | Implementado no modelo `Professor`. |
| RF-003 | O sistema deve permitir registrar matrícula única do professor. | Administrador Django | Implementado no modelo `Professor`. |
| RF-004 | O sistema deve permitir marcar professores como coordenadores. | Administrador Django | Implementado no modelo `Professor`. |
| RF-005 | O sistema deve permitir marcar professores como diretores. | Administrador Django | Implementado no modelo `Professor`. |
| RF-006 | O sistema deve permitir cadastrar, editar e excluir disciplinas. | Administrador Django | Implementado via Django Admin. |
| RF-007 | O sistema deve permitir registrar a quantidade de aulas de cada disciplina. | Administrador Django | Implementado no modelo `Disciplina`. |
| RF-008 | O sistema deve permitir cadastrar, editar e excluir horários. | Administrador Django | Implementado via Django Admin. |
| RF-009 | O sistema deve permitir definir dia da semana, hora inicial, hora final e turno de cada horário. | Administrador Django | Implementado no modelo `Horario`. |
| RF-010 | O sistema deve permitir cadastrar, editar e excluir turmas. | Administrador Django | Implementado via Django Admin. |
| RF-011 | O sistema deve permitir associar horários permitidos a uma turma. | Administrador Django | Implementado no modelo `Turma` e no Admin com seleção horizontal. |
| RF-012 | O sistema deve permitir cadastrar e manter registros de grade horária. | Administrador Django | Implementado via Django Admin e construtor de grade. |
| RF-013 | O sistema deve impedir duplicidade de aula para a mesma turma e o mesmo horário. | Sistema | Implementado por restrição única em `GradeHoraria`. |
| RF-014 | O sistema deve permitir associar uma ou mais pessoas professoras a uma aula da grade. | Administrador/Coordenador | Implementado por relacionamento muitos-para-muitos em `GradeHoraria`. |
| RF-015 | O sistema deve permitir cadastrar dias não letivos com data e descrição. | Administrador Django | Implementado no modelo `DiaNaoLetivo`. |
| RF-016 | O sistema deve permitir restringir dias não letivos a turmas específicas ou aplicar a toda a instituição. | Administrador Django | Implementado no modelo `DiaNaoLetivo`. |

## 4. Autenticação e autorização

| ID | Requisito funcional | Ator principal | Situação atual |
| --- | --- | --- | --- |
| RF-017 | O sistema deve permitir login de usuários. | Usuário autenticado | Implementado por `LoginView` do Django. |
| RF-018 | O sistema deve permitir logout de usuários. | Usuário autenticado | Implementado por `LogoutView` do Django. |
| RF-019 | O sistema deve redirecionar usuários não autenticados para a tela de login ao acessar páginas protegidas. | Sistema | Implementado com `@login_required` nas páginas protegidas. |
| RF-020 | O sistema deve restringir funcionalidades de coordenação a coordenadores ou superusuários. | Sistema | Implementado por decorator específico. |
| RF-021 | O sistema deve restringir funcionalidades de direção a diretores ou superusuários. | Sistema | Implementado por validações nas views. |
| RF-022 | O sistema deve restringir funcionalidades de gestão a gestores ou superusuários, quando aplicável. | Sistema | Implementado por decorator específico. |

## 5. Página inicial e pendências

| ID | Requisito funcional | Ator principal | Situação atual |
| --- | --- | --- | --- |
| RF-023 | O sistema deve exibir a página inicial apenas para usuários autenticados. | Usuário autenticado | Implementado. |
| RF-024 | O sistema deve listar as dívidas de aula do professor logado. | Professor | Implementado para solicitações aprovadas com devolução pendente em que o professor é solicitante. |
| RF-025 | O sistema deve listar os créditos de aula do professor logado. | Professor | Implementado para substituições e permutas aprovadas com devolução pendente em que o professor é substituto ou professor da aula de destino. |

## 6. Visualização de grades

| ID | Requisito funcional | Ator principal | Situação atual |
| --- | --- | --- | --- |
| RF-026 | O sistema deve permitir ao professor visualizar sua grade pessoal. | Professor | Implementado na rota `/grade/`. |
| RF-027 | O sistema deve permitir ao professor visualizar a grade por turma. | Professor | Implementado na rota `/grade/` com seleção de turma. |
| RF-028 | O sistema deve permitir navegar entre semanas da grade. | Professor | Implementado por parâmetro de data e cálculo de semana anterior/próxima. |
| RF-029 | O sistema deve exibir aulas da grade com turma, disciplina e identificação da aula. | Professor | Implementado na montagem do contexto da grade. |
| RF-030 | O sistema deve sobrepor informações de solicitações aprovadas na grade pessoal quando aplicáveis à semana selecionada. | Professor | Implementado para liberação, substituição e permuta aprovadas. |
| RF-031 | O sistema deve destacar visualmente ausências, substituições e permutas na grade. | Professor | Implementado por campos de cor e informação extra. |
| RF-032 | O sistema deve exibir aulas em que o professor logado atua como substituto na semana selecionada. | Professor | Implementado na grade pessoal. |
| RF-033 | O sistema deve exibir na grade da turma se a aula pertence ao professor logado. | Professor | Implementado por marcador `is_minha_aula`. |
| RF-034 | O sistema deve montar os slots de horário a partir dos horários cadastrados. | Sistema | Implementado por consulta aos horários existentes. |

## 7. Solicitações de permuta, substituição, liberação e assunção

| ID | Requisito funcional | Ator principal | Situação atual |
| --- | --- | --- | --- |
| RF-035 | O sistema deve permitir criar solicitação de permuta entre aulas. | Professor | Implementado via formulário legado e endpoint JSON. |
| RF-036 | O sistema deve permitir criar solicitação de substituição direta. | Professor | Implementado via formulário legado e ação de modal. |
| RF-037 | O sistema deve permitir registrar liberação/ausência em uma aula. | Professor | Implementado via formulário legado e ação de modal. |
| RF-038 | O sistema deve permitir criar solicitação para assumir horário. | Professor | Implementado via ação de modal. |
| RF-039 | O sistema deve armazenar tipo, status, solicitante, aula de origem, data de aplicação e caráter de cada solicitação. | Sistema | Implementado no modelo `Solicitacao`. |
| RF-040 | O sistema deve permitir classificar solicitações como temporárias ou definitivas. | Professor/Sistema | Implementado pelo campo `carater`. |
| RF-041 | O sistema deve manter solicitações novas como pendentes até aprovação, quando aplicável. | Sistema | Implementado em solicitações de permuta, substituição e assunção. |
| RF-042 | O sistema deve registrar substituto e disciplina substituta quando a solicitação exigir. | Professor/Sistema | Implementado nos campos `professor_substituto` e `disciplina_substituta`. |
| RF-043 | O sistema deve registrar aula de destino em solicitações de permuta. | Professor/Sistema | Implementado pelo campo `aula_destino`. |
| RF-044 | O sistema deve permitir informar data de devolução de aula ou marcar devolução como pendente. | Professor | Implementado no formulário legado de solicitação. |
| RF-045 | O sistema deve impedir que professor assuma/substitua aula quando houver choque de horário. | Sistema | Implementado no serviço de ação de modal. |
| RF-046 | O sistema deve permitir criar uma aula vazia quando a ação de modal for feita sobre horário e turma sem aula existente. | Sistema | Implementado na ação de modal, desde que turma e horário sejam informados. |
| RF-047 | O sistema deve enviar notificação por e-mail à coordenação quando houver novo pedido em fluxos específicos. | Sistema | Implementado em solicitação via formulário e assunção de horário. |

## 8. Aprovação de solicitações

| ID | Requisito funcional | Ator principal | Situação atual |
| --- | --- | --- | --- |
| RF-048 | O sistema deve disponibilizar painel de aprovações para coordenadores. | Coordenador | Implementado na rota `/aprovacoes/`. |
| RF-049 | O sistema deve listar solicitações pendentes em ordem decrescente de criação. | Coordenador | Implementado no painel de aprovações. |
| RF-050 | O sistema deve permitir aprovar uma solicitação pendente. | Coordenador | Implementado no endpoint de processamento de aprovação. |
| RF-051 | O sistema deve permitir rejeitar uma solicitação pendente. | Coordenador | Implementado no endpoint de processamento de aprovação. |
| RF-052 | O sistema deve marcar solicitação aprovada com status `A`. | Sistema | Implementado no processamento de aprovação. |
| RF-053 | O sistema deve marcar solicitação rejeitada com status `R`. | Sistema | Implementado no processamento de aprovação. |
| RF-054 | O sistema deve oficializar alterações definitivas de permuta na grade base ao aprovar solicitação definitiva. | Sistema | Implementado ao trocar professores e disciplinas entre aula de origem e destino. |
| RF-055 | O sistema deve oficializar alterações definitivas de substituição/assunção na grade base ao aprovar solicitação definitiva. | Sistema | Implementado ao alterar professores e disciplina da aula de origem. |

## 9. Construtor de grade

| ID | Requisito funcional | Ator principal | Situação atual |
| --- | --- | --- | --- |
| RF-056 | O sistema deve disponibilizar construtor de grade para coordenadores. | Coordenador | Implementado na rota `/construtor/`. |
| RF-057 | O sistema deve listar turmas para seleção no construtor. | Coordenador | Implementado. |
| RF-058 | O sistema deve carregar slots permitidos de uma turma selecionada. | Coordenador | Implementado a partir de `horarios_permitidos`. |
| RF-059 | O sistema deve exibir a grade existente da turma selecionada. | Coordenador | Implementado com disciplina, professores e identificação de horários. |
| RF-060 | O sistema deve permitir criar ou atualizar aula base para uma turma e horário. | Coordenador/Gestor | Implementado no endpoint `/api/construtor/salvar/`. |
| RF-061 | O sistema deve permitir alterar disciplina da aula base. | Coordenador/Gestor | Implementado no endpoint de salvar aula base. |
| RF-062 | O sistema deve permitir alterar professores da aula base. | Coordenador/Gestor | Implementado no endpoint de salvar aula base. |
| RF-063 | O sistema deve permitir remover aula base. | Coordenador/Gestor | Implementado no endpoint de salvar aula base. |
| RF-064 | O sistema deve permitir gerar uma grade vazia para uma turma com base em seus horários permitidos. | Coordenador | Implementado no endpoint `/api/grade/gerar-vazia/`. |
| RF-065 | O sistema deve apagar a grade atual da turma antes de gerar uma nova grade vazia. | Sistema | Implementado no serviço de geração de grade vazia. |

## 10. Minhas solicitações e devolução de aulas

| ID | Requisito funcional | Ator principal | Situação atual |
| --- | --- | --- | --- |
| RF-066 | O sistema deve permitir ao professor visualizar suas solicitações. | Professor | Implementado na rota `/minhas-solicitacoes/`. |
| RF-067 | O sistema deve listar solicitações do professor logado em ordem decrescente de criação. | Professor | Implementado. |
| RF-068 | O sistema deve permitir registrar pagamento/devolução de aula pendente. | Professor solicitante | Implementado no endpoint `/api/pagar/`. |
| RF-069 | O sistema deve impedir que professor registre pagamento/devolução de solicitação de outro solicitante. | Sistema | Implementado por validação de solicitante. |
| RF-070 | O sistema deve marcar a devolução como não pendente após registro do pagamento/devolução. | Sistema | Implementado no endpoint `/api/pagar/`. |

## 11. Relatórios e PDFs

| ID | Requisito funcional | Ator principal | Situação atual |
| --- | --- | --- | --- |
| RF-071 | O sistema deve disponibilizar relatório de carga horária para direção ou superusuário. | Diretor | Implementado na rota `/direcao/carga-horaria/`. |
| RF-072 | O sistema deve calcular total de aulas por professor no relatório de carga horária. | Sistema | Implementado por anotação de contagem das grades horárias. |
| RF-073 | O sistema deve gerar PDF SEI para solicitação aprovada. | Professor | Implementado na rota `/solicitacao/<id>/pdf-sei/`. |
| RF-074 | O sistema deve bloquear geração de PDF SEI para solicitação não aprovada. | Sistema | Implementado com resposta HTTP 403. |
| RF-075 | O sistema deve agrupar no PDF SEI solicitações aprovadas do mesmo solicitante e da mesma data de criação. | Sistema | Implementado na geração do PDF SEI. |
| RF-076 | O sistema deve identificar cursos/turmas e substitutos envolvidos no PDF SEI. | Sistema | Implementado na geração do PDF SEI. |

## 12. Simulador de grade

| ID | Requisito funcional | Ator principal | Situação atual |
| --- | --- | --- | --- |
| RF-077 | O sistema deve disponibilizar simulador de grade para coordenação, direção ou superusuário. | Coordenador/Diretor | Implementado na rota `/simulador/`. |
| RF-078 | O sistema deve carregar turmas, professores, horários e grade completa no simulador. | Coordenador/Diretor | Implementado na view do simulador. |
| RF-079 | O sistema deve permitir exportar a simulação de grade em PDF. | Coordenador/Diretor | Implementado na rota `/simulador/exportar-pdf/`. |
| RF-080 | O sistema deve receber o estado simulado da grade como JSON para gerar PDF. | Coordenador/Diretor | Implementado pelo campo `estado_grade_json`. |
| RF-081 | O sistema deve identificar alterações de dia e horário entre a grade original e a simulação. | Sistema | Implementado durante geração do PDF de simulação. |
| RF-082 | O sistema deve gerar um PDF da proposta de alteração para uso administrativo. | Sistema | Implementado com template de PDF da simulação. |

## 13. Importação de dados

| ID | Requisito funcional | Ator principal | Situação atual |
| --- | --- | --- | --- |
| RF-083 | O sistema deve permitir importar professores por comando de gerenciamento. | Administrador técnico | Implementado por comando `importar_professores`. |
| RF-084 | O sistema deve permitir importar disciplinas por comando de gerenciamento. | Administrador técnico | Implementado por comando `importar_disciplinas`. |

## 14. Requisitos funcionais expostos por endpoints JSON atuais

| ID | Endpoint | Requisito atendido |
| --- | --- | --- |
| RF-API-001 | `POST /api/permuta/solicitar/` | Criar solicitação de permuta. |
| RF-API-002 | `POST /api/aprovacao/processar/` | Aprovar ou rejeitar solicitação. |
| RF-API-003 | `POST /api/modal/acao/` | Liberar, assumir ou substituir aula via modal. |
| RF-API-004 | `POST /api/grade/gerar-vazia/` | Gerar grade vazia para turma. |
| RF-API-005 | `POST /api/construtor/salvar/` | Criar, atualizar ou remover aula base. |
| RF-API-006 | `POST /api/pagar/` | Registrar devolução/pagamento de aula pendente. |

## 15. Regras e observações funcionais importantes

- O sistema trabalha com dias da semana numerados de `1` a `7`, sendo `2` a segunda-feira e `6` a sexta-feira, que são os dias exibidos nas grades principais.
- A grade principal usa navegação semanal baseada em uma data de foco informada por parâmetro ou na data atual do servidor.
- Solicitações temporárias afetam a visualização da semana, mas não alteram a grade base ao serem aprovadas.
- Solicitações definitivas podem alterar a grade base quando aprovadas pela coordenação.
- Liberação de aula via ação de modal limpa professores e disciplina da aula e cria solicitação aprovada de liberação.
- O controle de dívida/crédito depende de solicitações aprovadas com `devolucao_pendente = true`.
- O frontend deve tratar permissões no nível de interface apenas como apoio de experiência; a autorização efetiva deve permanecer no backend.

## 16. Fora do escopo funcional atual

Os itens abaixo não aparecem implementados como funcionalidades completas no estado atual do software:

- API REST completa de leitura para todas as telas;
- autenticação JSON própria para SPA;
- cadastro público de usuários;
- recuperação de senha customizada;
- workflow formal de cancelamento de solicitações aprovadas;
- histórico/auditoria detalhada de alterações na grade;
- configuração de CORS para frontend hospedado em domínio separado;
- testes automatizados cobrindo todos os requisitos listados.
