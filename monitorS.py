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
            #print(str(self.control.get_new_instances()))
            instances_ipv4=self.control.get_ipv4(instances_id)
            insecure_chanel=str(instances_ipv4)+':50053'
            print(f'{insecure_chanel} la conexion con el monitor C')
            channel=grpc.insecure_channel(f'{str(instances_ipv4)}:50053')
            
            self.stub = monitor_pb2_grpc.MonitorStub(channel)
            self.my_stub.append(self.stub)
        self.min_cap=30
        self.max_cap=80

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
        
        if len(instances)==self.control.min_instances and uso<=self.min_cap: #caso1 minimo de instancias y bajo uso de CPU
            print('entro al caso 1')
            print('no se pueden eliminar mas intancias porque ya está en el minimo de instancias')
            return 60,60
        
        elif len(instances)<self.control.max_instances and uso>=self.max_cap: #caso2 normal de instancias y alto uso de
            print('entro al caso 2')
            #creo instancia
            self.control.create_instance()
            print('se ha creado la instancia nueva')
            return 60,60
        
        elif len(instances)>self.control.min_instances and len(instances)<=self.control.max_instances and uso<=self.min_cap: #caso3 normal de instancias y bajo uso de cpu
            print('entro al caso 3')
            #borro la ultima instancia en la lista
            last_instance=instances[-1]
            self.control.terminate_instance(last_instance)
            return 0,0
        
        elif len(instances)==self.control.max_instances and uso>=self.max_cap: #caso4 maximo de instancias y mucho uso
            print('entro al caso 4')
            print('No se pueden crear mas instancias porque ya está en el maximo de instancias')
            return 45,45
        
        
    def set_connection(self,instance_id):
        instances_ipv4=self.control.get_ipv4(instance_id)
        insecure_chanel=str(instances_ipv4)+':50053'
        print(f'{insecure_chanel} la conexion con el monitor C')
        channel=grpc.insecure_channel(f'{str(instances_ipv4)}:50053')
        self.stub = monitor_pb2_grpc.MonitorStub(channel)
        self.my_stub.append(self.stub)
        
def main():
    monitor_s=MonitorS()
    # Crear una instancia del servidor gRPC para el MonitorS
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    monitor_pb2_grpc.add_MonitorServicer_to_server(monitor_s, server)
    server.add_insecure_port('[::]:50051')
    server.start()
    print(f'MonitorS en ejecución en el puerto 50051')
    aumento=decremento=45
    cont=0
    # Loop principal para consultar el estado de las instancias de AppInstance
    try:
        while True:
            ans=monitor_s.GetMetrics()
            aumento+=ans[0]
            decremento-=ans[1]
            print(f'este es el uso de la maquina 0: {aumento} (sumo)')
            print(f'este es el uso de la maquina 1: {decremento} (resto)')
            try:
                aumento,decremento=monitor_s.autoscaling_policy(aumento)
                aumento,decremento=monitor_s.autoscaling_policy(decremento)
            except:
                print('no pasa nada')
            if aumento==0 and decremento==0:
                print('entra al 0-0')
                
            
            time.sleep(6)
    except KeyboardInterrupt:
        server.stop(0)
    
if __name__ == '__main__':
    main()

