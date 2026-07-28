import os
import sys
import json
import time
import subprocess
from typing import Dict, Any, List, Optional, Tuple
from dotenv import load_dotenv

from data_workflow_team.config.settings import settings
from data_workflow_team.core.audit_logger import log_audit_event

load_dotenv()

# Mapa de motores de base de datos a sus paquetes pip correspondientes
DB_DRIVER_MAP = {
    "postgres": {"module": "psycopg2", "package": "psycopg2-binary"},
    "postgresql": {"module": "psycopg2", "package": "psycopg2-binary"},
    "mysql": {"module": "pymysql", "package": "pymysql"},
    "snowflake": {"module": "snowflake.connector", "package": "snowflake-connector-python"},
    "oracle": {"module": "oracledb", "package": "oracledb"},
    "bigquery": {"module": "google.cloud.bigquery", "package": "google-cloud-bigquery"},
    "mssql": {"module": "pyodbc", "package": "pyodbc"},
    "sqlserver": {"module": "pyodbc", "package": "pyodbc"},
    "databricks": {"module": "databricks.sql", "package": "databricks-sql-connector"}
}

def install_python_package(package_name: str) -> str:
    """
    Instala un paquete de Python en el entorno virtual activo (.venv) mediante pip.
    
    Args:
        package_name: Nombre exacto del paquete de PyPI (ej. 'psycopg2-binary', 'snowflake-connector-python')
        
    Returns:
        Mensaje con el resultado de la instalación mediante pip.
    """
    print(f"  [Package Installer] Instalando paquete en .venv: {package_name}...")
    try:
        res = subprocess.run(
            [sys.executable, "-m", "pip", "install", package_name],
            capture_output=True,
            text=True,
            check=True
        )
        log_audit_event("PackageInstaller", "PIP_INSTALL", package_name, "SUCCESS")
        return f"Paquete '{package_name}' instalado exitosamente en el entorno virtual (.venv)."
    except subprocess.CalledProcessError as e:
        log_audit_event("PackageInstaller", "PIP_INSTALL", package_name, "FAILED", {"stderr": e.stderr})
        return f"Error al instalar el paquete '{package_name}': {e.stderr.strip() or e.stdout.strip()}"
    except Exception as e:
        return f"Error ejecutando pip install para '{package_name}': {str(e)}"

def _check_and_get_driver(source_uri: str) -> Tuple[Optional[str], Optional[str]]:
    uri_lower = source_uri.lower()
    for engine, info in DB_DRIVER_MAP.items():
        if engine in uri_lower:
            module_name = info["module"]
            package_name = info["package"]
            try:
                __import__(module_name)
                return module_name, None
            except ImportError:
                return None, (
                    f"PERMISSION_REQUIRED: El controlador para '{engine}' (paquete '{package_name}') "
                    f"no está instalado en el entorno virtual (.venv). "
                    f"Debes responder al usuario: 'Para conectarme a la base de datos {engine.capitalize()}, "
                    f"necesito instalar la librería `{package_name}`. ¿Autorizas su instalación?'"
                )
    return None, None

def _get_workspace_client():
    host = settings.DATABRICKS_HOST
    token = settings.DATABRICKS_TOKEN
    if not host or not token:
        return None
    try:
        from databricks.sdk import WorkspaceClient
        clean_host = host.replace("https://", "").replace("http://", "").strip("/")
        return WorkspaceClient(host=f"https://{clean_host}", token=token)
    except Exception as e:
        print(f"  [Databricks SDK Error] {e}")
        return None

