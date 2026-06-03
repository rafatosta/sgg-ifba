"""Automatiza a preparação e execução do projeto SGG IFBA."""

import argparse
import os
import platform
import shutil
import subprocess
import sys
import textwrap
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent
VENV_DIR = PROJECT_DIR / ".venv"
DATA_DIR = PROJECT_DIR / "data"
REQUIREMENTS_FILE = PROJECT_DIR / "requirements.txt"
ENV_FILE = PROJECT_DIR / ".env"
ENV_EXAMPLE_FILE = PROJECT_DIR / ".env.example"

IMAGE_NAME = "sgg-ifba:latest"
CONTAINER_NAME = "sgg_ifba_web"
CONTAINER_DATA_VOLUME = "sgg_ifba_data"
CONTAINER_PORT = "8000"

IS_WINDOWS = platform.system() == "Windows"

if IS_WINDOWS:
    PYTHON_BIN = VENV_DIR / "Scripts" / "python.exe"
    PIP_BIN = VENV_DIR / "Scripts" / "pip.exe"
    ACTIVATE_SCRIPT = VENV_DIR / "Scripts" / "activate.bat"
else:
    PYTHON_BIN = VENV_DIR / "bin" / "python"
    PIP_BIN = VENV_DIR / "bin" / "pip"
    ACTIVATE_SCRIPT = VENV_DIR / "bin" / "activate"


def command_exists(command):
    """Verifica se um comando existe no PATH."""
    return shutil.which(command) is not None


def run_command(command, description):
    """Executa um comando exibindo uma mensagem padronizada."""
    print(f"\n==> {description}")
    print("$ " + " ".join(str(part) for part in command))
    subprocess.run(command, cwd=PROJECT_DIR, check=True)


def ensure_env_file():
    """Cria o .env a partir do .env.example, se necessário."""
    if ENV_FILE.exists():
        print("\n==> Arquivo .env já existe")
        return

    if ENV_EXAMPLE_FILE.exists():
        shutil.copyfile(ENV_EXAMPLE_FILE, ENV_FILE)
        print("\n==> Arquivo .env criado a partir de .env.example")
        print("==> Revise SECRET_KEY, EMAIL_DO_SISTEMA e SENHA_DO_EMAIL quando necessário")
    else:
        print("\n==> .env.example não encontrado; seguindo com os padrões do settings.py")


def ensure_python_version():
    """Garante uma versão compatível com Django 6 para execução local."""
    if sys.version_info < (3, 12):
        current_version = ".".join(str(part) for part in sys.version_info[:3])
        print(
            "Python 3.12 ou superior é necessário para executar localmente. "
            f"Versão atual: {current_version}."
        )
        print("Dica: use `python run.py --mode container` para executar via Docker/Podman.")
        sys.exit(1)


def ensure_virtualenv():
    """Cria o ambiente virtual quando ele ainda não existe."""
    if not VENV_DIR.exists():
        run_command(
            [sys.executable, "-m", "venv", str(VENV_DIR)],
            "Criando ambiente virtual",
        )
    else:
        print(f"\n==> Ambiente virtual já existe em: {VENV_DIR}")

    print(f"==> Python do ambiente virtual: {PYTHON_BIN}")
    print(f"==> Script de ativação manual: {ACTIVATE_SCRIPT}")


def ensure_data_dir():
    """Garante a pasta usada pelo banco SQLite na execução local."""
    DATA_DIR.mkdir(exist_ok=True)
    print(f"\n==> Pasta do banco SQLite garantida em: {DATA_DIR}")


def pkg_config_has(package):
    """Verifica uma dependência nativa via pkg-config."""
    if not command_exists("pkg-config"):
        return False

    return subprocess.run(
        ["pkg-config", "--exists", package],
        cwd=PROJECT_DIR,
        check=False,
    ).returncode == 0


def linux_distribution():
    """Obtém o ID da distribuição Linux a partir de /etc/os-release."""
    os_release = Path("/etc/os-release")
    if not os_release.exists():
        return ""

    for line in os_release.read_text(encoding="utf-8", errors="ignore").splitlines():
        if line.startswith("ID="):
            return line.split("=", 1)[1].strip().strip('"').lower()

    return ""


