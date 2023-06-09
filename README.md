# PROYECTO 2

## Información de la asignatura.
Topicos Especiales en Telematica.

## Datos del estudiante (s).
Paulina Ocampo Duque ***mpocampod@eafit.edu.co***

Juan Jose Sanchez Cortes ***jjsanchezc@eafit.edu.co***

Maria José Gutiérrez Estrada. ***mjgutierre@eafit.edu.co***

## Tabla de contenido 
1. [Arquitectura](https://github.com/mpocampod/proyecto2/tree/master#arquitectura)
2. [Definición del Proyecto](https://github.com/mpocampod/proyecto2/tree/master#definición-del-proyecto)
3. [Documentación Técnica](https://github.com/mpocampod/proyecto2/tree/master#documentación-técnica)
4. [Logros](https://github.com/mpocampod/proyecto2/tree/master#logros)


## Arquitectura 

<p align="center">
  <img src="https://github.com/mpocampod/proyecto2/assets/68908889/ae810e52-220e-48da-96b1-306773c1a57c" alt="Arquitectura" width="" height="" style="display: block; margin: auto;">
</p>

## Definición del Proyecto. 

> Darle click a los metodos para ir directamente a la linea de estos en el codigo

Este proyecto diseñará e implementará un servicio de auto escalamiento que operará sobre instancias EC2 de AWS de Amazon. A nivel de aplicaciones o procesos, se diseñarán e implementarán tres así: 

1. [MonitorS:](https://github.com/mpocampod/proyecto2/blob/master/monitorS.py) Proceso principal de monitoreo que periódicamente consulta el estado de vivacidad y carga de las instancias de aplicación (AppInstance) en las cuales correo un proceso MonitorC que ofrece varios servicios mediante una API hacia el MonitorS.

  - Las comunicaciones entre MonitorS y MonitorC es a través de gRPC.
 
2. Algunos de los servicios que implementará [MonitorC](https://github.com/mpocampod/proyecto2/blob/master/monitorC.py) son:
  
   - [Ping/Pong](https://github.com/mpocampod/proyecto2/blob/master/monitorC.py#L50) o Heartbeat para detectar vivacidad de la instancia de la AppInstance 
   - [GetMetrics:](https://github.com/mpocampod/proyecto2/blob/master/monitorS.py#L32) conjunto de métricas como Carga (medida entre 0 y 100% que mide la carga de una máquina), para efectos de este proyecto, se simulo y modifico esta métrica. Haciendo que esta función de simulación cambie gradualmente y no bruscamente.
   - Existe el [Registro](https://github.com/mpocampod/proyecto2/blob/master/monitorC.py#L19) y [Desregistro](https://github.com/mpocampod/proyecto2/blob/master/monitorC.py#L35) del MonitorS

3. [ControllerASG:](https://github.com/mpocampod/proyecto2/blob/master/controllerASG.py) Es un proceso o aplicación que corre en la misma instancia del MonitorS. Tiene acceso a toda la información recolectada por el el MonitorS por medio de memoria compartida. Este ControllerASG ejecuta las siguientes funciones:

  - Se comunica con el API SDK de la nube para ejecutar diferentes funciones de Infraestructura como Código, es decir, mediante programación puede invocar la creación, modificación, borrado entre otros de diferentes servicios de nube.
      - En este caso, se requiere solo acceder al servicio de gestión de instancias EC2.
      - primero se instanciara una máquina EC2 con el software base, la [AppInstance](https://github.com/mpocampod/proyecto2/blob/master/app/calculadora.py) y el agente MonitorC.
  - Se define el mecanismo de configuración de la IP o URL o un servicio de localización del MonitorS.
  - A partir de esta instancia, se deberá crear una imagen AMI personalizada, que servirá de base para la creación de nuevas instancias por el ControllerASG.
  - Otros parámetros que requiera.
    - El ControllerASG define minInstances igual a 2, maxInstance menor a 5, con una politica de creación y otra política de destrucción de instancias

## Documentación Técnica
### Grupos de seguridad
para los grupos de seguridad debemos permitir el uso de los puertos 22 para el SSH, 50051,50052 y 50053 para permitir que el monitorS, monitorC y controllerASG puedan funcionar correctamente

### MonitorS

Crear instancias necesarias con las siguientes especificaciones. 

  - Hardware: usar t2.micro
  - Disco duro: EBS
  - VPC
  - Security Group
  - Key pair: asigne P2.pem

Luego se podra conectar por consola y ejecutar los siguientes comandos 

        #!/bin/bash
        cd /home/ubuntu/
        git clone https://github.com/mpocampod/proyecto2.git
        sudo apt update -y
        sudo apt install -y python3-pip
        cd proyecto2
        pip install -r requirements.txt
        
Luego de iniciar una nueva sesion de laboratorio en AWS se hace necesario cambiar las crendenciales en el controllerASG.py para esto dentro de nuestra consola y carpeta de Proyecto2 ejecutaremos el siguiente comando

        sudo nano controllerASG.py

y cambiaremos estas lineas con las credenciales de la sesion de AWS 

    aws_access_key_id='ASIATQCL7MV57HXFBHPW',
      aws_session_token='FwoGZXIvYXdzEO7//////////wEaDL+fQfVnOUncxWncRCLIAasRJwMPyfAQKfaL+IA42L2zn8lFLwnzpNT/DnZ3RO7Fc5xLLUZVLN+ia9l4CBzdamNv0PeT004uTaw9qMJy+9pc7Og1VPLeIwuxEn/olvd2TEuFs98XnkQDZUZMX6Vltdnc8IwXiprRslVbT0Z2/u/TdAp8hxdPqyE4o9DyBs7Lqq1BWh7XJqeaAtvU+D34EGfm7k+z285MaSn44ehMZxVMRUjYPR8hCOpLbr7roTTkNRT13r5j5FWWHarXCMl2PEnF7ZZYzFTwKJOvvaMGMi3LdzAOKhIMJWSJrdFn4OU0bl1pYlwTtMohbBP5z/zo6w4GCBDvQMnvA9g2t4w=',
    aws_secret_access_key='5aDXD31oyD2QyYdkR5ACRYTlLM/SDuQG6iPtNjv4'
    

Luego guardamos y podemos ejecutar nuestro monitorS

        python3 monitorS.py

Aqui se podra empezar a ver los siguientes sucesos.
### Caso 1 del autoscaling Policy monitoreado

<p align="center">
  <img src="https://github.com/mpocampod/proyecto2/assets/68908889/34f94c87-e21f-4e3c-8b57-72e89bdc60ae" alt="CASO1" width="521" height="" style="display: block; margin: auto;">
</p>

Esto sucede en el codigo del Monitor S cuando hay un numero minimo de instancias y bajo uso de CPU, entonces creará otra instancia

     if len(instances)==self.control.min_instances and uso<=self.min_cap: 
            print('entro al caso 1')
            print('no se pueden eliminar mas intancias porque ya está en el minimo de instancias')
            return 60,60

### Caso 2 del autoscaling Policy monitoreado

<p align="center">
  <img src="https://github.com/mpocampod/proyecto2/assets/68908889/dc6b08a6-8492-4f95-9f3e-58839dce0d4e" alt="CASO2" width="405" height="" style="display: block; margin: auto;">
</p>

Esto sucede en el codigo del Monitor S cuando hay un numero normal de instancias y alto uso de CPU entonces creará otra instancia

     elif len(instances)<self.control.max_instances and uso>=self.max_cap: #caso2 normal de instancias y alto uso de
            print('entro al caso 2')
            #creo instancia
            instance_id=self.control.create_instance()
            self.set_connection(instance_id)
            print('se ha creado la instancia nueva')
            return 60,60

### Caso 3 del autoscaling Policy monitoreado

<p align="center">
  <img src="https://github.com/mpocampod/proyecto2/assets/68908889/70cc951f-e7f2-4442-89ca-3784082129ca" alt="CASO3" width="754" height="" style="display: block; margin: auto;">
</p>

      elif len(instances)>self.control.min_instances and len(instances)<=self.control.max_instances and uso<=self.min_cap: 
            print('entro al caso 3')
            #borro la ultima instancia en la lista
            last_instance=instances[-1]
            self.control.terminate_instance(last_instance)
            return 0,0

Esto sucede en el codigo del Monitor S cuando hay un numero normal de instancias y bajo uso de cpu, entonces se elimina la ultima instancia de la lista

### Caso 4 del autoscaling Policy monitoreado, cuando hay un caso maximo de instancias y maximo de capacidad

<p align="center">
  <img src="https://github.com/mpocampod/proyecto2/assets/68908889/158fe951-5a43-4ae7-9df3-139ad0d4cf58" alt="CASO4" width="498" height="" style="display: block; margin: auto;">
</p>

      elif len(instances)==self.control.max_instances and uso>=self.max_cap: #caso4 maximo de instancias y mucho uso
            print('entro al caso 4')
            print('No se pueden crear mas instancias porque ya está en el maximo de instancias')
            return 45,45
            
Esto sucede en el codigo del Monitor S cuando hay un numero maximo de instancias (5) y mucho uso de CPU, entonces imprime el mensaje de no se pueden crear mas instancias. 
 
  
## Logros 

1. [x] MonitorS: Proceso principal de monitoreo que periódicamente consulta el estado de vivacidad y carga de las instancias de aplicación (AppInstance) en las cuales correo un proceso MonitorC que ofrece varios servicios mediante una API hacia el MonitorS.

2. [x] Las comunicaciones entre MonitorS y MonitorC es a través de gRPC.
 
3. [x] MonitorC con:
  
   - [x] Ping/Pong o Heartbeat para detectar vivacidad de la instancia de la AppInstance 
   - [x] GetMetrics: conjunto de métricas como Carga (medida entre 0 y 100% que mide la carga de una máquina), para efectos de este proyecto, se simulo y modifico esta métrica. Haciendo que esta función de simulación cambie gradualmente y no bruscamente.
   - [x] Existe el Registro y Desregistro del MonitorS

3. [x] ControllerASG con:

  - [x]  Se comunica con el API SDK de la nube para ejecutar diferentes funciones de Infraestructura como Código, es decir, mediante programación puede invocar la creación, modificación, borrado entre otros de diferentes servicios de nube.
      - [x] En este caso, se requiere solo acceder al servicio de gestión de instancias EC2.
      - [x] primero se instanciara una máquina EC2 con el software base, la AppInstance y el agente MonitorC.
  - [x] Se define el mecanismo de configuración de la IP o URL o un servicio de localización del MonitorS.
  - [x] A partir de esta instancia, se deberá crear una imagen AMI personalizada, que servirá de base para la creación de nuevas instancias por el ControllerASG.
  - Otros parámetros que requiera.
    - [x] El ControllerASG define minInstances igual a 2, maxInstance menor a 5, con una politica de creación y otra política de destrucción de instancias
