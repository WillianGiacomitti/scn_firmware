# CLAUDE.md: scn_firmware (firmware do ESP32-C6)

Firmware da unidade de atuadores do Scanner de Insetos: servo de disparo, servo de zoom e relé do USB da câmera Nikon L120. O PC manda comandos de texto pela serial e o ESP32 executa e responde.

**Leia antes de qualquer mudança:** [docs/architecture.md](docs/architecture.md), principalmente a seção 3 (pinos e relé), a seção 5 (protocolo, que é o contrato com o PC) e a seção 8 (segurança). Se algo aqui conflitar com o architecture.md, o architecture.md vale.

## Escopo desta frente
- Faz: interpretar o protocolo `ALVO:ACAO[:VALOR]`, mover os servos SHOT e ZOOM, comutar o relé do USB, responder `OK`/`ERRO`.
- Não faz: Wi-Fi, Bluetooth, servidor web, lógica do ciclo, decisões sozinho, controle da Ender. Tudo isso é do PC (`scn_calibrator`).
- Não mexer em código Python neste repositório. `calbrador.py` e `aconar_camera.py` vão sair daqui (ver "Limpeza pendente").

## Hardware
- Placa: **ESP32-C6** (tipo ESP32-C6-DevKitC-1). O código atual ainda está para `esp32dev`, e migrar é a primeira tarefa.
- Pinos (constantes no topo do código): servo ZOOM = GPIO18, servo SHOT = GPIO19, relé do USB = GPIO2.
- Relé **ativo em nível baixo**: `LOW` = câmera conectada (modo USB), `HIGH` = câmera desconectada (modo foto).
- Não usar no C6: GPIO 4, 5, 8, 9, 15 (boot), 12, 13 (USB nativo), 16, 17 (UART0).
- Ângulos que já funcionam (manter como constantes):
  - ZOOM: neutro 95°, zoom-in 115°, zoom-out 75°.
  - SHOT: pressiona 140° por 1000 ms, 145° por 500 ms, repouso 90°.

## Ambiente e comandos
- PlatformIO com Arduino core 3.x pela plataforma **pioarduino**:
  ```ini
  platform = https://github.com/pioarduino/platform-espressif32/releases/download/stable/platform-espressif32.zip
  board = esp32-c6-devkitc-1
  framework = arduino
  monitor_speed = 115200
  ```
- Se a placa for ligada pela porta USB nativa do C6, usar `build_flags = -DARDUINO_USB_CDC_ON_BOOT=1` para o `Serial` sair por ela. Confirmar com o Willian qual porta é usada.
- Ambientes:
  - `env:main`: firmware final (`src/main.cpp`).
  - `env:calibrador`: ferramenta de bancada para achar ângulos (`src/calibrador.cpp`, comandos `ZOOM:<angulo>` / `SHOT:<angulo>`). Migrar para o C6 também, mas não precisa seguir o protocolo novo.
  - `env:native`: testes do interpretador no PC (`pio test -e native`), sem hardware.
- Compilar: `pio run -e main`. Testar: `pio test -e native`. Gravar e monitorar (só o Willian, com a placa): `pio run -e main -t upload` e `pio device monitor`.

O Claude Code não tem a placa. Ele compila e roda os testes `native`. O teste no hardware é feito pelo Willian, e cada entrega lista os comandos que ele deve digitar no monitor serial e o que deve aparecer.

## Servos no core 3.x
A biblioteca `ESP32Servo` pode não compilar para o C6. Preferir o PWM nativo do core 3.x (`ledcAttach(pin, 50, 14)` e `ledcWrite`, convertendo ângulo → pulso de 500–2400 µs) numa classe pequena própria. Só usar `ESP32Servo` se compilar sem erro para `esp32-c6-devkitc-1`.

## Estrutura alvo
```
include/config.h          # pinos, ângulos, tempos, versão do firmware (FW_VERSION)
lib/protocol/             # interpretador puro: texto → comando; sem Arduino.h
  protocol.h / protocol.cpp
src/main.cpp              # setup/loop, leitura da serial, executa comandos
src/actuators.h/.cpp      # servos e relé (única parte que toca no hardware)
src/calibrador.cpp        # ferramenta de bancada
test/test_protocol/       # testes Unity do interpretador (env native)
docs/architecture.md
```

## Regras do protocolo (resumo; detalhe no architecture.md, seção 5)
- Uma linha por comando, terminada em `\n` (aceitar `\r\n`), sem diferenciar maiúsculas de minúsculas, máximo 64 caracteres.
- **Exatamente uma linha final por comando**, começando com `OK` ou `ERRO`, enviada **depois** de a ação terminar.
- Linhas de depuração começam com `#`.
- Comandos: `PING`, `STATUS`, `SHOT:CLICK`, `ZOOM:IN[:<ms>]`, `ZOOM:OUT[:<ms>]`, `ZOOM:HOME`, `USB:ON`, `USB:OFF`. `<ms>` de 50 a 5000, padrão 500.
- Erros: `ERRO FORMATO`, `ERRO ALVO`, `ERRO ACAO`, `ERRO VALOR`.
- Respostas sem acentos (ASCII).
- Mudou o protocolo? Aumente `FW_VERSION`, atualize `docs/architecture.md` aqui **e** no `scn_calibrator`.

## Regras de segurança
1. A **primeira instrução do `setup()`** é `pinMode(PIN_USB_RELAY, OUTPUT); digitalWrite(PIN_USB_RELAY, HIGH);`, antes de `Serial.begin`.
2. Nada de `delay()` longo no boot (o `delay(5000)` atual sai). O PC sincroniza com `PING`.
3. O firmware nunca liga o USB sozinho, nem depois de erro ou reset.
4. Servos voltam ao repouso ao fim de cada comando, mesmo em caminho de erro.

## Convenções
- C++ no estilo Arduino; nomes em inglês (`handleCommand`, `setUsbConnected`), constantes em `MAIÚSCULAS`.
- Comentários em português, só o essencial.
- Evitar `String` dinâmica no caminho do comando; usar buffer `char[65]` fixo.
- Commits em português, curtos, no imperativo.

## Tarefas da etapa 1 (em ordem)
1. Migrar `platformio.ini` para o C6 (pioarduino) e fazer `main` e `calibrador` compilarem.
2. Separar o interpretador em `lib/protocol` com testes `native` cobrindo todos os comandos e erros da tabela.
3. Implementar o protocolo completo em `main.cpp` (inclui `USB:ON/OFF`, `PING`, `STATUS`, `ZOOM:<dir>:<ms>`, `ZOOM:HOME`).
4. Entregar ao Willian o roteiro de teste no hardware (sequência de comandos e respostas esperadas, incluindo o relé estalando e a câmera aparecendo no Windows com `USB:ON`).

**Pronto quando:** `pio run -e main` e `pio test -e native` passam, e o roteiro de teste no hardware foi aprovado pelo Willian.

## Limpeza pendente (junto com a tarefa 1 do `scn_calibrator`)
- Mover `calbrador.py` e `aconar_camera.py` para `scn_calibrator/legacy/`.
- O painel `calbrador.py` usa `ZOOM:RESET`, que deixa de existir.
