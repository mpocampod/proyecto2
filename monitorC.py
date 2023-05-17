import time
import grpc
import monitor_pb2
import monitor_pb2_grpc
import psutil
import random 

class MonitorC(monitor_pb2_grpc.MonitorCServicer):
    def __init__(self):
        self.alive = True
        self.load = 0.0
        channel=grpc.insecure_channel('localhost:50051')
        self.stub = monitor_pb2_grpc.MonitorStub(channel)
        

    def register(self,instance_id):
        '''Este metodo le dice al monitor S cuando se ha creado una instancia nueva

        Args:
            instance_id (int o string): Identificador de la instancia que se acaba de crear y se quiere enviar al monitorC

        Returns:
            string: el mensaje de confirmación o error que recibe del monitorC
        '''        
        #Este metodo se utilizará despues de crear una instancia nueva para poder decirle al monitor c que se registró
        """with grpc.insecure_channel('localhost:50051') as channel: #colocamos los datos que necesitemos para poder hacer la conexión
            stub = monitor_pb2_grpc.MonitorStub(channel)"""
        
        respuesta=self.stub.Register(monitor_pb2.RegisterRequest(instance_id=instance_id))
        return respuesta.response
        
    
    # Función para desregistrar el MonitorS en el MonitorC
    def unregister(self,instance_id):
        '''Este metodo le dice al monitor S cuando se ha eliminado el registro de una instancia

        Args:
            instance_id (int o string): Identificador de la instancia que se quiere eliminar el registro y se quiere enviar al monitorC

        Returns:
            string: el mensaje de confirmación o error que recibe del monitorC
        '''  
        
        """with grpc.insecure_channel('localhost:50051') as channel: #colocamos los datos que necesitemos para poder hacer la conexión
            stub = monitor_pb2_grpc.MonitorStub(channel)"""
            
        
        respuesta=self.stub.Unregister(monitor_pb2.UnregisterRequest(instance_id=instance_id))
        return respuesta.response
    
    # Función para detectar la vivacidad de las instancias de AppInstance
    def ping_pong(self):
        """debo revisar el tema de las instancias o como es que se va a ver"""
        #El metodo se conecta con el MonitorS para dar su respuesta
        """with grpc.insecure_channel('localhost:50051') as channel: #colocamos los datos que necesitemos para poder hacer la conexión
            stub = monitor_pb2_grpc.MonitorStub(channel)"""

        # Nombre del programa que deseas verificar si está en ejecución
        program_name = "calculadora.py"

        if self.check_process_running(program_name):
            print(f"El programa '{program_name}' está en ejecución.")
        else:
            print(f"El programa '{program_name}' no está en ejecución.")
        
        return self.stub.Ping(monitor_pb2.PingRequest(message='Pong'))
    
    def simulacion(): 
    
        capacidad=random.randint(0, 100)
        cambio=random.uniform(-5, 5)
        capacidad+=cambio

        capacidad_actual=max(0, 100, capacidad)

        return capacidad_actual
        
        
    def get_metrics(self, request, context):
        return monitor_pb2.Metrics(load=self.load)
    

    def check_process_running(self,process_name):
        for process in psutil.process_iter(['name']):
            if process.info['name'] == process_name:
                return True
        return False

    def serve():
        server = grpc.server(grpc.Future.ThreadPoolExecutor(max_workers=10))
        monitor_pb2_grpc.add_MonitorCServicer_to_server(MonitorC(), server)
        server.add_insecure_port('[::]:50051')
        server.start()
        try:
            while True:
                # update the load metric in the MonitorC instance
                # this is just a placeholder for a real implementation
                MonitorC.load += 1
                time.sleep(5)
        except KeyboardInterrupt:
            server.stop(0)

    
if __name__ == '__main__':
    serve()
