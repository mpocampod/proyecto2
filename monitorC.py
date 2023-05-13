import time
import grpc
import monitor_pb2
import monitor_pb2_grpc

class MonitorC(monitor_pb2_grpc.MonitorCServicer):
    def __init__(self):
        self.alive = True
        self.load = 0.0


    def register(self, request, context):
        # falta agregar lógica para registrar el MonitorS en el MonitorC
        return monitor_pb2.MonitorSReply(message='MonitorS registrado con éxito en MonitorC')
    
    # Función para desregistrar el MonitorS en el MonitorC
    def unregister(self, request, context):
        # falta agregar la lógica para desregistrar el MonitorS en el MonitorC
        return monitor_pb2.MonitorSReply(message='MonitorS desregistrado con éxito de MonitorC')
    
    # Función para detectar la vivacidad de las instancias de AppInstance
    def PingPong(self, request, context):
        return monitor_pb2.Pong(message='Pong!')
    
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
