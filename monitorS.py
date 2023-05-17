import boto3 # Importar el SDK de AWS
import time
import grpc
import monitor_pb2
import monitor_pb2_grpc
from concurrent import futures
import controllerASG

# Definir las variables globales para la comunicación con el MonitorC
MONITORC_API_ENDPOINT = 'localhost:50051' # Endpoint del MonitorC
MONITORC_REGISTER_URL = '/register' # URL para registrar el MonitorS en el MonitorC
MONITORC_UNREGISTER_URL = '/unregister' # URL para desregistrar el MonitorS en el MonitorC
MONITOR_POLL_INTERVAL = 10 # Intervalo de tiempo en segundos para consultar el estado de las instancias

class MonitorSServicer(monitor_pb2_grpc.MonitorSServicer):
    def __init__(self)->None:
        #configuración inicial de la conexión con el controller
        self.control=controllerASG()

    
    # Función para consultar el estado de las instancias de AppInstance
    def get_metrics(self, request, context):
        # falta agregar la lógica para consultar el estado de las instancias de AppInstance
        # y retornar las métricas recolectadas
        return monitor_pb2.MonitorSMetrics(cpu_load=50, memory_usage=70)
    
    # Función para detectar la vivacidad de las instancias de AppInstance
    def ping(self, request, context):
        # falta agregar la lógica para detectar la vivacidad de las instancias de AppInstance
        return monitor_pb2.MonitorSReply(message='Pong')
    
    
    def autoscaling_policy(self):
        """Este método se encargaría de definir las políticas de creación y destrucción de instancias para el grupo
          de autoescalado. Debería tomar como parámetros la configuración de las políticas (por ejemplo,
          el número mínimo y máximo de instancias) y la configuración de las métricas que se utilizarán para
            determinar cuándo se deben crear o destruir instancias.
        """        
        pass
    
    def main():

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

#el monitor S cuando le pregunta al get metrics cuanta capacidad se esta usando y si es 40 o mas invoca al controles 