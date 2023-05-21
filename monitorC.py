import multiprocessing
import time
import grpc
import monitor_pb2
import monitor_pb2_grpc
import psutil
import random 
from concurrent import futures

class MonitorC(monitor_pb2_grpc.MonitorServicer):
    def __init__(self):
        host='[::]:50053'
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
    def Ping(self,request,context):
        """debo revisar el tema de las instancias o como es que se va a ver"""
        #El metodo se conecta con el MonitorS para dar su respuesta
        """for conexion in psutil.net_connections():
            if conexion.laddr.port == 50052 and conexion.status == psutil.CONN_LISTEN:
                return monitor_pb2.PingResponse(message='la app está ejecutandose')"""
        return monitor_pb2.PingResponse(message='la app no está ejecutandose')

    
    def simulacion(self): 
        cambio=random.uniform(-5, 5)
        self.capacidad+=cambio
        self.capacidad= max(0, min(100, self.capacidad))
        return self.capacidad
        
        
    def GetMetrics(self,request,context):
        metric=monitor_pb2.Metric(capacidad=float(5))
        return monitor_pb2.GetMetricsResponse(metrics=[metric])


def serve():
    monitorc_temp=MonitorC()
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    monitor_pb2_grpc.add_MonitorServicer_to_server(monitorc_temp, server)
    server.add_insecure_port('[::]:50053')
    server.start()
    server.wait_for_termination()

if __name__ == '__main__':
    serv = multiprocessing.Process(target=serve)
    #aca puede ir el ping
    serv.start()