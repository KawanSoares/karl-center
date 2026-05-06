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
├── automator.py        # Backend: lógica de envio (Selenium)
├── gui_automator.py    # Frontend: interface gráfica (customtkinter)
├── requirements.txt    # Dependências Python
├── message.txt         # Mensagem a ser enviada (criado por você)
├── numbers.txt         # Lista de números, um por linha (criado por você)
└── log_report.csv      # Log gerado automaticamente após o primeiro envio
```

---

## Instalação

### 1. Pré-requisitos

- **Python 3.8+** — [python.org](https://www.python.org/downloads/) (marque "Add Python to PATH" na instalação)
- **Google Chrome** — necessário para automação via Selenium

### 2. Clone o repositório

```bash
git clone <URL_DO_REPOSITORIO>
cd karl-center
```

### 3. Instale as dependências

```bash
pip install -r requirements.txt
```

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

## Hattip

- Inspirado em [anirudhbagri/whatsapp-bulk-messenger](https://github.com/anirudhbagri/whatsapp-bulk-messenger)
