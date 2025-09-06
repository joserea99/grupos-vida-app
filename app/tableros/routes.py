from flask import Blueprint, render_template, session, redirect, url_for, flash, request, jsonify, send_file
from io import BytesIO
from datetime import datetime
import pandas as pd
from app.models import storage

tableros_bp = Blueprint("tableros", __name__)

# Datos de plantillas (mantenemos las plantillas)
PLANTILLAS_EJEMPLO = {
    "direccion_adultos": {
        "liderazgo-1": {
            "nombre": "Reunión de Líderes",
            "descripcion": "Template para reuniones de liderazgo ministerial",
            "icono": "👥",
            "listas": ["Agenda", "Decisiones", "Seguimiento"],
        },
        "planificacion-1": {
            "nombre": "Planificación Anual",
            "descripcion": "Template para planificación estratégica",
            "icono": "📋",
            "listas": ["Objetivos", "Recursos", "Cronograma"],
        },
    },
    "familia": {
        "actividades-fam-1": {
            "nombre": "Actividades Familiares",
            "descripcion": "Template para eventos y actividades familiares",
            "icono": "👨‍👩‍👧‍👦",
            "listas": ["Planificación", "Participantes", "Recursos"],
        },
        "crecimiento-fam-1": {
            "nombre": "Crecimiento Familiar",
            "descripcion": "Template para seguimiento del crecimiento familiar",
            "icono": "🌱",
            "listas": ["Metas", "Progreso", "Reflexiones"],
        },
    },
    "estudiantes": {
        "juventud-1": {
            "nombre": "Grupo Juvenil",
            "descripcion": "Template para actividades y proyectos juveniles",
            "icono": "🎓",
            "listas": ["Actividades", "Participantes", "Recursos"],
        },
        "estudios-1": {
            "nombre": "Estudios Bíblicos",
            "descripcion": "Template para organizar estudios bíblicos",
            "icono": "📖",
            "listas": ["Temas", "Materiales", "Participantes"],
        },
    },
    "crecimiento": {
        "personal-1": {
            "nombre": "Crecimiento Personal",
            "descripcion": "Template para desarrollo personal y espiritual",
            "icono": "🚀",
            "listas": ["Metas", "Hábitos", "Reflexiones"],
        },
        "espiritual-1": {
            "nombre": "Metas Espirituales",
            "descripcion": "Template para el crecimiento espiritual",
            "icono": "🙏",
            "listas": ["Objetivos", "Prácticas", "Progreso"],
        },
    },
    "servicio": {
        "comunitario-1": {
            "nombre": "Proyectos de Servicio",
            "descripcion": "Template para proyectos de servicio comunitario",
            "icono": "🤝",
            "listas": ["Planificación", "Voluntarios", "Impacto"],
        },
        "ministerios-1": {
            "nombre": "Ministerios",
            "descripcion": "Template para gestionar diferentes ministerios",
            "icono": "⛪",
            "listas": ["Actividades", "Miembros", "Recursos"],
        },
    },
}


@tableros_bp.route("/")
def lista():
    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    # Obtener tableros reales del storage
    tableros = [t.to_dict() for t in storage.get_all_tableros()]
    stats = storage.get_stats()
    
    return render_template("tableros/lista.html", tableros=tableros, stats=stats)


@tableros_bp.route("/<tablero_id>")
def ver(tablero_id):
    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    tablero = storage.get_tablero(tablero_id)
    if not tablero:
        flash("Tablero no encontrado", "error")
        return redirect(url_for("tableros.lista"))

    tablero_dict = tablero.to_dict()
    listas = tablero_dict['listas']
    usuario = {"username": session.get("username")}
    
    return render_template("tableros/ver.html", tablero=tablero_dict, listas=listas, usuario=usuario)


@tableros_bp.route("/crear")
def crear():
    if "user_id" not in session:
        return redirect(url_for("auth.login"))
    return render_template("tableros/crear.html", plantillas=PLANTILLAS_EJEMPLO)


@tableros_bp.route("/procesar", methods=["POST"])
def procesar():
    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    # Obtener datos del formulario
    nombre = request.form.get("nombre", "").strip()
    descripcion = request.form.get("descripcion", "").strip()
    icono = request.form.get("icono", "📋").strip()
    
    if not nombre:
        flash("El nombre del tablero es obligatorio", "error")
        return redirect(url_for("tableros.crear"))

    # Crear tablero real
    tablero = storage.crear_tablero(
        nombre=nombre,
        descripcion=descripcion,
        icono=icono,
        creador_id=session.get("user_id")
    )
    
    # Agregar listas iniciales si se especificaron
    listas_nombres = request.form.getlist("listas[]")
    for lista_nombre in listas_nombres:
        if lista_nombre.strip():
            tablero.agregar_lista(lista_nombre.strip())
    
    flash(f"¡Tablero '{nombre}' creado exitosamente!", "success")
    return redirect(url_for("tableros.ver", tablero_id=tablero.id))


@tableros_bp.route("/plantillas")
def plantillas():
    if "user_id" not in session:
        return redirect(url_for("auth.login"))
    return render_template("tableros/plantillas.html", plantillas=PLANTILLAS_EJEMPLO)


