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



class MonitorS(monitor_pb2_grpc.MonitorSServicer):
    def __init__(self)->None:
        #configuración inicial de la conexión con el controller
        self.control=controllerASG()
        channel=grpc.insecure_channel('localhost:50052')
        self.stub = monitor_pb2_grpc.MonitorStub(channel)

    
    # Función para consultar el estado de las instancias de AppInstance
    def get_metrics(self, request, context):
    # Llama al método get_metrics del MonitorC para obtener la capacidad de la instancia
        monitor_c = monitor_pb2_grpc.MonitorStub(grpc.insecure_channel('localhost:50051'))
        respuesta_metricas = monitor_c.get_metrics(monitor_pb2.GetMetricsRequest())

        capacidad = respuesta_metricas.capacidad

        return monitor_pb2.GetMetricsResponse(capacidad=capacidad)

    
    # Función para detectar la vivacidad de las instancias de AppInstance
    def ping(self, request, context):
        response = self.stub.Ping(monitor_pb2.PingRequest(message='Ping'))
        return response.message
    
    
    def autoscaling_policy(self):
        """Este método se encargaría de definir las políticas de creación y destrucción de instancias para el grupo
          de autoescalado. Debería tomar como parámetros la configuración de las políticas (por ejemplo,
          el número mínimo y máximo de instancias) y la configuración de las métricas que se utilizarán para
            determinar cuándo se deben crear o destruir instancias.
        """        
        
        pass
    
    def main(self):

        # Crear una instancia del servidor gRPC para el MonitorS
        server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
        monitor_pb2_grpc.add_MonitorServicer_to_server(MonitorS(), server)
        server.add_insecure_port('[::]:50052')
        server.start()
        print('MonitorS en ejecución...')
        
        # Loop principal para consultar el estado de las instancias de AppInstance
        try:
            while True:
                estado = self.get_metrics()
                MonitorS.capacidad=estado
                time.sleep(2)
        except KeyboardInterrupt:
            server.stop(0)
        
    if __name__ == '__main__':
        main()

#el monitor S cuando le pregunta al get metrics cuanta capacidad se esta usando y si es 40 o mas invoca al controles 