# 📸 Project 3: GestorBot de Sarashot

**GestorBot** es un chatbot inteligente diseñado para asistir a clientes de Sarashot, una fotógrafa profesional especializada en sesiones de newborn, embarazo y seguimiento en Valencia, España. El bot permite a los usuarios informarse sobre servicios, comprobar disponibilidad, y gestionar reservas de forma autónoma e interactiva.

---

## 📄 Descripción

Este proyecto implementa un sistema de agente conversacional basado en inteligencia artificial que:

* Informa sobre los servicios fotográficos ofrecidos por Sarashot.
* Gestiona citas: comprueba disponibilidad, reserva, modifica y cancela sesiones.
* Considera aspectos como el clima para sesiones en exterior.
* Utiliza herramientas contextuales como calendario, clima y base de datos de productos.

Está pensado para automatizar la atención al cliente de una profesional autónoma, manteniendo una comunicación natural, eficaz y adaptada al contexto de cada cliente.

---

## 🧱 Tecnologías Principales

* **Python** (backend y lógica del agente)
* **FastAPI** (API REST para comunicación con el bot)
* **Streamlit** (interfaz visual, si aplica)
* **LangGraph / LangChain** (arquitectura del agente y herramientas)
* **OpenAI GPT-4o** (modelo conversacional)
* **Docker** (contenedorización)
* **Terraform** (infraestructura como código)
* **.env + dotenv** (gestión de variables de entorno)

---

## 💻 Instalación

### Requisitos

* Docker y Docker Compose instalados
* Claves API necesarias en `.env` (ver más abajo)

### Pasos

1. Clona el repositorio:

```bash
git clone https://github.com/tuusuario/gestorbot-sarashot.git
cd gestorbot-sarashot
```

2. Define las variables de entorno necesarias en un archivo `.env` en la raíz:

```env
OPENAI_API_KEY=tu_clave
WEATHER_API_KEY=tu_clave
...
```

3. Construye y ejecuta los contenedores con Docker:

```bash
docker-compose up --build
```

Cada módulo tiene su propio archivo `requirements.txt` si decides ejecutar fuera de contenedor.

---

## 🧪 Uso

Una vez el contenedor esté corriendo, accede a la API vía `http://localhost:8000`.

### Endpoints principales

* `GET /` → Verifica que la API está activa.
* `POST /chat` → Envía mensajes al agente. Requiere:

```json
{
  "thread_id": "usuario123",
  "message": "Hola, quiero una sesión newborn en septiembre"
}
```

---

## ⚙️ Arquitectura

* **LangGraph** se usa para crear un grafo de decisión con nodos que alternan entre el modelo LLM y la ejecución de herramientas.
* Se mantiene un historial de conversación por `thread_id`.
* El LLM (GPT-4o) actúa como núcleo de razonamiento.
* Las herramientas permiten actuar sobre información real: disponibilidad, productos, clima y reservas.

---

## 📜 Licencia

Este proyecto está licenciado bajo la **Licencia MIT**. Puedes utilizarlo, modificarlo y distribuirlo libremente siempre que mantengas la atribución al equipo original.

---

## 👥 Autores

Proyecto desarrollado por el equipo de Project 3:

* [Jorge Moltó](https://www.linkedin.com/in/jorgemoltomolto/)
* [Joel Seguí](https://www.linkedin.com/in/joel-segui-far/)
* [Juan Montoliu](https://www.linkedin.com/in/juan-montoliu-arrando-b05507325/)
* [Mauro Balaguer](https://www.linkedin.com/in/mauro-balaguer/)
* [Andreu Boigues](https://www.linkedin.com/in/andreu-boigues/)