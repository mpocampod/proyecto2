import boto3 # Importar el SDK de AWS
import time
import grpc
import monitor_pb2
import monitor_pb2_grpc
from concurrent import futures
import controllerASG


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
    
    
    def autoscaling_policy(self,min_ins, max_ins, min_cap, max_cap):
        """Este método se encargaría de definir las políticas de creación y destrucción de instancias para el grupo
          de autoescalado. Debería tomar como parámetros la configuración de las políticas (por ejemplo,
          el número mínimo y máximo de instancias) y la configuración de las métricas que se utilizarán para
            determinar cuándo se deben crear o destruir instancias.
        """        
        
        #si se tienen 2 instancias y la capacidad esta alta entonces se crea otra instancia (llamar al metodo del controller de create_intance)
        #si se tienen 5 instancias o menos y la capacidad es bajita eliminar instancias (llamar al metodo del controller terminate_instance)
        #si se tienen 5 instancias y la capacidad es alta, no se puede create_intance

        min_ins=2
        max_ins=5
        min_cap=20
        max_cap=60

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

