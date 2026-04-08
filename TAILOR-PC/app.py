# app.py
import os
import clips
import re
from flask import Flask, request, render_template, jsonify

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
    # Usamos el template de la captura azul (portada2.html)
    return render_template('portada2.html')

@app.route('/diagnostico-inicio')
def formulario_diagnostico():
    return render_template('index.html')

@app.route('/chat-interactivo', methods=['POST'])
def chat_interactivo():
    data = request.json
    msg  = data.get('mensaje', '').lower().strip()

    # Identidad y Creadores
    if any(p in msg for p in ["como te llamas", "quien eres", "nombre"]):
        return jsonify({"res": "Soy <b>Tailor AI</b>, asistente RETE de Tailor-PC.", "accion": None})
    
    if any(p in msg for p in ["creadores", "autores", "angel", "brandon", "uaeh"]):
        return jsonify({
            "res": "Desarrollado por 🧑‍💻 <b>Brandon Torres De Paz</b> y 🧑‍💻 <b>Ángel Ariel Mendoza López</b> (UAEH ICBI).",
            "accion": None
        })

    # Ayuda y Comandos
    if "ayuda" in msg or "comandos" in msg:
        return jsonify({
            "res": "<b>Comandos:</b> modo oscuro/claro, top 3, presupuesto, mejor opción, dónde comprar.",
            "accion": None
        })

    # Acciones de Interfaz
    if "oscuro" in msg: return jsonify({"res": "🌙 Modo oscuro.", "accion": "SET_THEME", "modo": "dark"})
    if "claro" in msg: return jsonify({"res": "☀️ Modo claro.", "accion": "SET_THEME", "modo": "light"})
    if "presupuesto" in msg: return jsonify({"res": "💰 Abriendo analizador.", "accion": "OPEN_BUDGET"})
    if "donde comprar" in msg: return jsonify({"res": "🏪 Tiendas sugeridas...", "accion": "HIGHLIGHT_STORES"})
    if "mejor" in msg and "opcion" in msg: return jsonify({"res": "✅ Expandiendo la mejor config.", "accion": "EXPAND_FIRST"})

    return jsonify({"res": "No reconocí eso. Escribe <b>ayuda</b>.", "accion": None})

@app.route('/diagnostico', methods=['POST'])
def ejecutar_diagnostico():
    env = inicializar_experto()
    env.reset()
    try:
        # Extracción de datos del formulario index.html
        presupuesto = float(request.form.get("presupuesto", 0))
        uso         = request.form.get("uso", "gaming")
        resolucion  = request.form.get("resolucion", "1080p")
        clima       = request.form.get("clima", "templado")
        prioridad   = request.form.get("prioridad", "rendimiento")
        streaming   = "SI" if request.form.get("streaming") else "NO"
        wifi_val    = 'SI' if 'Sí' in request.form.get('wifi', '') else 'NO'
        size_val    = request.form.get('size', 'ATX')
        almacenamiento = request.form.get("almacenamiento", "velocidad")
        longevidad  = "SI" if "Sí" in request.form.get('longevidad', '') else "NO"
        audio       = request.form.get('audio', 'estandar')

        # Assert en CLIPS
        env.assert_string(
            f'(usuario (presupuesto {presupuesto}) (uso "{uso}") (resolucion "{resolucion}") '
            f'(clima "{clima}") (prioridad "{prioridad}") (streaming {streaming}) '
            f'(longevidad {longevidad}) (almacenamiento "{almacenamiento}") '
            f'(wifi {wifi_val}) (size {size_val}) (audio "{audio}"))'
        )
        env.run()

        sugerencias = []
        for fact in env.facts():
            if fact.template.name == 'recomendacion' and "CONFIGURACION_COMPLETA" in str(fact['razon']):
                raw_text = str(fact['razon'])
                partes = raw_text.split("|")
                try:
                    total_pc = float(raw_text.split("TOTAL: $")[1].split("|")[0].strip())
                    balance = float(raw_text.split("BALANCE: $")[-1].strip())
                except: total_pc = 0.0; balance = 0.0

                sugerencias.append({
                    'prioridad': fact['prioridad'],
                    'razon': partes[0].strip(),
                    'detalles': [i.strip() for i in partes[1:] if "TOTAL" not in i and "BALANCE" not in i],
                    'balance': balance,
                    'total': total_pc,
                    'sinergia': 95.0, # Placeholder, se calcula abajo
                    'radar': [80, 70, 90, 85, 75] # Placeholder
                })

        return render_template('resultado.html', sugerencias=sugerencias)
    except Exception as e:
        return f"Error: {str(e)}"

if __name__ == '__main__':
    app.run(debug=True)