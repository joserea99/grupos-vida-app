#!/usr/bin/env python3
"""
Script para agregar visualización de campos del cónyuge en los templates
"""

def fix_template_ver_tarjetas():
    """Modificar template ver.html para mostrar información del cónyuge"""
    
    template_path = 'app/templates/tableros/ver.html'
    
    try:
        with open(template_path, 'r') as f:
            content = f.read()
        
        # Template de información del cónyuge (simple y efectivo)
        conyuge_template = '''
                        {% if tarjeta.nombre_conyuge %}
                        <div style="margin-top: 10px; padding: 8px; background-color: #f1f5f9; border-left: 3px solid #f59e0b; border-radius: 4px;">
                            <strong style="color: #f59e0b;">💑 Cónyuge:</strong> {{ tarjeta.nombre_conyuge }}
                            {% if tarjeta.telefono_conyuge %}
                            <br><small>📞 {{ tarjeta.telefono_conyuge }}</small>
                            {% endif %}
                            {% if tarjeta.edad_conyuge %}
                            <br><small>🎂 {{ tarjeta.edad_conyuge }} años</small>
                            {% endif %}
                            {% if tarjeta.trabajo_conyuge %}
                            <br><small>💼 {{ tarjeta.trabajo_conyuge }}</small>
                            {% endif %}
                        </div>
                        {% endif %}'''
        
        # Buscar donde insertar la información del cónyuge
        patterns_to_find = [
            # Después de la información del teléfono
            r'(<p[^>]*>.*?teléfono.*?</p>)',
            # Después de información personal
            r'(<p[^>]*>.*?edad.*?</p>)',
            # Después del estado civil
            r'(<p[^>]*>.*?estado.*?civil.*?</p>)',
            # Patrón genérico de información
            r'(<div[^>]*class[^>]*card-body[^>]*>.*?</div>)'
        ]
        
        import re
        pattern_found = False
        
        for pattern in patterns_to_find:
            matches = re.findall(pattern, content, re.IGNORECASE | re.DOTALL)
            if matches:
                # Insertar después del primer match encontrado
                content = re.sub(pattern, r'\1' + conyuge_template, content, count=1, flags=re.IGNORECASE | re.DOTALL)
                pattern_found = True
                print(f"✅ Información del cónyuge agregada en template ver.html")
                break
        
        if not pattern_found:
            # Buscar cualquier div de tarjeta y agregar al final
            tarjeta_pattern = r'(</div>\s*</div>\s*<!-- [^>]*tarjeta|card[^>]* -->)'
            if re.search(tarjeta_pattern, content, re.IGNORECASE):
                content = re.sub(tarjeta_pattern, conyuge_template + r'\1', content, flags=re.IGNORECASE)
                pattern_found = True
                print("✅ Información del cónyuge agregada al final de las tarjetas")
        
        if pattern_found:
            # Guardar archivo modificado
            with open(template_path, 'w') as f:
                f.write(content)
            print("✅ Template ver.html actualizado para mostrar información del cónyuge")
        else:
            print("⚠️ No se pudo encontrar un lugar apropiado para insertar información del cónyuge")
            print("🔧 Agrega manualmente este código al template ver.html:")
            print(conyuge_template)
        
    except FileNotFoundError:
        print(f"❌ Template no encontrado: {template_path}")
    except Exception as e:
        print(f"❌ Error modificando template: {e}")

def main():
    """Aplicar correcciones a los templates"""
    
    print("🚀 Agregando visualización de información del cónyuge...")
    
    # Modificar template de visualización
    fix_template_ver_tarjetas()
    
    print("\n🎉 ¡Template actualizado!")
    print("\n📋 Pasos siguientes:")
    print("1. Reiniciar la aplicación: python3 run.py")
    print("2. Ver las tarjetas - ahora deberían mostrar información del cónyuge")
    print("3. Si no aparece, limpiar caché del navegador (Ctrl+F5)")

if __name__ == "__main__":
    main()