@tableros_bp.route("/crear_desde_plantilla/<plantilla_id>")
def crear_desde_plantilla(plantilla_id):
    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    # Buscar la plantilla
    plantilla_encontrada = None
    for categoria_key, categoria in PLANTILLAS_EJEMPLO.items():
        if plantilla_id in categoria:
            plantilla_encontrada = categoria[plantilla_id]
            break

    if not plantilla_encontrada:
        flash("Plantilla no encontrada", "error")
        return redirect(url_for("tableros.plantillas"))

    # Crear tablero desde plantilla
    tablero = storage.crear_tablero(
        nombre=plantilla_encontrada["nombre"],
        descripcion=plantilla_encontrada["descripcion"],
        icono=plantilla_encontrada["icono"],
        creador_id=session.get("user_id")
    )
    
    # Agregar listas de la plantilla
    for lista_nombre in plantilla_encontrada["listas"]:
        tablero.agregar_lista(lista_nombre)
    
    flash(f"¡Tablero creado desde plantilla: {plantilla_encontrada['nombre']}!", "success")
    return redirect(url_for("tableros.ver", tablero_id=tablero.id))


# ===== RUTAS FUNCIONALES (REEMPLAZANDO PLACEHOLDERS) =====

@tableros_bp.route("/agregar_tarjeta", methods=["POST"])
def agregar_tarjeta():
    """Agregar nueva tarjeta a una lista (AJAX)"""
    if "user_id" not in session:
        return jsonify({'error': 'No autorizado'}), 401
    
    try:
        # El lista_id viene como query parameter
        lista_id = request.args.get('lista_id')
        
        # Los otros datos pueden venir como JSON o form data
        data = request.get_json()
        if not data:
            # Si no hay JSON, intentar form data
            data = request.form.to_dict()
        
        if not lista_id:
            return jsonify({'error': 'Lista ID es requerido'}), 400
        
        # Buscar la lista en todos los tableros
        lista_encontrada = None
        for tablero in storage.get_all_tableros():
            lista = tablero.get_lista(lista_id)
            if lista:
                lista_encontrada = lista
                break
        
        if not lista_encontrada:
            return jsonify({'error': 'Lista no encontrada'}), 404
        
        # Extraer datos de la persona
        nombre = data.get('nombre', '').strip()
        apellido = data.get('apellido', '').strip()
        direccion = data.get('direccion', '').strip()
        telefono = data.get('telefono', '').strip()
        
        # Si viene titulo en lugar de nombre/apellido (compatibilidad)
        titulo = data.get('titulo', '').strip()
        if titulo and not nombre:
            partes_titulo = titulo.split(' ', 1)
            nombre = partes_titulo[0] if partes_titulo else 'Persona'
            apellido = partes_titulo[1] if len(partes_titulo) > 1 else ''
        
        if not nombre:
            nombre = 'Nueva persona'
        
        # Crear nueva persona usando el método agregar_persona
        nueva_persona = lista_encontrada.agregar_persona(
            nombre=nombre,
            apellido=apellido,
            direccion=direccion,
            telefono=telefono,
            edad=int(data.get('edad')) if data.get('edad') else None,
            estado_civil=data.get('estado_civil', ''),
            numero_hijos=int(data.get('numero_hijos', 0)),
            edades_hijos=data.get('edades_hijos', ''),
            ocupacion=data.get('ocupacion', ''),
            nombre_conyuge=data.get('nombre_conyuge', ''),
            telefono_conyuge=data.get('telefono_conyuge', ''),
            email=data.get('email', ''),
            notas=data.get('notas', ''),
            responsable=data.get('responsable', session.get('username', ''))
        )
        
        return jsonify({
            'success': True,
            'tarjeta': nueva_persona.to_dict(),
            'message': f'Persona "{nueva_persona.nombre_completo}" creada exitosamente'
        }), 201
        
    except Exception as e:
        print(f"Error en agregar_tarjeta: {e}")
        return jsonify({'error': f'Error interno: {str(e)}'}), 500


