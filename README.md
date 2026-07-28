# Enterprise Data Workflow Multi-Agent Platform (Google ADK)

Plataforma empresarial de flujo de trabajo de datos multiagente construida nativamente con el **Google Agent Development Kit (`google-adk`)** y modelos **Google Gemini 2.5**.

---

## 🚀 Características Principales

1. **Arquitectura Multiagente Nativa en Google ADK:**
   - **Orchestrator (`gemini-2.5-pro`):** Supervisor y enrutador dinámico que evalúa la intención del usuario en cada mensaje.
   - **Analyst (`gemini-2.5-flash`):** Relevamiento funcional, historias de usuario y gestión del tablero Trello / Kanban.
   - **Explorer (`gemini-2.5-flash`):** Exploración de datos de SOLO LECTURA, inspección multischema (`SHOW SCHEMAS`) y consultas SELECT.
   - **Engineer (`gemini-2.5-flash`):** Construcción DDL/DML (CREATE TABLE, CREATE VIEW, ALTER, DROP), volúmenes Databricks SDK, DLT Pipelines y GitOps en GitHub.
   - **QA (`gemini-2.5-flash`):** Pruebas de calidad automatizadas, auditoría de seguridad y gobernanza PII.
   - **BI (`gemini-2.5-flash`):** Visualización de datos, KPIs analíticos y especificación de Databricks Lakeview Dashboards.
   - **DataOps (`gemini-2.5-flash`):** Monitoreo SRE de rendimiento, orquestación de clústeres y aprobación de Pull Requests (`git_merge_pr` en GitHub).

2. **Gobernanza y Auditoría Inmutable (`audit_logger.py`):**
   - Cada operación realizada por cualquier agente (sentencias SQL, comandos Git, tarjetas Trello, instalaciones pip) genera un evento inmutable registrado en `logs/audit.log` en formato JSON estructurado.

3. **Diagnóstico de Salud Global (`health_check_system`):**
   - Verificación de conectividad en un solo clic para Databricks SDK, GitHub API, Trello API y variables de entorno.

4. **Instalación Dinámica de Controladores:**
   - Detección automática e instalación bajo demanda de paquetes de base de datos (PostgreSQL, MySQL, Snowflake, Oracle, BigQuery) previa autorización del usuario.

---

## 🛠️ Estructura del Proyecto

```text
Data Workflow Multiagente/
├── .env.example                 # Plantilla completa de variables de entorno
├── .gitignore                   # Archivo de exclusiones Git
├── requirements.txt             # Dependencias de Python (.venv)
├── logs/                        # Registros de auditoría (audit.log)
├── docs/                        # Documentación funcional en Markdown
├── tests/                       # Suite de pruebas automatizadas (unittest)
└── data_workflow_team/          # Paquete principal ADK
    ├── agent.py                 # Entrypoint oficial ADK (root_agent & Orchestrator)
    ├── config/
    │   └── settings.py          # Configuración empresarial centralizada
    ├── core/
    │   └── audit_logger.py      # Logger de auditoría inmutable
    ├── agents/                  # Agentes especialistas
    │   ├── analyst.py
    │   ├── explorer.py
    │   ├── engineer.py
    │   ├── qa.py
    │   ├── bi.py
    │   └── dataops.py
    └── integrations/            # Integraciones de producción
        ├── data_connectors.py   # Databricks SDK, SQL, Volúmenes, Pipelines, Multi-schema
        ├── git_manager.py       # Git comandos reales & GitHub REST API
        └── agile_board.py       # Trello API & Kanban local
```

---

## ⚙️ Despliegue y Ejecución

### 1. Requisitos Previos
- Python 3.10+
- Entorno virtual configurado (`.venv`)

### 2. Ejecutar Suite de Pruebas
```powershell
.\.venv\Scripts\python.exe -m unittest discover tests
```

### 3. Iniciar la Interfaz Web ADK
```powershell
.\.venv\Scripts\adk.exe web
```
Accede localmente desde tu navegador en: **http://127.0.0.1:8000**
