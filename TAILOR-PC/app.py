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
        # 1. CAPTURA Y LIMPIEZA DE DATOS (Todo correctamente indentado dentro de la función)
        presupuesto = float(request.form.get("presupuesto", 0))
        uso = request.form.get("uso", "gaming")
        resolucion = request.form.get("resolucion", "1080p")
        clima = request.form.get("clima", "templado")
        prioridad = request.form.get("prioridad", "rendimiento")
        
        # Validaciones de Checkboxes y Selects
        streaming = "SI" if request.form.get("streaming") else "NO"
        wifi_val = 'SI' if 'Sí' in request.form.get('wifi', '') else 'NO'
        size_val = request.form.get('size', 'ATX') 
        almacenamiento = request.form.get("almacenamiento", "velocidad")
        
        # Nuevas variables (Fase 4 - Optimización)
        longevidad_raw = request.form.get('longevidad', '')
        # Detecta "SI", "Sí" o si es un checkbox marcado ("on")
        longevidad = "SI" if "Sí" in longevidad_raw or longevidad_raw == "on" else "NO" 
        audio = request.form.get('audio', 'estandar')

        # 2. INYECCIÓN AL MOTOR (Un solo assert con todos los slots del deftemplate usuario)
        env.assert_string(
            f'(usuario (presupuesto {presupuesto}) '
            f'(uso "{uso}") '
            f'(resolucion "{resolucion}") '
            f'(clima "{clima}") '
            f'(prioridad "{prioridad}") '
            f'(streaming {streaming}) '
            f'(longevidad {longevidad}) '
            f'(almacenamiento "{almacenamiento}") '
            f'(wifi {wifi_val}) '
            f'(size {size_val}) '
            f'(audio "{audio}"))'
        )

        # 3. EJECUCIÓN DEL ALGORITMO RETE
        env.run()

        # 4. PROCESAMIENTO DE RESULTADOS
        sugerencias = []
        for fact in env.facts():
            if fact.template.name == 'recomendacion':
                raw_text = str(fact['razon'])
                
                # Solo filtramos las configuraciones completas para la tabla
                if "CONFIGURACION_COMPLETA" in raw_text:
                    partes = raw_text.split("|")
                    try:
                        balance = float(raw_text.split("BALANCE: $")[-1].strip())
                    except Exception:
                        balance = 0.0
                    
                    sugerencias.append({
                        'prioridad': fact['prioridad'],
                        'razon': partes[0].strip(),
                        'detalles': [item.strip() for item in partes[1:-1]],
                        'balance': balance,
                        'titulo': "Diagnóstico de Hardware",
                        'es_lista': True
                    })

        # ORDENAMIENTO POR DEFECTO: Mayor ahorro primero (Menos gasto)
        # ORDENAMIENTO POR DEFECTO: Mayor ahorro primero, pero LIMITADO AL TOP 5
        sugerencias_ordenadas = sorted(sugerencias, key=lambda x: x['balance'], reverse=True)[:5]
        
        return render_template('resultado.html', sugerencias=sugerencias_ordenadas)
        
    except Exception as e:
        return f"Error crítico en el motor: {str(e)}"

if __name__ == '__main__':
    app.run(debug=True)