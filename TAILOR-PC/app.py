import os
from flask import Flask, request, render_template
import clips

app = Flask(__name__)

def inicializar_experto():
    """Configura el entorno de CLIPS y carga la base de conocimiento en orden """
    env = clips.Environment()
    base_path = os.path.dirname(os.path.abspath(__file__))
    ruta_logica = os.path.join(base_path, 'logic')
    
    try:
        # Carga secuencial obligatoria: Estructura -> Hechos -> Reglas 
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
    """Muestra la portada académica con la introducción """
    return render_template('portada.html')

@app.route('/diagnostico-inicio')
def formulario_diagnostico():
    """Muestra el formulario principal de preguntas """
    return render_template('index.html')

@app.route('/diagnostico', methods=['POST'])
def ejecutar_diagnostico():
    env = inicializar_experto()
    env.reset()
    try:
        # Captura de datos del formulario con "limpieza" para CLIPS
        wifi_val = 'SI' if 'Sí' in request.form.get('wifi', '') else 'NO'
        size_val = request.form.get('size', 'ATX') # ATX o Micro-ATX

        env.assert_string(
            f'(usuario (presupuesto {float(request.form.get("presupuesto", 0))}) '
            f'(uso "{request.form.get("uso", "gaming")}") '
            f'(resolucion "{request.form.get("resolucion", "1080p")}") '
            f'(clima "{request.form.get("clima", "templado")}") '
            f'(prioridad "{request.form.get("prioridad", "rendimiento")}") '
            f'(streaming {"SI" if request.form.get("streaming") else "NO"}) '
            f'(longevidad {"SI" if "Sí" in request.form.get("longevidad", "") else "NO"}) '
            f'(almacenamiento "{request.form.get("almacenamiento", "velocidad")}") '
            f'(wifi {wifi_val}) '
            f'(size {size_val}))'
        )

        env.run()

        sugerencias = []
        for fact in env.facts():
            if fact.template.name == 'recomendacion':
                raw = fact['razon']
                if "|" in raw:
                    partes = raw.split("|")
                    # Extrae solo el número después del signo $
                    balance_str = raw.split("BALANCE: $")[-1] if "BALANCE: $" in raw else "0"
                    sugerencias.append({
                        'prioridad': fact['prioridad'],
                        'razon': partes[0], # Análisis
                        'detalles': partes[1:-2], # Lista de componentes
                        'balance': balance_str, # Aquí ya no saldrá N/A
                        'es_lista': True
                    })

        return render_template('resultado.html', sugerencias=sugerencias)
    except Exception as e:
        return f"Error crítico en el motor: {str(e)}"

if __name__ == '__main__':
    app.run(debug=True)