def system_dependency_hint():
    """Retorna comandos de instalação para dependências nativas conhecidas."""
    system = platform.system()

    if system == "Linux":
        distro = linux_distribution()

        if distro in {"fedora", "rhel", "centos", "rocky", "almalinux"}:
            return "sudo dnf install -y gcc python3-devel cairo-devel pkgconf-pkg-config libjpeg-devel zlib-devel freetype-devel"

        if distro in {"arch", "manjaro"}:
            return "sudo pacman -S --needed base-devel cairo pkgconf libjpeg-turbo zlib freetype2"

        if distro in {"opensuse", "opensuse-leap", "opensuse-tumbleweed", "sles"}:
            return "sudo zypper install -y gcc python3-devel cairo-devel pkg-config libjpeg-devel zlib-devel freetype2-devel"

        return "sudo apt-get update && sudo apt-get install -y gcc python3-dev libcairo2-dev pkg-config libjpeg-dev zlib1g-dev libfreetype6-dev"

    if system == "Darwin":
        return "brew install cairo pkg-config jpeg zlib freetype"

    if system == "Windows":
        return "Instale as dependências de build do Python/Cairo ou prefira executar com Docker/Podman."

    return "Instale Cairo, pkg-config, compilador C e headers de desenvolvimento do Python pelo gerenciador de pacotes do seu sistema."


def ensure_system_dependencies(skip_system_check):
    """Valida dependências nativas exigidas por pacotes como pycairo na execução local."""
    if skip_system_check:
        print("\n==> Verificação de dependências do sistema ignorada por opção do usuário")
        return

    missing = []

    if not command_exists("pkg-config"):
        missing.append("pkg-config")

    if not pkg_config_has("cairo"):
        missing.append("cairo")

    if not missing:
        print("\n==> Dependências nativas verificadas: pkg-config e cairo encontrados")
        return

    print("\nERRO: dependências nativas ausentes para instalar os pacotes Python localmente.")
    print(f"Itens não encontrados: {', '.join(missing)}")
    print(
        textwrap.dedent(
            f"""
            O pacote pycairo precisa dos arquivos de desenvolvimento do Cairo.
            Instale as dependências do sistema e execute novamente:

                {system_dependency_hint()}

            Alternativas:

                python run.py --mode container
                python run.py --mode local --skip-system-check
            """
        ).strip()
    )
    sys.exit(1)


def install_dependencies(skip_install, skip_system_check):
    """Atualiza pip e instala requirements.txt na execução local."""
    if skip_install:
        print("\n==> Instalação de dependências ignorada por opção do usuário")
        return

    ensure_system_dependencies(skip_system_check)

    run_command(
        [str(PYTHON_BIN), "-m", "pip", "install", "--upgrade", "pip"],
        "Atualizando pip no ambiente virtual",
    )

    if not REQUIREMENTS_FILE.exists():
        print("\n==> requirements.txt não encontrado; pulei a instalação de dependências")
        return

    run_command(
        [str(PIP_BIN), "install", "-r", str(REQUIREMENTS_FILE)],
        "Instalando dependências do projeto",
    )


def run_django_setup(skip_migrate, skip_collectstatic):
    """Executa tarefas comuns de preparação do Django localmente."""
    if skip_migrate:
        print("\n==> Migrações ignoradas por opção do usuário")
    else:
        run_command(
            [str(PYTHON_BIN), "manage.py", "migrate"],
            "Aplicando migrações do banco de dados",
        )

    if skip_collectstatic:
        print("\n==> Coleta de arquivos estáticos ignorada por opção do usuário")
    else:
        run_command(
            [str(PYTHON_BIN), "manage.py", "collectstatic", "--noinput"],
            "Coletando arquivos estáticos",
        )


def run_local(args):
    """Prepara o ambiente local e inicia o servidor de desenvolvimento."""
    ensure_python_version()
    ensure_virtualenv()
    ensure_env_file()
    ensure_data_dir()
    install_dependencies(args.skip_install, args.skip_system_check)
    run_django_setup(args.skip_migrate, args.skip_collectstatic)

    if args.setup_only:
        print("\n==> Setup local concluído. Servidor não iniciado por opção do usuário.")
        return

    address = f"{args.host}:{args.port}"
    print("\n==> Servidor disponível após inicialização:")
    print(f"    Aplicação: http://127.0.0.1:{args.port}/")
    print(f"    Admin:      http://127.0.0.1:{args.port}/admin/")
    run_command(
        [str(PYTHON_BIN), "manage.py", "runserver", address],
        "Iniciando servidor de desenvolvimento local",
    )


