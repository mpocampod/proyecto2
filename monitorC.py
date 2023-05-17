import time
import grpc
import monitor_pb2
import monitor_pb2_grpc
import random 

class MonitorC(monitor_pb2_grpc.MonitorCServicer):
    def __init__(self):
        self.alive = True
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
        
        return self.stub.Ping(monitor_pb2.PingResponse(message='Pong'))
    
    def simulacion(): 
    
        capacidad=random.randint(0, 100)
        cambio=random.uniform(-5, 5)
        capacidad+=cambio
        capacidad_actual= max(0, min(100, capacidad))

        return capacidad_actual
        
        
    def get_metrics(self, request, context):
        self.capacidad= self.simulacion()
        return monitor_pb2.GetMetricsResponse(capacidad=self.capacidad)

    def serve(self):
        server = grpc.server(grpc.Future.ThreadPoolExecutor(max_workers=10))
        monitor_pb2_grpc.add_MonitorServicer_to_server(MonitorC(), server)
        server.add_insecure_port('[::]:50051')
        server.start()
        try:
            while True:
                estado = self.simulacion()
                MonitorC.capacidad = estado
                time.sleep(5)
        except KeyboardInterrupt:
            server.stop(0)

    if __name__ == '__main__':
        serve()
