# Contador de Produção Não-Intrusivo

## Identificação do Candidato

- **Nome completo:** Guilherme Emetério Santos Lima
- **GitHub:** [@DankAlighieri](https://github.com/DankAlighieri)

## Visão Geral da Solução

O projeto simula um contador de produção para esteiras industriais que não possuem CLP. Um sensor óptico LDR identifica a passagem das peças pela variação de luminosidade, enquanto um ESP32 processa os eventos e envia os resultados pela interface serial.

O sistema oferece três funções principais:

- contar uma peça depois que ela atravessa completamente o ponto de leitura;
- alertar quando uma obstrução permanece por 5 segundos, indicando uma microparada;
- zerar os estados do turno por meio de um botão físico.

O sistema se comunica com o mundo através de um terminal serial.

## Arquitetura do Sistema Embarcado

O firmware está concentrado em `src/main.py` e mantém um loop principal não bloqueante, executado a cada 10 ms. As responsabilidades foram separadas em funções curtas:

- `debouncing()`: estabiliza a leitura do botão antes de atualizar seu estado;
- `resetar_contadores()`: limpa a contagem e os estados associados ao turno;
- `calcular_percentual_luz()`: normaliza a leitura de 12 bits do ADC;
- `atualizar_contagem()`: controla a entrada e a saída de uma peça no sensor;
- `verificar_microparada()`: compara o tempo de obstrução com o limite configurado.

### Estados principais

| Estado | Finalidade |
|---|---|
| `counter` | Armazena o total de peças concluídas no turno |
| `objetoContado` | Indica que há uma peça bloqueando o sensor |
| `temporizadorBloqueio` | Guarda o instante em que a obstrução começou |
| `microparada` | Evita alertas repetidos durante a mesma obstrução |
| `resetado` | Controla uma única execução do reset por acionamento |

## Componentes Utilizados na Simulação

| Componente | Identificador | Conexão | Função |
|---|---|---|---|
| ESP32 DevKit C v4 | `esp` | — | Executa o firmware MicroPython |
| Sensor fotorresistor | `ldr1` | Saída analógica no GPIO 34 | Detecta a variação de luz causada pela passagem da peça |
| Botão de pressão | `btn1` | GPIO 18 e GND | Solicita o reset do turno |
| Monitor serial | `$serialMonitor` | UART RX/TX | Exibe inicialização, contagem, alerta e confirmação de reset |

O botão utiliza o resistor de pull-up interno do ESP32. Por isso, seu nível lógico é baixo quando pressionado. O ADC do LDR utiliza atenuação de 11 dB para trabalhar com a faixa de entrada disponível no ESP32.

## Decisões Técnicas Relevantes

- **Detecção por transição:** a peça é marcada quando bloqueia a luz, mas a contagem só é incrementada quando a iluminação retorna. Isso evita contar várias vezes o mesmo objeto.
- **Temporização não bloqueante:** `ticks_ms()` e `ticks_diff()` monitoram a duração da obstrução sem interromper as leituras do botão ou do LDR.
- **Debounce por software:** uma mudança no botão precisa permanecer estável durante 50 ms para ser aceita.
- **Alerta único:** o estado `microparada` garante que uma mesma obstrução gere somente um alerta.
- **Parâmetros centralizados:** pinos, limite de luminosidade, tempos e resolução do ADC ficam declarados como constantes no início do arquivo.
- **Mensagens compatíveis com o CI:** os textos enviados pela serial preservam a grafia exigida pelos testes automatizados.

### Parâmetros do firmware

| Parâmetro | Valor |
|---|---:|
| Pino do LDR | GPIO 34 |
| Pino do botão | GPIO 18 |
| Limite normalizado de detecção | 50% |
| Tempo de debounce | 50 ms |
| Limite para microparada | 5.000 ms |
| Intervalo do loop principal | 10 ms |

## Estrutura do Projeto

```text
.
├── binaries/              # Bootloader, tabela de partições e MicroPython
├── scenarios/
│   ├── light/             # Cenários automatizados do Wokwi CI
│   └── LIGHT.md           # Especificação do desafio selecionado
├── src/
│   ├── main.py            # Firmware do contador de produção
│   └── build_fs.py        # Gerador local da imagem LittleFS
├── diagram.json           # Circuito da simulação
├── Dockerfile             # Build reproduzível da imagem LittleFS
├── flasher_args.json      # Mapeamento dos binários na memória do ESP32
├── requirements.txt       # Dependências das ferramentas locais
└── wokwi.toml             # Configuração da simulação Wokwi
```

## Execução e Validação

### Ambiente local

Requisitos:

- Python 3;
- Docker, caso seja utilizado o mesmo processo de build da integração contínua;
- extensão Wokwi para VS Code e uma chave de acesso válida.

Instale as dependências:

```bash
pip install -r requirements.txt
```

Para gerar `fs.bin` localmente com o script Python:

```bash
python src/build_fs.py
```

Também é possível reproduzir o build usado pelo GitHub Actions:

```bash
docker build -t esp32-builder .
docker run --name esp32-fs-builder esp32-builder
docker cp esp32-fs-builder:/fs.bin .
```

Depois de gerar a imagem, abra o projeto no VS Code e inicie a simulação pela extensão Wokwi.

### Cenários automatizados

O pipeline executa três cenários:

| Cenário | Estímulo | Resultado esperado |
|---|---|---|
| Contagem normal | 800 lux → 50 lux → 800 lux | `Peca detectada! Total: 1` |
| Microparada | 50 lux por pelo menos 5 segundos | `Alerta: Micro-parada detectada!` |
| Reset do turno | Pressionamento e liberação do botão | `Turno resetado com sucesso. Contadores zerados.` |

## Resultados Obtidos

O firmware atende aos comportamentos definidos para o desafio:

- inicializa o sistema e confirma a inicialização pela serial;
- detecta a passagem completa de peças e mantém a contagem acumulada;
- identifica uma obstrução contínua sem bloquear o loop principal;
- emite somente um alerta por microparada;
- aplica debounce ao botão e limpa todos os estados do turno;
- evita mensagens repetidas de reset enquanto o botão permanece solto.

## Comentários Adicionais

A solução usa limites fixos adequados à simulação. Em uma aplicação industrial real, seria necessário calibrar o limiar do sensor conforme a iluminação do ambiente e adicionar proteção elétrica às entradas. Como evolução, o projeto poderia armazenar a contagem em memória não volátil, calcular o tempo de ciclo e transmitir métricas para um painel de monitoramento.
