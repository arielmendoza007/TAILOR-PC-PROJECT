import os
from flask import Flask, request, render_template
# Busca tu ruta del chat en app.py. Probablemente se vea así:
@app.route('/tu_ruta_de_chat', methods=['POST'])
def procesar_chat():
    datos = request.json
    mensaje_usuario = datos.get('mensaje', '').lower()

    # EL TRIGGER OCULTO
    if "estoy en ceros" in mensaje_usuario or "presupuesto" in mensaje_usuario:
        return jsonify({
            "respuesta": "Activando el módulo de asesoría financiera para ensamblaje...",
            "comando_sistema": "OPEN_BUDGET"
        })

    # ... Aquí abajo va tu código normal que llama a Tailor AI ...

import clips

app = Flask(__name__)

def inicializar_experto():
    env = clips.Environment()
    base_path = os.path.dirname(os.path.abspath(__file__))
    ruta_logica = os.path.join(base_path, 'logic')
    
    try:
        env.load(os.path.join(ruta_logica, 'templates.clip'))
        env.load(os.path.join(ruta_logica, 'componentes.clip'))
        env.load(os.path.join(ruta_logica, 'compatibilidad.clip'))
        env.load(os.path.join(ruta_logica, 'reglas_fisicas.clip'))
        env.load(os.path.join(ruta_logica, 'expert_rules.clip'))
        env.load(os.path.join(ruta_logica, 'reglas_optimizacion.clip'))
        env.load(os.path.join(ruta_logica, 'reglas_control.clip'))
    except Exception as e:
        print(f"Error crítico al cargar CLIPS: {e}")
        raise e
    return env

@app.route('/')
def portada():
    return render_template('portada.html')

@app.route('/diagnostico-inicio')
def formulario_diagnostico():
    return render_template('index.html')

@app.route('/diagnostico', methods=['POST'])
def ejecutar_diagnostico():
    env = inicializar_experto()
    env.reset()
    try:
        presupuesto = float(request.form.get("presupuesto", 0))
        uso = request.form.get("uso", "gaming")
        resolucion = request.form.get("resolucion", "1080p")
        clima = request.form.get("clima", "templado")
        prioridad = request.form.get("prioridad", "rendimiento")
        
        streaming = "SI" if request.form.get("streaming") else "NO"
        wifi_val = 'SI' if 'Sí' in request.form.get('wifi', '') else 'NO'
        size_val = request.form.get('size', 'ATX') 
        almacenamiento = request.form.get("almacenamiento", "velocidad")
        longevidad_raw = request.form.get('longevidad', '')
        longevidad = "SI" if "Sí" in longevidad_raw or longevidad_raw == "on" else "NO" 
        audio = request.form.get('audio', 'estandar')

        marca_cpu = request.form.get("marca_cpu", "indistinto")
        estilo_rgb = request.form.get("estilo_rgb", "minimalista")

        env.assert_string(
            f'(usuario (presupuesto {presupuesto}) '
            f'(uso "{uso}") (resolucion "{resolucion}") '
            f'(clima "{clima}") (prioridad "{prioridad}") '
            f'(streaming {streaming}) (longevidad {longevidad}) '
            f'(almacenamiento "{almacenamiento}") (wifi {wifi_val}) '
            f'(size {size_val}) (audio "{audio}"))'
        )

        env.run()

        sugerencias = []
        for fact in env.facts():
            if fact.template.name == 'recomendacion':
                raw_text = str(fact['razon'])
                if "CONFIGURACION_COMPLETA" in raw_text:
                    partes = raw_text.split("|")
                    try:
                        balance = float(raw_text.split("BALANCE: $")[-1].strip())
                        total_pc = float(raw_text.split("TOTAL: $")[1].split("|")[0].strip())
                    except Exception:
                        balance = 0.0; total_pc = 0.0
                    
                    detalles_limpios = [item.strip() for item in partes[1:] if "TOTAL" not in item and "BALANCE" not in item]
                    
                    sugerencias.append({
                        'prioridad': fact['prioridad'],
                        'razon': partes[0].strip(),
                        'detalles': detalles_limpios,
                        'balance': balance,
                        'total': total_pc,
                        'titulo': "Diagnóstico de Hardware",
                        'es_lista': True
                    })

        def sort_key(s):
            if s['balance'] >= 0:
                return (1, -s['balance'])
            else:
                return (0, s['balance'])

        sugerencias_ordenadas = sorted(sugerencias, key=sort_key, reverse=True)
        
        for i, s in enumerate(sugerencias_ordenadas):
            if s['balance'] >= 0:
                s['sinergia'] = max(80.5, round(99.5 - (i * 0.5), 1))
            else:
                s['sinergia'] = max(30.0, round(75.0 - (abs(s['balance']) / 150), 1))
                
            detalles_str = " ".join(s['detalles']).lower()
            if marca_cpu == "intel" and "ryzen" in detalles_str:
                s['sinergia'] -= 4.5
            elif marca_cpu == "amd" and "core" in detalles_str:
                s['sinergia'] -= 4.5

        return render_template('resultado.html', sugerencias=sugerencias_ordenadas, estilo_rgb=estilo_rgb)
        
    except Exception as e:
        return f"Error crítico en el motor: {str(e)}"

if __name__ == '__main__':
    app.run(debug=True)