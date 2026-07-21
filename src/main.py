from machine import Pin, ADC
from time import sleep_ms, ticks_ms, ticks_diff

BTN_PIN = 18
DEBOUNCE_DIFF_MS = 50

ldrPin = ADC(Pin(34))
ldrPin.atten(ADC.ATTN_11DB)

btn = Pin(BTN_PIN, Pin.IN, Pin.PULL_UP)

print(" ====== Sistema Kanban Inicializado ====== ")

counter = 0
objetoContado = False;

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

    if not pressionado:
        print(f"Sistema reiniciando")
        counter = 0

    valorBruto = ldrPin.read()

    percentualLuz = (((valorBruto / 4095) * 100) - 100) * -1

    print(f"Valor Lido: {percentualLuz}")

    if percentualLuz < 50 and not objetoContado:
        counter += 1
        objetoContado = True
        print(f"Novo objeto! Total: {counter}")
    if percentualLuz > 50 and objetoContado:
        objetoContado = False
    
    print(f"Total: {counter}")

    sleep_ms(10)