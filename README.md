# PROYECTO 2

## Información de la asignatura.
Topicos Especiales en Telematica.

## Datos del estudiante (s).
Paulina Ocampo Duque ***mpocampod@eafit.edu.co***

Juan Jose Sanchez Cortes ***jjsanchezc@eafit.edu.co***

Maria José Gutiérrez Estrada. ***mjgutierre@eafit.edu.co***



## Contexto.

Los servicios principales de alta escalabilidad en muchos sistemas distribuidos se diseñan e implementan mediante servicios de Alta Disponibilidad y Rendimiento. Diferentes mecanismos y
servicios en nube nos permiten diseñar e implementar mecanismos de alta disponibilidad y Rendimiento. Dos de ellos, son los servicios administrados de Balanceador de Carga (LB) y el Grupo de
Auto escalamiento (ASG). Los balanceadores de carga, permiten distribuir la carga entre varias unidades de procesamiento, aislar fallas, mejorar el rendimiento, entre otras. Los grupos de auto
escalamiento permiten mediante diferentes métricas adicionar o disminuir unidades de procesamiento, típicamente empleadas por un balanceador de carga

## Arquitectura 

![image](https://github.com/mpocampod/proyecto2/assets/68908889/ae810e52-220e-48da-96b1-306773c1a57c)

## Definición del Proyecto. 

Este proyecto diseñará e implementará un servicio de auto escalamiento que operará sobre instancias EC2 de AWS de Amazon. A nivel de aplicaciones o procesos, se diseñarán e implementarán tres así: 

1. MonitorS: Proceso principal de monitoreo que periódicamente consulta el estado de vivacidad y carga de las instancias de aplicación (AppInstance) en las cuales correo un proceso MonitorC que ofrece varios servicios mediante una API hacia el MonitorS.
  o Las comunicaciones entre MonitorS y MonitorC serán a través de gRPC.
  
  2. Algunos de los servicios que implementará MonitorC son:
  
   - Ping/Pong o Heartbeat para detectar vivacidad de la instancia de la AppInstance
   - GetMetrics: conjunto de métricas como Carga (medida entre 0 y 100% que mide la carga de una máquina), para efectos de este proyecto, cada grupo
    deberá simular e ir modificando esta métrica. Se espera que esta función de simulación cambie gradualmente y no bruscamente.
   - Registro y Desregistro del MonitorS
   - Eventualmente otros servicios que por su diseño requieran definir, diseñar e
    implementar.

3. ControllerASG: Es un proceso o aplicación que corre en la misma instancia del MonitorS. Tiene acceso a toda la información recolectada por el el MonitorS por medio de memoria
compartida. Este ControllerASG ejecuta las siguientes funciones:

  - Se comunica con el API SDK de la nube para ejecutar diferentes funciones de Infraestructura como Código, es decir, mediante programación puede invocar la creación, modificación, borrado entre otros de diferentes servicios de nube.
      - En este caso, se requiere solo acceder al servicio de gestión de instancias EC2.
      - En grupo de trabajo, primero deberá instanciar una máquina EC2 con el software base, la AppInstance y el agente MonitorC.
  - Deberá pensar y definir el mecanismo de configuración de la IP o URL o un servicio de localización del MonitorS.
  - A partir de esta instancia, se deberá crear una imagen AMI personalizada, que servirá de base para la creación de nuevas instancias por el ControllerASG.


### Configuración de Instancias en AWS

En la creación de nuevas instancias del ASG deberá configurarse o conocer previamente:
- Hardware: usar t2.micro
- Disco duro: EBS
- VPC
- Security Group
- Key pair: por defecto asigne vockey.pem
- Otros parámetros que requiera.
    - El ControllerASG deberá definir minInstances (no menor a dos), maxInstance (máx 5 por el tipo de cuenta aws academy), y una politica de creación y otra política de destrucción de instancias

