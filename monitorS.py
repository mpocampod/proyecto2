import boto3 # Importar el SDK de AWS
import time
import grpc
import monitor_pb2
import monitor_pb2_grpc
from concurrent import futures

# Definir las variables globales necesarias para la comunicación con el API SDK de la nube
AWS_REGION = 'us-west-2' # Región de AWS donde se encuentra el servicio EC2 - cambiar el AWS_REGION
EC2_INSTANCE_TYPE = 't2.micro' # Tipo de instancia EC2 que se creará
EC2_SECURITY_GROUP_ID = 'sg-xxxxxxxxxxxx' # ID del grupo de seguridad de la instancia EC2
EC2_AMI_ID = 'ami-xxxxxxxxxxxx' # ID de la imagen AMI personalizada que se utilizará como base para crear nuevas instancias
EC2_USER_DATA = '''#!/bin/bash
echo "Hello, World!" > index.html
nohup python app.py &
''' # Script que se ejecutará en la instancia EC2 para iniciar la AppInstance y el agente MonitorC (cambiar ese script)

# Definir las variables globales para la comunicación con el MonitorC
MONITORC_API_ENDPOINT = 'localhost:50051' # Endpoint del MonitorC
MONITORC_REGISTER_URL = '/register' # URL para registrar el MonitorS en el MonitorC
MONITORC_UNREGISTER_URL = '/unregister' # URL para desregistrar el MonitorS en el MonitorC
MONITOR_POLL_INTERVAL = 10 # Intervalo de tiempo en segundos para consultar el estado de las instancias

class MonitorSServicer(monitor_pb2_grpc.MonitorSServicer):
    
    # Función para registrar el MonitorS en el MonitorC
    def register(self, request, context):
        # falta agregar lógica para registrar el MonitorS en el MonitorC
        return monitor_pb2.MonitorSReply(message='MonitorS registrado con éxito en MonitorC')
    
    # Función para desregistrar el MonitorS en el MonitorC
    def unregister(self, request, context):
        # falta agregar la lógica para desregistrar el MonitorS en el MonitorC
        return monitor_pb2.MonitorSReply(message='MonitorS desregistrado con éxito de MonitorC')
    
    # Función para consultar el estado de las instancias de AppInstance
    def get_metrics(self, request, context):
        # falta agregar la lógica para consultar el estado de las instancias de AppInstance
        # y retornar las métricas recolectadas
        return monitor_pb2.MonitorSMetrics(cpu_load=50, memory_usage=70)
    
    # Función para detectar la vivacidad de las instancias de AppInstance
    def ping(self, request, context):
        # falta agregar la lógica para detectar la vivacidad de las instancias de AppInstance
        return monitor_pb2.MonitorSReply(message='Pong')
    
    def main():
    # Crear una instancia del cliente de EC2 
        ec2 = boto3.client('ec2', region_name=AWS_REGION)
        instance = ec2.run_instances(
            #poner la ami de la instancia principal
        ImageId='ami-xxxxxxxxxxxx',
            InstanceType='t2.micro',
            MinCount=2,
            MaxCount=5,
            #nombre de la llave, se pone esa por defecto
            KeyName='vockey.pem',
            #modificar el UserData para clonar el repo
            UserData='#!/bin/bash',
            SecurityGroupIds=['sg-xxxxxxxxxxxx']
        )['Instances'][0]

        # Obtener el ID de la instancia
        instance_id = instance.id

        # Eliminar la instancia
        response = ec2.terminate_instances(
            InstanceIds=[instance_id]
        )

        if response['ResponseMetadata']['HTTPStatusCode'] == 200:
            print('Instancia eliminada con éxito')
        else:
            print('Hubo un error al eliminar la instancia')

        # Crear una instancia del servidor gRPC para el MonitorS
        server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
        monitor_pb2_grpc.add_MonitorSServicer_to_server(MonitorSServicer(), server)
        server.add_insecure_port('[::]:50051')
        server.start()
        print('MonitorS en ejecución...')
        
        # Loop principal para consultar el estado de las instancias de AppInstance
        try:
            while True:
                # Consultar el estado de las instancias de AppInstance y almacenar los datos recolectados
                # Aquí también se puede incluir la lógica necesaria para crear o eliminar instancias EC2 según sea necesario
                time.sleep(MONITOR_POLL_INTERVAL)
        except KeyboardInterrupt:
            server.stop(0)
        
    if __name__ == '__main__':
        main()
