import os
import zipfile
from pathlib import Path

def extraer_y_eliminar_zips():
    # Definir la ruta de la carpeta "Files"
    carpeta_files = Path("Files")
    
    # Verificar si la carpeta existe
    if not carpeta_files.exists():
        print(f"La carpeta {carpeta_files} no existe.")
        return
    
    # Obtener todos los archivos ZIP en la carpeta
    archivos_zip = list(carpeta_files.glob("*.zip"))
    
    if not archivos_zip:
        print("No se encontraron archivos ZIP en la carpeta.")
        return
    
    print(f"Procesando {len(archivos_zip)} archivo(s) ZIP...")
    
    # Procesar cada archivo ZIP
    for zip_path in archivos_zip:
        try:
            print(f"Extrayendo {zip_path.name}...")
            
            # Extraer el contenido del ZIP en la misma carpeta
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(carpeta_files)
            
            # Eliminar el archivo ZIP después de extraer
            zip_path.unlink()
            print(f"{zip_path.name} extraído y eliminado correctamente.")
            
        except Exception as e:
            print(f"Error al procesar {zip_path.name}: {str(e)}")
    
    print("Proceso completado.")

if __name__ == "__main__":
    extraer_y_eliminar_zips()