def _connect_databricks_with_retry(max_retries: int = 3):
    host = settings.DATABRICKS_HOST
    token = settings.DATABRICKS_TOKEN
    http_path = settings.DATABRICKS_HTTP_PATH
    
    if not host or not token:
        return None, "ERROR DE AUTENTICACIÓN: No se encontraron las credenciales 'DATABRICKS_HOST' o 'DATABRICKS_TOKEN' en el archivo .env."
        
    try:
        from databricks import sql
        clean_host = host.replace("https://", "").replace("http://", "").strip("/")
        conn_kwargs = {"server_hostname": clean_host, "access_token": token}
        if http_path:
            conn_kwargs["http_path"] = http_path
            
        last_err = None
        for attempt in range(1, max_retries + 1):
            try:
                print(f"  [Data Connector] Conectando a Databricks (Intento {attempt}/{max_retries})...")
                conn = sql.connect(**conn_kwargs)
                return conn, None
            except Exception as e:
                last_err = e
                time.sleep(1)
                
        return None, f"Error de conexión a Databricks tras {max_retries} reintentos: {str(last_err)}"
    except Exception as e:
        return None, f"Error importando controlador Databricks: {str(e)}"

def health_check_system() -> str:
    """
    Verifica el estado de salud y conectividad de todos los servicios e integraciones empresariales (Databricks, GitHub, Trello, BBDD).
    
    Returns:
        Informe completo de salud del sistema.
    """
    report = ["=== INFORME DE SALUD Y DIAGNÓSTICO DEL SISTEMA EN TERRENO ==="]
    
    # 1. Databricks
    if settings.DATABRICKS_HOST and settings.DATABRICKS_TOKEN:
        conn, err = _connect_databricks_with_retry(max_retries=1)
        if conn:
            conn.close()
            report.append("✔ Databricks SQL Warehouse: CONECTADO (Autenticación OK)")
        else:
            report.append(f"✖ Databricks SQL Warehouse: DESCONECTADO ({err})")
    else:
        report.append("⚠ Databricks: Credenciales ausentes en .env")

    # 2. Databricks SDK
    w = _get_workspace_client()
    if w:
        report.append("✔ Databricks SDK (WorkspaceClient): OPERATIVO")
    else:
        report.append("⚠ Databricks SDK: No configurado o inalcanzable")

    # 3. GitHub API
    if settings.GITHUB_TOKEN:
        try:
            import requests
            headers = {"Authorization": f"Bearer {settings.GITHUB_TOKEN}"}
            res = requests.get("https://api.github.com/user", headers=headers, timeout=5)
            if res.status_code == 200:
                report.append(f"✔ GitHub API: AUTENTICADO como '{res.json().get('login')}'")
            else:
                report.append(f"✖ GitHub API: Error {res.status_code}")
        except Exception as e:
            report.append(f"✖ GitHub API: {e}")
    else:
        report.append("⚠ GitHub API: GITHUB_TOKEN ausente en .env")

    # 4. Trello API
    if settings.TRELLO_API_KEY and settings.TRELLO_TOKEN and settings.TRELLO_BOARD_ID:
        report.append(f"✔ Trello Kanban: CONFIGURADO (Board ID: {settings.TRELLO_BOARD_ID})")
    else:
        report.append("ℹ Trello Kanban: Modo local activo (.kanban_board.json)")

    log_audit_event("HealthChecker", "SYSTEM_HEALTH_CHECK", "System", "SUCCESS")
    return "\n".join(report)

