from machine import Pin, ADC
from time import sleep_ms, ticks_ms, ticks_diff

BTN_PIN = 18
DEBOUNCE_DIFF_MS = 50
TIMER_DIFF_MS = 5000
PERCENTAGE_THRESHOLD = 50

ldrPin = ADC(Pin(34))
ldrPin.atten(ADC.ATTN_11DB)

btn = Pin(BTN_PIN, Pin.IN, Pin.PULL_UP)

print("Contador de Producao Inicializado")

counter = 0
temporizador_bloqueio = 0 # testar microparada
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

while True:
    pressionado = debouncing()

    if not pressionado and not resetado:
        resetado = True
        counter = 0
        temporizador_bloqueio = 0
        microparada = False
        objetoContado = False
        print("Turno resetado com sucesso. Contadores zerados.")

    elif pressionado:
        resetado = False

    valorBruto = ldrPin.read()

    valorReal = 100 - (valorBruto / 4095 * 100)

    objetoDetectado = valorReal < PERCENTAGE_THRESHOLD

    if objetoDetectado and not objetoContado:
        objetoContado = True
        temporizador_bloqueio = ticks_ms()
        microparada = False
    elif not objetoDetectado and objetoContado:
        counter += 1
        print(f"Peca detectada! Total: {counter}")
        objetoContado = False

    temporizador_agora = ticks_ms()

    esteiraObstruida = (
        objetoContado and 
        ticks_diff(temporizador_agora, temporizador_bloqueio) >= TIMER_DIFF_MS
        )

    if esteiraObstruida and not microparada:
        microparada = True
        print("Alerta: Micro-parada detectada!")

    sleep_ms(10)