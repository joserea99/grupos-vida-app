#!/usr/bin/env python3
"""
Script para agregar completamente el soporte de campos del cónyuge
"""

def fix_modelo_tarjeta():
    """Agregar campos faltantes al modelo Tarjeta"""
    
    # Leer archivo actual
    with open('app/models.py', 'r') as f:
        content = f.read()
    
    # Buscar la sección de información del cónyuge y reemplazarla
    old_conyuge_section = '''        # Información del cónyuge
        self.nombre_conyuge = ""
        self.telefono_conyuge = ""'''
    
    new_conyuge_section = '''        # Información del cónyuge
        self.nombre_conyuge = ""
        self.telefono_conyuge = ""
        self.edad_conyuge = None
        self.trabajo_conyuge = ""
        self.fecha_matrimonio = ""'''
    
    content = content.replace(old_conyuge_section, new_conyuge_section)
    
    # Guardar archivo
    with open('app/models.py', 'w') as f:
        f.write(content)
    
    print("✅ Modelo Tarjeta actualizado con campos del cónyuge")

def fix_importacion():
    """Modificar función de importación para leer campos del cónyuge"""
    
    # Leer archivo actual
    with open('app/tableros/routes.py', 'r') as f:
        content = f.read()
    
    # 1. Agregar lectura de campos del cónyuge
    find_text = '''                            edades_hijos = (
                                fila.get('Edades Hijos', '') or 
                                fila.get('Edades de Hijos', '') or
                                fila.get('edades_hijos', '')
                            ).strip()'''
    
    replacement_text = '''                            edades_hijos = (
                                fila.get('Edades Hijos', '') or 
                                fila.get('Edades de Hijos', '') or
                                fila.get('edades_hijos', '')
                            ).strip()
                            
                            # Campos del cónyuge
                            nombre_conyuge = (
                                fila.get('Nombre Cónyuge', '') or 
                                fila.get('Nombre_Conyuge', '') or
                                fila.get('nombre_conyuge', '')
                            ).strip()
                            
                            edad_conyuge_str = (
                                fila.get('Edad Cónyuge', '') or 
                                fila.get('Edad_Conyuge', '') or
                                fila.get('edad_conyuge', '')
                            ).strip()
                            
                            telefono_conyuge = (
                                fila.get('Teléfono Cónyuge', '') or 
                                fila.get('Telefono_Conyuge', '') or
                                fila.get('telefono_conyuge', '')
                            ).strip()
                            
                            trabajo_conyuge = (
                                fila.get('Trabajo Cónyuge', '') or 
                                fila.get('Trabajo_Conyuge', '') or
                                fila.get('trabajo_conyuge', '')
                            ).strip()
                            
                            fecha_matrimonio = (
                                fila.get('Fecha Matrimonio', '') or 
                                fila.get('Fecha_Matrimonio', '') or
                                fila.get('fecha_matrimonio', '')
                            ).strip()
                            
                            # Procesar edad del cónyuge
                            edad_conyuge = None
                            if edad_conyuge_str:
                                try:
                                    edad_conyuge = int(float(edad_conyuge_str))
                                except:
                                    edad_conyuge = None'''
    
    content = content.replace(find_text, replacement_text)
    
    # 2. Modificar la llamada a agregar_persona para incluir campos del cónyuge
    old_agregar_persona = '''                            # Crear la persona usando el método correcto
                            nueva_persona = lista_encontrada.agregar_persona(
                                nombre=nombre,
                                apellido=apellido,
                                direccion=direccion,
                                telefono=telefono,
                                edad=edad,
                                estado_civil=estado_civil,
                                numero_hijos=numero_hijos,
                                edades_hijos=edades_hijos,
                                responsable=session.get('username', 'Usuario')
                            )'''
    
    new_agregar_persona = '''                            # Crear la persona usando el método correcto
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
                                edad_conyuge=edad_conyuge,
                                telefono_conyuge=telefono_conyuge,
                                trabajo_conyuge=trabajo_conyuge,
                                fecha_matrimonio=fecha_matrimonio,
                                responsable=session.get('username', 'Usuario')
                            )'''
    
    content = content.replace(old_agregar_persona, new_agregar_persona)
    
    print("✅ Función de importación actualizada para leer y pasar campos del cónyuge")
    
    return content

