import serial
from flask import Flask, render_template_string, request, jsonify

app = Flask(__name__)

# ==========================================
# ATENÇÃO: Altere para a porta do seu ESP32
PORTA_SERIAL = 'COM8' 
BAUD_RATE = 115200
# ==========================================

try:
    esp32 = serial.Serial(PORTA_SERIAL, BAUD_RATE, timeout=1)
    print(f"Conectado à porta {PORTA_SERIAL} com sucesso!")
except Exception as e:
    esp32 = None
    print(f"ERRO: Não foi possível abrir a porta {PORTA_SERIAL}.")
    print("Lembre-se de fechar o Monitor Serial no PlatformIO/VS Code!")

HTML_PAGE = """
<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <title>Painel ESP32 - Controle de Câmera</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #f0f2f5; margin: 0; padding: 20px; text-align: center; color: #333; }
        h1 { margin-bottom: 5px; }
        p.subtitle { color: #666; margin-bottom: 25px; }
        .container { display: flex; justify-content: center; gap: 20px; flex-wrap: wrap; max-width: 800px; margin: 0 auto; }
        .card { background: white; padding: 25px; border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.08); width: 340px; box-sizing: border-box; }
        .card h2 { margin-top: 0; border-bottom: 2px solid #eee; padding-bottom: 10px; font-size: 20px; color: #1a73e8; }
        .section-title { font-size: 12px; text-transform: uppercase; color: #888; font-weight: bold; margin: 15px 0 8px 0; text-align: left; }
        .btn-group { display: flex; gap: 8px; flex-wrap: wrap; margin-bottom: 15px; }
        button { flex: 1; min-width: 90px; padding: 10px; font-size: 14px; font-weight: 600; border: none; border-radius: 6px; cursor: pointer; transition: all 0.2s; background: #e4e6eb; color: #050505; }
        button:hover { background: #d8dadf; }
        button.primary { background: #1a73e8; color: white; }
        button.primary:hover { background: #1557b0; }
        button.success { background: #28a745; color: white; }
        button.success:hover { background: #218838; }
        .input-group { display: flex; gap: 8px; }
        input[type=number] { flex: 1; padding: 10px; font-size: 16px; text-align: center; border: 1px solid #ccc; border-radius: 6px; }
        #status { margin-top: 25px; font-size: 16px; font-weight: bold; min-height: 24px; }
        .success-msg { color: #28a745; }
        .error-msg { color: #dc3545; }
    </style>
</head>
<body>
    <h1>Controle de Câmera (ESP32)</h1>
    <p class="subtitle">Compatível com o ambiente MAIN (Ações) e CALIBRADOR (Ângulos)</p>
    
    <div class="container">
        <!-- CARD SERVO ZOOM -->
        <div class="card">
            <h2>Servo ZOOM</h2>
            
            <div class="section-title">Comandos Prontos (Env: Main)</div>
            <div class="btn-group">
                <button class="primary" onclick="enviar('ZOOM:IN')">Zoom IN</button>
                <button class="primary" onclick="enviar('ZOOM:OUT')">Zoom OUT</button>
                <button onclick="enviar('ZOOM:RESET')">Reset (90°)</button>
            </div>

            <div class="section-title">Calibração Manual (Env: Calibrador)</div>
            <div class="input-group">
                <input type="number" id="zoomAngle" min="0" max="180" placeholder="Ângulo (0-180)" value="90">
                <button class="success" onclick="enviarAngulo('ZOOM', 'zoomAngle')">Enviar</button>
            </div>
        </div>
        
        <!-- CARD SERVO SHOT -->
        <div class="card">
            <h2>Servo SHOT</h2>
            
            <div class="section-title">Comandos Prontos (Env: Main)</div>
            <div class="btn-group">
                <button class="primary" style="width: 100%; font-size: 16px;" onclick="enviar('SHOT:CLICK')">Disparar Câmera</button>
            </div>

            <div class="section-title">Calibração Manual (Env: Calibrador)</div>
            <div class="input-group">
                <input type="number" id="shotAngle" min="0" max="180" placeholder="Ângulo (0-180)" value="90">
                <button class="success" onclick="enviarAngulo('SHOT', 'shotAngle')">Enviar</button>
            </div>
        </div>
    </div>

    <div id="status"></div>

    <script>
        function enviar(comando) {
            enviarParaESP(comando);
        }

        function enviarAngulo(alvo, inputId) {
            let angulo = document.getElementById(inputId).value;
            if (angulo === '') return;
            enviarParaESP(alvo + ':' + angulo);
        }

        function enviarParaESP(comandoCompleto) {
            let statusDiv = document.getElementById('status');
            
            fetch('/enviar', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ comando: comandoCompleto })
            })
            .then(response => response.json())
            .then(data => {
                if (data.sucesso) {
                    statusDiv.className = 'success-msg';
                    statusDiv.innerText = '✅ Enviado: ' + comandoCompleto;
                } else {
                    statusDiv.className = 'error-msg';
                    statusDiv.innerText = '⚠️ Erro: ' + data.mensagem;
                }
            })
            .catch(err => {
                statusDiv.className = 'error-msg';
                statusDiv.innerText = '❌ Erro na comunicação com o servidor Python.';
            });
        }
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_PAGE)

@app.route('/enviar', methods=['POST'])
def enviar():
    if not esp32 or not esp32.is_open:
        return jsonify({"sucesso": False, "mensagem": "ESP32 desconectado da porta Serial!"})
    
    dados = request.json
    comando = dados.get('comando', '').strip()
    
    if not comando:
        return jsonify({"sucesso": False, "mensagem": "Comando inválido!"})
    
    # Envia o comando com a quebra de linha exigida pelo ESP32 (\n)
    esp32.write(f"{comando}\n".encode('utf-8'))
    
    return jsonify({"sucesso": True, "mensagem": "OK"})

if __name__ == '__main__':
    print("Servidor rodando em: http://localhost:5000")
    app.run(port=5000)