def databricks_volume_operations(action: str, volume_path: str, local_file_path: str = None) -> str:
    """
    Operaciones reales sobre Unity Catalog Volumes y DBFS en Databricks (Subir archivos, descargar, listar).
    
    Args:
        action: Acción a realizar ('LIST', 'UPLOAD', 'DOWNLOAD')
        volume_path: Ruta del volumen en Databricks (ej. '/Volumes/main/bakehouse/mi_volumen/archivo.csv')
        local_file_path: Ruta local del archivo si la acción es UPLOAD o DOWNLOAD.
        
    Returns:
        Resultado detallado de la operación sobre el volumen.
    """
    print(f"  [Databricks Volume] Ejecutando {action} en {volume_path}...")
    w = _get_workspace_client()
    if not w:
        return "ERROR: No se pudo instanciar el cliente del Databricks SDK (Verifica DATABRICKS_HOST y DATABRICKS_TOKEN)."
        
    try:
        action_upper = action.upper()
        if action_upper == "LIST":
            files = list(w.files.list_directory_contents(volume_path))
            file_names = [f.path for f in files]
            log_audit_event("Engineer", "VOLUME_LIST", volume_path, "SUCCESS")
            return f"Archivos en el Volumen ({volume_path}): {file_names}"
            
        elif action_upper == "UPLOAD":
            if not local_file_path or not os.path.exists(local_file_path):
                return f"ERROR: El archivo local '{local_file_path}' no existe para subir a Databricks."
            with open(local_file_path, "rb") as f:
                w.files.upload(volume_path, f)
            log_audit_event("Engineer", "VOLUME_UPLOAD", volume_path, "SUCCESS", {"local_path": local_file_path})
            return f"Archivo local '{local_file_path}' subido exitosamente al Volumen Databricks '{volume_path}'."
            
        elif action_upper == "DOWNLOAD":
            if not local_file_path:
                return "ERROR: Especifica 'local_file_path' donde guardar el archivo descargado."
            res = w.files.download(volume_path)
            os.makedirs(os.path.dirname(os.path.abspath(local_file_path)), exist_ok=True)
            with open(local_file_path, "wb") as f:
                f.write(res.contents.read())
            log_audit_event("Engineer", "VOLUME_DOWNLOAD", volume_path, "SUCCESS", {"local_path": local_file_path})
            return f"Archivo del Volumen Databricks '{volume_path}' descargado a '{local_file_path}'."
            
        return f"Acción '{action}' no soportada en volúmenes."
    except Exception as e:
        log_audit_event("Engineer", f"VOLUME_{action.upper()}", volume_path, "FAILED", {"error": str(e)})
        return f"Error en operación de volumen Databricks ({action}): {str(e)}"

def databricks_pipeline_operations(action: str, pipeline_name_or_id: str = None) -> str:
    """
    Gestiona y monitorea Delta Live Tables (DLT) y Databricks Jobs/Pipelines reales.
    
    Args:
        action: Acción a realizar ('LIST_JOBS', 'LIST_PIPELINES', 'START_PIPELINE')
        pipeline_name_or_id: ID o nombre del pipeline o Job si aplica.
        
    Returns:
        Estado del pipeline o lista de pipelines/jobs.
    """
    print(f"  [Databricks Pipelines] Ejecutando {action}...")
    w = _get_workspace_client()
    if not w:
        return "ERROR: Databricks SDK no autenticado."
        
    try:
        action_upper = action.upper()
        if action_upper == "LIST_JOBS":
            jobs = list(w.jobs.list())
            job_list = [{"id": j.job_id, "name": j.settings.name if j.settings else "N/A"} for j in jobs[:10]]
            log_audit_event("DataOps", "LIST_JOBS", "Databricks", "SUCCESS")
            return f"Databricks Jobs encontrados ({len(jobs)}): {job_list}"
            
        elif action_upper == "LIST_PIPELINES":
            pipes = list(w.pipelines.list_pipeline_events(pipeline_id=pipeline_name_or_id) if pipeline_name_or_id else w.pipelines.list_pipelines())
            log_audit_event("DataOps", "LIST_PIPELINES", pipeline_name_or_id or "All", "SUCCESS")
            return f"Databricks DLT Pipelines obtenidos exitosamente."
            
        elif action_upper == "START_PIPELINE":
            if not pipeline_name_or_id:
                return "ERROR: Especifica el ID del pipeline a iniciar."
            w.pipelines.start_update(pipeline_id=pipeline_name_or_id)
            log_audit_event("DataOps", "START_PIPELINE", pipeline_name_or_id, "SUCCESS")
            return f"Pipeline DLT '{pipeline_name_or_id}' iniciado exitosamente."
            
        return f"Acción de pipeline '{action}' no reconocida."
    except Exception as e:
        log_audit_event("DataOps", f"PIPELINE_{action.upper()}", pipeline_name_or_id or "Unknown", "FAILED", {"error": str(e)})
        return f"Error en operación de Pipelines Databricks: {str(e)}"

