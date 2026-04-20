# app.py — Tailor-PC Expert System
import os
import re
import clips
import requests  # <-- ¡Nuestra nueva solución!
from flask import Flask, request, render_template, jsonify

app = Flask(__name__)

# Tu llave institucional va aquí directo
GEMINI_API_KEY = "AQ.Ab8RN6LpZGifqb23zUKFwjwu88M5PjRGK77rYTez0BX7dwlWBw"

SYSTEM_PROMPT = """Eres Tailor AI, el asistente experto integrado en Tailor-PC Expert System.
Tailor-PC es un sistema experto académico desarrollado por Brandon Torres De Paz y Ángel Ariel Mendoza López, estudiantes de Licenciatura en Ciencias Computacionales de la UAEH ICBI, para la materia Sistemas Basados en Conocimiento.

=== ARQUITECTURA DEL SISTEMA ===
- Motor de inferencia: CLIPS 6.4 con algoritmo RETE (encadenamiento hacia adelante)
- Backend: Python 3.12 + Flask
- Frontend: HTML5 + CSS3 + JavaScript + Bootstrap 5 + Chart.js
- Integración: librería clips-python

=== BASE DE CONOCIMIENTO ===
7 archivos .clip organizados por responsabilidad:
- templates.clip: definición de plantillas (deftemplate) para cpu, gpu, placa, gabinete, ram, fuente, disco, soporte-gpu, usuario, recomendacion
- componentes.clip: catálogo de hardware con precios en MXN
- compatibilidad.clip: hechos de sockets y factor de forma
- reglas_fisicas.clip: validación de dimensiones GPU vs gabinete
- expert_rules.clip: reglas de perfil de usuario (streaming, render, ofimática, longevidad, etc.)
- reglas_optimizacion.clip: regla central validar-fuente-poder-integral que genera CONFIGURACION_COMPLETA
- reglas_compatibilidad.clip: compatibilidad socket, factor forma, VRAM, PSU, cuello de botella
- reglas_control.clip: inicio y fin del ciclo de inferencia

=== TU FUNCIÓN ===
Eres un asistente conversacional de hardware y del sistema. Responde en español, de forma clara, amigable y técnicamente precisa. Puedes:
- Explicar cómo funciona Tailor-PC y CLIPS/RETE
- Ayudar a entender los resultados del diagnóstico
- Dar recomendaciones personalizadas basadas en las configuraciones actuales

IMPORTANTE: Responde SIEMPRE en español. Sé conciso (máximo 4-5 líneas). Usa HTML básico (<b>, <br>) para formatear si es necesario."""

def preguntar_a_gemini(mensaje: str, historial: list, contexto_configs: str) -> str:
    # 1. Armamos el prompt con la info de la pantalla
    partes = [SYSTEM_PROMPT]
    
    if contexto_configs:
        partes.append(f"\n=== CONFIGURACIONES ACTUALES EN PANTALLA ===\n{contexto_configs}")

    if historial:
        partes.append("\n=== HISTORIAL RECIENTE ===")
        for turno in historial[-6:]:
            rol = "Usuario" if turno.get("rol") == "user" else "Tailor AI"
            partes.append(f"{rol}: {turno.get('texto', '')}")

    partes.append(f"\nUsuario: {mensaje}\nTailor AI:")
    prompt_final = "\n".join(partes)

    # 2. Petición directa a la API (replicando tu cURL )
