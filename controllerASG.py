import base64
import time
import boto3

class controllerASG:
    def __init__(self) -> None:
        HOST = '[::]:8080'
        my_session = boto3.session.Session()
        self.ec2_client = boto3.client(
            'ec2',
            region_name='us-east-1',
            aws_access_key_id='ASIATQCL7MV57HXFBHPW',
            aws_session_token='FwoGZXIvYXdzEO7//////////wEaDL+fQfVnOUncxWncRCLIAasRJwMPyfAQKfaL+IA42L2zn8lFLwnzpNT/DnZ3RO7Fc5xLLUZVLN+ia9l4CBzdamNv0PeT004uTaw9qMJy+9pc7Og1VPLeIwuxEn/olvd2TEuFs98XnkQDZUZMX6Vltdnc8IwXiprRslVbT0Z2/u/TdAp8hxdPqyE4o9DyBs7Lqq1BWh7XJqeaAtvU+D34EGfm7k+z285MaSn44ehMZxVMRUjYPR8hCOpLbr7roTTkNRT13r5j5FWWHarXCMl2PEnF7ZZYzFTwKJOvvaMGMi3LdzAOKhIMJWSJrdFn4OU0bl1pYlwTtMohbBP5z/zo6w4GCBDvQMnvA9g2t4w=',
            aws_secret_access_key='5aDXD31oyD2QyYdkR5ACRYTlLM/SDuQG6iPtNjv4'
        )
        #self.new_instance_list=['i-05dc535858d4e1972','i-042bcd096ae1c99f3']
        self.new_instance_list=["i-0aa0fc58715d11af1"]
        self.existing_instance_list=[]
        self.min_instances=2
        self.max_instances=5
        self.get_my_instances()

    def create_instance(self):
        """Este método se encargaría de crear una nueva instancia de EC2 basada en la imagen AMI personalizada que
        se ha definido previamente. Debería tomar como parámetros la configuración de la instancia
        """        
        self.get_my_instances()
        try:
            print('Creando Instancia en EC2 ...')

            response=self.ec2_client.run_instances(
                LaunchTemplate={
                    'LaunchTemplateId': 'lt-0527ca52e2b9524f8'
                },
                ImageId='ami-007855ac798b5175e',
                MinCount=1,
                MaxCount=1
                )
            instance_id = response['Instances'][0]['InstanceId']
            self.ec2_client.get_waiter('instance_running').wait(InstanceIds=[instance_id])
            
            # Obtener la dirección IP pública de la instancia
            response = self.ec2_client.describe_instances(InstanceIds=[instance_id])
            ipv4_publico = response['Reservations'][0]['Instances'][0]['PublicIpAddress']
            print(f"La dirección IP pública de la instancia es: {ipv4_publico}")
            self.new_instance_list.append(instance_id)
            time.sleep(80)
            return instance_id
        except Exception as e:
            print(e)
        

    def terminate_instance(self,instance_id)->bool:
        """Este método se encargaría de terminar una instancia de EC2 específica.
        Debería tomar como parámetro el ID de la instancia que se desea terminar.
        """
        try:
            print(f'terminando instancia {instance_id} ...')
            self.ec2_client.terminate_instances(InstanceIds=[instance_id])
            self.new_instance_list.remove(instance_id)
            print(f"se ha terminado la instancia con id: {instance_id}")
            print(f'instancias restantes: {str(self.new_instance_list)}')
            return True
        except Exception as e:
            print(e)
            return False
        
    def describe_my_instances(self):
        """Este método se encargaría de obtener información sobre las instancias de EC2 que se están ejecutando
        actualmente en la cuenta de AWS. Debería devolver información como el ID de la instancia, la dirección IP,
        el estado de la instancia, etc.
        """        
        ans=self.ec2_client.describe_instances()
        for reservation in ans['Reservations']:
            for instance in reservation['Instances']:
                #aca podemos poner los datos que querramos ver
            #   https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ec2/client/describe_instances.html#describe-instances
                pass 
        
    def check_min_instances(self):
        """metodo se encargará de revisar el numero de instancias que haya, en caso tal de que no se cumpla, deberá crear una instancia nueva
        """        
        print(f'estos son las new_instance_list {self.new_instance_list}')
        try:
            while len(self.new_instance_list)<self.min_instances: 
                self.create_instance()
                print(f'estas son las instanias de new_instance {self.new_instance_list}')
        except Exception as e:
            print(e)
    

    def get_new_instances(self):
        """_summary_
        """       
        return self.new_instance_list

    def get_my_instances(self):
        """metodo para obtener las instancias que ya se tienen creadas y no permitir que se creen duplicadas
        """        
        ans=self.ec2_client.describe_instances()
        try:
            for reservation in ans['Reservations']:
                for instance in reservation['Instances']:
                    if instance['InstanceId'] not in self.existing_instance_list:
                        self.existing_instance_list.append(instance['InstanceId'])
            return self.existing_instance_list
        except Exception as e:
            print(e)      
    
    def get_ipv4(self,instance_id):
        response = self.ec2_client.describe_instances(InstanceIds=[instance_id])
        try:
            ipv4_publico = response['Reservations'][0]['Instances'][0]['PublicIpAddress']
            print(f"La dirección IPv4 pública de la instancia {instance_id} es {ipv4_publico}")
            return ipv4_publico
        except:
            print(f'No se ha encontrado una ip para {instance_id}')

    def set_new_instance(self,instance_id):
        """metodo para poder añadir a la lista de instancias creadas la instancia que acabamos de crear
        """        
        self.new_instance_list.append(instance_id)

    def get_all_instances(self):
        """metodo que devuelve la union de las instancias ya existentes con las nuevas
        """
        lista_combinada=self.existing_instance_list+self.new_instance_list
        print(lista_combinada)
        return lista_combinada
