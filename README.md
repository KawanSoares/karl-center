# Karl Center - WhatsApp Bulk Messenger

Ferramenta de envio em massa de mensagens via WhatsApp Web, com interface gráfica (GUI) e suporte a uso via terminal.

**Importante:** Esta ferramenta utiliza o WhatsApp Web e exige que você esteja logado em sua conta do WhatsApp. Use com responsabilidade e de acordo com os termos de serviço do WhatsApp. O envio de mensagens não solicitadas pode levar ao banimento da sua conta.

---

## Funcionalidades

- **Interface Gráfica (GUI):** Controle tudo por uma interface moderna sem precisar editar arquivos.
- **Modo Terminal (CLI):** Execute diretamente via linha de comando lendo `message.txt` e `numbers.txt`.
- **Envio em Massa:** Envie a mesma mensagem para múltiplos destinatários.
- **Limite de Lote:** Controle quantas mensagens são enviadas por execução.
- **Delays Aleatórios:** Aguarda um intervalo aleatório entre mensagens para imitar comportamento humano.
- **Registro (Log):** Salva o resultado de cada envio em `log_report.csv` (timestamp, número, status, erro).
- **Modo de Teste:** Simula o envio sem abrir o navegador — útil para validar a lista de números.
- **Perfil Chrome persistente:** Mantém o login do WhatsApp Web salvo entre execuções na pasta `chrome_profile/`.

---

## Estrutura dos Arquivos

```
karl-center/
├── automator.py                    # Backend: lógica de envio (Selenium)
├── gui_automator.py                # Frontend: interface gráfica (customtkinter)
├── installer.py                    # Assistente de instalação (GUI wizard)
├── build_karl_center_installer.py  # Script de build do instalador
├── requirements.txt                # Dependências Python
├── message.txt                     # Mensagem a ser enviada (criado por você)
├── numbers.txt                     # Lista de números, um por linha (criado por você)
└── log_report.csv                  # Log gerado automaticamente após o primeiro envio
```

---

## Instalação

### Opção 1 — Instalador compilado (recomendado para usuários finais)

Baixe o instalador correspondente ao seu sistema operacional:

| Sistema | Arquivo |
|---------|---------|
| Windows | `KarlCenterInstaller.exe` |
| Linux   | `KarlCenterInstaller` |

Execute o arquivo e siga o assistente de instalação. O Google Chrome precisa estar instalado para o programa funcionar.

---

### Opção 2 — Direto do código-fonte (para desenvolvedores)

#### Pré-requisitos

- **Python 3.8+** — [python.org](https://www.python.org/downloads/)
- **Google Chrome**

#### Clone e instale

```bash
git clone <URL_DO_REPOSITORIO>
cd karl-center
pip install -r requirements.txt
```

---

## Detecção do Chrome

O Karl Center usa o Selenium Manager (nativo do Selenium 4.6+) para localizar automaticamente o Google Chrome instalado na máquina e baixar o driver correspondente. Isso funciona sem nenhuma configuração para instalações padrão do Chrome (instalador oficial do google.com).

Se o Chrome não for encontrado automaticamente — por exemplo, em instalações via Scoop, que não registram o navegador nos caminhos/registro padrão do Windows — defina a variável de ambiente `KARL_CENTER_CHROME_PATH` apontando para o executável do navegador:

```powershell
[Environment]::SetEnvironmentVariable("KARL_CENTER_CHROME_PATH", "C:\caminho\para\chrome.exe", "User")
```

É preciso abrir um novo terminal (ou reiniciar a sessão) após definir a variável pela primeira vez para que ela seja reconhecida. Uma vez definida no escopo `User`, ela persiste entre reinicializações do computador — não precisa ser configurada novamente. Quando a variável não está definida, a detecção automática padrão é usada normalmente.

---

## Como Usar

### Modo GUI (Recomendado)

```bash
python gui_automator.py
```

1. A janela **Karl Center - WhatsApp Bulk Messenger GUI** será aberta.
2. Cole sua mensagem no campo da esquerda e os números no campo da direita (um por linha, com código do país).
3. Ajuste o **Limite de Envios** e os **Delays (min/max)** no painel de configurações.
4. Clique em **INICIAR ENVIOS**.
5. O Chrome abrirá o WhatsApp Web — aguarde o login ser detectado automaticamente.
6. O log de progresso aparece em tempo real na área verde na parte inferior da janela.

> A GUI carrega automaticamente `message.txt` e `numbers.txt` se esses arquivos já existirem na pasta do projeto.

---

### Modo Terminal (CLI)

1. Crie o arquivo `message.txt` com o texto da mensagem.
2. Crie o arquivo `numbers.txt` com os números, um por linha, incluindo o código do país:
   ```
   5511987654321
   5521912345678
   ```
3. Execute:
   ```bash
   python automator.py
   ```
4. O Chrome abrirá o WhatsApp Web. Após escanear o QR code e ver seus chats, pressione **ENTER** no terminal.
5. O script enviará mensagens para os primeiros 3 números (padrão do CLI). Para alterar, edite a chamada no fim de `automator.py`:
   ```python
   run_bulk_messages(nums, msg, batch_limit=3, min_delay=10, max_delay=20)
   ```

---

## Formato dos Números

Os números devem estar no formato internacional, **sem `+` ou espaços**:

```
5511987654321   # Brasil
14085551234     # EUA
447911123456    # Reino Unido
```

---

## Log de Resultados

Após cada execução, o arquivo `log_report.csv` é criado/atualizado com:

| timestamp | phone_number | status | error |
|-----------|-------------|--------|-------|
| 2026-05-05 10:30:00 | 5511987654321 | SUCCESS | |
| 2026-05-05 10:31:15 | 5521000000000 | FAILURE | timeout |
| 2026-05-05 10:32:00 | 5511999999999 | SIMULATED | |

---

## Build do Instalador (para desenvolvedores)

O script `build_karl_center_installer.py` gera o instalador compilado para a plataforma atual.
Cada desenvolvedor compila para o seu próprio sistema operacional — não há cross-compilation.

### Windows

```bash
python build_karl_center_installer.py
```

Saída: `dist/KarlCenterInstaller.exe`

### Linux / WSL

#### Pré-requisitos (primeira vez)

```bash
# Dependências de build do Tcl/Tk e Python shared lib
sudo apt install tk-dev tcl-dev libffi-dev libssl-dev libbz2-dev \
  libreadline-dev libsqlite3-dev liblzma-dev zlib1g-dev

# Instalar pyenv
curl https://pyenv.run | bash
source ~/.zshrc

# Instalar Python com shared lib habilitada
PYTHON_CONFIGURE_OPTS="--enable-shared" pyenv install 3.12.4
pyenv local 3.12.4
```

#### Build

```bash
python build_karl_center_installer.py
```

Saída: `dist/KarlCenterInstaller`

---

## Hattip

- Inspirado em [anirudhbagri/whatsapp-bulk-messenger](https://github.com/anirudhbagri/whatsapp-bulk-messenger)
