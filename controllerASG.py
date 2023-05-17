import boto3

class controllerASG:
    def __init__(self) -> None:
        self.ec2 = boto3.resource(
            'ec2', region_name='tu_region', 
            aws_access_key_id='tu_access_key', 
            aws_secret_access_key='tu_secret_access_key')
        self.new_intance_list=[]
        self.existing_instance_list=[]
        self.min_instances=2
        self.max_instances=5

    def create_intance(self):
        """Este método se encargaría de crear una nueva instancia de EC2 basada en la imagen AMI personalizada que
        se ha definido previamente. Debería tomar como parámetros la configuración de la instancia
        """        
        self.get_my_instances()
        try:
            print('Creando Instancia en EC2 ...')
            self.ec2.run_instances(
                ImageId='',
                InstanceType='t2.micro',
                KeyName='',
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
            self.ec2.terminate_instances(InstanceIds=[instance_id])
            self.new_intance_list.remove(instance_id)
            print(f"se ha terminado la instancia con id: {instance_id}")
            print(f'instancias restantes: {str(self.new_intance_list)}')
            return True
        except Exception as e:
            print(e)
            return False
        
    def describe_my_instances(self):
        """Este método se encargaría de obtener información sobre las instancias de EC2 que se están ejecutando
        actualmente en la cuenta de AWS. Debería devolver información como el ID de la instancia, la dirección IP,
        el estado de la instancia, etc.
        """        
        ans=self.ec2.describe_instances()
        for reservation in ans['Reservations']:
            for instance in reservation['Instances']:
                #aca podemos poner los datos que querramos ver
             #   https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ec2/client/describe_instances.html#describe-instances
                pass 
         
    def check_min_instances(self):
        #creo que esto debe de ir en el monitorS
        """metodo se encargará de revisar el numero de instancias que haya, en caso tal de que no se cumpla, deberá crear una instancia nueva
        """        
        try:
            while len(self.instance_list)<self.min_instances: 
                self.create_intance()
        except Exception as e:
            print(e)
    
    def get_my_instances(self):
        """metodo para obtener las instancias que ya se tienen creadas y no permitir que se creen duplicadas
        """        
        ans=self.ec2.describe_instances()
        try:
            for reservation in ans['Reservations']:
                for instance in reservation['Instances']:
                    if instance['InstanceId'] not in self.existing_instance_list:
                        self.new_intance_list.append(instance['InstanceId'])
        except Exception as e:
            print(e)      

    def set_new_instance(self):
        """metodo para poder añadir a la lista de instancias creadas la instancia que acabamos de crear
        """        
        ans=self.ec2.describe_instances()
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
        lista_combinada=self.existing_instance_list+self.new_intance_list
        print(lista_combinada)
        return lista_combinada


