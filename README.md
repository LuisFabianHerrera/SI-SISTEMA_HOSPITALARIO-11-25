# 🏥 SI-GESTION-PACIENTES-VILLA-CARMEN ✨

![Estado del Proyecto](https://img.shields.io/badge/Estado-Completado-brightgreen)
![Lenguaje Principal](https://img.shields.io/badge/Lenguaje-Python-blue.svg)
[![Licencia: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Sistema de Información automatizado basado en **Django** para la gestión integral de pacientes en la Clínica Villa Carmen. Resuelve los problemas de lentitud y errores del manejo manual, centralizando el historial clínico y garantizando la seguridad y confidencialidad de los datos.

## 📚 Tabla de Contenidos
- Acerca del Proyecto
- Características
- Tecnologías Usadas
- Instalación
- Uso
- Estructura del Proyecto
- Contacto

## 🚀 Acerca del Proyecto
### Problema
La gestión manual de pacientes genera demoras, errores en el registro, dificultad para rastrear el historial clínico y riesgos de seguridad, afectando la eficiencia operativa y la calidad del servicio en la clínica.
### Solución
Este 'Sistema de Información para la Gestión de Pacientes' es una solución web que digitaliza el proceso completo. Permite registrar pacientes, gestionar citas, centralizar el historial clínico y generar reportes, asegurando una administración clínica optimizada.
### Beneficios y Valor
El sistema garantiza una **reducción del 50% en los tiempos de consulta y registro**. Ofrece una alta disponibilidad (95% mensual) y cumple normativas de seguridad mediante respaldos automáticos, modernizando la administración y mejorando la atención al paciente.

## ✨ Características
- Gestión de Usuarios y Roles (Administrador, Recepcionista, Médico).
- Registro completo y actualización de la información de Pacientes.
- Funcionalidad de asignación, reprogramación y seguimiento de **Citas**.
- Centralización del **Historial Clínico Digital** (diagnósticos, tratamientos, observaciones).
- Módulo de generación de **Reportes** (estadísticas de atención y rendimiento).
- Cumplimiento de **Requerimientos No Funcionales** (Rendimiento < 3s, Escalabilidad > 10,000 registros).

## 🛠️ Tecnologías Usadas
- **Lenguaje:** Python
- **Backend Framework:** Django
- **Frontend:** HTML, CSS, JavaScript
- **Base de Datos:** MySQL (22 tablas en el modelo relacional)
- **Metodología de Desarrollo:** Scrum
- **Control de Versiones:** Git & GitHub

## ⚙️ Instalación
Requiere **Python 3.x** y un **Servidor MySQL** en ejecución.

1.  **Clonar el Repositorio:**
    git clone [https://github.com/tu_usuario/SI-SISTEMA_HOSPITALARIO-11-25.git]
    cd SI-SISTEMA_HOSPITALARIO-11-25
2.  **Configuración del Entorno:**
    * Crear y activar el entorno virtual, e instalar las dependencias:
      python -m venv venv
      source venv/bin/activate # En Windows usa: venv\Scripts\activate
      pip install -r requirements.txt
3.  **Configuración de la Base de Datos:**
    * Asegúrate de tener MySQL activo y crea la base de datos (ej. gestion_clinica_db).
    * Configura las credenciales de conexión en el archivo si_sistema_hospitalario/settings.py.
    * Importa el esquema SQL (si el archivo .sql está disponible).
4.  **Migrar y Ejecutar:**
    * Aplica las migraciones de Django y crea un superusuario para acceder al sistema:
      python manage.py makemigrations && python manage.py migrate
      python manage.py createsuperuser
      python manage.py runserver

## 🚀 Uso
Una vez que el servidor Django esté en funcionamiento, accede a la aplicación en http://127.0.0.1:8000/. Utiliza el superusuario creado en el paso de instalación para acceder al panel de administración y empezar a configurar médicos y recepcionistas.

## 📂 Estructura del Proyecto
El proyecto sigue una estructura estándar de Django:
├── SI-SISTEMA_HOSPITALARIO-11-25/
│   ├── (nombre_app_citas)/     # Módulo Funcional: Citas
│   ├── (nombre_app_pacientes)/ # Módulo Funcional: Pacientes/Historial
│   ├── si_sistema_hospitalario/  # Configuración del proyecto (settings, urls)
│   ├── database/               # Script SQL (Opcional)
│   └── manage.py
* **Flujo de trabajo principal:** Recepcionista registra, Médico consulta/actualiza historial.

## ✉️ Contacto
Para cualquier consulta o colaboración, no dudes en contactar al equipo de desarrollo:

* **Estudiantes:**
    * Fabian Herrera Luis Benjamín
    * Mendoza Conde Rolando Junior
    * Quino Serrano Yonatan
    * Siles Mejía Marvin
    * Torrez Miranda Luis Ángel
* **Docente Guía:** Ing. Edson David Veneros Vásquez