@tableros_bp.route("/mover_tarjeta", methods=["POST"])
def mover_tarjeta():
    """Mover tarjeta entre listas (Drag & Drop)"""
    if "user_id" not in session:
        return jsonify({'error': 'No autorizado'}), 401
    
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No se enviaron datos'}), 400
        
        tarjeta_id = data.get('tarjeta_id')
        lista_origen_id = data.get('lista_origen_id')
        lista_destino_id = data.get('lista_destino_id')
        nueva_posicion = data.get('nueva_posicion', 0)
        
        if not all([tarjeta_id, lista_origen_id, lista_destino_id]):
            return jsonify({'error': 'Datos incompletos'}), 400
        
        # Buscar tarjeta en lista origen
        tarjeta_encontrada = None
        lista_origen = None
        lista_destino = None
        
        for tablero in storage.get_all_tableros():
            # Buscar lista origen
            if not lista_origen:
                lista_origen = tablero.get_lista(lista_origen_id)
            # Buscar lista destino
            if not lista_destino:
                lista_destino = tablero.get_lista(lista_destino_id)
            
            # Buscar tarjeta
            if lista_origen and not tarjeta_encontrada:
                tarjeta_encontrada = lista_origen.get_tarjeta(tarjeta_id)
        
        if not all([tarjeta_encontrada, lista_origen, lista_destino]):
            return jsonify({'error': 'Elementos no encontrados'}), 404
        
        # Mover tarjeta
        if lista_origen_id != lista_destino_id:
            # Remover de lista origen
            lista_origen.eliminar_tarjeta(tarjeta_id)
            # Agregar a lista destino
            lista_destino.tarjetas.insert(nueva_posicion, tarjeta_encontrada)
        else:
            # Reordenar dentro de la misma lista
            lista_origen.tarjetas.remove(tarjeta_encontrada)
            lista_origen.tarjetas.insert(nueva_posicion, tarjeta_encontrada)
        
        return jsonify({
            'success': True,
            'message': 'Tarjeta movida exitosamente'
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Error interno: {str(e)}'}), 500


@tableros_bp.route("/agregar_lista", methods=["POST"])
def agregar_lista():
    """Agregar nueva lista a un tablero (AJAX)"""
    if "user_id" not in session:
        return jsonify({'error': 'No autorizado'}), 401
    
    try:
        data = request.get_json()
        if not data:
            # Si no hay JSON, intentar form data
            data = request.form.to_dict()
        
        titulo = data.get('titulo', '').strip()
        color = data.get('color', '#3b82f6').strip()
        tablero_id = data.get('tablero_id', '').strip()
        
        if not titulo:
            return jsonify({'error': 'El título de la lista es requerido'}), 400
        
        if not tablero_id:
            return jsonify({'error': 'El ID del tablero es requerido'}), 400
        
        # Buscar el tablero
        tablero = storage.get_tablero(tablero_id)
        if not tablero:
            return jsonify({'error': 'Tablero no encontrado'}), 404
        
        # Agregar nueva lista usando el método existente
        nueva_lista = tablero.agregar_lista(titulo, color)
        
        return jsonify({
            'success': True,
            'lista': nueva_lista.to_dict(),
            'message': f'Lista "{titulo}" creada exitosamente'
        }), 201
        
    except Exception as e:
        print(f"Error en agregar_lista: {e}")
        return jsonify({'error': f'Error interno: {str(e)}'}), 500


@tableros_bp.route("/importar_excel/<lista_id>", methods=["GET", "POST"])
def importar_excel(lista_id):
    """Importar tarjetas desde archivo Excel/CSV REAL"""
    if "user_id" not in session:
        return redirect(url_for("auth.login"))
    
    try:
        # Buscar la lista en todos los tableros
        lista_encontrada = None
        tablero_encontrado = None
        
        for tablero in storage.get_all_tableros():
            lista = tablero.get_lista(lista_id)
            if lista:
                lista_encontrada = lista
                tablero_encontrado = tablero
                break
        
        if not lista_encontrada:
            flash('Lista no encontrada', 'error')
            return redirect(url_for('tableros.lista'))
        
        if request.method == 'GET':
            # Preparar datos para el template
            lista_data = lista_encontrada.to_dict()
            lista_data['tablero_id'] = tablero_encontrado.id
            lista_data['tablero_nombre'] = tablero_encontrado.nombre
            
            return render_template('tableros/importar.html', lista=lista_data)
        
        elif request.method == 'POST':
            # Procesar archivo subido REAL
            if 'archivo' not in request.files:
                flash('No se seleccionó ningún archivo', 'error')
                return redirect(request.url)
            
            archivo = request.files['archivo']
            if archivo.filename == '':
                flash('No se seleccionó ningún archivo', 'error')
                return redirect(request.url)
            
            archivo.seek(0, 2)  # Ir al final
            file_size = archivo.tell()
            archivo.seek(0)  # Volver al inicio

            if file_size > 10 * 1024 * 1024:  # 10MB
                flash('❌ El archivo es demasiado grande. Máximo 10MB permitido.', 'error')
                return redirect(request.url)
            
            if archivo:
                filename = archivo.filename.lower()
                
                # Procesamiento para archivos Excel
                if filename.endswith('.xlsx') or filename.endswith('.xls'):
                    try:
                        import openpyxl
                        
                        # Procesar Excel
                        workbook = openpyxl.load_workbook(archivo)
                        sheet = workbook.active
                        
                        # Convertir Excel a formato similar a CSV
                        filas_datos = []
                        headers = [cell.value for cell in sheet[1]]
                        
                        for row in sheet.iter_rows(min_row=2, values_only=True):
                            fila_dict = {}
                            for i, value in enumerate(row):
                                if i < len(headers) and headers[i]:
                                    fila_dict[headers[i]] = str(value) if value else ''
                            if any(fila_dict.values()):
                                filas_datos.append(fila_dict)
                        
                        # Procesar datos de Excel
                        tarjetas_importadas = 0
                        errores = []
                        
                        for i, fila in enumerate(filas_datos, start=2):
                            try:
                                # Extraer datos de la fila Excel
                                nombre_completo = (
                                    fila.get('Nombre Completo', '') or 
                                    fila.get('Nombre', '') or 
                                    fila.get('Name', '') or
                                    fila.get('nombre', '')
                                ).strip()
                                
                                direccion = (
                                    fila.get('Dirección', '') or 
                                    fila.get('Direccion', '') or 
                                    fila.get('direccion', '')
                                ).strip()
                                
                                telefono = (
                                    fila.get('Teléfono', '') or 
                                    fila.get('Telefono', '') or 
                                    fila.get('telefono', '')
                                ).strip()
                                
                                edad_str = str(fila.get('Edad', '') or '').strip()
                                estado_civil = str(fila.get('Estado Civil', '') or '').strip()
                                hijos_str = str(fila.get('Num Hijos', '') or '0').strip()
                                edades_hijos = str(fila.get('Edades Hijos', '') or '').strip()
                                
                                # Campos del cónyuge
                                nombre_conyuge = str(fila.get('Nombre Cónyuge', '') or '').strip()
                                telefono_conyuge = str(fila.get('Teléfono Cónyuge', '') or '').strip()
                                edad_conyuge_str = str(fila.get('Edad Cónyuge', '') or '').strip()
                                trabajo_conyuge = str(fila.get('Trabajo Cónyuge', '') or '').strip()
                                fecha_matrimonio = str(fila.get('Fecha Matrimonio', '') or '').strip()
                                
                                # Validaciones
                                if not nombre_completo:
                                    errores.append(f'Fila {i}: Nombre es obligatorio')
                                    continue
                                
                                # Procesar nombre
                                partes_nombre = nombre_completo.split(' ', 1)
                                nombre = partes_nombre[0]
                                apellido = partes_nombre[1] if len(partes_nombre) > 1 else ''
                                
                                # Convertir edad
                                edad = None
                                if edad_str:
                                    try:
                                        edad = int(float(edad_str))
                                    except:
                                        pass
                                
                                # Convertir edad del cónyuge
                                edad_conyuge = None
                                if edad_conyuge_str:
                                    try:
                                        edad_conyuge = int(float(edad_conyuge_str))
                                    except:
                                        pass
                                
                                # Convertir hijos
                                numero_hijos = 0
                                if hijos_str:
                                    try:
                                        numero_hijos = int(float(hijos_str))
                                    except:
                                        pass
                                
                                # Crear persona desde Excel
                                nueva_persona = lista_encontrada.agregar_persona(
                                    nombre=nombre,
                                    apellido=apellido,
                                    direccion=direccion,
                                    telefono=telefono,
                                    edad=edad,
                                    estado_civil=estado_civil,
                                    numero_hijos=numero_hijos,
                                    edades_hijos=edades_hijos,
                                    nombre_conyuge=nombre_conyuge,
                                    telefono_conyuge=telefono_conyuge,
                                    edad_conyuge=edad_conyuge,
                                    trabajo_conyuge=trabajo_conyuge,
                                    fecha_matrimonio=fecha_matrimonio,
                                    responsable=session.get('username', 'Usuario')
                                )
                                
                                tarjetas_importadas += 1
                                
                            except Exception as e:
                                errores.append(f'Fila {i}: Error - {str(e)}')
                                continue
                        
                        # Mostrar resultados Excel
                        if tarjetas_importadas > 0:
                            flash(f'✅ Importadas {tarjetas_importadas} personas desde Excel', 'success')
                        if errores:
                            flash(f'⚠️ {len(errores)} errores encontrados', 'warning')
                        if tarjetas_importadas == 0:
                            flash('❌ No se importaron datos desde Excel', 'error')
                            return redirect(request.url)
                        
                        return redirect(url_for('tableros.ver', tablero_id=tablero_encontrado.id))
                            
                    except ImportError:
                        flash('openpyxl no instalado. Procesando como CSV...', 'warning')
                        # Continuar con procesamiento CSV
                    except Exception as e:
                        flash(f'Error procesando Excel: {str(e)}', 'error')
                        # Intentar procesar como CSV
                
                # Procesamiento para archivos CSV
                if filename.endswith('.csv') or True:  # Fallback a CSV si Excel falla
                    try:
                        import csv
                        import io
                        
                        # Leer el archivo
                        archivo_contenido = archivo.read().decode('utf-8')
                        
                        # Detectar si es CSV o intentar como CSV
                        lineas = archivo_contenido.strip().split('\n')
                        
                        if len(lineas) < 2:
                            flash('El archivo debe tener al menos una fila de encabezados y una fila de datos', 'error')
                            return redirect(request.url)
                        
                        # Leer como CSV
                        csv_reader = csv.DictReader(io.StringIO(archivo_contenido))
                        
                        tarjetas_importadas = 0
                        errores = []
                        
                        for i, fila in enumerate(csv_reader, start=2):  # Empezar en 2 porque la fila 1 son headers
                            try:
                                # Extraer datos de la fila (flexible con diferentes nombres de columnas)
                                nombre_completo = (
                                    fila.get('Nombre Completo', '') or 
                                    fila.get('Nombre', '') or 
                                    fila.get('Name', '') or
                                    fila.get('nombre', '') or
                                    fila.get('titulo', '') or
                                    fila.get('Titulo', '')
                                ).strip()
                                
                                direccion = (
                                    fila.get('Dirección', '') or 
                                    fila.get('Direccion', '') or 
                                    fila.get('Address', '') or
                                    fila.get('direccion', '') or
                                    fila.get('Descripción', '') or
                                    fila.get('Descripcion', '')
                                ).strip()
                                
                                telefono = (
                                    fila.get('Teléfono', '') or 
                                    fila.get('Telefono', '') or 
                                    fila.get('Phone', '') or
                                    fila.get('telefono', '')
                                ).strip()
                                
                                edad_str = (
                                    fila.get('Edad', '') or 
                                    fila.get('Age', '') or
                                    fila.get('edad', '')
                                ).strip()
                                
                                estado_civil = (
                                    fila.get('Estado Civil', '') or 
                                    fila.get('Estado_Civil', '') or
                                    fila.get('Marital Status', '') or
                                    fila.get('estado_civil', '')
                                ).strip()
                                
                                hijos_str = (
                                    fila.get('Num Hijos', '') or 
                                    fila.get('Número de Hijos', '') or
                                    fila.get('Numero de Hijos', '') or
                                    fila.get('Children', '') or
                                    fila.get('numero_hijos', '') or
                                    '0'
                                ).strip()
                                
                                edades_hijos = (
                                    fila.get('Edades Hijos', '') or 
                                    fila.get('Edades de Hijos', '') or
                                    fila.get('edades_hijos', '')
                                ).strip()
                                
                                # Campos del cónyuge - VERSIÓN CORREGIDA
                                nombre_conyuge = (
                                    fila.get('Nombre Cónyuge', '') or
                                    fila.get('Nombre Conyuge', '') or  # Sin tilde
                                    fila.get('nombre_conyuge', '')
                                ).strip()
                                
                                telefono_conyuge = (
                                    fila.get('Teléfono Cónyuge', '') or
                                    fila.get('Telefono Conyuge', '') or  # Sin tilde
                                    fila.get('telefono_conyuge', '')
                                ).strip()
                                
                                # Edad del cónyuge
                                edad_conyuge_str = (
                                    fila.get('Edad Cónyuge', '') or
                                    fila.get('Edad Conyuge', '') or  # Sin tilde
                                    fila.get('edad_conyuge', '')
                                ).strip()
                                
                                edad_conyuge = None
                                if edad_conyuge_str:
                                    try:
                                        edad_conyuge = int(edad_conyuge_str)
                                    except ValueError:
                                        pass  # Mantener como None si no es válido
                                
                                # Trabajo del cónyuge
                                trabajo_conyuge = (
                                    fila.get('Trabajo Cónyuge', '') or
                                    fila.get('Trabajo Conyuge', '') or  # Sin tilde
                                    fila.get('trabajo_conyuge', '')
                                ).strip()
                                
                                # Fecha de matrimonio
                                fecha_matrimonio = (
                                    fila.get('Fecha Matrimonio', '') or
                                    fila.get('fecha_matrimonio', '')
                                ).strip()
                                
                                # Validaciones básicas
                                if not nombre_completo:
                                    errores.append(f"Fila {i}: Nombre es obligatorio")
                                    continue
                                
                                # Separar nombre y apellido si viene junto
                                partes_nombre = nombre_completo.split(' ', 1)
                                nombre = partes_nombre[0] if partes_nombre else nombre_completo
                                apellido = partes_nombre[1] if len(partes_nombre) > 1 else ''
                                
                                # Convertir edad
                                edad = None
                                if edad_str:
                                    try:
                                        edad = int(edad_str)
                                    except ValueError:
                                        errores.append(f"Fila {i}: Edad '{edad_str}' no es un número válido")
                                
                                # Convertir número de hijos
                                numero_hijos = 0
                                if hijos_str:
                                    try:
                                        numero_hijos = int(hijos_str)
                                    except ValueError:
                                        errores.append(f"Fila {i}: Número de hijos '{hijos_str}' no es válido")
                                
                                # Crear la persona usando el método correcto con TODOS los campos
                                nueva_persona = lista_encontrada.agregar_persona(
                                    nombre=nombre,
                                    apellido=apellido,
                                    direccion=direccion,
                                    telefono=telefono,
                                    edad=edad,
                                    estado_civil=estado_civil,
                                    numero_hijos=numero_hijos,
                                    edades_hijos=edades_hijos,
                                    nombre_conyuge=nombre_conyuge,
                                    telefono_conyuge=telefono_conyuge,
                                    edad_conyuge=edad_conyuge,
                                    trabajo_conyuge=trabajo_conyuge,
                                    fecha_matrimonio=fecha_matrimonio,
                                    responsable=session.get('username', 'Usuario')
                                )
                                
                                tarjetas_importadas += 1
                                
                            except Exception as e:
                                errores.append(f"Fila {i}: Error procesando datos - {str(e)}")
                                continue
                        
                        # Mostrar resultados
                        if tarjetas_importadas > 0:
                            flash(f'✅ Se importaron {tarjetas_importadas} personas exitosamente', 'success')
                        
                        if errores:
                            flash(f'⚠️ Se encontraron {len(errores)} errores: {"; ".join(errores[:3])}{"..." if len(errores) > 3 else ""}', 'warning')
                        
                        if tarjetas_importadas == 0:
                            flash('❌ No se importó ninguna persona. Verifica el formato del archivo.', 'error')
                            return redirect(request.url)
                        
                        return redirect(url_for('tableros.ver', tablero_id=tablero_encontrado.id))
                        
                    except Exception as e:
                        flash(f'Error procesando el archivo: {str(e)}', 'error')
                        return redirect(request.url)
                    
    except Exception as e:
        flash(f'Error en la importación: {str(e)}', 'error')
        return redirect(url_for('tableros.lista'))


@tableros_bp.route("/descargar_plantilla")
def descargar_plantilla_excel():
    """Descargar template de Excel REAL para importación con campos del cónyuge"""
    if "user_id" not in session:
        return redirect(url_for("auth.login"))
    
    try:
        # Intentar generar Excel real
        try:
            import pandas as pd
            
            # Crear datos de ejemplo (igual estructura que tu CSV actual)
            data = {
                'Nombre': ['Juan Pérez', 'María García', 'Carlos López', 'Ana Martínez', 'Pedro Sánchez'],
                'Dirección': ['Calle 123 Col. Centro', 'Av. Principal 456', 'Blvd. Sur 789', 'Col. Norte 321', 'Calle Centro 654'],
                'Teléfono': ['555-0123', '555-0124', '555-0125', '555-0126', '555-0127'],
                'Edad': [35, 28, 42, 31, 29],
                'Estado Civil': ['Casado', 'Soltera', 'Casado', 'Casada', 'Soltero'],
                'Num Hijos': [2, 0, 3, 1, 0],
                'Edades Hijos': ['5, 8', '', '10, 12, 15', '7', ''],
                'Nombre Cónyuge': ['María Pérez', '', 'Ana López', 'Roberto Martínez', ''],
                'Edad Cónyuge': [32, '', 38, 33, ''],
                'Teléfono Cónyuge': ['555-0130', '', '555-0131', '555-0132', ''],
                'Trabajo Cónyuge': ['Maestra', '', 'Doctora', 'Ingeniero', ''],
                'Fecha Matrimonio': ['2018-06-15', '', '2005-03-20', '2015-09-10', '']
            }
            
            # Crear DataFrame
            df = pd.DataFrame(data)
            
            # Crear archivo Excel en memoria
            output = BytesIO()
            
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='Plantilla', index=False)
                
                # Ajustar ancho de columnas
                workbook = writer.book
                worksheet = writer.sheets['Plantilla']
                
                for column in worksheet.columns:
                    max_length = 0
                    column_letter = column[0].column_letter
                    
                    for cell in column:
                        try:
                            if len(str(cell.value)) > max_length:
                                max_length = len(str(cell.value))
                        except:
                            pass
                    
                    adjusted_width = min(max_length + 2, 50)
                    worksheet.column_dimensions[column_letter].width = adjusted_width
            
            output.seek(0)
            
            return send_file(
                output,
                as_attachment=True,
                download_name='plantilla_personas_con_conyuge.xlsx',
                mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
            
        except ImportError:
            # Fallback a CSV si pandas no está disponible
            flash('⚠️ Generando CSV (pandas no disponible)', 'warning')
            
            # Tu contenido CSV original exacto
            contenido_csv = """Nombre,Dirección,Teléfono,Edad,Estado Civil,Num Hijos,Edades Hijos,Nombre Cónyuge,Edad Cónyuge,Teléfono Cónyuge,Trabajo Cónyuge,Fecha Matrimonio
Juan Pérez,Calle 123 Col. Centro,555-0123,35,Casado,2,"5,8",María Pérez,32,555-0130,Maestra,2018-06-15
María García,Av. Principal 456,555-0124,28,Soltera,0,,,,,
Carlos López,Blvd. Sur 789,555-0125,42,Casado,3,"10,12,15",Ana López,38,555-0131,Doctora,2005-03-20
Ana Martínez,Col. Norte 321,555-0126,31,Casada,1,"7",Roberto Martínez,33,555-0132,Ingeniero,2015-09-10
Pedro Sánchez,Calle Centro 654,555-0127,29,Soltero,0,,,,,"""
            
            output = BytesIO()
            output.write(contenido_csv.encode('utf-8'))
            output.seek(0)
            
            return send_file(
                output,
                as_attachment=True,
                download_name='plantilla_personas_con_conyuge.csv',
                mimetype='text/csv'
            )
        
    except Exception as e:
        flash(f'Error generando plantilla: {str(e)}', 'error')
        return redirect(url_for('tableros.lista'))


# ===== RUTAS ADICIONALES =====

@tableros_bp.route("/eliminar_lista/<lista_id>", methods=["DELETE"])
def eliminar_lista(lista_id):
    """Eliminar una lista del tablero"""
    if "user_id" not in session:
        return jsonify({'error': 'No autorizado'}), 401
    
    try:
        # Buscar la lista en todos los tableros
        for tablero in storage.get_all_tableros():
            lista = tablero.get_lista(lista_id)
            if lista:
                # Verificar que la lista no tenga tarjetas
                if len(lista.tarjetas) > 0:
                    return jsonify({
                        'error': 'No se puede eliminar una lista que contiene tarjetas'
                    }), 400
                
                # Eliminar lista usando el método existente
                tablero.eliminar_lista(lista_id)
                
                return jsonify({
                    'success': True,
                    'message': 'Lista eliminada exitosamente'
                }), 200
        
        return jsonify({'error': 'Lista no encontrada'}), 404
        
    except Exception as e:
        return jsonify({'error': f'Error interno: {str(e)}'}), 500


@tableros_bp.route("/eliminar_tarjeta/<tarjeta_id>", methods=["DELETE"])
def eliminar_tarjeta(tarjeta_id):
    """Eliminar una tarjeta de una lista"""
    if "user_id" not in session:
        return jsonify({'error': 'No autorizado'}), 401
    
    try:
        # Buscar la tarjeta en todos los tableros y listas
        for tablero in storage.get_all_tableros():
            for lista in tablero.listas:
                tarjeta = lista.get_tarjeta(tarjeta_id)
                if tarjeta:
                    # Eliminar tarjeta usando el método existente
                    lista.eliminar_tarjeta(tarjeta_id)
                    
                    return jsonify({
                        'success': True,
                        'message': 'Tarjeta eliminada exitosamente'
                    }), 200
        
        return jsonify({'error': 'Tarjeta no encontrada'}), 404
        
    except Exception as e:
        return jsonify({'error': f'Error interno: {str(e)}'}), 500


@tableros_bp.route("/editar/<tablero_id>", methods=["GET", "POST"])
def editar(tablero_id):
    if "user_id" not in session:
        return redirect(url_for("auth.login"))
    
    tablero = storage.get_tablero(tablero_id)
    if not tablero:
        flash("Tablero no encontrado", "error")
        return redirect(url_for("tableros.lista"))
    
    if request.method == 'POST':
        # Procesar edición del tablero
        nuevo_nombre = request.form.get('nombre', '').strip()
        nueva_descripcion = request.form.get('descripcion', '').strip()
        nuevo_icono = request.form.get('icono', tablero.icono)
        
        if nuevo_nombre:
            tablero.nombre = nuevo_nombre
            tablero.descripcion = nueva_descripcion
            tablero.icono = nuevo_icono
            flash('Tablero actualizado exitosamente', 'success')
        
        return redirect(url_for('tableros.ver', tablero_id=tablero.id))
    
    return render_template("tableros/editar.html", tablero=tablero.to_dict())


@tableros_bp.route("/editar_lista/<lista_id>", methods=["GET", "POST"])
def editar_lista(lista_id):
    """Editar una lista del tablero"""
    if "user_id" not in session:
        return redirect(url_for("auth.login"))
    
    # Buscar la lista en todos los tableros
    lista_encontrada = None
    tablero_encontrado = None
    
    for tablero in storage.get_all_tableros():
        lista = tablero.get_lista(lista_id)
        if lista:
            lista_encontrada = lista
            tablero_encontrado = tablero
            break
    
    if not lista_encontrada:
        flash('Lista no encontrada', 'error')
        return redirect(url_for('tableros.lista'))
    
    if request.method == 'GET':
        # Mostrar formulario de edición
        return render_template('tableros/editar_lista.html', 
                             lista=lista_encontrada.to_dict(),
                             tablero=tablero_encontrado.to_dict())
    
    elif request.method == 'POST':
        # Procesar edición
        nuevo_nombre = request.form.get('nombre', '').strip()
        nuevo_color = request.form.get('color', lista_encontrada.color)
        
        if not nuevo_nombre:
            flash('El nombre de la lista es requerido', 'error')
            return redirect(request.url)
        
        # Actualizar lista
        lista_encontrada.nombre = nuevo_nombre
        lista_encontrada.color = nuevo_color
        
        flash(f'Lista "{nuevo_nombre}" actualizada exitosamente', 'success')
        return redirect(url_for('tableros.ver', tablero_id=tablero_encontrado.id))


@tableros_bp.route("/editar_tarjeta/<lista_id>/<tarjeta_id>", methods=["GET", "POST"])
def editar_tarjeta(lista_id, tarjeta_id):
    """Editar una tarjeta"""
    if "user_id" not in session:
        return redirect(url_for("auth.login"))
    
    # Buscar la tarjeta en todos los tableros
    tarjeta_encontrada = None
    lista_encontrada = None
    tablero_encontrado = None
    
    for tablero in storage.get_all_tableros():
        for lista in tablero.listas:
            tarjeta = lista.get_tarjeta(tarjeta_id)
            if tarjeta:
                tarjeta_encontrada = tarjeta
                lista_encontrada = lista
                tablero_encontrado = tablero
                break
        if tarjeta_encontrada:
            break
    
    if not tarjeta_encontrada:
        flash('Tarjeta no encontrada', 'error')
        return redirect(url_for('tableros.lista'))
    
    if request.method == 'GET':
        # Mostrar formulario de edición
        return render_template('tableros/editar_tarjeta.html', 
                             tarjeta=tarjeta_encontrada.to_dict(),
                             lista=lista_encontrada.to_dict(),
                             tablero=tablero_encontrado.to_dict())
    
    elif request.method == 'POST':
        # Procesar edición completa con todos los campos
        try:
            # Información básica
            nombre = request.form.get('nombre', '').strip()
            apellido = request.form.get('apellido', '').strip()
            
            if not nombre:
                flash('El nombre es requerido', 'error')
                return redirect(request.url)
            
            # Actualizar todos los campos de persona
            tarjeta_encontrada.nombre = nombre
            tarjeta_encontrada.apellido = apellido
            tarjeta_encontrada.telefono = request.form.get('telefono', '').strip()
            tarjeta_encontrada.email = request.form.get('email', '').strip()
            tarjeta_encontrada.direccion = request.form.get('direccion', '').strip()
            
            # Edad (convertir a entero si existe)
            edad_str = request.form.get('edad', '').strip()
            tarjeta_encontrada.edad = int(edad_str) if edad_str else None
            
            # Información familiar
            tarjeta_encontrada.estado_civil = request.form.get('estado_civil', '').strip()
            
            # Número de hijos (convertir a entero)
            numero_hijos_str = request.form.get('numero_hijos', '0').strip()
            tarjeta_encontrada.numero_hijos = int(numero_hijos_str) if numero_hijos_str else 0
            
            tarjeta_encontrada.edades_hijos = request.form.get('edades_hijos', '').strip()
            tarjeta_encontrada.ocupacion = request.form.get('ocupacion', '').strip()
            
            # Información del cónyuge
            tarjeta_encontrada.nombre_conyuge = request.form.get('nombre_conyuge', '').strip()
            tarjeta_encontrada.telefono_conyuge = request.form.get('telefono_conyuge', '').strip()
            
            # Información adicional
            tarjeta_encontrada.responsable = request.form.get('responsable', '').strip()
            tarjeta_encontrada.estado = request.form.get('estado', 'activa').strip()
            tarjeta_encontrada.notas = request.form.get('notas', '').strip()
            
            # Actualizar campos calculados
            tarjeta_encontrada.titulo = tarjeta_encontrada.nombre_completo
            tarjeta_encontrada.descripcion = tarjeta_encontrada.direccion
            tarjeta_encontrada.fecha_actualizacion = datetime.now()
            
            flash(f'Persona "{tarjeta_encontrada.nombre_completo}" actualizada exitosamente', 'success')
            return redirect(url_for('tableros.ver', tablero_id=tablero_encontrado.id))
            
        except ValueError as e:
            flash(f'Error en los datos: {str(e)}', 'error')
            return redirect(request.url)
        except Exception as e:
            flash(f'Error al actualizar la persona: {str(e)}', 'error')
            return redirect(request.url)


@tableros_bp.route("/descargar/<formato>")
def descargar_datos(formato):
    if "user_id" not in session:
        return redirect(url_for("auth.login"))
    flash(f"Descarga {formato} (funcionalidad próximamente)", "info")
    return redirect(url_for("tableros.lista"))


@tableros_bp.route("/exportar_datos/<tablero_id>/<formato>")
def exportar_datos(tablero_id, formato):
    """Exportar datos del tablero en diferentes formatos"""
    if "user_id" not in session:
        return redirect(url_for("auth.login"))
    
    try:
        # Buscar el tablero
        tablero = storage.get_tablero(tablero_id)
        if not tablero:
            flash('Tablero no encontrado', 'error')
            return redirect(url_for('tableros.lista'))
        
        # Recopilar todos los datos
        datos_exportacion = []
        for lista in tablero.listas:
            for tarjeta in lista.tarjetas:
                # Convertir tarjeta a diccionario con información completa
                persona_data = {
                    'Lista': lista.nombre,
                    'Nombre Completo': getattr(tarjeta, 'nombre_completo', tarjeta.titulo or ''),
                    'Nombre': getattr(tarjeta, 'nombre', ''),
                    'Apellido': getattr(tarjeta, 'apellido', ''),
                    'Teléfono': getattr(tarjeta, 'telefono', ''),
                    'Email': getattr(tarjeta, 'email', ''),
                    'Dirección': getattr(tarjeta, 'direccion', tarjeta.descripcion or ''),
                    'Edad': getattr(tarjeta, 'edad', ''),
                    'Estado Civil': getattr(tarjeta, 'estado_civil', ''),
                    'Número de Hijos': getattr(tarjeta, 'numero_hijos', ''),
                    'Edades de Hijos': getattr(tarjeta, 'edades_hijos', ''),
                    'Ocupación': getattr(tarjeta, 'ocupacion', ''),
                    'Nombre Cónyuge': getattr(tarjeta, 'nombre_conyuge', ''),
                    'Teléfono Cónyuge': getattr(tarjeta, 'telefono_conyuge', ''),
                    'Responsable': getattr(tarjeta, 'responsable', ''),
                    'Estado': getattr(tarjeta, 'estado', 'activa'),
                    'Notas': getattr(tarjeta, 'notas', ''),
                    'Fecha Creación': getattr(tarjeta, 'fecha_creacion', ''),
                    'Fecha Actualización': getattr(tarjeta, 'fecha_actualizacion', '')
                }
                datos_exportacion.append(persona_data)
        
        if not datos_exportacion:
            flash('No hay datos para exportar en este tablero', 'warning')
            return redirect(url_for('tableros.ver', tablero_id=tablero_id))
        
        # Generar archivo según formato
        if formato == 'csv':
            return _generar_csv(datos_exportacion, tablero.nombre)
        elif formato == 'excel':
            return _generar_excel(datos_exportacion, tablero.nombre)
        elif formato == 'json':
            return _generar_json(datos_exportacion, tablero.nombre)
        else:
            flash('Formato no soportado', 'error')
            return redirect(url_for('tableros.ver', tablero_id=tablero_id))
            
    except Exception as e:
        flash(f'Error al exportar datos: {str(e)}', 'error')
        return redirect(url_for('tableros.ver', tablero_id=tablero_id))


def _generar_csv(datos, nombre_tablero):
    """Generar archivo CSV"""
    import csv
    from io import StringIO
    
    output = StringIO()
    if datos:
        fieldnames = datos[0].keys()
        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(datos)
    
    # Convertir a bytes
    csv_bytes = BytesIO()
    csv_bytes.write(output.getvalue().encode('utf-8'))
    csv_bytes.seek(0)
    
    filename = f"{nombre_tablero}_datos_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    
    return send_file(
        csv_bytes,
        as_attachment=True,
        download_name=filename,
        mimetype='text/csv'
    )


def _generar_excel(datos, nombre_tablero):
    """Generar archivo Excel"""
    try:
        import pandas as pd
        
        # Crear DataFrame
        df = pd.DataFrame(datos)
        
        # Crear archivo Excel en memoria
        output = BytesIO()
        
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Datos', index=False)
            
            # Ajustar ancho de columnas
            worksheet = writer.sheets['Datos']
            for column in worksheet.columns:
                max_length = 0
                column_letter = column[0].column_letter
                for cell in column:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except:
                        pass
                adjusted_width = min(max_length + 2, 50)
                worksheet.column_dimensions[column_letter].width = adjusted_width
        
        output.seek(0)
        
        filename = f"{nombre_tablero}_datos_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        
        return send_file(
            output,
            as_attachment=True,
            download_name=filename,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        
    except ImportError:
        # Si pandas no está disponible, generar CSV con extensión xlsx
        return _generar_csv(datos, nombre_tablero)


def _generar_json(datos, nombre_tablero):
    """Generar archivo JSON"""
    import json
    
    output_data = {
        'tablero': nombre_tablero,
        'fecha_exportacion': datetime.now().isoformat(),
        'total_personas': len(datos),
        'datos': datos
    }
    
    json_bytes = BytesIO()
    json_bytes.write(json.dumps(output_data, indent=2, ensure_ascii=False).encode('utf-8'))
    json_bytes.seek(0)
    
    filename = f"{nombre_tablero}_datos_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    return send_file(
        json_bytes,
        as_attachment=True,
        download_name=filename,
        mimetype='application/json'
    )


@tableros_bp.route("/mover_lista", methods=["POST"])
def mover_lista():
    """Reordenar listas en el tablero (Drag & Drop)"""
    if "user_id" not in session:
        return jsonify({'error': 'No autorizado'}), 401
    
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No se enviaron datos'}), 400
        
        lista_id = data.get('lista_id')
        nueva_posicion = data.get('nueva_posicion', 0)
        
        if not lista_id:
            return jsonify({'error': 'Lista ID requerido'}), 400
        
        # Buscar la lista y el tablero
        lista_encontrada = None
        tablero_encontrado = None
        
        for tablero in storage.get_all_tableros():
            lista = tablero.get_lista(lista_id)
            if lista:
                lista_encontrada = lista
                tablero_encontrado = tablero
                break
        
        if not lista_encontrada or not tablero_encontrado:
            return jsonify({'error': 'Lista no encontrada'}), 404
        
        # Reordenar lista en el tablero
        tablero_encontrado.listas.remove(lista_encontrada)
        tablero_encontrado.listas.insert(nueva_posicion, lista_encontrada)
        
        return jsonify({
            'success': True,
            'message': 'Lista reordenada exitosamente'
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Error interno: {str(e)}'}), 500