def fix_metodo_agregar_persona():
    """Modificar método agregar_persona para aceptar campos del cónyuge"""
    
    # Leer archivo actual
    with open('app/models.py', 'r') as f:
        content = f.read()
    
    # Buscar el método agregar_persona en la clase Lista
    import re
    
    # Patrón para encontrar el método agregar_persona
    pattern = r'(def agregar_persona\(self[^:]+):.*?return tarjeta'
    
    # Buscar el método actual
    match = re.search(pattern, content, re.DOTALL)
    
    if match:
        old_method = match.group(0)
        
        # Crear nueva versión del método con campos del cónyuge
        new_method = '''def agregar_persona(self, nombre: str, apellido: str = "", direccion: str = "", telefono: str = "",
                     edad: int = None, estado_civil: str = "", numero_hijos: int = 0, edades_hijos: str = "",
                     nombre_conyuge: str = "", edad_conyuge: int = None, telefono_conyuge: str = "",
                     trabajo_conyuge: str = "", fecha_matrimonio: str = "", responsable: str = ""):
        """Agregar una nueva persona (tarjeta) a la lista con información completa incluyendo cónyuge"""
        tarjeta = Tarjeta(nombre, apellido, direccion, telefono)
        
        # Asignar información personal
        tarjeta.edad = edad
        tarjeta.estado_civil = estado_civil
        tarjeta.numero_hijos = numero_hijos
        tarjeta.edades_hijos = edades_hijos
        tarjeta.responsable = responsable
        
        # Asignar información del cónyuge
        tarjeta.nombre_conyuge = nombre_conyuge
        tarjeta.edad_conyuge = edad_conyuge
        tarjeta.telefono_conyuge = telefono_conyuge
        tarjeta.trabajo_conyuge = trabajo_conyuge
        tarjeta.fecha_matrimonio = fecha_matrimonio
        
        self.tarjetas.append(tarjeta)
        return tarjeta'''
        
        content = content.replace(old_method, new_method)
        
        # Guardar archivo
        with open('app/models.py', 'w') as f:
            f.write(content)
        
        print("✅ Método agregar_persona actualizado para manejar campos del cónyuge")
    else:
        print("⚠️ No se encontró el método agregar_persona - puede que tenga una estructura diferente")
        
        # Buscar alternativa - buscar toda la clase Lista
        lista_pattern = r'class Lista:.*?(?=class|\Z)'
        lista_match = re.search(lista_pattern, content, re.DOTALL)
        
        if lista_match:
            print("📋 Clase Lista encontrada - revisa manualmente el método agregar_persona")
            # Mostrar parte de la clase Lista para debug
            lista_content = lista_match.group(0)[:500] + "..."
            print(f"Contenido de clase Lista: {lista_content}")


def main():
    """Aplicar todas las correcciones"""
    
    print("🚀 Iniciando corrección completa de campos del cónyuge...")
    
    # 1. Corregir modelo Tarjeta
    try:
        fix_modelo_tarjeta()
    except Exception as e:
        print(f"❌ Error actualizando modelo: {e}")
    
    # 2. Corregir método agregar_persona
    try:
        fix_metodo_agregar_persona()
    except Exception as e:
        print(f"❌ Error actualizando método agregar_persona: {e}")
    
    # 3. Corregir importación
    try:
        content = fix_importacion()
        
        # Guardar archivo corregido
        with open('app/tableros/routes.py', 'w') as f:
            f.write(content)
        
        print("✅ Función de importación completamente actualizada")
        
    except Exception as e:
        print(f"❌ Error actualizando importación: {e}")
    
    print("\n🎉 ¡Correcciones aplicadas!")
    print("\n📋 Pasos siguientes:")
    print("1. Reiniciar la aplicación: python3 run.py")
    print("2. Descargar nueva plantilla con campos del cónyuge")
    print("3. Importar CSV - ahora mostrará información del cónyuge")
    print("4. Verificar que las tarjetas muestran datos del cónyuge")
    print("\n🔧 Si hay errores, verifica manualmente:")
    print("   - app/models.py - clase Tarjeta y método agregar_persona")
    print("   - app/tableros/routes.py - función importar_excel")

if __name__ == "__main__":
    main()