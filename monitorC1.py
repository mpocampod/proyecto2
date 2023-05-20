import grpc
import monitor_pb2
import monitor_pb2_grpc
import multiprocessing
import time
import psutil 


class MonitorC:
    def __init__(self, host):
        self.channel = grpc.insecure_channel(host)
        self.stub = monitor_pb2_grpc.MonitorStub(self.channel)

    def register(self, instance_id):
        request = monitor_pb2.RegisterRequest(instance_id=instance_id)
        response = self.stub.Register(request)
        return response.response

    def unregister(self, instance_id):
        request = monitor_pb2.UnregisterRequest(instance_id=instance_id)
        response = self.stub.Unregister(request)
        return response.response

    def ping(self):
        program_name = "calculadora.py"

        if self.check_process_running(program_name):
            ans=(f"El programa '{program_name}' está en ejecución.")
            print(ans)
        else:
            ans=(f"El programa '{program_name}' no está en ejecución.")
            print(ans)
        
        return self.stub.Ping(monitor_pb2.PingResponse(message=ans))
    

    def get_metrics(self, capacidad):
        request = monitor_pb2.GetMetricsRequest(capacidad=capacidad)
        response = self.stub.GetMetrics(request)
        return response.metrics


def main():
    host = 'localhost:50051'  # Dirección del servidor MonitorS
    monitor_c = MonitorC(host)

    # Registro de la instancia
    instance_id = '12345'  # ID de la instancia
    result = monitor_c.register(instance_id)
    print(result)

    # Simulación del uso de la instancia
    capacidad = int(input('Ingrese el valor de capacidad de la instancia: '))
    metrics = monitor_c.get_metrics(capacidad)
    print('Métricas recibidas:')
    for metric in metrics:
        print(f'Capacidad: {metric.capacidad}')

    # Desregistro de la instancia
    result = monitor_c.unregister(instance_id)
    print(result)


if __name__ == '__main__':
    main()

