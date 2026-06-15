import os
import sys
import json
import urllib.request
import urllib.error
import zipfile
import shutil
import threading
import subprocess

# Determinar directorios clave
SRC_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE_DIR = os.path.dirname(SRC_DIR)  # facturacion_app
PROJECT_ROOT = os.path.dirname(BASE_DIR)  # Raíz del proyecto (donde está iniciar.bat)

SETTINGS_PATH = os.path.join(BASE_DIR, "config", "settings.json")
TEMP_UPDATE_DIR = os.path.join(BASE_DIR, "update_temp")
ZIP_FILE_PATH = os.path.join(BASE_DIR, "update_temp.zip")

class UpdateManager:
    """Clase encargada de buscar actualizaciones en GitHub, descargarlas y lanzar el actualizador."""

    @staticmethod
    def parse_version(version_str):
        """Parsea una cadena de versión semántica (ej. 'v0.1.2' o '0.1.2') en una tupla de exactamente 3 enteros."""
        if version_str.startswith('v'):
            version_str = version_str[1:]
        try:
            parts = version_str.split('.')
            # Convertir partes numéricas a enteros
            ints = [int(x) for x in parts[:3]]
            # Rellenar con ceros si hay menos de 3 componentes (ej. '2.0' -> (2, 0, 0))
            while len(ints) < 3:
                ints.append(0)
            return tuple(ints)
        except ValueError:
            return (0, 0, 0)

    @classmethod
    def check_for_updates(cls, current_version, repo_owner="dramosrodriguez", repo_name="cronofactura"):
        """Busca actualizaciones en GitHub consultando la API de releases.
        Compara la versión actual con la remota, asegurando que tengan la misma versión mayor.
        """
        # Cargar configuración para ver si el usuario la tiene activada
        if os.path.exists(SETTINGS_PATH):
            try:
                with open(SETTINGS_PATH, "r", encoding="utf-8") as f:
                    config = json.load(f)
                if not config.get("buscar_actualizaciones", True):
                    return {"update_available": False, "reason": "settings_disabled"}
            except Exception:
                pass  # Si falla el parseo de settings, continuamos con la búsqueda por defecto

        url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/releases/latest"
        req = urllib.request.Request(
            url,
            headers={'User-Agent': 'Cronofactura-Updater'}
        )

        try:
            with urllib.request.urlopen(req, timeout=10) as response:
                if response.status == 200:
                    data = json.loads(response.read().decode('utf-8'))
                    remote_tag = data.get("tag_name", "")
                    
                    if not remote_tag:
                        return {"update_available": False, "reason": "no_tag"}

                    local_v = cls.parse_version(current_version)
                    remote_v = cls.parse_version(remote_tag)

                    # Verificar si la versión remota es superior
                    if remote_v > local_v:
                        # Restricción: la versión mayor debe ser idéntica
                        if local_v[0] == remote_v[0]:
                            return {
                                "update_available": True,
                                "current_version": current_version,
                                "new_version": remote_tag,
                                "zipball_url": data.get("zipball_url"),
                                "body": data.get("body", ""),
                                "published_at": data.get("published_at", "")
                            }
                        else:
                            return {
                                "update_available": False,
                                "reason": "major_mismatch",
                                "local_version": current_version,
                                "remote_version": remote_tag
                            }
                    else:
                        return {"update_available": False, "reason": "already_latest"}
        except urllib.error.URLError as e:
            print(f"[Updater] Error de red al comprobar actualizaciones: {e}", file=sys.stderr)
            return {"update_available": False, "reason": "network_error", "error": str(e)}
        except Exception as e:
            print(f"[Updater] Error inesperado: {e}", file=sys.stderr)
            return {"update_available": False, "reason": "exception", "error": str(e)}

        return {"update_available": False, "reason": "unknown"}

    @classmethod
    def check_for_updates_async(cls, current_version, callback):
        """Ejecuta la búsqueda de actualizaciones en un hilo de fondo y llama a la callback con los resultados."""
        def run():
            res = cls.check_for_updates(current_version)
            callback(res)
        thread = threading.Thread(target=run, daemon=True)
        thread.start()

    @classmethod
    def download_and_extract_update(cls, zipball_url, progress_callback):
        """Descarga de forma progresiva el zip de GitHub y lo extrae en el directorio temporal."""
        # Asegurar que limpiamos cualquier descarga anterior
        cls.cleanup_temp_files()
        
        req = urllib.request.Request(
            zipball_url,
            headers={'User-Agent': 'Cronofactura-Updater'}
        )

        try:
            with urllib.request.urlopen(req, timeout=30) as response:
                total_size = int(response.info().get('Content-Length', 0))
                
                # Si GitHub no envía Content-Length (lo cual es normal para zipballs dinámicos), 
                # usaremos una aproximación o una descarga sin porcentaje fijo, pero simulando chunks
                downloaded = 0
                block_size = 8192
                
                os.makedirs(os.path.dirname(ZIP_FILE_PATH), exist_ok=True)
                
                with open(ZIP_FILE_PATH, 'wb') as f:
                    while True:
                        buffer = response.read(block_size)
                        if not buffer:
                            break
                        downloaded += len(buffer)
                        f.write(buffer)
                        
                        # Si conocemos el tamaño total, calculamos porcentaje, sino pasamos None
                        percent = (downloaded / total_size) if total_size > 0 else None
                        progress_callback(percent, downloaded)

            # Extraer el zip en la carpeta temporal
            os.makedirs(TEMP_UPDATE_DIR, exist_ok=True)
            with zipfile.ZipFile(ZIP_FILE_PATH, 'r') as zip_ref:
                zip_ref.extractall(TEMP_UPDATE_DIR)
                
            return True
        except Exception as e:
            print(f"[Updater] Error durante la descarga/extracción: {e}", file=sys.stderr)
            cls.cleanup_temp_files()
            return False

    @classmethod
    def launch_external_updater(cls):
        """Escribe el script updater.py en la raíz del proyecto y lo ejecuta de forma independiente."""
        updater_content = """# -*- coding: utf-8 -*-
import os
import sys
import time
import shutil
import subprocess

def main():
    # Esperar un momento a que el proceso principal de CustomTkinter se cierre por completo
    time.sleep(2.0)
    
    # Directorio raíz del proyecto
    base_dir = os.path.dirname(os.path.abspath(__file__))
    temp_dir = os.path.join(base_dir, "facturacion_app", "update_temp")
    
    if not os.path.exists(temp_dir):
        print("Error: No se encontró el directorio temporal de actualizaciones.")
        sys.exit(1)
        
    # Buscar el subdirectorio del código fuente extraído dentro de update_temp
    extracted = [d for d in os.listdir(temp_dir) if os.path.isdir(os.path.join(temp_dir, d))]
    if not extracted:
        print("Error: El zip no contiene carpetas válidas.")
        sys.exit(1)
        
    source_root = os.path.join(temp_dir, extracted[0])
    
    # 1. Eliminar directorios antiguos de código y templates para no dejar archivos huérfanos
    src_dest = os.path.join(base_dir, "facturacion_app", "src")
    templates_dest = os.path.join(base_dir, "facturacion_app", "templates")
    
    try:
        if os.path.exists(src_dest):
            shutil.rmtree(src_dest)
        if os.path.exists(templates_dest):
            shutil.rmtree(templates_dest)
    except Exception as e:
        print(f"Error al limpiar carpetas de código antiguas: {e}")
        sys.exit(1)
        
    # 2. Copiar directorios nuevos
    src_src = os.path.join(source_root, "facturacion_app", "src")
    templates_src = os.path.join(source_root, "facturacion_app", "templates")
    
    try:
        if os.path.exists(src_src):
            shutil.copytree(src_src, src_dest)
        if os.path.exists(templates_src):
            shutil.copytree(templates_src, templates_dest)
    except Exception as e:
        print(f"Error al copiar carpetas nuevas: {e}")
        sys.exit(1)
        
    # 3. Copiar otros archivos root individuales (iniciar.bat, iniciar.sh, requirements.txt, pyproject.toml, initialize_project.py)
    # Ignoramos explícitamente bases de datos o configuraciones si existieran
    for item in os.listdir(source_root):
        src_item = os.path.join(source_root, item)
        dest_item = os.path.join(base_dir, item)
        
        if os.path.isfile(src_item):
            # Seguridad: jamás sobrescribir la base de datos o configuraciones en la raíz
            if item in ["facturacion.db", "settings.json"]:
                continue
            try:
                shutil.copy2(src_item, dest_item)
            except Exception as e:
                print(f"Error al copiar archivo de raíz {item}: {e}")
                
    # 4. Lanzar el iniciador del programa según el sistema operativo
    try:
        if sys.platform == "win32" or os.name == "nt":
            # Ejecutar cmd en segundo plano para iniciar el batch
            subprocess.Popen(["cmd.exe", "/c", "iniciar.bat"], shell=True)
        else:
            # Unix: Copiar permisos de ejecución de iniciar.sh y lanzarlo
            shutil.copymode(os.path.join(source_root, "iniciar.sh"), os.path.join(base_dir, "iniciar.sh"))
            subprocess.Popen(["/bin/bash", "./iniciar.sh"])
    except Exception as e:
        print(f"Error al reiniciar la aplicación: {e}")

if __name__ == "__main__":
    main()
"""
        updater_script_path = os.path.join(PROJECT_ROOT, "updater.py")
        
        # Escribir el script con codificación UTF-8
        with open(updater_script_path, "w", encoding="utf-8") as f:
            f.write(updater_content)
            
        # Lanzar el proceso de forma asíncrona
        subprocess.Popen([sys.executable, updater_script_path])

    @classmethod
    def cleanup_temp_files(cls):
        """Elimina todos los residuos de descargas y actualizaciones anteriores."""
        # Eliminar archivo zip temporal si existe
        if os.path.exists(ZIP_FILE_PATH):
            try:
                os.remove(ZIP_FILE_PATH)
            except OSError:
                pass
                
        # Eliminar carpeta temporal si existe
        if os.path.exists(TEMP_UPDATE_DIR):
            try:
                shutil.rmtree(TEMP_UPDATE_DIR)
            except OSError:
                pass

        # Eliminar el script updater.py de la raíz del proyecto
        updater_path = os.path.join(PROJECT_ROOT, "updater.py")
        if os.path.exists(updater_path):
            try:
                os.remove(updater_path)
            except OSError:
                pass
