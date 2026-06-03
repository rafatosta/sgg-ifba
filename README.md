# SGG IFBA — Sistema de Gestão de Grades

Aplicação web Django para gerenciamento de grades horárias, solicitações de permuta/substituição/liberação de aulas, aprovações, relatórios de carga horária e simulação/exportação de grades em PDF.

## Sumário

- [Requisitos](#requisitos)
- [Variáveis de ambiente](#variáveis-de-ambiente)
- [Execução automatizada com Docker/Podman](#execução-automatizada-com-dockerpodman)
- [Execução local com ambiente virtual](#execução-local-com-ambiente-virtual)
- [Execução com Docker Compose](#execução-com-docker-compose)
- [Primeiro acesso e carga inicial de dados](#primeiro-acesso-e-carga-inicial-de-dados)
- [Rotas principais](#rotas-principais)
- [Requisitos funcionais atuais](#requisitos-funcionais-atuais)
- [Documentação da API para frontend React](#documentação-da-api-para-frontend-react)
- [Comandos úteis](#comandos-úteis)
- [Solução de problemas](#solução-de-problemas)

## Requisitos

### Para execução com container (recomendado)

- Podman ou Docker.
- Python disponível apenas para chamar o script `run.py` (as dependências Python do projeto são instaladas dentro da imagem).

O projeto já possui `Dockerfile`, então a execução recomendada é via container. Isso evita instalar no host dependências nativas como Cairo, `pkg-config`, JPEG, Zlib e FreeType.

### Para execução local sem container

- Python 3.12 ou superior.
- `pip` e `venv` disponíveis no ambiente.
- Dependências de sistema necessárias para geração de PDF/imagens, principalmente Cairo, JPEG, Zlib e FreeType.

Se você optar por rodar sem container, instale também as dependências nativas usadas por pacotes como `pycairo` e `xhtml2pdf`. Exemplos por sistema:

Debian/Ubuntu:

```bash
sudo apt-get update
sudo apt-get install -y gcc python3-dev libcairo2-dev pkg-config libjpeg-dev zlib1g-dev libfreetype6-dev
```

Fedora/RHEL/CentOS/Rocky/AlmaLinux:

```bash
sudo dnf install -y gcc python3-devel cairo-devel pkgconf-pkg-config libjpeg-devel zlib-devel freetype-devel
```

Arch/Manjaro:

```bash
sudo pacman -S --needed base-devel cairo pkgconf libjpeg-turbo zlib freetype2
```

macOS com Homebrew:

```bash
brew install cairo pkg-config jpeg zlib freetype
```

### Para execução com Compose (opcional)

- Docker Compose, `podman compose` ou `podman-compose`.

O projeto também possui `docker-compose.yml` para subir a aplicação com Gunicorn usando Compose.

## Variáveis de ambiente

Crie um arquivo `.env` na raiz do projeto. Você pode começar copiando o arquivo de exemplo:

```bash
cp .env.example .env
```

Variáveis suportadas:

| Variável | Obrigatória? | Descrição |
| --- | --- | --- |
| `SECRET_KEY` | Recomendada | Chave secreta usada pelo Django. Troque em qualquer ambiente compartilhado ou de produção. |
| `EMAIL_DO_SISTEMA` | Recomendada | Conta SMTP remetente usada pelo sistema. |
| `SENHA_DO_EMAIL` | Recomendada | Senha do e-mail ou senha de app SMTP. |

> Observação: se uma variável não for definida, o projeto usa valores padrão de desenvolvimento configurados em `core/settings.py`.

## Execução automatizada com Docker/Podman

Como o projeto já possui `Dockerfile`, esta é a forma recomendada de executar a aplicação. O container instala as dependências nativas e Python dentro da imagem, evitando erros no host como falhas de build do `pycairo` por ausência do Cairo.

A partir da raiz do repositório, execute:

```bash
python run.py
```

Por padrão, o `run.py` usa `--mode container`, tenta usar Podman primeiro e, se não encontrar, usa Docker. O script executa automaticamente as seguintes tarefas:

- Cria `.env` a partir de `.env.example`, se necessário.
- Constrói a imagem a partir do `Dockerfile`.
- Cria/usa um volume nomeado para persistir o SQLite em `/app/data`.
- Executa `python manage.py migrate` dentro do container.
- Inicia o Gunicorn definido no `Dockerfile`.
- Publica a aplicação em `http://127.0.0.1:8000/`.

Acesse:

- Aplicação: <http://127.0.0.1:8000/>
- Admin Django: <http://127.0.0.1:8000/admin/>

Exemplos úteis:

```bash
python run.py --help
python run.py --engine podman
python run.py --engine docker
python run.py --port 8080
python run.py --setup-only
python run.py --skip-migrate
```

Para criar um superusuário usando o script:

```bash
python run.py --createsuperuser
```

Esse comando aplica as migrações no volume de dados e abre um terminal interativo dentro do container. Se preferir executar manualmente, use `-it`; sem isso o Django pula a criação com a mensagem `Superuser creation skipped due to not running in a TTY`.

Com Podman:

```bash
podman run --rm -it --env-file .env -v sgg_ifba_data:/app/data sgg-ifba:latest python manage.py createsuperuser
```

Com Docker:

```bash
docker run --rm -it --env-file .env -v sgg_ifba_data:/app/data sgg-ifba:latest python manage.py createsuperuser
```

Para parar o container iniciado pelo script em outro terminal:

```bash
podman stop sgg_ifba_web
# ou
docker stop sgg_ifba_web
```

## Execução local com ambiente virtual

A execução local sem container continua disponível, mas não é a opção recomendada quando você não quer instalar Cairo e outras bibliotecas nativas diretamente no sistema.

Use:

```bash
python run.py --mode local
```

Nesse modo, o script:

- Valida se o Python atual é 3.12 ou superior.
- Cria o ambiente virtual em `.venv/`, se ele ainda não existir.
- Cria `.env` a partir de `.env.example`, se necessário.
- Cria a pasta `data/` usada pelo SQLite.
- Verifica se `pkg-config` e Cairo estão instalados para evitar erro na instalação do `pycairo`.
- Atualiza o `pip` e instala as dependências de `requirements.txt`.
- Executa `python manage.py migrate`.
- Executa `python manage.py collectstatic --noinput`.
- Inicia o servidor com `python manage.py runserver 0.0.0.0:8000`.

Opções úteis para o modo local:

```bash
python run.py --mode local --skip-install
python run.py --mode local --skip-system-check
python run.py --mode local --skip-migrate --skip-collectstatic
```

Depois da primeira execução local, crie um administrador quando necessário:

```bash
.venv/bin/python manage.py createsuperuser
```

No Windows, use:

```bat
.venv\Scripts\python.exe manage.py createsuperuser
```

## Execução local manual detalhada

A partir da raiz do repositório:

### 1. Criar e ativar o ambiente virtual

```bash
python3.12 -m venv .venv
source .venv/bin/activate
```

Se o comando `python3.12` não existir no seu sistema, use o executável Python compatível disponível, por exemplo `python3`.

### 2. Instalar as dependências Python

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

### 3. Configurar o arquivo `.env`

```bash
cp .env.example .env
```

Edite o `.env` e informe os valores reais quando necessário.

### 4. Criar a pasta do banco SQLite

O banco local fica em `data/db.sqlite3`. Como a pasta `data/` não é versionada, crie-a antes das migrações:

```bash
mkdir -p data
```

### 5. Aplicar as migrações

```bash
python manage.py migrate
```

### 6. Criar um usuário administrador

```bash
python manage.py createsuperuser
```

### 7. Coletar arquivos estáticos

```bash
python manage.py collectstatic --noinput
```

### 8. Subir o servidor de desenvolvimento

```bash
python manage.py runserver 0.0.0.0:8000
```

Acesse:

- Aplicação: <http://127.0.0.1:8000/>
- Admin Django: <http://127.0.0.1:8000/admin/>

## Execução com Docker Compose

O `run.py` usa o `Dockerfile` diretamente por padrão, mas também é possível usar Compose. O `docker-compose.yml` publica a aplicação na porta `80` do host.

### Via `run.py`

Com Docker Compose:

```bash
python run.py --mode container --engine docker --compose
```

Com Podman Compose ou `podman-compose`:

```bash
python run.py --mode container --engine podman --compose
```

### Manualmente com Docker Compose

```bash
cp .env.example .env
docker compose up --build -d
docker compose exec web python manage.py migrate
docker compose run --rm web python manage.py createsuperuser
```

Acesse:

- Aplicação: <http://localhost/>
- Admin Django: <http://localhost/admin/>

Ver logs:

```bash
docker compose logs -f web
```

Parar containers:

```bash
docker compose down
```

Para remover também o volume com o banco SQLite do Docker, use:

```bash
docker compose down -v
```

## Primeiro acesso e carga inicial de dados

Depois de aplicar as migrações e criar o superusuário, acesse `/admin/` para cadastrar ou revisar:

- Professores.
- Disciplinas.
- Horários.
- Turmas.
- Grades horárias.
- Solicitações.

O repositório inclui CSVs de apoio e dois comandos de importação.

### Importar professores

Arquivo esperado: CSV com colunas `nome,email`.

Exemplo usando o arquivo versionado `lista_professores.csv`:

```bash
python manage.py importar_professores lista_professores.csv
```

No container direto com Podman:

```bash
podman run --rm --env-file .env -v sgg_ifba_data:/app/data sgg-ifba:latest python manage.py importar_professores lista_professores.csv
```

No Docker Compose:

```bash
docker compose exec web python manage.py importar_professores lista_professores.csv
```

Esse comando cria usuários Django usando a parte do e-mail antes de `@` como login e a senha padrão `IFBA@2026`.

### Importar disciplinas

Arquivo esperado: CSV com colunas `nome,aulas`.

Exemplo usando o arquivo versionado `lista_disciplinas.csv`:

```bash
python manage.py importar_disciplinas lista_disciplinas.csv
```

No container direto com Podman:

```bash
podman run --rm --env-file .env -v sgg_ifba_data:/app/data sgg-ifba:latest python manage.py importar_disciplinas lista_disciplinas.csv
```

No Docker Compose:

```bash
docker compose exec web python manage.py importar_disciplinas lista_disciplinas.csv
```

### Montar grades

As turmas, horários permitidos e a composição da grade podem ser administrados pelo Django Admin ou pela tela de construtor de grade em `/construtor/`, após login com um usuário autorizado.

## Rotas principais

| Caminho | Finalidade |
| --- | --- |
| `/` | Página inicial autenticada. |
| `/login/` | Login. |
| `/logout/` | Logout. |
| `/admin/` | Administração Django. |
| `/grade/` | Visualização de grade pessoal e por turma. |
| `/construtor/` | Construção/edição da grade. |
| `/aprovacoes/` | Painel de aprovações. |
| `/minhas-solicitacoes/` | Lista de solicitações do usuário logado. |
| `/direcao/carga-horaria/` | Relatório de carga horária. |
| `/simulador/` | Simulador de grade. |
| `/simulador/exportar-pdf/` | Exportação em PDF da simulação. |

## Requisitos funcionais atuais

A lista consolidada dos requisitos funcionais atualmente implementados no software está disponível em [`docs/REQUISITOS_FUNCIONAIS.md`](docs/REQUISITOS_FUNCIONAIS.md).

## Documentação da API para frontend React

A documentação dos contratos HTTP existentes, exemplos de consumo com `fetch`, modelos de dados e recomendações para desacoplar um frontend React está disponível em [`docs/API.md`](docs/API.md).

## Comandos úteis

### Verificar problemas de configuração do Django

```bash
python manage.py check
```

### Criar novas migrações após alterar modelos

```bash
python manage.py makemigrations
python manage.py migrate
```

### Recoletar estáticos

```bash
python manage.py collectstatic --noinput
```

### Abrir shell Django

```bash
python manage.py shell
```

## Solução de problemas

### `unable to open database file`

Crie a pasta do banco antes de rodar as migrações locais:

```bash
mkdir -p data
python manage.py migrate
```

### Dependências Python falham ao instalar pacotes de PDF/imagem

Esse erro geralmente indica ausência dos arquivos de desenvolvimento do Cairo ao rodar sem container. A solução recomendada é usar o `Dockerfile` via Podman/Docker:

```bash
python run.py --mode container
```

Se você realmente quiser executar com ambiente virtual local, instale as dependências nativas do seu sistema operacional e execute `python run.py --mode local` novamente.

Debian/Ubuntu:

```bash
sudo apt-get update
sudo apt-get install -y gcc python3-dev libcairo2-dev pkg-config libjpeg-dev zlib1g-dev libfreetype6-dev
```

Fedora/RHEL/CentOS/Rocky/AlmaLinux:

```bash
sudo dnf install -y gcc python3-devel cairo-devel pkgconf-pkg-config libjpeg-devel zlib-devel freetype-devel
```

Arch/Manjaro:

```bash
sudo pacman -S --needed base-devel cairo pkgconf libjpeg-turbo zlib freetype2
```

macOS com Homebrew:

```bash
brew install cairo pkg-config jpeg zlib freetype
```

No modo local, o `run.py` valida `pkg-config` e Cairo antes de executar `pip install -r requirements.txt`. Caso queira ignorar somente essa validação, rode:

```bash
python run.py --mode local --skip-system-check
```

### E-mails não são enviados

Verifique `EMAIL_DO_SISTEMA` e `SENHA_DO_EMAIL` no `.env`. Para Gmail, normalmente é necessário usar uma senha de app em vez da senha normal da conta.

### A aplicação não abre no container

Se você iniciou via `python run.py` sem `--compose`, confira o container com a engine usada:

```bash
podman ps
podman logs -f sgg_ifba_web
# ou
docker ps
docker logs -f sgg_ifba_web
```

Se você iniciou com Compose, leia os logs:

```bash
docker compose ps
docker compose logs -f web
```
