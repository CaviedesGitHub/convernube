\# convernube

INSTALACION

1. Descargue el código del repositorio a su equipo.

Git clone https://github.com/CaviedesGitHub/convernube.git

Debería funcionar cualquiera de las ramas: Main o unarchivo.

1. Abra la carpeta convernube en vs code
1. Instale un entorno virtual en la carpeta venv.

En la terminal digite lo siguiente.

En windows:

Python -m venv venv

En linux:

Virtualenv venv

1. Active el entorno virtual.

En windows:

.\venv\scripts\activate

En linux:

Source venv/bin/activate

1. Instale las dependencias.

Pip freeze > requirements.txt

1. Debe tener instalado postgres y una base de

Datos llamada AudioConv con usuario admin

Y contraseña admin.

En linux:

Sudo apt update

Sudo apt install postgresql postgresql.contrib

Sudo su - postgres

Create user admin with password 'admin'

Create database AudioConv with owner admin

Alter user postgres with super user

\q

Exit

1. Debe instalar redis.

En linux:

Sudo apt update

Sudo apt install -y redis

1. Debe instalar ffmpeg

En linux:

Sudo apt install ffmpeg

1. Ejecute el microservicio auth\_ms.

En la terminal:

CD auth\_ms

Sh run.sh

1. Ejecute el microservicio task\_ms.

Abra una nueva terminal. Asegúrese que el virtual env

Este activo.

En esa terminal ejecutar:

CD task\_ms

Sh run.sh

1. Ejecute el microservicio conv\_ms.

Abra una nueva terminal. Asegúrese que el virtual env

Este activo.

En esa terminal ejecutar:

CD conv\_ms

Sh run.sh

1. Ejecute el schedule de celery.

Abra una nueva terminal. Asegúrese que el virtual env

Este activo.

En esa terminal ejecutar:

Celery -A conv\_ms.app.celery\_app beat

1. Ejecute el trabajador celery.

Abra una nueva terminal. Asegúrese que el virtual env

Este activo.

En esa terminal ejecutar:

Celery -A conv\_ms.app.celery\_app worker -l info --pool=solo

En este momento deberían estar desplegados los microservicios asi:

Auth\_ms 127.0.0.1:5001

Task\_ms 127.0.0.1:5002

Conv\_ms 127.0.0.1:5003

El programador de Celery debe generar una nueva

Tarea Celery cada segundo.