def detect_container_engine(preferred_engine):
    """Escolhe Podman ou Docker para execução em container."""
    if preferred_engine != "auto":
        if command_exists(preferred_engine):
            return preferred_engine

        print(f"\nERRO: engine solicitada não encontrada no PATH: {preferred_engine}")
        sys.exit(1)

    for engine in ("podman", "docker"):
        if command_exists(engine):
            return engine

    print("\nERRO: Podman ou Docker não encontrado no PATH.")
    print("Instale Podman/Docker ou execute localmente com: python run.py --mode local")
    sys.exit(1)


def compose_command(engine):
    """Retorna o comando de Compose disponível para Docker ou Podman."""
    if engine == "docker":
        return ["docker", "compose"]

    if command_exists("podman-compose"):
        return ["podman-compose"]

    if subprocess.run(
        ["podman", "compose", "version"],
        cwd=PROJECT_DIR,
        check=False,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    ).returncode == 0:
        return ["podman", "compose"]

    return None


def remove_existing_container(engine, container_name):
    """Remove um container anterior com o mesmo nome, se existir."""
    exists = subprocess.run(
        [engine, "container", "inspect", container_name],
        cwd=PROJECT_DIR,
        check=False,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    ).returncode == 0

    if exists:
        run_command(
            [engine, "rm", "-f", container_name],
            f"Removendo container anterior ({container_name})",
        )


def run_container_management_command(args, engine, management_command, description):
    """Executa um comando de gerenciamento Django em um container interativo."""
    ensure_env_file()
    run_command(
        [engine, "build", "-t", args.image, "."],
        f"Construindo imagem com {engine}",
    )

    if not args.skip_migrate:
        run_command(
            [
                engine,
                "run",
                "--rm",
                "--env-file",
                str(ENV_FILE),
                "-v",
                f"{args.volume}:/app/data",
                args.image,
                "python",
                "manage.py",
                "migrate",
            ],
            "Aplicando migrações antes do comando interativo",
        )

    run_command(
        [
            engine,
            "run",
            "--rm",
            "-it",
            "--env-file",
            str(ENV_FILE),
            "-v",
            f"{args.volume}:/app/data",
            args.image,
            "python",
            "manage.py",
            *management_command,
        ],
        description,
    )


def run_container_with_engine(args, engine):
    """Executa o projeto usando diretamente Dockerfile com Podman/Docker."""
    if args.createsuperuser:
        run_container_management_command(
            args,
            engine,
            ["createsuperuser"],
            "Criando superusuário em container interativo",
        )
        return

    ensure_env_file()

    run_command(
        [engine, "build", "-t", args.image, "."],
        f"Construindo imagem com {engine}",
    )

    if not args.skip_migrate:
        run_command(
            [
                engine,
                "run",
                "--rm",
                "--env-file",
                str(ENV_FILE),
                "-v",
                f"{args.volume}:/app/data",
                args.image,
                "python",
                "manage.py",
                "migrate",
            ],
            "Aplicando migrações no volume do container",
        )
    else:
        print("\n==> Migrações no container ignoradas por opção do usuário")

    if args.setup_only:
        print("\n==> Imagem/volume preparados. Container web não iniciado por opção do usuário.")
        return

    remove_existing_container(engine, args.container_name)

    print("\n==> Servidor disponível após inicialização:")
    print(f"    Aplicação: http://127.0.0.1:{args.port}/")
    print(f"    Admin:      http://127.0.0.1:{args.port}/admin/")
    run_command(
        [
            engine,
            "run",
            "--rm",
            "--name",
            args.container_name,
            "--env-file",
            str(ENV_FILE),
            "-p",
            f"{args.port}:{CONTAINER_PORT}",
            "-v",
            f"{args.volume}:/app/data",
            args.image,
        ],
        f"Iniciando aplicação com {engine}",
    )


