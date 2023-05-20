import base64
import boto3

class controllerASG:
    def __init__(self) -> None:
        HOST = '[::]:8080'
        my_session = boto3.session.Session()
        self.ec2_client = boto3.client(
            'ec2',
            region_name='us-east-1',
            aws_access_key_id='ASIATQCL7MV5TTD2KD4R',
            aws_session_token='FwoGZXIvYXdzEGkaDDZy+I6+Ti2zC5YhGyLIAT9t7gA1+Dx6fovSC9jz829R6+xl0GlBsXzvnPPQ/o3Wsnjf+Z1bmSKIGchoIirZtDCEwvOiJYXHubPkfqt4EM6pT7ZtHJtSOW9urhHonwfKZPff4/BCOjae+HX43bavx85OwM764aQMy9QupnBC8Cf4NiF7lSRSM2BYfWu11lEHBnVEYKF1PKkbPmzoDrXkb6+8t7Njbu4SL4Nxwo19cePH7sTHY/KQXfPSQ+baXrbB9ccShS8kVN19akyB0wy1e73qi34gMSX0KI6YoKMGMi0X2bKLViptfV0uy+m6VQUY+4pDgIBiZajnU+xCuN1cROUixIris/cyRadTGeU=',
            aws_secret_access_key='yOnCkBBKEXTVWefGBNeCl90dCifzarjEEQfKiH32'
            )

        self.new_instance_list=[]
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
            # Contenido del script que deseas ejecutar
            script_content = '''#!/bin/bash
            git clone https://github.com/mpocampod/proyecto2.git
            sudo apt update -y
            sudo apt install -y python3-pip
            cd Proyecto2
            pip install -r requirements.txt
            cd app
            python3 calculadora.py &
            cd ..
            python3 monitorC.py 

            '''

# Codifica el contenido del script en Base64
            encoded_script = base64.b64encode(script_content.encode('utf-8')).decode('utf-8')
            response=self.ec2_client.run_instances(
                ImageId='ami-07c4c758eb44a38cd',
                InstanceType='t2.micro',
                KeyName='p2',
                MinCount=1,
                MaxCount=1,
                UserData=encoded_script
            )
            instance_id = response['Instances'][0]['InstanceId']
            self.ec2_client.get_waiter('instance_running').wait(InstanceIds=[instance_id])
            # Obtener la dirección IP pública de la instancia
            response = self.ec2_client.describe_instances(InstanceIds=[instance_id])
            ipv4_publico = response['Reservations'][0]['Instances'][0]['PublicIpAddress']

            print(f"La dirección IP pública de la instancia es: {ipv4_publico}")
            self.new_instance_list.append(instance_id)
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
