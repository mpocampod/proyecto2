import time
import grpc
import monitor_pb2
import monitor_pb2_grpc

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
    def PingPong(self):
        """debo revisar el tema de las instancias o como es que se va a ver"""
        #El metodo se conecta con el MonitorS para dar su respuesta
        """with grpc.insecure_channel('localhost:50051') as channel: #colocamos los datos que necesitemos para poder hacer la conexión
            stub = monitor_pb2_grpc.MonitorStub(channel)"""
        
        return self.stub.Ping(monitor_pb2.PingRequest(message='Pong'))

    
    def GetMetrics(self, request, context):
        return monitor_pb2.Metrics(load=self.load)

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
