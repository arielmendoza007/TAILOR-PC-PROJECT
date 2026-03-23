from flask import Flask, request, render_template
import clips

app = Flask(__name__)
env = clips.Environment()

@app.route('/diagnostico', methods=['POST'])
def diagnostico():
    # 1. Cargar la lógica del experto
    env.load('reglas_expertas.clp')
    env.reset()

    # 1. Cargar el conocimiento completo
    env.load('logic/templates.clp')
    env.load('logic/componentes.clp')
    env.load('logic/reglas_expertas.clp')
    env.reset()

    # 2. Capturar datos del formulario (Ariel, aquí va lo que Brandon investigó)
    presupuesto = request.form.get('presupuesto')
    uso = request.form.get('uso')
    
    # 3. Insertar HECHOS en el motor
    env.assert_string(f'(usuario (presupuesto {presupuesto}) (uso "{uso}"))')
    
    # 4. DISPARAR EL MOTOR (Encadenamiento hacia adelante)
    env.run()
    
    # 5. Extraer resultados para mostrar en la interfaz
    resultados = []
    for fact in env.facts():
        if fact.template.name == 'recomendacion':
            resultados.append(fact[0])
            
    return render_template('resultados.html', data=resultados)