# app.py completo - Tailor-PC
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
    return render_template('portada.html')

@app.route('/diagnostico-inicio')
def formulario_diagnostico():
    return render_template('index.html')


# ══════════════════════════════════════════════════════
#  CHATBOT INTERACTIVO
# ══════════════════════════════════════════════════════
@app.route('/chat-interactivo', methods=['POST'])
def chat_interactivo():
    data = request.json
    msg  = data.get('mensaje', '').lower().strip()

    # ── IDENTIDAD ──────────────────────────────────────────────
    if any(p in msg for p in ["como te llamas", "cómo te llamas", "tu nombre", "quien eres",
                               "quién eres", "que eres", "qué eres", "presentate", "preséntate"]):
        return jsonify({
            "res": ("Soy <b>Tailor AI</b>, el asistente experto integrado en Tailor-PC. "
                    "Estoy construido sobre un motor de inferencia <b>RETE</b> con base de conocimiento en <b>CLIPS</b>. "
                    "Mi misión: ayudarte a entender, filtrar y sacarle el máximo provecho a las configuraciones de hardware generadas para ti."),
            "accion": None
        })

    # ── CREADORES ──────────────────────────────────────────────
    if any(p in msg for p in ["creadores", "quien te hizo", "quién te hizo", "quien te creo",
                               "quién te creó", "autores", "desarrolladores", "quienes te hicieron",
                               "uaeh", "icbi", "quien te diseño", "quién te diseñó"]):
        return jsonify({
            "res": ("Fui desarrollado por:<br>"
                    "🧑‍💻 <b>Brandon Torres De Paz</b><br>"
                    "🧑‍💻 <b>Ángel Ariel Mendoza López</b><br>"
                    "Proyecto de <i>Sistemas Basados en Conocimiento</i> — <b>UAEH ICBI</b>."),
            "accion": None
        })

    # ── QUÉ PUEDES HACER / AYUDA ───────────────────────────────
    if any(p in msg for p in ["ayuda", "help", "comandos", "qué puedes", "que puedes",
                               "funciones", "opciones", "para que sirves", "para qué sirves", "menu"]):
        return jsonify({
            "res": ("<b>Comandos disponibles:</b><br>"
                    "🎨 <b>modo oscuro / claro</b> → cambia el tema<br>"
                    "📊 <b>top 3</b> (cualquier N) → filtra los mejores N<br>"
                    "🔼 <b>ordenar mayor precio</b> → de caro a barato<br>"
                    "🔽 <b>ordenar menor precio</b> → de barato a caro<br>"
                    "⚡ <b>ordenar sinergia</b> → por mejor score<br>"
                    "🏪 <b>dónde comprar</b> → guía de tiendas en México<br>"
                    "💰 <b>presupuesto</b> → analizador financiero<br>"
                    "✅ <b>mejor opción</b> → expande la config #1<br>"
                    "🔄 <b>mostrar todo</b> → quita filtros activos<br>"
                    "🆕 <b>nueva consulta</b> → reinicia el diagnóstico<br>"
                    "ℹ️ <b>qué es [cpu/gpu/ram/ssd]</b> → explico el componente"),
            "accion": None
        })

    # ── TEMA: OSCURO ───────────────────────────────────────────
    if any(p in msg for p in ["modo oscuro", "dark mode", "pon oscuro", "activa oscuro",
                               "tema oscuro", "quiero oscuro", "oscuro"]):
        return jsonify({
            "res": "🌙 Modo oscuro activado. Ajustando paleta de colores del sistema.",
            "accion": "SET_THEME", "modo": "dark"
        })

    # ── TEMA: CLARO ────────────────────────────────────────────
    if any(p in msg for p in ["modo claro", "light mode", "pon claro", "activa claro",
                               "tema claro", "quiero claro", "claro"]):
        return jsonify({
            "res": "☀️ Modo claro activado. Restaurando interfaz a paleta estándar.",
            "accion": "SET_THEME", "modo": "light"
        })

    if any(p in msg for p in ["cambia tema", "cambiar tema", "toggle tema", "cambiar modo"]):
        return jsonify({
            "res": "Alternando tema de la interfaz.",
            "accion": "TOGGLE_THEME"
        })

    # ── ORDENAR POR PRECIO DESCENDENTE ────────────────────────
    if any(p in msg for p in ["mayor precio", "mas caro", "más caro", "precio descendente",
                               "ordenar mayor", "de mayor a menor", "mas costoso", "más costoso"]):
        return jsonify({
            "res": "🔼 Reordenando de mayor a menor precio.",
            "accion": "SORT", "criterio": "precio_desc"
        })

    # ── ORDENAR POR PRECIO ASCENDENTE ─────────────────────────
    if any(p in msg for p in ["menor precio", "mas barato", "más barato", "precio ascendente",
                               "ordenar menor", "de menor a mayor", "economico", "económico",
                               "mas economico", "más económico", "barato primero"]):
        return jsonify({
            "res": "🔽 Reordenando de menor a mayor precio.",
            "accion": "SORT", "criterio": "precio_asc"
        })

    # ── ORDENAR POR SINERGIA ───────────────────────────────────
    if any(p in msg for p in ["sinergia", "mejor score", "ordenar sinergia",
                               "orden original", "por rendimiento", "por score"]):
        return jsonify({
            "res": "⚡ Ordenando por índice de sinergia del motor experto.",
            "accion": "SORT", "criterio": "sinergia"
        })

    # ── DÓNDE COMPRAR ──────────────────────────────────────────
    if any(p in msg for p in ["donde comprar", "dónde comprar", "tienda", "tiendas",
                               "comprar barato", "donde conseguir", "dónde conseguir",
                               "mejores tiendas", "recomendacion tienda", "donde lo consigo"]):
        return jsonify({
            "res": ("🏪 <b>Tiendas recomendadas en México:</b><br>"
                    "1️⃣ <b>Cyberpuerta</b> (cyberpuerta.mx) — generalmente el más barato<br>"
                    "2️⃣ <b>DDTech</b> (ddtech.com.mx) — buen stock de componentes<br>"
                    "3️⃣ <b>Mercado Libre</b> — revisa vendedores con buena reputación<br>"
                    "4️⃣ <b>Amazon México</b> — conveniente con Prime<br><br>"
                    "Los precios estimados por tienda ya aparecen en la analítica financiera de cada opción 👇"),
            "accion": "HIGHLIGHT_STORES"
        })

    # ── CUÁL ES LA MÁS BARATA ─────────────────────────────────
    if any(p in msg for p in ["cual es la mas barata", "cuál es la más barata",
                               "opcion barata", "la mas economica", "la más económica",
                               "cual cuesta menos", "cuál cuesta menos"]):
        return jsonify({
            "res": "🔽 Ordenando de menor a mayor precio para mostrarte la más accesible primero.",
            "accion": "SORT", "criterio": "precio_asc"
        })

    # ── CUÁNTAS OPCIONES ───────────────────────────────────────
    if any(p in msg for p in ["cuantas opciones", "cuántas opciones", "cuantos resultados",
                               "cuántos resultados", "cuantas configuraciones", "cuantas hay"]):
        return jsonify({
            "res": "Contando las configuraciones visibles en pantalla...",
            "accion": "COUNT_CARDS"
        })

    # ── MEJOR OPCIÓN ───────────────────────────────────────────
    if any(p in msg for p in ["cual es la mejor", "cuál es la mejor", "mejor configuracion",
                               "mejor opcion", "mejor opción", "primera", "recomienda",
                               "recomendación", "recomendacion", "cual eliges", "cuál eliges"]):
        return jsonify({
            "res": "✅ Expandiendo la configuración con mayor índice de sinergia.",
            "accion": "EXPAND_FIRST"
        })

    # ── FILTRADO TOP N ─────────────────────────────────────────
    top_match = re.search(r'top\s*(\d+)', msg)
    if top_match:
        num = top_match.group(1)
        return jsonify({
            "res": f"📊 Mostrando las mejores <b>{num}</b> configuraciones.",
            "accion": "FILTER_TOP", "valor": num
        })

    # ── MOSTRAR TODAS ──────────────────────────────────────────
    if any(p in msg for p in ["mostrar todo", "ver todo", "todas", "quitar filtro",
                               "reset", "sin filtro", "mostrar todas", "quitar orden"]):
        return jsonify({
            "res": "🔄 Mostrando todas las configuraciones sin filtro ni orden.",
            "accion": "FILTER_TOP", "valor": "999"
        })

    # ── PRESUPUESTO ────────────────────────────────────────────
    if any(p in msg for p in ["presupuesto", "pobre", "dinero", "financiero",
                               "ceros", "ahorro", "cuanto tengo", "mis finanzas"]):
        return jsonify({
            "res": "💰 Abriendo el analizador financiero.",
            "accion": "OPEN_BUDGET"
        })

    # ── NUEVA CONSULTA ─────────────────────────────────────────
    if any(p in msg for p in ["nueva consulta", "reiniciar", "volver", "inicio",
                               "nueva busqueda", "nueva búsqueda", "empezar de nuevo"]):
        return jsonify({
            "res": "🆕 Redirigiendo al formulario de diagnóstico...",
            "accion": "REDIRECT", "url": "/diagnostico-inicio"
        })

    # ── SALUDOS ────────────────────────────────────────────────
    if any(p in msg for p in ["hola", "buenas", "hey", "saludos", "hi",
                               "buenos dias", "buenas tardes", "buenas noches"]):
        return jsonify({
            "res": "¡Hola! Soy <b>Tailor AI</b>. Motor RETE en línea ⚡ Escribe <b>ayuda</b> para ver todo lo que puedo hacer.",
            "accion": None
        })

    # ── GRACIAS ────────────────────────────────────────────────
    if any(p in msg for p in ["gracias", "thanks", "perfecto", "excelente", "muy bien", "genial"]):
        return jsonify({
            "res": "Con gusto 😊 ¿Hay algo más en lo que pueda asistirte?",
            "accion": None
        })

    # ── COMPONENTES ────────────────────────────────────────────
    if any(p in msg for p in ["cpu", "procesador", "intel", "amd", "ryzen", "core i", "que es el cpu"]):
        return jsonify({
            "res": ("🧠 <b>Procesador (CPU):</b> El cerebro del equipo. "
                    "AMD Ryzen destaca en multitarea y precio/rendimiento; "
                    "Intel Core lidera en gaming single-thread. "
                    "El motor experto eligió el mejor para tu perfil de uso."),
            "accion": None
        })

    if any(p in msg for p in ["gpu", "tarjeta grafica", "tarjeta gráfica", "nvidia",
                               "radeon", "rtx", "rx ", "que es la gpu"]):
        return jsonify({
            "res": ("🎮 <b>Tarjeta Gráfica (GPU):</b> El componente más impactante para gaming y render. "
                    "NVIDIA RTX → ray tracing y DLSS. AMD RX → rasterización eficiente. "
                    "Un balance positivo indica que podrías hacer upgrade en el futuro."),
            "accion": None
        })

    if any(p in msg for p in ["ram", "memoria", "ddr4", "ddr5", "que es la ram"]):
        return jsonify({
            "res": ("💾 <b>Memoria RAM:</b> DDR4 = plataformas actuales/legacy (AM4, LGA1700 gen12). "
                    "DDR5 = plataformas de nueva generación (AM5, LGA1700 gen13+). "
                    "Tu preferencia de longevidad en el formulario definió esto."),
            "accion": None
        })

    if any(p in msg for p in ["ssd", "disco", "almacenamiento", "nvme", "hdd", "que es el ssd"]):
        return jsonify({
            "res": ("💽 <b>Almacenamiento:</b> NVMe PCIe 4.0 = hasta 7000 MB/s (ideal para carga rápida). "
                    "Para gaming: 500 GB NVMe es suficiente. "
                    "Para edición/render: 1 TB+ recomendado."),
            "accion": None
        })

    if any(p in msg for p in ["fuente", "psu", "watts", "consumo", "poder"]):
        return jsonify({
            "res": ("⚡ <b>Fuente de Poder (PSU):</b> Dimensionada con margen del 20% sobre el consumo total. "
                    "Una fuente con certificación 80+ Bronze o superior garantiza eficiencia y estabilidad."),
            "accion": None
        })

    if any(p in msg for p in ["motherboard", "placa", "placa base", "tarjeta madre"]):
        return jsonify({
            "res": ("🔌 <b>Tarjeta Madre:</b> Define el socket del CPU y la generación de RAM compatible. "
                    "También determina si puedes usar PCIe 4.0/5.0 para la GPU y el NVMe."),
            "accion": None
        })

    # ── FALLBACK ───────────────────────────────────────────────
    return jsonify({
        "res": "No reconocí ese comando. Escribe <b>ayuda</b> para ver todo lo que puedo hacer por ti.",
        "accion": None
    })


