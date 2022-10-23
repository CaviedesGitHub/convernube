# convernube
INSTALACION

1. Descargue el código del repositorio a su equipo.
   Git clone 
   Debería funcionar cualquiera de las ramas: Maine o unarchivo.
2. Abra la carpeta convernube en vs code
3. Instale un entorno virtual en la carpeta venv.
   En la terminal digite lo siguiente.
   En windows:
      Python -m venv venv
   En linux:
      Virtualenv venv
4. Active el entorno virtual.
   En windows:
      .\venv\scripts\activate 
   En linux:
      Source venv/bin/activate
5. Instale las dependencias.
   Pip freeze > requirements.txt
6. Debe tener instalado postgres y una base de 
   Datos llamada AudioConv con usuario administrador 
   Y contraseña admin.
   En linux:
      Sudo apt update
      Sudo apt install postgresql postgresql.contrib
      Sudo su - postgres 
      Create user admin with password 'postgres'
      Create database AudioConv with owner admin
      Alter user postgres with super user
      \q
      Exit
7. Debe instalar redis.
    En linux:
       Sudo apt update 
       Sudo apt install -y redis 
8. Debe instalar ffmpeg 
   En linux:
       Sudo apt install ffmpeg
9. Ejecute el microservicio auth_ms.
   En la terminal:
      CD auth_ms
      Sh run.sh
10. Ejecute el microservicio task_ms.
   Abra una nueva terminal. Asegúrese que el virtual env
   Este activo.
   En esa terminal ejecutar:
      CD task_ms
      Sh run.sh
11. Ejecute el microservicio conv_ms.
   Abra una nueva terminal. Asegúrese que el virtual env 
   Este activo.
   En esa terminal ejecutar:
      CD conv_ms
      Sh run.sh
12. Ejecute el schedule de celery.
   Abra una nueva terminal. Asegúrese que el virtual env 
   Este activo.
   En esa terminal ejecutar:
      Celery -A conv_ms.celery_app beat
13. Ejecute el trabajador celery.
   Abra una nueva terminal. Asegúrese que el virtual env 
   Este activo.
   En esa terminal ejecutar:
      Celery -A conv_ms.celery_app l info --pool=solo

En este momento deberían estar desplegados los microservicios asi:
Auth_ms 127.0.0.1:5001
Task_ms 127.0.0.1:5002
Conv_ms 127.0.0.1:5003
El programador de Celery debe generar una nueva
Tarea Celery cada segundo.


