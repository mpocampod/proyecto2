import boto3

class controllerASG:
    def __init__(self) -> None:
        HOST = '[::]:8080'
        my_session = boto3.session.Session()
        """
        self.ec2 = boto3.resource(
            'ec2', 
            region_name='us-east-1',
            aws_access_key_id='tu_access_key',
            aws_secret_access_key='tu_secret_access_key')
        """
        self.ec2_client = boto3.client(
            'ec2',
            region_name='us-east-1',
            aws_access_key_id='ASIATQCL7MV54F26J4HR',
            aws_session_token='FwoGZXIvYXdzEGEaDELCxrBTc3q7dDWtRyLIAYlYkZQGy7R05SBUlVn5pVflrx4iwUOB+mLImlCIspfkIjikKpwlhI0zXkR85XzSMRSSjJDAOlCECW9P6PUySmuSpZ5B6L+eY/p6xt0tHqWOanRkGFCQlDDrc6w/oEemudbLKf5mVtet8K/LjifM2t+ZzZDlPlmoSYYtKtN8cyyPdaAE2Pp96SmdE3xDlrLYlZEiMSzaG8/N2azVSXEsDzOTOXs8PctPsgtaCVsIdSSqpP0CNY9j1CT4kmQz7z7JA8F5v1tVdg6lKNu3nqMGMi27Ln7F7Zf6FxUw5DIPdc4CKF9epJIW9LgvrgvoNH9OPyGkyLjAJ3vB9ngABVo=',
            aws_secret_access_key='UsaCq+fYYl7DtvAkos3xqYTYFPz647i8/qDUPkA/'
            )

        self.new_instance_list=[]
        self.existing_instance_list=[]
        self.min_instances=2
        self.max_instances=5

    def create_instance(self):
        """Este método se encargaría de crear una nueva instancia de EC2 basada en la imagen AMI personalizada que
        se ha definido previamente. Debería tomar como parámetros la configuración de la instancia
        """        
        self.get_my_instances()
        try:
            print('Creando Instancia en EC2 ...')
            self.ec2_client.run_instances(
                ImageId='ami-013d6ae76556595f0',
                InstanceType='t2.micro',
                KeyName='p2',
                MinCount=1,
                MaxCount=1      
            )
        except Exception as e:
            print(e)
        self.set_new_instance()

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
        except Exception as e:
            print(e)
    
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

    def set_new_instance(self):
        """metodo para poder añadir a la lista de instancias creadas la instancia que acabamos de crear
        """        
        ans=self.ec2_client.describe_instances()
        try:
            for reservation in ans['Reservations']:
                for instance in reservation['Instances']:
                    if instance['InstanceId'] not in self.existing_instance_list:
                        self.existing_instance_list.append(instance['InstanceId'])
        except Exception as e:
            print(e) 

    def get_all_instances(self):
        """metodo que devuelve la union de las instancias ya existentes con las nuevas
        """
        lista_combinada=self.existing_instance_list+self.new_instance_list
        print(lista_combinada)
        return lista_combinada