def run_container_with_compose(args, engine):
    """Executa o projeto usando docker compose ou podman compose."""
    ensure_env_file()
    command = compose_command(engine)

    if command is None:
        print("\nERRO: compose não encontrado para Podman.")
        print("Use `python run.py --mode container --no-compose` ou instale podman-compose.")
        sys.exit(1)

    if args.createsuperuser:
        if not args.skip_migrate:
            run_command(
                [*command, "run", "--rm", "web", "python", "manage.py", "migrate"],
                "Aplicando migrações antes de criar superusuário",
            )
        run_command(
            [*command, "run", "--rm", "web", "python", "manage.py", "createsuperuser"],
            "Criando superusuário em serviço Compose interativo",
        )
        return

    run_command(
        [*command, "up", "--build", "-d"],
        f"Construindo e subindo serviços com {' '.join(command)}",
    )

    if not args.skip_migrate:
        run_command(
            [*command, "exec", "web", "python", "manage.py", "migrate"],
            "Aplicando migrações no serviço web",
        )
    else:
        print("\n==> Migrações no container ignoradas por opção do usuário")

    print("\n==> Serviços iniciados via Compose.")
    print("    docker-compose.yml publica a aplicação em: http://127.0.0.1/")
    print(f"    Para acompanhar logs: {' '.join(command)} logs -f web")


def run_container(args):
    """Executa o projeto em container usando Podman ou Docker."""
    engine = detect_container_engine(args.engine)
    print(f"\n==> Engine de container selecionada: {engine}")

    if args.compose:
        run_container_with_compose(args, engine)
    else:
        run_container_with_engine(args, engine)


def parse_args():
    parser = argparse.ArgumentParser(
        description="Prepara e executa o projeto Django SGG IFBA. Por padrão usa container."
    )
    parser.add_argument(
        "--mode",
        choices=("container", "local"),
        default=os.environ.get("RUN_MODE", "container"),
        help="Modo de execução. Padrão: container",
    )
    parser.add_argument(
        "--engine",
        choices=("auto", "podman", "docker"),
        default=os.environ.get("CONTAINER_ENGINE", "auto"),
        help="Engine para o modo container. Padrão: auto (prefere Podman, depois Docker).",
    )
    parser.add_argument(
        "--compose",
        action="store_true",
        help="No modo container, usa docker compose/podman compose em vez de podman/docker build/run direto.",
    )
    parser.add_argument(
        "--host",
        default=os.environ.get("RUNSERVER_HOST", "0.0.0.0"),
        help="Host usado apenas no modo local. Padrão: 0.0.0.0",
    )
    parser.add_argument(
        "--port",
        default=os.environ.get("RUNSERVER_PORT", "8000"),
        help="Porta publicada no host. Padrão: 8000",
    )
    parser.add_argument(
        "--image",
        default=os.environ.get("CONTAINER_IMAGE", IMAGE_NAME),
        help=f"Nome da imagem no modo container. Padrão: {IMAGE_NAME}",
    )
    parser.add_argument(
        "--container-name",
        default=os.environ.get("CONTAINER_NAME", CONTAINER_NAME),
        help=f"Nome do container no modo container. Padrão: {CONTAINER_NAME}",
    )
    parser.add_argument(
        "--volume",
        default=os.environ.get("CONTAINER_DATA_VOLUME", CONTAINER_DATA_VOLUME),
        help=f"Volume de dados no modo container. Padrão: {CONTAINER_DATA_VOLUME}",
    )
    parser.add_argument(
        "--createsuperuser",
        action="store_true",
        help="No modo container, abre um terminal interativo para criar superusuário e encerra.",
    )
    parser.add_argument(
        "--skip-install",
        action="store_true",
        help="No modo local, não atualiza pip nem instala requirements.txt.",
    )
    parser.add_argument(
        "--skip-system-check",
        action="store_true",
        help="No modo local, não verifica Cairo/pkg-config antes do pip install.",
    )
    parser.add_argument(
        "--skip-migrate",
        action="store_true",
        help="Não executa python manage.py migrate.",
    )
    parser.add_argument(
        "--skip-collectstatic",
        action="store_true",
        help="No modo local, não executa python manage.py collectstatic --noinput.",
    )
    parser.add_argument(
        "--setup-only",
        action="store_true",
        help="Prepara ambiente/imagem, mas não inicia o servidor.",
    )
    return parser.parse_args()


def main():
    args = parse_args()

    print("SGG IFBA — execução automatizada")
    print(f"Sistema Operacional: {platform.system()}")
    print(f"Diretório do projeto: {PROJECT_DIR}")

    if args.mode == "container":
        run_container(args)
    else:
        run_local(args)


if __name__ == "__main__":
    main()
