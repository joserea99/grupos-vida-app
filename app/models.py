import uuid
import json
import os
from datetime import datetime
from typing import Dict, List, Optional
from werkzeug.security import generate_password_hash, check_password_hash

class Usuario:
    def __init__(self, username: str, email: str, password: str, nombre_completo: str = ""):
        self.id = str(uuid.uuid4())
        self.username = username
        self.email = email
        self.password_hash = generate_password_hash(password)
        self.nombre_completo = nombre_completo
        self.fecha_registro = datetime.now()
        self.activo = True
        self.rol = "admin" # admin, user
        self.suscripcion_activa = False
        self.stripe_customer_id = None
    
    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'password_hash': self.password_hash,
            'nombre_completo': self.nombre_completo,
            'fecha_registro': self.fecha_registro.isoformat(),
            'activo': self.activo,
            'rol': self.rol,
            'suscripcion_activa': self.suscripcion_activa,
            'stripe_customer_id': self.stripe_customer_id
        }

class UserStorage:
    def __init__(self, data_file: str = "data/users.json"):
        self.users: Dict[str, Usuario] = {}
        self.data_file = data_file
        self.load_from_disk()
    
    def create_user(self, username: str, email: str, password: str, nombre_completo: str = "") -> Optional[Usuario]:
        # Validar duplicados
        if self.get_user_by_username(username) or self.get_user_by_email(email):
            return None
            
        user = Usuario(username, email, password, nombre_completo)
        self.users[user.id] = user
        self.save_to_disk()
        return user
    
    def get_user(self, user_id: str) -> Optional[Usuario]:
        return self.users.get(user_id)
    
    def get_user_by_username(self, username: str) -> Optional[Usuario]:
        for user in self.users.values():
            if user.username.lower() == username.lower():
                return user
        return None
        
    def get_user_by_email(self, email: str) -> Optional[Usuario]:
        for user in self.users.values():
            if user.email.lower() == email.lower():
                return user
        return None
    
    def save_to_disk(self):
        try:
            os.makedirs(os.path.dirname(self.data_file), exist_ok=True)
            data = {
                'users': [u.to_dict() for u in self.users.values()]
            }
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Error saving users: {e}")
            
    def load_from_disk(self):
        if not os.path.exists(self.data_file):
            return
            
        try:
            with open(self.data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            for user_data in data.get('users', []):
                user = Usuario.__new__(Usuario)
                user.id = user_data['id']
                user.username = user_data['username']
                user.email = user_data['email']
                user.password_hash = user_data['password_hash']
                user.nombre_completo = user_data.get('nombre_completo', '')
                user.fecha_registro = datetime.fromisoformat(user_data['fecha_registro'])
                user.activo = user_data.get('activo', True)
                user.rol = user_data.get('rol', 'user')
                user.suscripcion_activa = user_data.get('suscripcion_activa', False)
                user.stripe_customer_id = user_data.get('stripe_customer_id')
                
                self.users[user.id] = user
        except Exception as e:
            print(f"Error loading users: {e}")


class Tarjeta:
    def __init__(self, nombre: str, apellido: str = "", direccion: str = "", telefono: str = ""):
        self.id = str(uuid.uuid4())
        
        # Información personal básica
        self.nombre = nombre
        self.apellido = apellido
        self.direccion = direccion
        self.telefono = telefono
        self.edad = None
        self.fecha_nacimiento = None
        
        # Información familiar
        self.estado_civil = ""  # Soltero, Casado, Divorciado, Viudo, Unión libre
        self.numero_hijos = 0
        self.edades_hijos = ""  # "5,8,12" - separadas por comas
        
        # Información del cónyuge
        self.nombre_conyuge = ""
        self.edad_conyuge = None
        self.telefono_conyuge = ""
        self.trabajo_conyuge = ""
        self.fecha_matrimonio = ""
        
        # Información profesional
        self.ocupacion = ""
        
        # Información adicional
        self.email = ""
        self.notas = ""
        self.fecha_creacion = datetime.now()
        self.fecha_actualizacion = datetime.now()
        
        # Información geográfica
        self.latitud = None
        self.longitud = None
        self.codigo_postal = ""
        
        # Campos para compatibilidad con el sistema actual
        self.titulo = f"{nombre} {apellido}".strip()  # Para compatibilidad
        self.descripcion = direccion  # Para compatibilidad con mapas
        self.responsable = ""  # Quien registró a la persona
        self.completada = False  # Para marcar como "contactado" o similar
        self.etiquetas = []
        self.prioridad = "media"
        self.estado = "activa"
        self.color = "#3b82f6"
        self.tipo = "persona"
        
        # Campos eclesiásticos
        self.bautizado = False
        self.asiste_grupo = False
        self.ministerio = ""
        self.es_lider = False
    
    @property
    def nombre_completo(self):
        return f"{self.nombre} {self.apellido}".strip()
    
    @property
    def hijos_lista(self):
        """Devuelve lista de edades de hijos como enteros"""
        if not self.edades_hijos:
            return []
        try:
            return [int(edad.strip()) for edad in self.edades_hijos.split(',') if edad.strip()]
        except:
            return []
    
    @property
    def tiene_hijos(self):
        return self.numero_hijos > 0
    
    @property
    def es_casado(self):
        return self.estado_civil.lower() in ['casado', 'casada', 'unión libre']
    
    def to_dict(self):
        return {
            'id': self.id,
            'nombre': self.nombre,
            'apellido': self.apellido,
            'nombre_completo': self.nombre_completo,
            'direccion': self.direccion,
            'codigo_postal': self.codigo_postal,
            'latitud': self.latitud,
            'longitud': self.longitud,
            'telefono': self.telefono,
            'edad': self.edad,
            'fecha_nacimiento': self.fecha_nacimiento.isoformat() if self.fecha_nacimiento else None,
            'estado_civil': self.estado_civil,
            'numero_hijos': self.numero_hijos,
            'edades_hijos': self.edades_hijos,
            'hijos_lista': self.hijos_lista,
            'tiene_hijos': self.tiene_hijos,
            'nombre_conyuge': self.nombre_conyuge,
            'edad_conyuge': self.edad_conyuge,
            'telefono_conyuge': self.telefono_conyuge,
            'trabajo_conyuge': self.trabajo_conyuge,
            'fecha_matrimonio': self.fecha_matrimonio,
            'ocupacion': self.ocupacion,
            'email': self.email,
            'notas': self.notas,
            'fecha_creacion': self.fecha_creacion.isoformat(),
            'fecha_actualizacion': self.fecha_actualizacion.isoformat(),
            
            # Campos de compatibilidad
            'titulo': self.titulo,
            'descripcion': self.descripcion,
            'responsable': self.responsable,
            'completada': self.completada,
            'etiquetas': self.etiquetas,
            'prioridad': self.prioridad,
            'estado': self.estado,
            'color': self.color,
            'tipo': self.tipo,
            'es_casado': self.es_casado,
            
            # Campos eclesiásticos
            'bautizado': self.bautizado,
            'asiste_grupo': self.asiste_grupo,
            'ministerio': self.ministerio,
            'es_lider': self.es_lider
        }

class Lista:
    def __init__(self, nombre: str, color: str = "#3b82f6", descripcion: str = ""):
        self.id = str(uuid.uuid4())
        self.nombre = nombre
        self.color = color
        self.tarjetas: List[Tarjeta] = []
        self.fecha_creacion = datetime.now()
        self.descripcion = descripcion
    
    def agregar_persona(self, nombre: str, apellido: str = "", direccion: str = "", telefono: str = "", **kwargs):
        """Crear una nueva persona en la lista"""
        persona = Tarjeta(nombre, apellido, direccion, telefono)
        
        # Asignar campos adicionales si se proporcionan
        for campo, valor in kwargs.items():
            if hasattr(persona, campo):
                setattr(persona, campo, valor)
        
        # Actualizar campos calculados
        persona.titulo = persona.nombre_completo
        persona.descripcion = direccion
        persona.fecha_actualizacion = datetime.now()
        
        self.tarjetas.append(persona)
        return persona

    def to_dict(self):
        return {
            'id': self.id,
            'nombre': self.nombre,
            'color': self.color,
            'descripcion': self.descripcion,
            'fecha_creacion': self.fecha_creacion.isoformat(),
            'tarjetas': [t.to_dict() for t in self.tarjetas]
        }
    
    def agregar_tarjeta(self, titulo: str, descripcion: str = "", responsable: str = ""):
        """Método de compatibilidad - parsea nombre completo"""
        partes_nombre = titulo.split()
        nombre = partes_nombre[0] if partes_nombre else titulo
        apellido = " ".join(partes_nombre[1:]) if len(partes_nombre) > 1 else ""
        
        return self.agregar_persona(
            nombre=nombre,
            apellido=apellido,
            direccion=descripcion,
            responsable=responsable
        )
    
    def eliminar_tarjeta(self, tarjeta_id: str):
        self.tarjetas = [t for t in self.tarjetas if t.id != tarjeta_id]
    
    def get_tarjeta(self, tarjeta_id: str) -> Optional[Tarjeta]:
        return next((t for t in self.tarjetas if t.id == tarjeta_id), None)
    
    def actualizar_persona(self, persona_id: str, **campos):
        """Actualizar información de una persona"""
        persona = self.get_tarjeta(persona_id)
        if persona:
            for campo, valor in campos.items():
                if hasattr(persona, campo):
                    setattr(persona, campo, valor)
            
            # Actualizar campos calculados
            persona.titulo = persona.nombre_completo
            persona.fecha_actualizacion = datetime.now()
            return persona
        return None
    
    def get_estadisticas(self):
        """Obtener estadísticas de la lista"""
        total = len(self.tarjetas)
        casados = len([p for p in self.tarjetas if p.es_casado])
        con_hijos = len([p for p in self.tarjetas if p.tiene_hijos])
        sin_telefono = len([p for p in self.tarjetas if not p.telefono])
        
        return {
            'total_personas': total,
            'casados': casados,
            'solteros': total - casados,
            'con_hijos': con_hijos,
            'sin_hijos': total - con_hijos,
            'sin_telefono': sin_telefono,
            'con_telefono': total - sin_telefono
        }
    
    def to_dict(self):
        return {
            'id': self.id,
            'nombre': self.nombre,
            'descripcion': self.descripcion,
            'color': self.color,
            'tarjetas': [t.to_dict() if hasattr(t, 'to_dict') else t for t in self.tarjetas],
            'fecha_creacion': self.fecha_creacion.isoformat(),
            'estadisticas': self.get_estadisticas()
        }

class Tablero:
    def __init__(self, nombre: str, descripcion: str = "", icono: str = "👥"):
        self.id = str(uuid.uuid4())
        self.nombre = nombre
        self.descripcion = descripcion
        self.icono = icono
        self.listas: Dict[str, Lista] = {} # Changed from List to Dict
        self.orden_listas: List[str] = [] # New attribute for order
        self.fecha_creacion = datetime.now()
        self.activo = True
        self.creador_id = None
        self.tipo = "ministerio"  # ministerio, grupo, evento, etc.
        self.historial: List[Dict] = [] # Registro de acciones

    def registrar_accion(self, usuario: str, accion: str, detalles: str):
        """Registrar una acción en el historial"""
        registro = {
            'fecha': datetime.now().isoformat(),
            'usuario': usuario,
            'accion': accion,
            'detalles': detalles
        }
        self.historial.insert(0, registro) # Agregar al principio (más reciente)
        # Limitar historial a los últimos 50 eventos
        if len(self.historial) > 50:
            self.historial = self.historial[:50]

        self.undo_stack: List[Dict] = []
        self.redo_stack: List[Dict] = []

    def registrar_undo(self, action_type: str, undo_data: dict, clear_redo: bool = True):
        """Registrar información para deshacer una acción"""
        self.undo_stack.append({
            'type': action_type,
            'data': undo_data,
            'timestamp': datetime.now().isoformat()
        })
        # Limitar stack
        if len(self.undo_stack) > 20:
            self.undo_stack.pop(0)
        
        if clear_redo:
            self.redo_stack = []
    def agregar_lista(self, nombre: str, color: str = "#e2e8f0", descripcion: str = "") -> Lista:
        """Crear una nueva lista en el tablero"""
        lista = Lista(nombre, color, descripcion)
        self.listas[lista.id] = lista
        self.orden_listas.append(lista.id)
        return lista
        
    def editar_lista(self, lista_id: str, nombre: str, color: str, descripcion: str = "") -> Optional[Lista]:
        """Editar una lista existente"""
        if lista_id in self.listas:
            lista = self.listas[lista_id]
            lista.nombre = nombre
            lista.color = color
            lista.descripcion = descripcion # Added description update
            return lista
        return None
        
    def eliminar_lista(self, lista_id: str) -> bool:
        """Eliminar una lista y sus tarjetas"""
        if lista_id in self.listas:
            del self.listas[lista_id]
            if lista_id in self.orden_listas:
                self.orden_listas.remove(lista_id)
            return True
        return False

    def reordenar_listas(self, nuevo_orden: List[str]):
        """Reordenar las listas del tablero"""
        # Asegurarse de que el nuevo orden contenga solo IDs válidos y todos los IDs existentes
        valid_ids = [lid for lid in nuevo_orden if lid in self.listas]
        if len(valid_ids) == len(self.listas):
            self.orden_listas = valid_ids
        else:
            # Si el nuevo orden no es completo o contiene IDs inválidos,
            # se puede optar por lanzar un error o reconstruir el orden
            # manteniendo los elementos válidos y añadiendo los que faltan al final.
            # Por simplicidad, aquí solo se actualiza si es un orden completo y válido.
            # Para una implementación más robusta, se podría fusionar.
            pass
    
    def get_lista(self, lista_id: str) -> Optional[Lista]:
        return self.listas.get(lista_id) # Changed to dictionary lookup
    
    def get_todas_las_personas(self):
        """Obtener todas las personas de todas las listas"""
        personas = []
        for lista in self.listas.values():
            for persona in lista.tarjetas:
                personas.append({
                    **persona.to_dict(),
                    'lista_nombre': lista.nombre,
                    'lista_id': lista.id
                })
        return personas
    
    def buscar_personas(self, termino: str):
        """Buscar personas por nombre, dirección, teléfono, etc."""
        termino = termino.lower()
        resultados = []
        
        for lista in self.listas.values():
            for persona in lista.tarjetas:
                if (termino in persona.nombre_completo.lower() or 
                    termino in persona.direccion.lower() or
                    termino in persona.telefono or
                    termino in persona.ocupacion.lower() or
                    termino in persona.nombre_conyuge.lower()):
                    resultados.append({
                        **persona.to_dict(),
                        'lista_nombre': lista.nombre,
                        'lista_id': lista.id
                    })
        
        return resultados
    
    def get_estadisticas_completas(self):
        """Estadísticas completas del tablero"""
        todas_personas = self.get_todas_las_personas()
        total_personas = len(todas_personas)
        
        if total_personas == 0:
            return {
                'total_personas': 0,
                'total_listas': len(self.listas),
                'casados': 0,
                'solteros': 0,
                'con_hijos': 0,
                'sin_telefono': 0,
                'edad_promedio': 0,
                'ocupaciones_top': []
            }
        
        casados = len([p for p in todas_personas if p.get('es_casado')])
        con_hijos = len([p for p in todas_personas if p.get('tiene_hijos')])
        sin_telefono = len([p for p in todas_personas if not p.get('telefono')])
        
        # Calcular edad promedio
        edades = [p.get('edad') for p in todas_personas if p.get('edad')]
        edad_promedio = sum(edades) / len(edades) if edades else 0
        
        # Top ocupaciones
        ocupaciones = {}
        for p in todas_personas:
            ocup = p.get('ocupacion', '').strip()
            if ocup:
                ocupaciones[ocup] = ocupaciones.get(ocup, 0) + 1
        
        ocupaciones_top = sorted(ocupaciones.items(), key=lambda x: x[1], reverse=True)[:5]
        
        return {
            'total_personas': total_personas,
            'total_listas': len(self.listas),
            'casados': casados,
            'solteros': total_personas - casados,
            'con_hijos': con_hijos,
            'sin_hijos': total_personas - con_hijos,
            'sin_telefono': sin_telefono,
            'con_telefono': total_personas - sin_telefono,
            'edad_promedio': round(edad_promedio, 1),
            'ocupaciones_top': ocupaciones_top
        }
    

    def to_dict(self):
        try:
            listas_data = []
            # Listas ordenadas
            for lid in self.orden_listas:
                if lid in self.listas:
                    l = self.listas[lid]
                    if hasattr(l, 'to_dict'):
                        listas_data.append(l.to_dict())
                    else:
                        listas_data.append(l)
            
            # Listas no ordenadas (por si acaso)
            for l in self.listas.values():
                if l.id not in self.orden_listas:
                    if hasattr(l, 'to_dict'):
                        listas_data.append(l.to_dict())
                    else:
                        listas_data.append(l)

            return {
                'id': self.id,
                'nombre': self.nombre,
                'descripcion': self.descripcion,
                'color': getattr(self, 'color', '#ffffff'), # Handle missing color
                'icono': self.icono,
                'tipo': self.tipo,
                'activo': self.activo,
                'creador_id': self.creador_id,
                'fecha_creacion': self.fecha_creacion.isoformat() if isinstance(self.fecha_creacion, datetime) else str(self.fecha_creacion),
                'total_listas': len(self.listas),
                'total_tarjetas': sum(len(l.tarjetas) if hasattr(l, 'tarjetas') else 0 for l in self.listas.values()),
                'historial': self.historial,
                'undo_stack': self.undo_stack,
                'redo_stack': self.redo_stack,
                'listas': listas_data,
                'orden_listas': self.orden_listas
            }
        except Exception as e:
            print(f"ERROR in Tablero.to_dict: {e}")
            import traceback
            traceback.print_exc()
            return {
                'id': self.id,
                'nombre': self.nombre,
                'error': str(e),
                'listas': []
            }

# Storage con persistencia en JSON
class TableroStorage:
    def __init__(self, data_file: str = "data/tableros.json"):
        self.tableros: Dict[str, Tablero] = {}
        self.data_file = data_file
        
        # Intentar cargar datos existentes, o crear datos de ejemplo
        if not self.load_from_disk():
            self._crear_datos_ejemplo()
            self.save_to_disk()
    
    def _crear_datos_ejemplo(self):
        """Crear algunos tableros de ejemplo con personas reales"""
        # Tablero 1: Grupo de Vida Central
        tablero1 = Tablero("Grupo de Vida Central", "Ministerio de adultos del centro", "👥")
        
        # Lista de Líderes
        lideres = tablero1.agregar_lista("Líderes", "#ef4444", "Líderes del grupo")
        lideres.agregar_persona(
            nombre="Juan Carlos", 
            apellido="Pérez García",
            direccion="Calle Principal 123, Orlando, FL",
            telefono="407-555-0123",
            edad=35,
            estado_civil="Casado",
            numero_hijos=2,
            edades_hijos="8,12",
            ocupacion="Ingeniero",
            nombre_conyuge="María Elena Pérez",
            telefono_conyuge="407-555-0124",
            responsable="Pastor Miguel"
        )
        
        lideres.agregar_persona(
            nombre="Ana Isabel",
            apellido="Martínez López", 
            direccion="Avenida Central 456, Orlando, FL",
            telefono="407-555-0125",
            edad=32,
            estado_civil="Casada",
            numero_hijos=1,
            edades_hijos="5",
            ocupacion="Profesora",
            nombre_conyuge="Carlos Martínez",
            telefono_conyuge="407-555-0126",
            responsable="Pastor Miguel"
        )
        
        # Lista de Miembros
        miembros = tablero1.agregar_lista("Miembros", "#f59e0b", "Miembros activos")
        miembros.agregar_persona(
            nombre="Pedro",
            apellido="Sánchez Rivera",
            direccion="Boulevard Norte 789, Orlando, FL", 
            telefono="407-555-0127",
            edad=28,
            estado_civil="Soltero",
            numero_hijos=0,
            ocupacion="Contador",
            responsable="Juan Carlos"
        )
        
        miembros.agregar_persona(
            nombre="María José",
            apellido="González Herrera",
            direccion="Calle Sur 321, Orlando, FL",
            telefono="407-555-0128", 
            edad=26,
            estado_civil="Soltera",
            numero_hijos=0,
            ocupacion="Diseñadora",
            responsable="Ana Isabel"
        )
        
        # Lista de Visitantes
        visitantes = tablero1.agregar_lista("Visitantes", "#10b981", "Nuevos visitantes")
        visitantes.agregar_persona(
            nombre="Roberto",
            apellido="Vargas Castro",
            direccion="Calle Este 654, Orlando, FL",
            telefono="407-555-0129",
            edad=42,
            estado_civil="Divorciado", 
            numero_hijos=3,
            edades_hijos="10,14,16",
            ocupacion="Vendedor",
            responsable="Pedro"
        )
        
        self.tableros[tablero1.id] = tablero1
        
        # Tablero 2: Ministerio Juvenil
        tablero2 = Tablero("Ministerio Juvenil", "Jóvenes de 18-30 años", "🎓")
        
        # Lista de Jóvenes
        jovenes = tablero2.agregar_lista("Jóvenes", "#8b5cf6", "Jóvenes activos")
        jovenes.agregar_persona(
            nombre="Sofía",
            apellido="Ramírez Torres",
            direccion="Avenida Universitaria 987, Orlando, FL",
            telefono="407-555-0130",
            edad=22,
            estado_civil="Soltera",
            numero_hijos=0,
            ocupacion="Estudiante",
            responsable="Coordinador Juvenil"
        )
        
        jovenes.agregar_persona(
            nombre="Daniel",
            apellido="López Mendoza", 
            direccion="Calle Campus 147, Orlando, FL",
            telefono="407-555-0131",
            edad=24,
            estado_civil="Soltero",
            numero_hijos=0,
            ocupacion="Programador",
            responsable="Coordinador Juvenil"
        )
        
        self.tableros[tablero2.id] = tablero2
    
    def get_all_tableros(self) -> List[Tablero]:
        return list(self.tableros.values())
    
    def get_tablero(self, tablero_id: str) -> Optional[Tablero]:
        return self.tableros.get(tablero_id)
    
    def crear_tablero(self, nombre: str, descripcion: str = "", icono: str = "👥", creador_id: str = None):
        tablero = Tablero(nombre, descripcion, icono)
        tablero.creador_id = creador_id
        self.tableros[tablero.id] = tablero
        self.save_to_disk()
        return tablero
    
    def eliminar_tablero(self, tablero_id: str):
        if tablero_id in self.tableros:
            del self.tableros[tablero_id]
            self.save_to_disk()
    
    def buscar_personas_global(self, termino: str):
        """Buscar personas en todos los tableros"""
        resultados = []
        for tablero in self.tableros.values():
            personas = tablero.buscar_personas(termino)
            for persona in personas:
                persona['tablero_nombre'] = tablero.nombre
                persona['tablero_id'] = tablero.id
                resultados.append(persona)
        return resultados
    
    def get_stats(self):
        tableros_activos = [t for t in self.tableros.values() if t.activo]
        total_listas = sum(len(t.listas) for t in tableros_activos)
        total_personas = sum(sum(len(l.tarjetas) for l in t.listas.values()) for t in tableros_activos)
        
        # Estadísticas demográficas
        todas_personas = []
        for tablero in tableros_activos:
            todas_personas.extend(tablero.get_todas_las_personas())
        
        casados = len([p for p in todas_personas if p.get('es_casado')])
        con_hijos = len([p for p in todas_personas if p.get('tiene_hijos')])
        sin_telefono = len([p for p in todas_personas if not p.get('telefono')])
        
        return {
            'total_tableros': len(tableros_activos),
            'total_listas': total_listas,
            'total_tarjetas': total_personas,  # Para compatibilidad
            'total_personas': total_personas,
            'tableros_activos': len(tableros_activos),
            'personas_casadas': casados,
            'personas_solteras': total_personas - casados,
            'personas_con_hijos': con_hijos,
            'personas_sin_telefono': sin_telefono,
            'porcentaje_casados': round((casados / total_personas * 100) if total_personas > 0 else 0, 1),
            'porcentaje_con_hijos': round((con_hijos / total_personas * 100) if total_personas > 0 else 0, 1)
        }
    
    def save_to_disk(self):
        """Guardar todos los tableros a disco como JSON"""
        try:
            # Crear directorio si no existe
            os.makedirs(os.path.dirname(self.data_file), exist_ok=True)
            
            # Serializar todos        try:
            print(f"DEBUG: Saving {len(self.tableros)} tableros to disk...")
            data = {
                'tableros': [
                    self._serialize_tablero(tablero) 
                    for tablero in self.tableros.values()
                ],
                'saved_at': datetime.now().isoformat()
            }
            
            # Guardar a archivo
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            print(f"DEBUG: Successfully saved to {self.data_file}")
            return True
        except Exception as e:
            print(f"Error guardando datos: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def load_from_disk(self) -> bool:
        """Cargar tableros desde disco"""
        try:
            if not os.path.exists(self.data_file):
                return False
            
            with open(self.data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Deserializar tableros
            self.tableros = {}
            for tablero_data in data.get('tableros', []):
                tablero = self._deserialize_tablero(tablero_data)
                self.tableros[tablero.id] = tablero
            
            return len(self.tableros) > 0
        except Exception as e:
            print(f"Error cargando datos: {e}")
            return False
    
    def _serialize_tablero(self, tablero: Tablero) -> dict:
        """Convertir tablero a diccionario serializable"""
        return {
            'id': tablero.id,
            'nombre': tablero.nombre,
            'descripcion': tablero.descripcion,
            'icono': tablero.icono,
            'tipo': tablero.tipo,
            'activo': tablero.activo,
            'creador_id': tablero.creador_id,
            'fecha_creacion': tablero.fecha_creacion.isoformat(),
            'historial': getattr(tablero, 'historial', []),
            'undo_stack': getattr(tablero, 'undo_stack', []),
            'redo_stack': getattr(tablero, 'redo_stack', []),
            'listas': [
            self._serialize_lista(tablero.listas[lid]) 
            for lid in tablero.orden_listas 
            if lid in tablero.listas
        ] + [
            self._serialize_lista(l) 
            for l in tablero.listas.values() 
            if l.id not in tablero.orden_listas
        ]
        }
    
    def _serialize_lista(self, lista: Lista) -> dict:
        """Convertir lista a diccionario serializable"""
        return {
            'id': lista.id,
            'nombre': lista.nombre,
            'color': lista.color,
            'descripcion': lista.descripcion,
            'fecha_creacion': lista.fecha_creacion.isoformat(),
            'tarjetas': [
                self._serialize_tarjeta(tarjeta) 
                for tarjeta in lista.tarjetas
            ]
        }
    
    def _serialize_tarjeta(self, tarjeta: Tarjeta) -> dict:
        """Convertir tarjeta a diccionario serializable"""
        return {
            'id': tarjeta.id,
            'nombre': tarjeta.nombre,
            'apellido': tarjeta.apellido,
            'direccion': tarjeta.direccion,
            'latitud': getattr(tarjeta, 'latitud', None),
            'longitud': getattr(tarjeta, 'longitud', None),
            'telefono': tarjeta.telefono,
            'edad': tarjeta.edad,
            'fecha_nacimiento': tarjeta.fecha_nacimiento.isoformat() if tarjeta.fecha_nacimiento else None,
            'estado_civil': tarjeta.estado_civil,
            'numero_hijos': tarjeta.numero_hijos,
            'edades_hijos': tarjeta.edades_hijos,
            'nombre_conyuge': tarjeta.nombre_conyuge,
            'edad_conyuge': tarjeta.edad_conyuge,
            'telefono_conyuge': tarjeta.telefono_conyuge,
            'trabajo_conyuge': tarjeta.trabajo_conyuge,
            'fecha_matrimonio': tarjeta.fecha_matrimonio,
            'ocupacion': tarjeta.ocupacion,
            'email': tarjeta.email,
            'notas': tarjeta.notas,
            'fecha_creacion': tarjeta.fecha_creacion.isoformat(),
            'fecha_actualizacion': tarjeta.fecha_actualizacion.isoformat(),
            'responsable': tarjeta.responsable,
            'completada': tarjeta.completada,
            'etiquetas': tarjeta.etiquetas,
            'prioridad': tarjeta.prioridad,
            'estado': tarjeta.estado,
            'color': tarjeta.color,
            'tipo': tarjeta.tipo
        }
    
    def _deserialize_tablero(self, data: dict) -> Tablero:
        """Recrear tablero desde diccionario"""
        tablero = Tablero.__new__(Tablero)
        tablero.id = data['id']
        tablero.nombre = data['nombre']
        tablero.descripcion = data['descripcion']
        tablero.icono = data['icono']
        tablero.tipo = data.get('tipo', 'ministerio')
        tablero.activo = data.get('activo', True)
        tablero.creador_id = data.get('creador_id')
        tablero.fecha_creacion = datetime.fromisoformat(data['fecha_creacion'])
        tablero.historial = data.get('historial', [])
        tablero.undo_stack = data.get('undo_stack', [])
        tablero.redo_stack = data.get('redo_stack', [])
        tablero.listas = {}
        tablero.orden_listas = []
        
        for lista_data in data.get('listas', []):
            lista = self._deserialize_lista(lista_data)
            tablero.listas[lista.id] = lista
            tablero.orden_listas.append(lista.id)
            
        return tablero
    
    def _deserialize_lista(self, data: dict) -> Lista:
        """Recrear lista desde diccionario"""
        lista = Lista.__new__(Lista)
        lista.id = data['id']
        lista.nombre = data['nombre']
        lista.color = data['color']
        lista.descripcion = data.get('descripcion', '')
        lista.fecha_creacion = datetime.fromisoformat(data['fecha_creacion'])
        lista.tarjetas = [
            self._deserialize_tarjeta(tarjeta_data) 
            for tarjeta_data in data.get('tarjetas', [])
        ]
        return lista
    
    def _deserialize_tarjeta(self, data: dict) -> Tarjeta:
        """Recrear tarjeta desde diccionario"""
        tarjeta = Tarjeta.__new__(Tarjeta)
        tarjeta.id = data['id']
        tarjeta.nombre = data['nombre']
        tarjeta.apellido = data.get('apellido', '')
        tarjeta.direccion = data.get('direccion', '')
        tarjeta.codigo_postal = data.get('codigo_postal', '')
        tarjeta.latitud = data.get('latitud')
        tarjeta.longitud = data.get('longitud')
        tarjeta.telefono = data.get('telefono', '')
        tarjeta.edad = data.get('edad')
        tarjeta.fecha_nacimiento = datetime.fromisoformat(data['fecha_nacimiento']) if data.get('fecha_nacimiento') else None
        tarjeta.estado_civil = data.get('estado_civil', '')
        tarjeta.numero_hijos = data.get('numero_hijos', 0)
        tarjeta.edades_hijos = data.get('edades_hijos', '')
        tarjeta.nombre_conyuge = data.get('nombre_conyuge', '')
        tarjeta.edad_conyuge = data.get('edad_conyuge')
        tarjeta.telefono_conyuge = data.get('telefono_conyuge', '')
        tarjeta.trabajo_conyuge = data.get('trabajo_conyuge', '')
        tarjeta.fecha_matrimonio = data.get('fecha_matrimonio', '')
        tarjeta.ocupacion = data.get('ocupacion', '')
        tarjeta.email = data.get('email', '')
        tarjeta.notas = data.get('notas', '')
        tarjeta.fecha_creacion = datetime.fromisoformat(data['fecha_creacion'])
        tarjeta.fecha_actualizacion = datetime.fromisoformat(data['fecha_actualizacion'])
        tarjeta.titulo = f"{tarjeta.nombre} {tarjeta.apellido}".strip()
        tarjeta.descripcion = tarjeta.direccion
        tarjeta.responsable = data.get('responsable', '')
        tarjeta.completada = data.get('completada', False)
        tarjeta.etiquetas = data.get('etiquetas', [])
        tarjeta.prioridad = data.get('prioridad', 'media')
        tarjeta.estado = data.get('estado', 'activa')
        tarjeta.color = data.get('color', '#3b82f6')
        tarjeta.tipo = data.get('tipo', 'persona')
        
        # Campos eclesiásticos
        tarjeta.bautizado = data.get('bautizado', False)
        tarjeta.asiste_grupo = data.get('asiste_grupo', False)
        tarjeta.ministerio = data.get('ministerio', '')
        tarjeta.es_lider = data.get('es_lider', False)
        
        return tarjeta

# Instancia global
storage = TableroStorage()