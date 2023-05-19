import boto3 # Importar el SDK de AWS
import time
import grpc
import monitor_pb2
import monitor_pb2_grpc
from concurrent import futures
from controllerASG import controllerASG


class MonitorS(monitor_pb2_grpc.MonitorServicer):
    def __init__(self)->None:
        #configuración inicial de la conexión con el controller
        self.control=controllerASG()

        #ciclo para crear la conexión con todos las instancias
        self.my_stub=[]
        for instances_id in self.control.get_my_instances():
            instances_ipv4=self.control.get_ipv4(instances_id)
            channel=grpc.insecure_channel(f'{str(instances_ipv4)}:50052')
            self.stub = monitor_pb2_grpc.MonitorStub(channel)
            self.my_stub.append(self.stub)
            print(f'este es my_stub {str(self.my_stub)}')
        
        self.min_cap=30
        self.max_cap=60

    
    # Función para consultar el estado de las instancias de AppInstance
    def get_metrics(self):
    # Llama al método get_metrics del MonitorC para obtener la capacidad de la instancia
        for stubs in self.my_stub:
            respuesta_metricas=stubs.GetMetrics(monitor_pb2.GetMetricsRequest())
        
            capacidad = respuesta_metricas.capacidad
            print(capacidad)

        return monitor_pb2.GetMetricsResponse(capacidad=capacidad) #revisar esto


    
    # Función para detectar la vivacidad de las instancias de AppInstance
    def ping(self):
        for stubs in self.my_stub:
            response = stubs.Ping(monitor_pb2.PingRequest(message='Ping'))
            print(str(response.message))
        return response.message
    
    
    def autoscaling_policy(self):
        """Este método se encargaría de definir las políticas de creación y destrucción de instancias para el grupo
          de autoescalado. Debería tomar como parámetros la configuración de las políticas (por ejemplo,
          el número mínimo y máximo de instancias) y la configuración de las métricas que se utilizarán para
            determinar cuándo se deben crear o destruir instancias.
        """        
        instances = self.control.get_all_instances()
        metricas = self.get_metrics()

        #si se tienen 2 instancias y la capacidad esta alta entonces se crea otra instancia (llamar al metodo del controller de create_intance)
        if len(instances) < self.control.min_instances or len(instances ) >= self.control.min_instances and metricas > self.max_cap:
        # Crear una nueva instancia
            self.control.create_instance()
    
        #si se tienen 5 instancias o menos y la capacidad es bajita eliminar instancias (llamar al metodo del controller terminate_instance)
        elif len(instances) <= self.control.max_instances and metricas < self.min_cap:
            self.control.terminate_instance()

        #si se tienen 5 instancias y la capacidad es alta, no se puede create_intance
        elif len(instances)>self.control.max_instances and metricas > self.max_cap:
            print('Ya no se pueden crear mas instancias ya que está en el limite')
    
def main():
    monitor_s=MonitorS()
    # Crear una instancia del servidor gRPC para el MonitorS
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    monitor_pb2_grpc.add_MonitorServicer_to_server(monitor_s, server)
    server.add_insecure_port('[::]:50052')
    server.start()
    print(f'MonitorS en ejecución en el puerto ')
    monitor_s.control.check_min_instances()
    # Loop principal para consultar el estado de las instancias de AppInstance
    try:
        while True:
            estado = monitor_s.get_metrics()
            MonitorS.capacidad=estado
            monitor_s.autoscaling_policy()
            time.sleep(2)
    except KeyboardInterrupt:
        server.stop(0)
    
if __name__ == '__main__':
    main()