def connect_to_universal_source(source_uri: str) -> str:
    """
    Se conecta y valida un origen de datos escaneando TODOS los schemas y tablas.
    
    Args:
        source_uri: Identificador del origen (ej. 'Databricks Bakehouse', 'postgresql://...', 'data.csv')
        
    Returns:
        Resumen multischema detallado con esquemas y tablas encontradas.
    """
    print(f"  [Data Connector] Intentando conexión e inspección de TODOS los schemas en: {source_uri}")
    
    driver_module, perm_msg = _check_and_get_driver(source_uri)
    if perm_msg:
        return perm_msg

    # Databricks / Bakehouse
    if "databricks" in source_uri.lower() or "bakehouse" in source_uri.lower() or settings.DATABRICKS_HOST:
        conn, err = _connect_databricks_with_retry(max_retries=settings.MAX_CONNECTIVITY_RETRIES)
        if err:
            log_audit_event("Explorer", "CONNECT_SOURCE", source_uri, "FAILED", {"error": err})
            return err
        try:
            cursor = conn.cursor()
            cursor.execute("SHOW SCHEMAS")
            raw_schemas = [row[0] for row in cursor.fetchall()]
            schemas = [s for s in raw_schemas if s.lower() not in ['information_schema', 'sys']]
            
            schema_tables = {}
            total_tables = 0
            
            for schema in schemas:
                try:
                    cursor.execute(f"SHOW TABLES IN `{schema}`")
                    rows = cursor.fetchall()
                    table_names = [r[1] if len(r) > 1 else r[0] for r in rows]
                    schema_tables[schema] = table_names
                    total_tables += len(table_names)
                except Exception:
                    schema_tables[schema] = ["(Error al listar tablas)"]
                    
            conn.close()
            log_audit_event("Explorer", "CONNECT_SOURCE", source_uri, "SUCCESS", {"schemas_found": len(schemas), "total_tables": total_tables})
            return (
                f"Conexión exitosa a Databricks ({source_uri}).\n"
                f"Total de Schemas encontrados: {len(schemas)} {schemas}\n"
                f"Total de Tablas encontradas: {total_tables}\n"
                f"Detalle por Schema:\n{json.dumps(schema_tables, indent=2, ensure_ascii=False)}"
            )
        except Exception as e:
            return f"Error ejecutando inspección multischema en Databricks: {str(e)}"

    # PostgreSQL / MySQL / SQLAlchemy Multischema
    if "://" in source_uri or any(db in source_uri.lower() for db in ["postgres", "postgresql", "mysql"]):
        try:
            import sqlalchemy as sa
            engine = sa.create_engine(source_uri)
            inspector = sa.inspect(engine)
            schemas = [s for s in inspector.get_schema_names() if s.lower() not in ['pg_catalog', 'information_schema']]
            
            schema_tables = {}
            total_tables = 0
            for s in schemas:
                tbls = inspector.get_table_names(schema=s)
                schema_tables[s] = tbls
                total_tables += len(tbls)
                
            log_audit_event("Explorer", "CONNECT_SQL_SOURCE", source_uri, "SUCCESS")
            return (
                f"Conexión exitosa a BBDD SQL ({source_uri}).\n"
                f"Schemas encontrados ({len(schemas)}): {schemas}\n"
                f"Total de Tablas: {total_tables}\n"
                f"Detalle por Schema:\n{json.dumps(schema_tables, indent=2, ensure_ascii=False)}"
            )
        except Exception as e:
            return f"Error de conexión e inspección multischema en ({source_uri}): {str(e)}"

    # CSV
    if source_uri.endswith('.csv'):
        if not os.path.exists(source_uri):
            return f"ERROR: El archivo '{source_uri}' no existe en la ruta especificada."
        try:
            import pandas as pd
            df = pd.read_csv(source_uri, nrows=5)
            dtypes_dict = {col: str(dtype) for col, dtype in df.dtypes.items()}
            return f"Conectado a CSV exitosamente ({source_uri}).\nColumnas y tipos: {json.dumps(dtypes_dict, indent=2)}"
        except Exception as e:
            return f"Error al leer el archivo CSV '{source_uri}': {str(e)}"

    # DuckDB / SQLite
    if source_uri.endswith('.db') or source_uri.endswith('.duckdb') or source_uri.endswith('.sqlite'):
        if not os.path.exists(source_uri):
            return f"ERROR: La base de datos local '{source_uri}' no existe."
        try:
            import duckdb
            conn = duckdb.connect(source_uri)
            tables = conn.execute("SHOW TABLES").fetchall()
            conn.close()
            return f"Conectado a la base de datos local '{source_uri}'. Tablas: {tables}"
        except Exception as e:
            return f"Error al abrir la base de datos local '{source_uri}': {str(e)}"

    return f"Conexión inicial a '{source_uri}' establecida."