# ══════════════════════════════════════════════════════
#  MOTOR DE DIAGNÓSTICO
# ══════════════════════════════════════════════════════
@app.route('/diagnostico', methods=['POST'])
def ejecutar_diagnostico():
    env = inicializar_experto()
    env.reset()
    try:
        presupuesto    = float(request.form.get("presupuesto", 0))
        uso            = request.form.get("uso", "gaming")
        resolucion     = request.form.get("resolucion", "1080p")
        clima          = request.form.get("clima", "templado")
        prioridad      = request.form.get("prioridad", "rendimiento")
        streaming      = "SI" if request.form.get("streaming") else "NO"
        wifi_val       = 'SI' if 'Sí' in request.form.get('wifi', '') else 'NO'
        size_val       = request.form.get('size', 'ATX')
        almacenamiento = request.form.get("almacenamiento", "velocidad")
        longevidad_raw = request.form.get('longevidad', '')
        longevidad     = "SI" if "Sí" in longevidad_raw or longevidad_raw == "on" else "NO"
        audio          = request.form.get('audio', 'estandar')
        marca_cpu      = request.form.get("marca_cpu", "indistinto")
        estilo_rgb     = request.form.get("estilo_rgb", "minimalista")

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
                        balance  = float(raw_text.split("BALANCE: $")[-1].strip())
                        total_pc = float(raw_text.split("TOTAL: $")[1].split("|")[0].strip())
                    except Exception:
                        balance = 0.0; total_pc = 0.0

                    detalles_limpios = [item.strip() for item in partes[1:]
                                        if "TOTAL" not in item and "BALANCE" not in item]
                    sugerencias.append({
                        'prioridad': fact['prioridad'],
                        'razon':     partes[0].strip(),
                        'detalles':  detalles_limpios,
                        'balance':   balance,
                        'total':     total_pc,
                        'titulo':    "Diagnóstico de Hardware",
                        'es_lista':  True
                    })

        def sort_key(s):
            return (1, -s['balance']) if s['balance'] >= 0 else (0, s['balance'])

        sugerencias_ordenadas = sorted(sugerencias, key=sort_key, reverse=True)

        for i, s in enumerate(sugerencias_ordenadas):
            if s['balance'] >= 0:
                s['sinergia'] = max(80.5, round(99.5 - (i * 0.5), 1))
            else:
                s['sinergia'] = max(30.0, round(75.0 - (abs(s['balance']) / 150), 1))

            detalles_str = " ".join(s['detalles']).lower()
            if (marca_cpu == "intel" and "ryzen" in detalles_str) or \
               (marca_cpu == "amd"   and "core"  in detalles_str):
                s['sinergia'] -= 4.5

        return render_template('resultado.html',
                               sugerencias=sugerencias_ordenadas,
                               estilo_rgb=estilo_rgb)

    except Exception as e:
        return f"Error crítico en el motor: {str(e)}"


if __name__ == '__main__':
    app.run(debug=True)
