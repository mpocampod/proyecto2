import multiprocessing
import time
import grpc
import monitor_pb2
import monitor_pb2_grpc
import psutil
import random 
from concurrent import futures

class MonitorC(monitor_pb2_grpc.MonitorServicer):
    def __init__(self,jost,):
        host=jost
        self.alive = True
        self.capacidad=40
        channel=grpc.insecure_channel(host)
        self.stub = monitor_pb2_grpc.MonitorStub(channel)
        

    def Register(self,request,context):
        '''Este metodo le dice al monitor S cuando se ha creado una instancia nueva

        Args:
            instance_id (int o string): Identificador de la instancia que se acaba de crear y se quiere enviar al monitorC

        Returns:
            string: el mensaje de confirmación o error que recibe del monitorC
        '''        
        #Este metodo se utilizará despues de crear una instancia nueva para poder decirle al monitor c que se registró
        
        #respuesta=self.stub.Register(monitor_pb2.RegisterRequest(instance_id=instance_id))
        respuesta=self.stub.Register(monitor_pb2.RegisterResponse('se ha registrado'))
        return respuesta.response
        
    
    def unregister(self,instance_id):
        '''Este metodo le dice al monitor S cuando se ha eliminado el registro de una instancia

        Args:
            instance_id (int o string): Identificador de la instancia que se quiere eliminar el registro y se quiere enviar al monitorC

        Returns:
            string: el mensaje de confirmación o error que recibe del monitorC
        '''      
        
        #respuesta=self.stub.Unregister(monitor_pb2.UnregisterRequest(instance_id=instance_id))
        respuesta=self.stub.Unregister(monitor_pb2.UnregisterResponse('se ha eliminado del registro'))
        return respuesta.response
    
    # Función para detectar la vivacidad de las instancias de AppInstance
    def ping_pong(self):
        """debo revisar el tema de las instancias o como es que se va a ver"""
        #El metodo se conecta con el MonitorS para dar su respuesta

        # Nombre del programa que deseas verificar si está en ejecución
        program_name = "calculadora.py"

        if self.check_process_running(program_name):
            ans=(f"El programa '{program_name}' está en ejecución.")
            print(ans)
        else:
            ans=(f"El programa '{program_name}' no está en ejecución.")
            print(ans)
        
        return self.stub.Ping(monitor_pb2.PingResponse(message=ans))

    
    def simulacion(self): 
        cambio=random.uniform(-5, 5)
        self.capacidad+=cambio
        self.capacidad= max(0, min(100, self.capacidad))

        return self.capacidad
        
        
    def GetMetrics(self,request):

        self.capacidad= self.simulacion()
        return monitor_pb2.GetMetricsResponse(capacidad=self.capacidad)

    

    def check_process_running(self,process_name):
        for process in psutil.process_iter(['name']):
            if process.info['name'] == process_name:
                return True
        return False


def serve():
    host='[::]:50051'
    monitorc_temp=MonitorC(host)
    
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    monitor_pb2_grpc.add_MonitorServicer_to_server(MonitorC(host), server)
    server.add_insecure_port(host)
    server.start()
    try:
        while True:
            estado = monitorc_temp.simulacion()
            MonitorC.capacidad = estado
            time.sleep(5)
    except KeyboardInterrupt:
        server.stop(0)

if __name__ == '__main__':
    serv = multiprocessing.Process(target=serve)
    serv.start()