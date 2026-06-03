# Documentação da API — Frontend React separado

Esta documentação descreve os contratos HTTP atualmente expostos pelo SGG IFBA para apoiar a implementação de um frontend separado em React. O backend é uma aplicação Django tradicional, com autenticação por sessão e proteção CSRF, e ainda não expõe uma API REST completa para todas as telas.

## 1. Visão geral

| Item | Valor |
| --- | --- |
| Base URL em desenvolvimento | `http://127.0.0.1:8000` |
| Base URL em produção | Defina conforme o domínio implantado, por exemplo `https://sgg.jsambarreto.com.br` |
| Formato preferencial dos endpoints `api/*` | JSON (`application/json`) |
| Autenticação atual | Cookie de sessão Django (`sessionid`) |
| Proteção contra CSRF | Cookie `csrftoken` + header `X-CSRFToken` em métodos mutáveis |
| Timezone configurado | UTC |
| Datas | `YYYY-MM-DD` |
| Horas | `HH:MM` quando renderizadas nas páginas |

> **Importante para frontend separado:** se o React for servido em outro domínio/porta, será necessário configurar CORS e CSRF no Django antes de consumir a API no navegador. O repositório atualmente não inclui `django-cors-headers`; portanto, o caminho mais simples é servir o React no mesmo domínio do Django ou adicionar essa configuração ao backend.

## 2. Autenticação, sessão e CSRF

### 2.1 Fluxo atual de login

O login existente usa a view padrão do Django em `POST /login/`, com formulário HTML. Para consumir via React sem criar um endpoint JSON de login, envie `application/x-www-form-urlencoded` e mantenha os cookies da sessão.

**Endpoint**

```http
POST /login/
Content-Type: application/x-www-form-urlencoded
```

**Campos**

| Campo | Tipo | Obrigatório | Descrição |
| --- | --- | --- | --- |
| `username` | string | Sim | Nome de usuário Django. |
| `password` | string | Sim | Senha do usuário. |
| `csrfmiddlewaretoken` | string | Sim | Token CSRF emitido pelo Django. |

**Exemplo com `fetch`**

```ts
async function login(username: string, password: string) {
  const csrfToken = getCookie('csrftoken');
  const body = new URLSearchParams({
    username,
    password,
    csrfmiddlewaretoken: csrfToken ?? '',
  });

  const response = await fetch('http://127.0.0.1:8000/login/', {
    method: 'POST',
    credentials: 'include',
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
      'X-CSRFToken': csrfToken ?? '',
    },
    body,
  });

  return response;
}
```

### 2.2 Envio de requisições JSON autenticadas

Use `credentials: 'include'` para enviar `sessionid` e `csrftoken` ao backend.

