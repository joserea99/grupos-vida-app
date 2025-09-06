import uuid
from datetime import datetime
from typing import Dict, List, Optional

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
        self.telefono_conyuge = ""
        
        # Información profesional
        self.ocupacion = ""
        
        # Información adicional
        self.email = ""
        self.notas = ""
        self.fecha_creacion = datetime.now()
        self.fecha_actualizacion = datetime.now()
        
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
            'telefono': self.telefono,
            'edad': self.edad,
            'fecha_nacimiento': self.fecha_nacimiento.isoformat() if self.fecha_nacimiento else None,
            'estado_civil': self.estado_civil,
            'numero_hijos': self.numero_hijos,
            'edades_hijos': self.edades_hijos,
            'hijos_lista': self.hijos_lista,
            'tiene_hijos': self.tiene_hijos,
            'nombre_conyuge': self.nombre_conyuge,
            'telefono_conyuge': self.telefono_conyuge,
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
            'es_casado': self.es_casado
        }

class Lista:
    def __init__(self, nombre: str, color: str = "#3b82f6"):
        self.id = str(uuid.uuid4())
        self.nombre = nombre
        self.color = color
        self.tarjetas: List[Tarjeta] = []
        self.fecha_creacion = datetime.now()
        self.descripcion = ""
    
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
            'tarjetas': [t.to_dict() for t in self.tarjetas],
            'fecha_creacion': self.fecha_creacion.isoformat(),
            'estadisticas': self.get_estadisticas()
        }

class Tablero:
    def __init__(self, nombre: str, descripcion: str = "", icono: str = "👥"):
        self.id = str(uuid.uuid4())
        self.nombre = nombre
        self.descripcion = descripcion
        self.icono = icono
        self.listas: List[Lista] = []
        self.fecha_creacion = datetime.now()
        self.activo = True
        self.creador_id = None
        self.tipo = "ministerio"  # ministerio, grupo, evento, etc.
    
    def agregar_lista(self, nombre: str, color: str = "#3b82f6", descripcion: str = ""):
        lista = Lista(nombre, color)
        lista.descripcion = descripcion
        self.listas.append(lista)
        return lista
    
    def eliminar_lista(self, lista_id: str):
        self.listas = [l for l in self.listas if l.id != lista_id]
    
    def get_lista(self, lista_id: str) -> Optional[Lista]:
        return next((l for l in self.listas if l.id == lista_id), None)
    
    def get_todas_las_personas(self):
        """Obtener todas las personas de todas las listas"""
        personas = []
        for lista in self.listas:
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
        
        for lista in self.listas:
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
        return {
            'id': self.id,
            'nombre': self.nombre,
            'descripcion': self.descripcion,
            'icono': self.icono,
            'tipo': self.tipo,
            'listas': [l.to_dict() for l in self.listas],
            'fecha_creacion': self.fecha_creacion.isoformat(),
            'activo': self.activo,
            'total_listas': len(self.listas),
            'total_tarjetas': sum(len(l.tarjetas) for l in self.listas),
            'total_personas': sum(len(l.tarjetas) for l in self.listas),
            'estadisticas': self.get_estadisticas_completas()
        }

# Storage en memoria (por ahora)
class TableroStorage:
    def __init__(self):
        self.tableros: Dict[str, Tablero] = {}
        self._crear_datos_ejemplo()
    
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
        return tablero
    
    def eliminar_tablero(self, tablero_id: str):
        if tablero_id in self.tableros:
            del self.tableros[tablero_id]
    
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
        total_personas = sum(sum(len(l.tarjetas) for l in t.listas) for t in tableros_activos)
        
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

# Instancia global (por ahora)
storage = TableroStorage()