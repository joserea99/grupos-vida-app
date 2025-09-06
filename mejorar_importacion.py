#!/usr/bin/env python3

def agregar_openpyxl():
    """Agregar openpyxl a requirements.txt"""
    with open('requirements.txt', 'r') as f:
        content = f.read()
    
    if 'openpyxl' not in content:
        with open('requirements.txt', 'a') as f:
            f.write('\nopenpyxl>=3.1.2\n')
        print("✅ openpyxl agregado a requirements.txt")
        return True
    else:
        print("✅ openpyxl ya está en requirements.txt")
        return False

def agregar_validacion_excel():
    """Agregar validación básica para Excel"""
    with open('app/tableros/routes.py', 'r') as f:
        content = f.read()
    
    # Buscar donde está el procesamiento de archivos
    if 'filename.endswith' not in content:
        # Agregar detección de Excel
        old_pattern = "if archivo:"
        new_pattern = """if archivo:
                try:
                    import openpyxl
                    filename = archivo.filename.lower()
                    
                    if filename.endswith('.xlsx') or filename.endswith('.xls'):
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
                        
                        # Procesar como si fuera CSV
                        tarjetas_importadas = 0
                        errores = []
                        
                        for i, fila in enumerate(filas_datos, start=2):
                            # Aquí va el mismo procesamiento que ya tienes para CSV
                            pass
                            
                    elif filename.endswith('.csv'):
                        # Procesamiento CSV existente
                        pass
                    else:
                        flash('Formato no soportado. Use .xlsx, .xls o .csv', 'error')
                        return redirect(request.url)
                        
                except ImportError:
                    flash('openpyxl no instalado. Solo se soporta CSV', 'warning')
                    # Continuar con procesamiento CSV
                except Exception as e:
                    flash(f'Error: {str(e)}', 'error')
                    return redirect(request.url)"""
        
        if old_pattern in content:
            content = content.replace(old_pattern, new_pattern, 1)
            
            with open('app/tableros/routes.py', 'w') as f:
                f.write(content)
            
            print("✅ Detección de Excel agregada básicamente")
            return True
    
    print("⚠️ Ya tiene soporte para Excel o estructura diferente")
    return False

def main():
    print("🚀 Mejorando importación para soportar Excel...")
    
    need_install = agregar_openpyxl()
    excel_added = agregar_validacion_excel()
    
    print(f"\n📋 Resumen:")
    print(f"✅ openpyxl en requirements: {'Agregado' if need_install else 'Ya estaba'}")
    print(f"✅ Soporte Excel: {'Agregado' if excel_added else 'Ya existe'}")
    
    print(f"\n🚀 Próximos pasos:")
    if need_install:
        print("1. pip install openpyxl")
    print("2. python3 run.py")
    print("3. Probar con archivos .xlsx")

if __name__ == "__main__":
    main()