```ts
function getCookie(name: string) {
  return document.cookie
    .split('; ')
    .find((row) => row.startsWith(`${name}=`))
    ?.split('=')[1];
}

async function postJson<TBody>(path: string, body: TBody) {
  const csrfToken = getCookie('csrftoken');

  const response = await fetch(`http://127.0.0.1:8000${path}`, {
    method: 'POST',
    credentials: 'include',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': csrfToken ?? '',
    },
    body: JSON.stringify(body),
  });

  return response.json();
}
```

### 2.3 Perfis de acesso

| Perfil | Como é identificado no backend | Uso principal |
| --- | --- | --- |
| Professor | `request.user.professor` vinculado ao usuário Django | Visualizar grade e criar solicitações. |
| Coordenador | `Professor.is_coordenador = true` ou superusuário em rotas específicas | Aprovar solicitações, gerar grade vazia e editar construtor. |
| Diretor | `Professor.is_diretor = true` ou superusuário em rotas específicas | Relatórios e simulador. |
| Superusuário | `request.user.is_superuser = true` | Acesso administrativo e permissões elevadas. |

## 3. Convenções de resposta

Os endpoints JSON seguem, em geral, o padrão abaixo:

### Sucesso

```json
{
  "sucesso": true,
  "mensagem": "Operação concluída com sucesso."
}
```

### Erro de negócio ou validação

```json
{
  "sucesso": false,
  "erro": "Descrição do erro."
}
```

### Observações importantes

- Alguns endpoints retornam HTTP `200` mesmo quando `sucesso` é `false`.
- Alguns endpoints retornam HTTP `405` para método inválido.
- Em caso de falha interna, alguns endpoints retornam HTTP `500` com `sucesso: false`.
- Rotas decoradas com `@login_required` podem redirecionar para `/login/?next=...` quando chamadas sem sessão autenticada.

## 4. Modelos de domínio

### 4.1 Professor

```ts
type Professor = {
  id: number;
  nome_completo: string;
  matricula?: string | null;
  is_coordenador: boolean;
  is_diretor: boolean;
};
```

### 4.2 Disciplina

```ts
type Disciplina = {
  id: number;
  nome: string;
  quantidade_aulas: number;
};
```

### 4.3 Horário

```ts
type Horario = {
  id: number;
  dia_semana: 1 | 2 | 3 | 4 | 5 | 6 | 7;
  hora_inicio: string; // HH:MM:SS no banco; geralmente HH:MM nas telas
  hora_fim: string;
  turno: 'M' | 'V' | 'N';
};
```

**Dias da semana**

| Valor | Dia |
| --- | --- |
| `1` | Domingo |
| `2` | Segunda-feira |
| `3` | Terça-feira |
| `4` | Quarta-feira |
| `5` | Quinta-feira |
| `6` | Sexta-feira |
| `7` | Sábado |

### 4.4 Turma

```ts
type Turma = {
  id: number;
  nome: string;
  horarios_permitidos: Horario[];
};
```

### 4.5 GradeHoraria / Aula

```ts
type GradeHoraria = {
  id: number;
  turma: Turma;
  horario: Horario;
  disciplina?: Disciplina | null;
  professores: Professor[];
  nomes_professores: string; // Ex.: "Ana / João" ou "Sem Prof."
};
```

### 4.6 Solicitação

```ts
type TipoSolicitacao = 'P' | 'S' | 'L' | 'A';
type StatusSolicitacao = 'P' | 'A' | 'R';
type CaraterSolicitacao = 'T' | 'D';

