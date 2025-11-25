# SI-SISTEMA_HOSPITALARIO-11-25
Sistema de información hospitalaria 
🏥 SI-GESTION-PACIENTES-VILLA-CARMEN ✨

Sistema de Información automatizado basado en Django (Python) para la gestión integral de pacientes en la Clínica Villa Carmen. Resuelve los problemas de lentitud y errores del manejo manual, centralizando el historial clínico y garantizando la seguridad y confidencialidad de los datos.

📚 Tabla de Contenidos

Acerca del Proyecto

Funcionalidades Clave

Tecnología y Stack

Instalación Rápida

Estructura

Contacto

🚀 Acerca del Proyecto

Resumen

La implementación de esta solución web optimiza la administración clínica, logrando una reducción del 50% en los tiempos de consulta y registro. Se garantiza una alta disponibilidad (95% mensual) y se cumplen normativas de seguridad médica mediante respaldos automáticos y un acceso riguroso por roles.

✨ Funcionalidades Clave

El sistema maneja el flujo completo de la clínica:

Gestión de Roles: Control de acceso para Administradores, Recepcionistas y Médicos.

Pacientes y Citas: Registro completo de pacientes, asignación y seguimiento de citas.

Expediente Digital: Centralización del Historial Clínico (diagnósticos, tratamientos).

Reportes: Generación de estadísticas de atención y rendimiento.

🛠️ Tecnología y Stack

El proyecto utiliza metodología Scrum y una arquitectura de Tres Capas.

Componente

Tecnología

Propósito

Backend

Python / Django Framework

Lógica de Negocio y ORM.

Frontend

HTML, CSS, JavaScript

Interfaz de usuario web.

Base de Datos

MySQL

Persistencia de datos (Modelo de 22 tablas).

Arquitectura de Despliegue

La aplicación opera bajo una arquitectura de servidor web, separando claramente la presentación de la lógica de negocio.

⚙️ Instalación Rápida

Requiere Python 3.x y Servidor MySQL.

Pasos

Clonar e Instalar: Clonar el repositorio y configurar el entorno virtual e instalar dependencias.

git clone [[https://es.stackoverflow.com/questions/191716/cambiar-de-repositorio-remoto-en-un-repositorio-local-con-git](https://es.stackoverflow.com/questions/191716/cambiar-de-repositorio-remoto-en-un-repositorio-local-con-git)]
cd SI-SISTEMA_HOSPITALARIO-11-25
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt


Configurar DB: Crear la base de datos MySQL, configurar credenciales en settings.py e importar el esquema SQL.

Migrar y Ejecutar: Aplicar migraciones, crear superusuario e iniciar el servidor.

python manage.py makemigrations && python manage.py migrate
python manage.py createsuperuser
python manage.py runserver


Accede en http://127.0.0.1:8000/.

📂 Estructura

├── SI-SISTEMA_HOSPITALARIO-11-25/
│   ├── (nombre_app_citas)/     # Módulos Funcionales
│   ├── (nombre_app_pacientes)/ 
│   ├── si_sistema_hospitalario/  # Configuración (settings, urls)
│   ├── database/               # Script SQL
│   └── manage.py


Equipo de Desarrollo:

Fabian Herrera Luis Benjamín

Mendoza Conde Rolando Junior

Quino Serrano Yonatan

Siles Mejía Marvin

Torrez Miranda Luis Ángel
