 TalentCore API - SDLC Automatizado con Agentes de IA

    Sistema integral de gestión de vacaciones y RRHH desarrollado de forma automatizada mediante una cadena de
    **Agentes de IA autónomos** que simulan el ciclo de vida de desarrollo de software (**SDLC** - *Software
    Development Life Cycle*).

   ## 📌 ¿De qué trata el proyecto?
    Este repositorio contiene dos capas principales:
    1. **Flujo de Agentes SDLC (`00` a `06`)**: Utiliza LLMs (vía Groq / `mini_crew`) para
    orquestar la especificación, diseño, codificación, pruebas unitarias, auditoría de código y despliegue.
    2. **TalentCore API (`generated_project/`)**: El microservicio FastAPI resultante, diseñado para la
    administración de empleados y solicitudes de días de vacaciones con reglas de negocio y jerarquías de aprobación.

   ## 🔄 El Flujo Multi-Agente (SDLC)
    |           Script           |         Agente / Rol         |                 Responsabilidad                 |
    |----------------------------|------------------------------|-------------------------------------------------|
    | 00_test_conexion.py        | **Verificación**             | Valida la conectividad con el proveedor LLM.    |
                                                                  
    | 01_agente_product_owner.py | **Senior IT Product Owner**  | Genera el documento de requerimientos funcionales|
                                                                  |y criterios de aceptación (PRD.md).             |
                                                                 
    | 02_agente_arquitecto.py    | **Software Architect**       | Diseña los esquemas de base de datos, endpoints  |
                                                                  |REST y reglas (ARCHITECTURE.md).                |
                                                                  
    | 03_agente_developer.py     | **Senior Python Backend Dev**| Genera el código de la API en FastAPI y modelos  |
                                                                  |SQLAlchemy en `generated_project/app/`.         |
                                                                  
    | 04_agente_qa.py            | **Senior QA Automation       | Diseña e implementa la suite de tests en `pytest`|
                                 |     Engineer**               | cubriendo los criterios de aceptación en Gherkin.|
                                   
    | 05_agente_reviewer.py      | **Staff Security & Code      | Audita seguridad, cobertura de reglas y calidad  |
                                 | Reviewer**                   | de código (AUDIT_REPORT.md).                     |
                                                  
    | 06_agente_devops.py        | **Senior DevOps Engineer**   | Genera `Dockerfile`, `docker-compose.yml` y el   |
                                                                | pipeline de GitHub Actions (`ci.yml`).           |   

   ## 🏢 Reglas de Negocio de TalentCore API
   ### 1. Roles
    - **`ADMIN_RRHH`**: Único usuario autorizado para crear y registrar nuevos empleados.
    - **`EMPLEADO`**: Consulta su saldo disponible y genera solicitudes de vacaciones para sí mismo.
    - **`MANAGER`**: Revisa, aprueba o rechaza solicitudes de sus subordinados directos (`empleado.manager_id ==
    manager.id`).

   ### 2. Cálculo de Saldo de Vacaciones
    - **Antigüedad < 1 año**: `12` días base.
    - **Antigüedad ≥ 1 año**: min(12 + 2 × (años - 1), 20) días.
    - **Saldo Disponible**: días totales - ∑(días aprobados).
    - **Validación de saldo**: No se permite crear solicitudes si la suma de días en estado `PENDING` y `APPROVED`
    sobrepasa los días totales.

   ### 3. Máquina de Estados
    - `PENDING` → Estado inicial al solicitar.
    - `APPROVED` → Descuenta el saldo disponible del empleado.
    - `REJECTED` → Solicitud desestimada (no descuenta saldo).

    
    
   ## 🚀 Puesta en Marcha
    ### Prerrequisitos
    - Python 3.10+
    - Clave de API de [Groq](https://console.groq.com/) (para ejecutar los agentes)
    - Docker y Docker Compose (opcional, para despliegue del proyecto generado)

   ### 1. Configuración del Entorno
    Clona el repositorio y crea un archivo `.env` en la raíz:
    ```bash
    git clone https://github.com/TU_USUARIO/TU_REPOSITORIO.git
    cd TU_REPOSITORIO
    python -m venv venv
    # En Windows:
    venv\Scripts\activate
    # En Linux/macOS:
    source venv/bin/activate

    pip install -r generated_project/requirements.txt python-dotenv

  Crea tu archivo .env:

    GROQ_API_KEY=tu_api_key_aqui
    GROQ_MODEL_NAME=qwen/qwen3.8-27b
    WORKSPACE_DIR=./generated_project

  ### 2. Ejecutar la Cadena de Agentes

  Puedes ejecutar cada etapa de forma secuencial:

    python 00_test_conexion.py
    python 01_agente_product_owner.py
    python 02_agente_arquitecto.py
    python 03_agente_developer.py
    python 04_agente_qa.py
    python 05_agente_reviewer.py
    python 06_agente_devops.py

  ### 3. Ejecutar la API Generada

  #### Opción Local (Uvicorn):

    cd generated_project
    uvicorn app.main:app --reload --port 8000

  La documentación interactiva Swagger estará disponible en: http://localhost:8000/docs

  #### Opción Contenedor (Docker Compose):

    cd generated_project
    docker-compose up --build

  ### 4. Ejecutar las Pruebas

    cd generated_project
    pytest tests/ -v
    
   ## 🛠️ Tecnologías Utilizadas

  • Agentes & Orquestación: Python, mini_crew, Groq Cloud API.
  • Backend: FastAPI, Pydantic, SQLAlchemy, SQLite.
  • Testing: PyTest, HTTPX / Starlette TestClient.
  • DevOps: Docker, Docker Compose, GitHub Actions.


https://talentcore-api-cristal.onrender.com/docs
