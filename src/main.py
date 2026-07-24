from machine import Pin, ADC
from time import sleep_ms, ticks_ms, ticks_diff

LDR_PIN = 34
BTN_PIN = 18

DEBOUNCE_DIFF_MS = 50
TIMER_DIFF_MS = 5000
LOOP_DELAY_MS = 10

ADC_MAX_VALUE = 4095
PERCENTAGE_THRESHOLD = 50

ldrPin = ADC(Pin(LDR_PIN))
ldrPin.atten(ADC.ATTN_11DB)

btn = Pin(BTN_PIN, Pin.IN, Pin.PULL_UP)

print("Contador de Producao Inicializado")

counter = 0
temporizadorBloqueio = 0
microparada = False
objetoContado = False
resetado = False

ultima_leitura = btn.value()
estado = ultima_leitura
momento_mudanca = ticks_ms()


def debouncing():
    global ultima_leitura, estado, momento_mudanca

    agora = ticks_ms()
    leitura = btn.value()

    if leitura != ultima_leitura:
        ultima_leitura = leitura
        momento_mudanca = agora

    if ticks_diff(agora, momento_mudanca) >= DEBOUNCE_DIFF_MS:
        if leitura != estado:
            estado = leitura

    return estado


def resetar_contadores():
    global counter, temporizadorBloqueio, microparada, objetoContado

    counter = 0
    temporizadorBloqueio = 0
    microparada = False
    objetoContado = False


def calcular_percentual_luz(valor_bruto):
    return 100 - (valor_bruto / ADC_MAX_VALUE * 100)


def atualizar_contagem(objeto_detectado):
    global counter, temporizadorBloqueio, microparada, objetoContado

    if objeto_detectado and not objetoContado:
        objetoContado = True
        temporizadorBloqueio = ticks_ms()
        microparada = False
    elif not objeto_detectado and objetoContado:
        counter += 1
        print(f"Peca detectada! Total: {counter}")
        objetoContado = False


def verificar_microparada():
    global microparada

    esteiraObstruida = (
        objetoContado
        and ticks_diff(ticks_ms(), temporizadorBloqueio) >= TIMER_DIFF_MS
    )

    if esteiraObstruida and not microparada:
        microparada = True
        print("Alerta: Micro-parada detectada!")


while True:
    botaoPressionado = not debouncing()

    if botaoPressionado and not resetado:
        resetado = True
        resetar_contadores()
    elif not botaoPressionado and resetado:
        resetado = False
        print("Turno resetado com sucesso. Contadores zerados.")

    valorBruto = ldrPin.read()
    valorReal = calcular_percentual_luz(valorBruto)
    objetoDetectado = valorReal < PERCENTAGE_THRESHOLD

    atualizar_contagem(objetoDetectado)
    verificar_microparada()

    sleep_ms(LOOP_DELAY_MS)