def execute_read_only_query(query: str, source_uri: str) -> str:
    """
    Ejecuta una consulta SELECT de solo lectura en el origen de datos.
    
    Args:
        query: Sentencia SQL de lectura (ej. 'SELECT * FROM bakehouse.sales_customers LIMIT 10')
        source_uri: Identificador del origen de datos.
        
    Returns:
        Resultados en formato tabular o mensaje de error.
    """
    query_upper = query.upper().strip()
    forbidden = ["DROP", "DELETE", "UPDATE", "INSERT", "CREATE", "ALTER", "TRUNCATE"]
    
    if any(keyword in query_upper for keyword in forbidden):
        log_audit_event("Explorer", "READ_QUERY", source_uri, "DENIED", {"query": query})
        return "ERROR DE SEGURIDAD: Operación denegada. Este rol tiene únicamente acceso de SOLO LECTURA (SELECT)."
        
    print(f"  [Data Connector] Ejecutando SELECT real en {source_uri}...")
    
    driver_module, perm_msg = _check_and_get_driver(source_uri)
    if perm_msg:
        return perm_msg

    if "databricks" in source_uri.lower() or "bakehouse" in source_uri.lower() or settings.DATABRICKS_HOST:
        conn, err = _connect_databricks_with_retry(max_retries=settings.MAX_CONNECTIVITY_RETRIES)
        if err:
            return err
        try:
            cursor = conn.cursor()
            cursor.execute(query)
            columns = [desc[0] for desc in cursor.description] if cursor.description else []
            rows = cursor.fetchall()
            conn.close()
            
            sample = [list(r) for r in rows[:10]]
            log_audit_event("Explorer", "READ_QUERY", source_uri, "SUCCESS", {"rows_total": len(rows)})
            return f"Consulta ejecutada en Databricks.\nFilas totales: {len(rows)}\nColumnas: {columns}\nMuestra de datos:\n{sample}"
        except Exception as e:
            log_audit_event("Explorer", "READ_QUERY", source_uri, "FAILED", {"error": str(e)})
            return f"Error ejecutando consulta en Databricks: {str(e)}"

    if "://" in source_uri or any(db in source_uri.lower() for db in ["postgres", "postgresql", "mysql"]):
        try:
            import sqlalchemy as sa
            engine = sa.create_engine(source_uri)
            with engine.connect() as conn:
                result = conn.execute(sa.text(query))
                rows = result.fetchall()
                columns = list(result.keys())
                sample = [list(r) for r in rows[:10]]
                log_audit_event("Explorer", "READ_QUERY", source_uri, "SUCCESS")
                return f"Consulta ejecutada en {source_uri}.\nFilas totales: {len(rows)}\nColumnas: {columns}\nMuestra de datos:\n{sample}"
        except Exception as e:
            return f"Error ejecutando consulta en {source_uri}: {str(e)}"
            
    return f"Error: No se especificó una URI de conexión válida para '{source_uri}'."

