# Leer template
with open('app/templates/tableros/ver.html', 'r') as f:
    content = f.read()

# Código simple del cónyuge
conyuge_code = '''
                            {% if tarjeta.nombre_conyuge %}
                            <div style="margin-top: 8px; padding: 6px; background: #fff7ed; border-left: 3px solid #f59e0b; border-radius: 4px;">
                                <strong style="color: #f59e0b;">💑 {{ tarjeta.nombre_conyuge }}</strong>
                                {% if tarjeta.telefono_conyuge %}<br><small>📞 {{ tarjeta.telefono_conyuge }}</small>{% endif %}
                            </div>
                            {% endif %}'''

# Agregar después del teléfono de la persona
content = content.replace('</div>\n                        </div>', conyuge_code + '\n                        </div>\n                        </div>')

# Guardar
with open('app/templates/tableros/ver.html', 'w') as f:
    f.write(content)

print("✅ Info del cónyuge agregada")
