# WhatsApp Bulk Messenger

This script allows you to send bulk messages to a list of phone numbers via WhatsApp. It automates the process of sending messages, making it easier to communicate with many contacts at once.

**Important:** This tool uses WhatsApp Web and requires you to be logged in to your WhatsApp account on your computer. Always use this tool responsibly and in accordance with WhatsApp's terms of service. Sending unsolicited messages can lead to your WhatsApp account being banned.

## Features:

- **Bulk Messaging:** Send the same message to multiple recipients.
- **Customizable Messages:** Write your own message in a `message.txt` file.
- **Phone Number List:** Provide phone numbers in a `numbers.txt` file.
- **Logging:** Records the status of each message sent (success, failure, simulated) in a `log_report.csv` file.
- **Test Mode:** Allows you to simulate the sending process without actually sending messages.
- **Delay between messages:** Random delays to mimic human behavior and avoid WhatsApp detection.
- **Batch Limit:** Control how many messages are sent in a single run.

---

## Installation and Usage (English)

### 1. Prerequisites:

- **Python:** You need to have Python installed on your computer. You can download it from [python.org](https://www.python.org/downloads/). During installation, make sure to check the box that says "Add Python to PATH".
- **Google Chrome:** This script uses Google Chrome for automation. Make sure it's installed on your computer.
- **WhatsApp Account:** You need an active WhatsApp account.

### 2. Project Setup:

1.  **Clone the repository:** Open your command prompt or terminal and run the following command to download the project files:

    ```bash
    git clone <URL_OF_YOUR_GITHUB_REPOSITORY>
    cd <YOUR_PROJECT_FOLDER_NAME>
    ```

    _(Replace `<URL_OF_YOUR_GITHUB_REPOSITORY>` with the actual URL of your GitHub repository and `<YOUR_PROJECT_FOLDER_NAME>` with the name of the folder that is created after cloning.)_

2.  **Install Dependencies:** Navigate to the project folder in your terminal and install the required Python libraries using pip:

    ```bash
    pip install -r requirements.txt
    ```

    _(This command will read the `requirements.txt` file and install all necessary packages automatically.)_

3.  **Create `message.txt`:** Inside the project folder, create a new text file named `message.txt`. Write the message you want to send to all your contacts inside this file.

    - _Example `message.txt` content:_
      ```
      Hello! This is a bulk message from my new project. Hope you are doing well!
      ```

4.  **Create `numbers.txt`:** Inside the project folder, create another text file named `numbers.txt`. Add the phone numbers you want to send messages to, one number per line. Make sure to include the country code.
    - _Example `numbers.txt` content:_
      ```
      14085551234
      447911123456
      5511987654321
      ```

### 3. How to Use:

1.  **Configure Settings (Optional):**

    - Open the `whatsapp_bulk_sender.py` script in a text editor (like VS Code, Notepad++, or even the default Notepad).
    - **`TEST_MODE = True`**: By default, the script is in `TEST_MODE`. This means it will simulate sending messages and log them without actually sending anything. This is highly recommended for your first run to ensure everything is set up correctly! To send real messages, change this line to `TEST_MODE = False`.
    - **`BATCH_LIMIT`**: This sets the maximum number of messages to send in one run. For example, `BATCH_LIMIT = 5` will send messages to only the first 5 unprocessed numbers found in `numbers.txt`. If you want to send to all numbers at once, you can set this to a very high number or the total count of numbers.
    - **`MIN_DELAY` and `MAX_DELAY`**: These control the random waiting time (in seconds) between sending each message. The default values (10-20 seconds) are set to mimic human behavior and help avoid WhatsApp's automated detection systems. You can adjust these if needed, but it's generally safer to keep them within a reasonable range.

2.  **Execute the Script:**

    - Open your command prompt or terminal.
    - Navigate to the project folder using the `cd` command (e.g., `cd whatsapp-bulk-messenger`).
    - Run the script using the following command:
      ```bash
      python whatsapp_bulk_sender.py
      ```

3.  **Log in to WhatsApp Web:**

    - If you set `TEST_MODE = False`, a Chrome browser window will automatically open and navigate to WhatsApp Web (`web.whatsapp.com`).
    - You will see a QR code. Open your WhatsApp app on your phone, go to "Settings" > "Linked Devices," and scan the QR code shown in the browser.
    - Once your WhatsApp chats are visible in the browser window, return to your command prompt/terminal and press the `ENTER` key.

4.  **Monitor the Process:**

    - The script will now begin sending messages (or simulating them if `TEST_MODE` is still `True`).
    - You will see status updates directly in the terminal, indicating which number is being processed and whether the message was sent successfully or encountered an error.
    - A file named `log_report.csv` will be created or updated in the project folder. This file logs the timestamp, phone number, status (SUCCESS, FAILURE, SIMULATED), and any error messages for each attempt.

5.  **Continuing or Rerunning:**
    - If the script stops before processing all numbers (e.g., because you reached the `BATCH_LIMIT` or encountered an error), you can simply run the script again using `python whatsapp_bulk_sender.py`.
    - The script automatically checks the `log_report.csv` file and skips any numbers that were already successfully processed, allowing you to resume where you left off.
    - **Important:** Do not close the Chrome browser window that the script opens while it's running, and do not log out of WhatsApp Web on your computer until the script has finished its execution.

---

####

- Hattip to Anirudh @ https://github.com/anirudhbagri/whatsapp-bulk-messenger

---

# Mensageiro em Massa do WhatsApp

Este script permite que você envie mensagens em massa para uma lista de números de telefone via WhatsApp. Ele automatiza o processo de envio de mensagens, facilitando a comunicação com vários contatos ao mesmo tempo.

**Importante:** Esta ferramenta utiliza o WhatsApp Web e exige que você esteja logado em sua conta do WhatsApp em seu computador. Sempre use esta ferramenta de forma responsável e de acordo com os termos de serviço do WhatsApp. O envio de mensagens não solicitadas pode levar ao banimento da sua conta do WhatsApp.

## Funcionalidades:

- **Mensagens em Massa:** Envie a mesma mensagem para vários destinatários.
- **Mensagens Personalizáveis:** Escreva sua própria mensagem em um arquivo `message.txt`.
- **Lista de Números de Telefone:** Forneça os números de telefone em um arquivo `numbers.txt`.
- **Registro (Log):** Registra o status de cada mensagem enviada (sucesso, falha, simulado) em um arquivo `log_report.csv`.
- **Modo de Teste:** Permite simular o processo de envio sem realmente enviar as mensagens.
- **Atraso entre mensagens:** Atrasos aleatórios para imitar o comportamento humano e evitar a detecção pelo WhatsApp.
- **Limite de Lote:** Controle quantas mensagens são enviadas em uma única execução.

---

## Instalação e Uso (Português)

### 1. Pré-requisitos:

- **Python:** Você precisa ter o Python instalado em seu computador. Você pode baixá-lo em [python.org](https://www.python.org/downloads/). Durante a instalação, certifique-se de marcar a caixa que diz "Add Python to PATH".
- **Google Chrome:** Este script usa o Google Chrome para automação. Certifique-se de que ele esteja instalado em seu computador.
- **Conta do WhatsApp:** Você precisa de uma conta ativa do WhatsApp.

### 2. Configuração do Projeto:

1.  **Clone o repositório:** Abra seu prompt de comando ou terminal e execute o seguinte comando para baixar os arquivos do projeto:

    ```bash
    git clone <URL_DO_SEU_REPOSITORIO_GITHUB>
    cd <NOME_DA_PASTA_DO_SEU_PROJETO>
    ```

    _(Substitua `<URL_DO_SEU_REPOSITORIO_GITHUB>` pela URL real do seu repositório GitHub e `<NOME_DA_PASTA_DO_SEU_PROJETO>` pelo nome da pasta que é criada após o clone.)_

2.  **Instale as Dependências:** Navegue até a pasta do projeto em seu terminal e instale as bibliotecas Python necessárias usando pip:

    ```bash
    pip install -r requirements.txt
    ```

    _(Este comando lerá o arquivo `requirements.txt` e instalará todos os pacotes necessários automaticamente.)_

3.  **Crie `message.txt`:** Dentro da pasta do projeto, crie um novo arquivo de texto chamado `message.txt`. Escreva a mensagem que você deseja enviar para todos os seus contatos dentro deste arquivo.

    - _Exemplo de conteúdo de `message.txt`:_
      ```
      Olá! Esta é uma mensagem em massa do meu novo projeto. Espero que você esteja bem!
      ```

4.  **Crie `numbers.txt`:** Dentro da pasta do projeto, crie outro arquivo de texto chamado `numbers.txt`. Adicione os números de telefone para os quais você deseja enviar mensagens, um número por linha. Certifique-se de incluir o código do país.
    - _Exemplo de conteúdo de `numbers.txt`:_
      ```
      14085551234
      447911123456
      5511987654321
      ```

### 3. Como Usar:

1.  **Configure as Definições (Opcional):**

    - Abra o script `whatsapp_bulk_sender.py` em um editor de texto (como VS Code, Notepad++, ou o Bloco de Notas padrão).
    - **`TEST_MODE = True`**: Por padrão, o script está no `TEST_MODE`. Isso significa que ele simulará o envio de mensagens e as registrará sem enviar nada de fato. Isso é altamente recomendado para sua primeira execução, para garantir que tudo está configurado corretamente! Para enviar mensagens reais, mude esta linha para `TEST_MODE = False`.
    - **`BATCH_LIMIT`**: Isso define o número máximo de mensagens a serem enviadas em uma única execução. Por exemplo, `BATCH_LIMIT = 5` enviará mensagens apenas para os 5 primeiros números não processados encontrados em `numbers.txt`. Se você quiser enviar para todos os números de uma vez, pode definir este valor para um número muito alto ou a contagem total de números.
    - **`MIN_DELAY` e `MAX_DELAY`**: Estes controlam o tempo de espera aleatório (em segundos) entre o envio de cada mensagem. Os valores padrão (10-20 segundos) são definidos para imitar o comportamento humano e ajudar a evitar os sistemas de detecção automática do WhatsApp. Você pode ajustá-los se necessário, mas geralmente é mais seguro mantê-los dentro de uma faixa razoável.

2.  **Execute o Script:**

    - Abra seu prompt de comando ou terminal.
    - Navegue até a pasta do projeto usando o comando `cd` (por exemplo, `cd mensageiro-whatsapp-em-massa`).
    - Execute o script usando o seguinte comando:
      ```bash
      python whatsapp_bulk_sender.py
      ```

3.  **Faça login no WhatsApp Web:**

    - Se você definiu `TEST_MODE = False`, uma janela do navegador Chrome será aberta automaticamente e acessará o WhatsApp Web (`web.whatsapp.com`).
    - Você verá um código QR. Abra o aplicativo WhatsApp no seu telefone, vá para "Configurações" > "Aparelhos conectados" e escaneie o código QR exibido no navegador.
    - Assim que seus chats do WhatsApp estiverem visíveis na janela do navegador, retorne ao seu prompt de comando/terminal e pressione a tecla `ENTER`.

4.  **Monitore o Processo:**

    - O script agora começará a enviar mensagens (ou simulá-las se `TEST_MODE` ainda for `True`).
    - Você verá atualizações de status diretamente no terminal, indicando qual número está sendo processado e se a mensagem foi enviada com sucesso ou encontrou um erro.
    - Um arquivo chamado `log_report.csv` será criado ou atualizado na pasta do projeto. Este arquivo registra o carimbo de data/hora, o número de telefone, o status (SUCESSO, FALHA, SIMULADO) e quaisquer mensagens de erro para cada tentativa.

5.  **Continuando ou Reexecutando:**
    - Se o script parar antes de processar todos os números (por exemplo, porque você atingiu o `BATCH_LIMIT` ou encontrou um erro), você pode simplesmente executar o script novamente usando `python whatsapp_bulk_sender.py`.
    - O script verifica automaticamente o arquivo `log_report.csv` e pula quaisquer números que já foram processados com sucesso, permitindo que você continue de onde parou.
    - **Importante:** Não feche a janela do navegador Chrome que o script abrir enquanto ele estiver em execução, e não saia do WhatsApp Web no seu computador até que o script termine sua execução.

---