def execute_data_mutation_query(query: str, source_uri: str) -> str:
    """
    Ejecuta operaciones DML/DDL reales en Databricks o BBDD SQL (CREATE TABLE, CREATE VIEW, ALTER, DROP).
    
    Args:
        query: Sentencia DDL/DML a ejecutar (ej. 'CREATE VIEW bakehouse.resumen AS SELECT...')
        source_uri: Identificador del origen de datos.
        
    Returns:
        Confirmación de ejecución o mensaje de error.
    """
    print(f"  [Data Connector] Ejecutando Mutación DDL/DML real: {query[:80]}...")
    
    driver_module, perm_msg = _check_and_get_driver(source_uri)
    if perm_msg:
        return perm_msg

    if "databricks" in source_uri.lower() or "bakehouse" in source_uri.lower() or settings.DATABRICKS_HOST:
        conn, err = _connect_databricks_with_retry(max_retries=settings.MAX_CONNECTIVITY_RETRIES)
        if err:
            return err
        try:
            cursor = conn.cursor()
            cursor.execute(query)
            conn.close()
            log_audit_event("Engineer", "DDL_MUTATION", source_uri, "SUCCESS", {"query_snippet": query[:100]})
            return f"Operación DML/DDL (Tablas/Vistas) ejecutada con éxito en Databricks: {query}"
        except Exception as e:
            log_audit_event("Engineer", "DDL_MUTATION", source_uri, "FAILED", {"error": str(e)})
            return f"Error ejecutando mutación en Databricks: {str(e)}"

    if "://" in source_uri or any(db in source_uri.lower() for db in ["postgres", "postgresql", "mysql"]):
        try:
            import sqlalchemy as sa
            engine = sa.create_engine(source_uri)
            with engine.connect() as conn:
                conn.execute(sa.text(query))
                conn.commit()
                log_audit_event("Engineer", "DDL_MUTATION", source_uri, "SUCCESS")
                return f"Operación DML/DDL ejecutada con éxito en {source_uri}."
        except Exception as e:
            return f"Error ejecutando mutación en {source_uri}: {str(e)}"
            
    return f"Error: No hay motor configurado para ejecutar mutaciones en '{source_uri}'."

def file_system_operations(action: str, path: str, content: str = None) -> str:
    """
    Operaciones reales sobre el sistema de archivos local del servidor.
    
    Args:
        action: Acción ('READ', 'WRITE', 'DELETE')
        path: Ruta absoluta o relativa del archivo.
        content: Contenido de texto a escribir si la acción es WRITE.
        
    Returns:
        Resultado de la operación de archivos.
    """
    action_upper = action.upper()
    print(f"  [File System] Ejecutando {action_upper} en {path}...")
    
    try:
        if action_upper == "READ":
            if not os.path.exists(path):
                return f"Error: El archivo '{path}' no existe."
            with open(path, "r", encoding="utf-8") as f:
                return f.read()
                
        elif action_upper == "WRITE":
            os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
            with open(path, "w", encoding="utf-8") as f:
                f.write(content or "")
            log_audit_event("FileSystem", "FILE_WRITE", path, "SUCCESS")
            return f"Archivo '{path}' escrito exitosamente."
            
        elif action_upper == "DELETE":
            if os.path.exists(path):
                os.remove(path)
                log_audit_event("FileSystem", "FILE_DELETE", path, "SUCCESS")
                return f"Archivo '{path}' eliminado exitosamente."
            return f"El archivo '{path}' no existe para eliminar."
            
        return f"Acción '{action}' no soportada."
    except Exception as e:
        return f"Error en operación de archivos ({action}): {str(e)}"
