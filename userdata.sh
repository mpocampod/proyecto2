git clone https://github.com/mpocampod/proyecto2.git
sudo apt update -y
sudo apt install -y python3-pip
cd proyecto2
pip install -r requirements.txt
cd app
python3 calculadora.py &
cd ..
python3 monitorC.py 
