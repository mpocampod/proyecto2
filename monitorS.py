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
        self.control.check_min_instances()
        self.my_stub=[]
        
        for instances_id in self.control.get_new_instances():
            print(str(self.control.get_new_instances()))
            instances_ipv4=self.control.get_ipv4(instances_id)
            insecure_chanel=str(instances_ipv4)+':5005'
            print(f'{insecure_chanel} este es el INSECURE CHANNEL')
            channel=grpc.insecure_channel(f'{str(instances_ipv4)}:50053')
            
            self.stub = monitor_pb2_grpc.MonitorStub(channel)
            self.my_stub.append(self.stub)
        time.sleep(120)
        self.min_cap=30
        self.max_cap=80

    #used instances NUEVO_____________
    def get_used_instances(self):
        used_instances = []
        instances = self.control.get_all_instances()  

        for instance in instances:
            if instance.state == "running":  # Verificar el estado de la instancia
                used_instances.append(instance)

        return used_instances 
    # Función para consultar el estado de las instancias de AppInstance
    def GetMetrics(self):
        # Llama al método GetMetrics del MonitorC para obtener la capacidad de la instancia
        capacidad_list=[]
        for stubs in self.my_stub:
            peticion=stubs.GetMetrics(monitor_pb2.GetMetricsRequest())
            capacidad_metrics = peticion.metrics
            capacidad=capacidad_metrics[0].capacidad
            print(f'este es la capacidad {capacidad}')
            capacidad_list.append(capacidad)
        print(f'lista de capacidades {capacidad_list}')
        return capacidad_list


    
    # Función para detectar la vivacidad de las instancias de AppInstance
    def ping(self):
        for stubs in self.my_stub:
            response = stubs.Ping(monitor_pb2.PingRequest(message='Ping'))
            print(str(response.message))
        return response.message


    def autoscaling_policy(self,uso):
        """Este método se encargaría de definir las políticas de creación y destrucción de instancias para el grupo
          de autoescalado. Debería tomar como parámetros la configuración de las políticas (por ejemplo,
          el número mínimo y máximo de instancias) y la configuración de las métricas que se utilizarán para
            determinar cuándo se deben crear o destruir instancias.
        """        
        instances = self.control.new_instance_list
        print(f'en este momento existen {len(instances)} instancias')
        
        '''#si se tienen 2 instancias y la capacidad esta alta entonces se crea otra instancia (llamar al metodo del controller de create_intance)
        if len(instances) < self.control.min_instances or len(instances ) >= self.control.min_instances and metricas > self.max_cap:
        # Crear una nueva instancia
            self.control.create_instance()
    
        #si se tienen 5 instancias o menos y la capacidad es bajita eliminar instancias (llamar al metodo del controller terminate_instance)
        elif len(instances) <= self.control.max_instances and metricas < self.min_cap:
            self.control.terminate_instance('i-0b13cb0b4921008b4')
            print('terminando instancia i-0b13cb0b4921008b4')

        #si se tienen 5 instancias y la capacidad es alta, no se puede create_intance
        elif len(instances)>self.control.max_instances and metricas > self.max_cap:
            print('Ya no se pueden crear mas instancias ya que está en el limite')
        '''
    
def main():
    monitor_s=MonitorS()
    # Crear una instancia del servidor gRPC para el MonitorS
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    monitor_pb2_grpc.add_MonitorServicer_to_server(monitor_s, server)
    server.add_insecure_port('[::]:50051')
    server.start()
    print(f'MonitorS en ejecución en el puerto 50051')
    aumento=decremento=60
    
    # Loop principal para consultar el estado de las instancias de AppInstance
    try:
        while True:
            ans=monitor_s.GetMetrics()
            aumento+=ans[0]
            decremento-=ans[1]
            print(f'este es el uso de la maquina 0: {aumento} (sumo)')
            print(f'este es el uso de la maquina 0: {decremento} (resto)')
            monitor_s.autoscaling_policy(aumento)
            monitor_s.autoscaling_policy(decremento)
            #monitor_s.autoscaling_policy()
            
            time.sleep(3)
    except KeyboardInterrupt:
        server.stop(0)
    
if __name__ == '__main__':
    main()