type Solicitacao = {
  id: number;
  tipo: TipoSolicitacao;
  status: StatusSolicitacao;
  carater: CaraterSolicitacao;
  solicitante: Professor;
  data_criacao: string;
  data_aplicacao: string;
  data_devolucao?: string | null;
  devolucao_pendente: boolean;
  aula_origem: GradeHoraria;
  aula_destino?: GradeHoraria | null;
  professor_substituto?: Professor | null;
  disciplina_substituta?: Disciplina | null;
};
```

**Tipos**

| Código | Significado |
| --- | --- |
| `P` | Permuta |
| `S` | Substituição direta |
| `L` | Liberação / aviso de falta |
| `A` | Assumir horário |

**Status**

| Código | Significado |
| --- | --- |
| `P` | Pendente |
| `A` | Aprovada |
| `R` | Rejeitada |

**Caráter**

| Código | Significado |
| --- | --- |
| `T` | Temporário, apenas na data indicada |
| `D` | Definitivo, para o restante do período |

## 5. Endpoints JSON existentes

### 5.1 Solicitar permuta

Cria uma solicitação de permuta entre duas aulas.

```http
POST /api/permuta/solicitar/
Content-Type: application/json
```

**Autenticação:** usuário autenticado com professor vinculado.

> A view atual não possui `@login_required`, mas acessa `request.user.professor`. No frontend, trate esta rota como autenticada.

**Body**

| Campo | Tipo | Obrigatório | Descrição |
| --- | --- | --- | --- |
| `aula_origem_id` | number | Sim | ID da aula do solicitante. |
| `aula_destino_id` | number | Sim | ID da aula que será permutada. |
| `data_aplicacao` | string | Não | Data `YYYY-MM-DD`. Se ausente, usa a data atual do servidor. |
| `carater` | `'T' \| 'D'` | Não | Padrão `T`. |

**Exemplo**

```json
{
  "aula_origem_id": 10,
  "aula_destino_id": 22,
  "data_aplicacao": "2026-06-10",
  "carater": "T"
}
```

**Resposta esperada**

```json
{
  "sucesso": true,
  "mensagem": "Pedido enviado para aprovação."
}
```

**Erros comuns**

```json
{
  "sucesso": false,
  "erro": "O seu utilizador não está vinculado a um perfil de Professor no sistema."
}
```

---

### 5.2 Processar aprovação

Aprova ou rejeita uma solicitação pendente.

```http
POST /api/aprovacao/processar/
Content-Type: application/json
```

**Autenticação recomendada:** coordenador ou superusuário.

> A rota é usada pelo painel de aprovações, que é restrito a coordenadores. A função JSON atual não possui decoradores de autenticação/autorização; recomenda-se adicionar `@login_required` e `@apenas_coordenadores` antes de expor para um frontend separado.

**Body**

| Campo | Tipo | Obrigatório | Descrição |
| --- | --- | --- | --- |
| `solicitacao_id` | number | Sim | Solicitação que será processada. |
| `acao` | `'aprovar' \| 'rejeitar'` | Sim | Ação desejada. |

**Exemplo de aprovação**

```json
{
  "solicitacao_id": 42,
  "acao": "aprovar"
}
```

**Resposta de aprovação**

```json
{
  "sucesso": true,
  "mensagem": "Alteração oficializada com sucesso!"
}
```

**Resposta de rejeição**

```json
{
  "sucesso": true,
  "mensagem": "Solicitação rejeitada."
}
```

**Regra de negócio**

- Se `carater = 'D'` e a ação for aprovação, a grade base é alterada definitivamente.
- Para `tipo = 'P'`, professores e disciplinas das aulas de origem e destino são trocados.
- Para outros tipos definitivos, a aula de origem recebe o professor e a disciplina substitutos.

---

### 5.3 Executar ação pelo modal da grade

Registra liberação, substituição ou assunção de aula a partir do modal da grade.

```http
POST /api/modal/acao/
Content-Type: application/json
```

**Autenticação:** usuário autenticado com professor vinculado.

> A view atual não possui `@login_required`, mas depende de `request.user.professor`. No frontend, trate esta rota como autenticada.

**Body**

| Campo | Tipo | Obrigatório | Descrição |
| --- | --- | --- | --- |
| `aula_id` | number \| string \| null | Condicional | ID da aula. Pode ficar vazio quando a aula será criada a partir de `turma_id` e `horario_id`. |
| `acao` | `'liberar' \| 'assumir' \| 'substituir'` | Sim | Ação solicitada. |
| `prof_id` | number | Condicional | Professor substituto. Se ausente em `assumir`, usa o professor logado. |
| `disc_id` | number | Sim para `assumir` e `substituir` | Disciplina que será assumida/substituída. |
| `data_aplicacao` | string | Recomendado | Data `YYYY-MM-DD`. A implementação atual usa fallback fixo `2026-03-20` se ausente. |
| `horario_id` | number | Condicional | Necessário quando `aula_id` está vazio. |
| `turma_id` | number | Condicional | Necessário quando `aula_id` está vazio. |
| `carater` | `'T' \| 'D'` | Não | Caráter da solicitação para `assumir`/`substituir`. |

**Exemplo — liberar aula**

```json
{
  "aula_id": 10,
  "acao": "liberar",
  "data_aplicacao": "2026-06-10"
}
```

**Resposta — liberar aula**

```json
{
  "sucesso": true,
  "mensagem": "Ausência registada! O horário está agora vago."
}
```

**Exemplo — assumir horário vago**

```json
{
  "aula_id": null,
  "acao": "assumir",
  "disc_id": 5,
  "data_aplicacao": "2026-06-10",
  "horario_id": 8,
  "turma_id": 3,
  "carater": "T"
}
```

**Resposta — assumir/substituir**

```json
{
  "sucesso": true,
  "mensagem": "Pedido enviado para a coordenação com sucesso!"
}
```

**Erros comuns**

```json
{
  "sucesso": false,
  "erro": "Usuário sem perfil de professor."
}
```

```json
{
  "sucesso": false,
  "erro": "Choque de horário: O Prof. Nome já tem aula na turma Turma X."
}
```

---

### 5.4 Gerar grade vazia para turma

Apaga a grade atual de uma turma e recria os slots com base nos horários permitidos da turma.

```http
POST /api/grade/gerar-vazia/
Content-Type: application/json
```

**Autenticação:** coordenador ou superusuário.

**Body**

| Campo | Tipo | Obrigatório | Descrição |
| --- | --- | --- | --- |
| `turma_id` | number | Sim | Turma que terá a grade reinicializada. |

**Exemplo**

```json
{
  "turma_id": 3
}
```

**Resposta de sucesso**

```json
{
  "sucesso": true,
  "mensagem": "Grade reiniciada! 20 novos horários vazios foram gerados para Turma A."
}
```

**Erros comuns**

```json
{
  "sucesso": false,
  "erro": "ID da turma não fornecido."
}
```

```json
{
  "sucesso": false,
  "erro": "A turma Turma A não possui horários permitidos vinculados no Admin."
}
```

---

### 5.5 Salvar aula base no construtor

Cria, atualiza ou remove uma aula da grade base.

```http
POST /api/construtor/salvar/
Content-Type: application/json
```

**Autenticação:** a implementação atual exige simultaneamente as regras de gestor e coordenador. Na prática, use coordenador/superusuário e valide permissões no ambiente real.

**Body para criar/atualizar**

| Campo | Tipo | Obrigatório | Descrição |
| --- | --- | --- | --- |
| `turma_id` | number | Sim | Turma da aula. |
| `horario_id` | number | Sim | Horário da aula. |
| `disciplina_id` | number \| string | Sim | Disciplina da aula. String vazia remove a aula. |
| `professores_ids` | number[] | Não | Lista de professores atribuídos. Lista vazia limpa os professores. |
| `excluir` | boolean | Não | Se `true`, remove a aula. |

**Exemplo — criar/atualizar**

```json
{
  "turma_id": 3,
  "horario_id": 8,
  "disciplina_id": 5,
  "professores_ids": [1, 2]
}
```

**Resposta**

```json
{
  "sucesso": true
}
```

**Exemplo — remover**

```json
{
  "turma_id": 3,
  "horario_id": 8,
  "excluir": true
}
```

**Resposta de remoção**

```json
{
  "sucesso": true,
  "removido": true
}
```

---

### 5.6 Informar pagamento/devolução de aula

Registra a data em que uma aula devida foi devolvida/paga e marca a pendência como resolvida.

```http
POST /api/pagar/
Content-Type: application/json
```

**Autenticação:** professor solicitante da pendência.

> A view atual não possui `@login_required`, mas valida `request.user.professor`. No frontend, trate esta rota como autenticada.

**Body**

| Campo | Tipo | Obrigatório | Descrição |
| --- | --- | --- | --- |
| `solicitacao_id` | number | Sim | Solicitação pendente. |
| `data_pagamento` | string | Sim | Data `YYYY-MM-DD` em que a aula foi devolvida. |

**Exemplo**

```json
{
  "solicitacao_id": 42,
  "data_pagamento": "2026-06-17"
}
```

**Resposta**

```json
{
  "sucesso": true,
  "mensagem": "Pagamento registrado com sucesso!"
}
```

**Erro de permissão**

```json
{
  "sucesso": false,
  "erro": "Sem permissão para alterar esta dívida."
}
```

## 6. Endpoints HTML/PDF existentes úteis para migração

Estas rotas renderizam HTML ou PDF. Elas podem ser mantidas temporariamente, mas um frontend React separado normalmente precisará de endpoints JSON equivalentes.

| Método | Caminho | Tipo de resposta | Autenticação | Finalidade |
| --- | --- | --- | --- | --- |
| `GET` | `/` | HTML | Login | Página inicial com dívidas e créditos. |
| `GET` | `/grade/?aba=pessoal&data=YYYY-MM-DD` | HTML | Login | Grade pessoal da semana. |
| `GET` | `/grade/?aba=turma&turma=<id>&data=YYYY-MM-DD` | HTML | Login | Grade da turma na semana. |
| `GET` | `/aprovacoes/` | HTML | Coordenador | Lista de solicitações pendentes. |
| `GET` | `/construtor/?turma=<id>` | HTML | Coordenador | Construtor de grade base. |
| `GET` | `/direcao/carga-horaria/` | HTML | Diretor ou superusuário | Relatório de carga horária. |
| `GET` | `/minhas-solicitacoes/` | HTML | Login | Solicitações do professor logado. |
| `GET` | `/solicitacao/<id>/pdf-sei/` | PDF | Login | PDF SEI de solicitações aprovadas do lote. |
| `GET`/`POST` | `/solicitar/<aula_id>/<tipo>/` | HTML/form | Login | Formulário legado para permuta, substituição e liberação. |
| `GET` | `/simulador/` | HTML | Coordenador, diretor ou superusuário | Simulador de grade. |
| `POST` | `/simulador/exportar-pdf/` | PDF | Coordenador, diretor ou superusuário | Exporta a simulação para PDF. |

## 7. Contrato do exportador PDF de simulação

Embora não seja JSON, esta rota pode ser chamada pelo React com `FormData` para baixar um PDF.

```http
POST /simulador/exportar-pdf/
Content-Type: multipart/form-data
```

**Campo do formulário**

| Campo | Tipo | Obrigatório | Descrição |
| --- | --- | --- | --- |
| `estado_grade_json` | string JSON | Sim | Estado simulado da grade serializado como JSON. |

**Formato esperado de cada item em `estado_grade_json`**

```ts
type ItemSimulacao = {
  id: number;
  turmaNome: string;
  diaSemana: 2 | 3 | 4 | 5 | 6;
  horaInicio: string; // HH:MM
  professoresStr: string;
  disciplina: string;
};
```

**Exemplo de envio pelo React**

```ts
async function baixarPdfSimulacao(estado: ItemSimulacao[]) {
  const csrfToken = getCookie('csrftoken');
  const formData = new FormData();
  formData.append('estado_grade_json', JSON.stringify(estado));

  const response = await fetch('http://127.0.0.1:8000/simulador/exportar-pdf/', {
    method: 'POST',
    credentials: 'include',
    headers: {
      'X-CSRFToken': csrfToken ?? '',
    },
    body: formData,
  });

  if (!response.ok) throw new Error(await response.text());

  const blob = await response.blob();
  const url = URL.createObjectURL(blob);
  window.open(url, '_blank');
}
```

## 8. Endpoints JSON recomendados para um frontend React completo

A API atual cobre principalmente ações de escrita. Para substituir as telas Django por React, recomenda-se implementar também endpoints JSON de leitura.

### 8.1 Sessão atual

```http
GET /api/auth/me/
```

**Resposta sugerida**

```json
{
  "id": 7,
  "username": "professor1",
  "professor": {
    "id": 3,
    "nome_completo": "Professor Exemplo",
    "matricula": "12345",
    "is_coordenador": false,
    "is_diretor": false
  },
  "is_superuser": false,
  "permissoes": ["professor"]
}
```

### 8.2 Listagens base

```http
GET /api/professores/
GET /api/disciplinas/
GET /api/turmas/
GET /api/horarios/
```

Use estes endpoints para popular selects do construtor, solicitações e simulador.

### 8.3 Grade semanal do professor

```http
GET /api/grade/pessoal/?data=YYYY-MM-DD
```

**Resposta sugerida**

```json
{
  "inicio_semana": "2026-06-01",
  "fim_semana": "2026-06-07",
  "semana_anterior": "2026-05-25",
  "proxima_semana": "2026-06-08",
  "dias_semana": [2, 3, 4, 5, 6],
  "slots_horarios": ["07:00", "08:40"],
  "grade": {
    "2-07:00": {
      "id": 10,
      "turma": "INFO 1",
      "disciplina": "Matemática",
      "info_extra": "",
      "cor": ""
    }
  }
}
```

### 8.4 Grade semanal por turma

```http
GET /api/grade/turma/<turma_id>/?data=YYYY-MM-DD
```

**Resposta sugerida**

```json
{
  "turma": { "id": 3, "nome": "INFO 1" },
  "inicio_semana": "2026-06-01",
  "fim_semana": "2026-06-07",
  "dias_semana": [2, 3, 4, 5, 6],
  "slots_horarios": ["07:00", "08:40"],
  "grade": {
    "2-07:00": {
      "id": 10,
      "professor": "Ana",
      "disciplina": "Matemática",
      "is_minha_aula": true,
      "info_extra": "",
      "cor": ""
    }
  }
}
```

### 8.5 Solicitações

```http
GET /api/solicitacoes/minhas/
GET /api/solicitacoes/pendentes/
GET /api/solicitacoes/<id>/
```

### 8.6 Pendências da página inicial

```http
GET /api/dashboard/pendencias/
```

**Resposta sugerida**

```json
{
  "dividas": [],
  "creditos": []
}
```

### 8.7 Relatório de carga horária

```http
GET /api/relatorios/carga-horaria/
```

**Resposta sugerida**

```json
[
  {
    "professor_id": 3,
    "nome_completo": "Professor Exemplo",
    "total_aulas": 12
  }
]
```

## 9. Recomendações de implementação para desacoplar React e Django

1. **Criar endpoints JSON de leitura antes de remover templates.** As telas atuais montam grande parte do estado no contexto de templates Django.
2. **Proteger todos os endpoints JSON com autenticação explícita.** Algumas funções `api_*` dependem do usuário autenticado, mas não têm `@login_required` no código atual.
3. **Padronizar HTTP status codes.** Sugestão: `200/201` para sucesso, `400` para validação, `401` para não autenticado, `403` para sem permissão, `404` para recurso inexistente e `500` para falhas internas.
4. **Adicionar CORS somente para origens confiáveis.** Em desenvolvimento, liberar `http://localhost:5173` ou a porta usada pelo Vite; em produção, liberar apenas o domínio do frontend.
5. **Manter `credentials: 'include'` no React** enquanto a autenticação for por sessão Django.
6. **Evitar dados mágicos no backend.** A rota `/api/modal/acao/` usa fallback `2026-03-20` para `data_aplicacao`; o frontend deve sempre enviar a data, e o backend deveria validar ausência explicitamente.
7. **Considerar Django REST Framework.** Para evoluir a API, serializers e viewsets reduzem divergência entre modelos e JSON.
8. **Documentar versões.** Ao estabilizar contratos, prefixar rotas com `/api/v1/` facilita mudanças futuras.

## 10. Checklist mínimo para iniciar o frontend React

- [ ] Confirmar se o React será servido no mesmo domínio do Django ou configurar CORS/CSRF para outro domínio.
- [ ] Implementar helper global de `fetch` com `credentials: 'include'` e `X-CSRFToken`.
- [ ] Criar telas consumindo os endpoints JSON existentes para ações de escrita.
- [ ] Implementar os endpoints JSON de leitura recomendados para substituir as páginas HTML.
- [ ] Validar permissões de coordenador/diretor no frontend apenas para UX; a autorização real deve continuar no backend.
- [ ] Criar testes de integração para os fluxos de permuta, aprovação, construtor e pagamento/devolução.