# 2. Petición directa a la API (replicando tu cURL)
    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-latest:generateContent"
    
    headers = {
        "Content-Type": "application/json",
        "X-goog-api-key": GEMINI_API_KEY
    }
    
    payload = {
        "contents": [{"parts": [{"text": prompt_final}]}],
        "generationConfig": {"temperature": 0.7, "maxOutputTokens": 600}
    }
    payload = {
        "contents": [{"parts": [{"text": prompt_final}]}],
        "generationConfig": {"temperature": 0.7, "maxOutputTokens": 600}
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status() # Lanza error si Google nos bloquea
        datos = response.json()

        # Extraemos el texto de la respuesta
        texto = datos['candidates'][0]['content']['parts'][0]['text'].strip()

        # Limpiamos los asteriscos de Markdown a HTML para tu frontend
        texto = texto.replace("**", "<b>").replace("**", "</b>")
        texto = re.sub(r'\*([^*]+)\*', r'<i>\1</i>', texto)
        return texto

    except Exception as e:
        print(f"[Gemini HTTP Error] {e}")
        if hasattr(e, 'response') and e.response is not None:
            print("Respuesta de Google:", e.response.text)
        return "Tuve un problema de conexión al contactar al motor. Intenta de nuevo."

# A PARTIR DE AQUÍ DEJA EL CÓDIGO INTACTO (inicializar_experto, calcular_radar, rutas, etc.)
    # Construir el prompt completo
    partes = [SYSTEM_PROMPT]

    if contexto_configs:
        partes.append(f"\n=== CONFIGURACIONES ACTUALES EN PANTALLA ===\n{contexto_configs}")

    # Historial de conversación (últimos 6 intercambios)
    if historial:
        partes.append("\n=== HISTORIAL RECIENTE ===")
        for turno in historial[-6:]:
            rol = "Usuario" if turno.get("rol") == "user" else "Tailor AI"
            partes.append(f"{rol}: {turno.get('texto', '')}")

    partes.append(f"\nUsuario: {mensaje}\nTailor AI:")
    prompt_final = "\n".join(partes)

    try:
        respuesta = model.generate_content(prompt_final)
        texto = respuesta.text.strip()
        # Limpiar markdown innecesario que Gemini puede añadir
        texto = texto.replace("**", "<b>").replace("**", "</b>")
        texto = re.sub(r'\*([^*]+)\*', r'<i>\1</i>', texto)
        return texto
    except Exception as e:
        print(f"[Gemini Error] {e}")
        return "Tuve un problema al procesar tu pregunta. Intenta de nuevo en un momento."


# ═══════════════════════════════════════════════════════════
#  INICIALIZACIÓN CLIPS
# ═══════════════════════════════════════════════════════════
def inicializar_experto():
    env = clips.Environment()
    base = os.path.dirname(os.path.abspath(__file__))
    logic = os.path.join(base, 'logic')

    archivos = [
        'templates.clip',
        'componentes.clip',
        'compatibilidad.clip',
        'reglas_compatibilidad.clip',
        'reglas_fisicas.clip',
        'expert_rules.clip',
        'reglas_optimizacion.clip',
        'reglas_control.clip',
    ]
    for archivo in archivos:
        ruta = os.path.join(logic, archivo)
        if os.path.exists(ruta):
            env.load(ruta)
        else:
            print(f"[WARN] No encontrado: {archivo}")
    return env


def calcular_radar(detalles_str, uso, sinergia, balance, presupuesto, total, rank_idx):
    d = detalles_str.lower()

    # Gaming — tier GPU
    gaming = 50
    for kws, score in [
        (["rtx 4090", "rtx 4080"], 96),
        (["4070 ti"], 88),
        (["rtx 4070", "rx 6700"], 80),
        (["rtx 4060", "rx 6600"], 65),
        (["gtx 1660"], 57),
        (["gtx 1650"], 40),
        (["graficos integrados"], 18),
    ]:
        if any(k in d for k in kws):
            gaming = score; break
    else:
        gaming = max(30, int(sinergia * 0.80) - rank_idx * 8)
    if uso == "gaming":    gaming = min(97, gaming + 8)
    if uso == "ofimatica": gaming = max(15, gaming - 20)
    gaming = max(15, min(97, gaming))

    # Trabajo — tier CPU
    trabajo = 50
    for kws, score in [
        (["i9-13900", "ryzen 9"], 94),
        (["i7-13700", "ryzen 7 7800"], 79),
        (["i5-12400", "ryzen 5 7600"], 65),
        (["ryzen 5 5600"], 58),
        (["i3-12100", "ryzen 3", "ryzen 5 5600g"], 40),
    ]:
        if any(k in d for k in kws):
            trabajo = score; break
    else:
        trabajo = max(30, int(sinergia * 0.78) - rank_idx * 7)
    if "32gb" in d or "64gb" in d: trabajo = min(97, trabajo + 10)
    elif "16gb" in d:               trabajo = min(97, trabajo + 4)
    if uso == "render":    trabajo = min(97, trabajo + 12)
    if uso == "ofimatica": trabajo = min(97, trabajo + 6)
    trabajo = max(15, min(97, trabajo))

    # Precio — eficiencia financiera
    if presupuesto and presupuesto > 0:
        pct = (total / presupuesto) * 100
        precio = max(15, min(97, int(105 - pct)))
        if balance < 0:
            precio = max(10, int(50 + balance / presupuesto * 50))
    else:
        precio = 60

    # Térmica
    termica = 65
    for kws, score in [
        (["360"], 92), (["280mm", "280 aio"], 84),
        (["240mm", "aio"], 77), (["noctua", "arctic", "be quiet"], 72),
        (["stock"], 50),
    ]:
        if any(k in d for k in kws):
            termica = score; break
    else:
        termica = max(45, 75 - rank_idx * 7)
    if "acteck" in d or "micro-atx" in d: termica = max(40, termica - 6)
    termica = max(30, min(95, termica))

    # Longevidad
    if any(x in d for x in ["am5", "ddr5"]):   longevidad = 90
    elif any(x in d for x in ["lga1700", "am4", "ddr4"]): longevidad = 70
    else:                                        longevidad = 55
    longevidad = max(30, min(97, longevidad - rank_idx * 5))

    return [int(gaming), int(trabajo), int(precio), int(termica), int(longevidad)]


# ═══════════════════════════════════════════════════════════
#  RUTAS
# ═══════════════════════════════════════════════════════════
@app.route('/')
def portada():
    return render_template('portada2.html')

@app.route('/diagnostico-inicio')
def formulario_diagnostico():
    return render_template('index.html')


# ── CHATBOT HÍBRIDO ────────────────────────────────────────
@app.route('/chat-interactivo', methods=['POST'])
def chat_interactivo():
    data           = request.json
    msg            = data.get('mensaje', '').strip()
    msg_lower      = msg.lower()
    historial      = data.get('historial', [])       # últimos turnos del chat
    contexto_cfg   = data.get('contexto', '')        # configs en pantalla

    # ════════════════════════════════════════════════════
    # CAPA 1 — COMANDOS DE ACCIÓN (hardcoded, instantáneos)
    # Estos NO van a Gemini porque necesitan retornar
    # una acción específica para el frontend.
    # ════════════════════════════════════════════════════

    # Tema oscuro
    if any(p in msg_lower for p in ["modo oscuro", "dark mode", "pon oscuro", "activa oscuro"]):
        return jsonify({"res": "🌙 Modo oscuro activado.", "accion": "SET_THEME", "modo": "dark"})

    # Tema claro
    if any(p in msg_lower for p in ["modo claro", "light mode", "pon claro", "activa claro"]):
        return jsonify({"res": "☀️ Modo claro activado.", "accion": "SET_THEME", "modo": "light"})

    # Toggle tema
    if any(p in msg_lower for p in ["cambia tema", "cambiar tema", "toggle tema"]):
        return jsonify({"res": "Alternando tema.", "accion": "TOGGLE_THEME"})

    # Filtrado Top N — regex para cualquier número
    top_match = re.search(r'\btop\s*(\d+)\b', msg_lower)
    if top_match:
        num = top_match.group(1)
        return jsonify({
            "res": f"📊 Mostrando las mejores <b>{num}</b> configuraciones.",
            "accion": "FILTER_TOP", "valor": num
        })

    # Mostrar todo
    if any(p in msg_lower for p in ["mostrar todo", "ver todo", "quitar filtro", "sin filtro", "mostrar todas"]):
        return jsonify({"res": "🔄 Mostrando todas las configuraciones.", "accion": "FILTER_TOP", "valor": "999"})

    # Ordenar de menor a mayor precio
    if any(p in msg_lower for p in ["menor precio", "mas barato", "más barato", "barato primero",
                                     "de menor a mayor", "precio asc"]):
        return jsonify({"res": "🔽 Ordenando de menor a mayor precio.", "accion": "SORT", "criterio": "precio_asc"})

    # Ordenar de mayor a menor precio
    if any(p in msg_lower for p in ["mayor precio", "mas caro", "más caro", "caro primero",
                                     "de mayor a menor", "precio desc"]):
        return jsonify({"res": "🔼 Ordenando de mayor a menor precio.", "accion": "SORT", "criterio": "precio_desc"})

    # Ordenar por sinergia
    if any(p in msg_lower for p in ["sinergia", "mejor score", "por score", "ordenar sinergia"]):
        return jsonify({"res": "⚡ Ordenando por índice de sinergia.", "accion": "SORT", "criterio": "sinergia"})

    # Ordenar por balance
    if any(p in msg_lower for p in ["mejor balance", "mas sobra", "más sobra"]):
        return jsonify({"res": "💚 Ordenando por mejor balance.", "accion": "SORT", "criterio": "balance"})

    # Analizador financiero
    if any(p in msg_lower for p in ["presupuesto", "analizador financiero", "mis finanzas",
                                     "cuanto tengo", "analiza mis"]):
        return jsonify({"res": "💰 Abriendo el analizador financiero.", "accion": "OPEN_BUDGET"})

    # Expandir mejor opción
    if any(p in msg_lower for p in ["mejor opcion", "mejor opción", "primera opcion",
                                     "expande la mejor", "ver la mejor"]):
        return jsonify({"res": "✅ Expandiendo la configuración con mayor sinergia.", "accion": "EXPAND_FIRST"})

    # Contar configuraciones
    if any(p in msg_lower for p in ["cuantas hay", "cuántas hay", "cuantas configuraciones",
                                     "cuantos resultados"]):
        return jsonify({"res": "Contando configuraciones visibles...", "accion": "COUNT_CARDS"})

    # Tiendas / highlight
    if any(p in msg_lower for p in ["donde comprar", "dónde comprar", "tiendas",
                                     "donde conseguir", "dónde conseguir", "tienda"]):
        return jsonify({
            "res": ("🏪 <b>Tiendas recomendadas en México:</b><br>"
                    "1️⃣ <b>Cyberpuerta</b> (cyberpuerta.mx) — generalmente el más barato<br>"
                    "2️⃣ <b>DDTech</b> (ddtech.com.mx) — buen stock de componentes<br>"
                    "3️⃣ <b>Mercado Libre</b> — revisa vendedores con buena reputación<br>"
                    "4️⃣ <b>Amazon México</b> — conveniente con Prime"),
            "accion": "HIGHLIGHT_STORES"
        })

    # Nueva consulta / redirigir
    if any(p in msg_lower for p in ["nueva consulta", "reiniciar", "volver al inicio",
                                     "empezar de nuevo", "nuevo diagnostico", "nuevo diagnóstico"]):
        return jsonify({
            "res": "🆕 Redirigiendo al formulario de diagnóstico...",
            "accion": "REDIRECT", "url": "/diagnostico-inicio"
        })

    # ════════════════════════════════════════════════════
    # CAPA 2 — GEMINI (inteligencia conversacional)
    # Todo lo que no es un comando de acción va aquí.
    # ════════════════════════════════════════════════════
    respuesta = preguntar_a_gemini(msg, historial, contexto_cfg)
    return jsonify({"res": respuesta, "accion": None})


# ── MOTOR DE DIAGNÓSTICO ───────────────────────────────────
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
            f'(usuario (presupuesto {presupuesto}) (uso "{uso}") (resolucion "{resolucion}") '
            f'(clima "{clima}") (prioridad "{prioridad}") (streaming {streaming}) '
            f'(longevidad {longevidad}) (almacenamiento "{almacenamiento}") '
            f'(wifi {wifi_val}) (size {size_val}) (audio "{audio}"))'
        )
        env.run()

        sugerencias = []
        for fact in env.facts():
            if fact.template.name == 'recomendacion':
                raw = str(fact['razon'])
                if "CONFIGURACION_COMPLETA" not in raw:
                    continue
                partes = raw.split("|")
                try:
                    total_pc = float(raw.split("TOTAL: $")[1].split("|")[0].strip())
                    balance  = float(raw.split("BALANCE: $")[-1].strip())
                except Exception:
                    total_pc = 0.0; balance = 0.0

                detalles = [
                    p.strip() for p in partes[1:]
                    if "TOTAL" not in p and "BALANCE" not in p and ":" in p
                ]
                sugerencias.append({
                    'prioridad': fact['prioridad'],
                    'razon':     partes[0].strip(),
                    'detalles':  detalles,
                    'balance':   balance,
                    'total':     total_pc,
                    'sinergia':  0.0,
                    'radar':     []
                })

        def sort_key(s):
            return (1, -s['balance']) if s['balance'] >= 0 else (0, s['balance'])

        sugerencias = sorted(sugerencias, key=sort_key, reverse=True)

        for i, s in enumerate(sugerencias):
            if s['balance'] >= 0:
                s['sinergia'] = max(80.5, round(99.5 - (i * 0.5), 1))
            else:
                s['sinergia'] = max(30.0, round(75.0 - (abs(s['balance']) / 150), 1))

            detalles_str = " ".join(s['detalles']).lower()

            if (marca_cpu == "intel" and "ryzen" in detalles_str) or \
               (marca_cpu == "amd"   and "core"  in detalles_str):
                s['sinergia'] -= 4.5

            s['sinergia'] = max(20.0, round(s['sinergia'], 1))
            s['radar'] = calcular_radar(
                detalles_str, uso, s['sinergia'],
                s['balance'], presupuesto,
                total=s['total'], rank_idx=i
            )

        return render_template('resultado.html', sugerencias=sugerencias, estilo_rgb=estilo_rgb)

    except Exception as e:
        import traceback; traceback.print_exc()
        return f"<h3>Error en el motor CLIPS:</h3><pre>{str(e)}</pre>"


if __name__ == '__main__':
    app.run(debug=True)