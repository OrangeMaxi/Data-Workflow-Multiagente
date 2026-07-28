import os

def write_document(filename: str, content: str) -> str:
    """
    Escribe contenido de texto o markdown en un archivo local en el directorio de salida (out_).
    Útil para guardar documentación, especificaciones o reportes.
    
    Args:
        filename: Nombre del archivo a crear (ej. especificaciones.md).
        content: Contenido a escribir en el archivo.
    """
    print(f"  [Herramienta System] Guardando documento '{filename}'...")
    
    # Crear un directorio 'output' temporal en el actual working directory
    out_dir = os.path.join(os.getcwd(), "output")
    os.makedirs(out_dir, exist_ok=True)
    
    safe_path = os.path.join(out_dir, filename)
    
    try:
        with open(safe_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return f"Documento '{filename}' guardado exitosamente en '{safe_path}'."
    except Exception as e:
        return f"Error al escribir archivo: {str(e)}"
