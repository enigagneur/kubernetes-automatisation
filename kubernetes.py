# Kubernetes

import boto3
import paramiko
import time
import os
#Setting up the aws id, password and region
ACCESS_KEY = os.environ['ACCESS_KEY']
SECRET_KEY = os.environ['SECRET_KEY']
REGION = os.environ['REGION']
print("-------------------------")
print(ACCESS_KEY)
print(SECRET_KEY)
print(REGION)
print("-------------------------")
resource = boto3.resource('ec2',aws_access_key_id=ACCESS_KEY,aws_secret_access_key=SECRET_KEY,region_name=REGION)
client = boto3.client('ec2',aws_access_key_id=ACCESS_KEY,aws_secret_access_key=SECRET_KEY,region_name=REGION)

# This fonction create a key named key in aws and stores
# it's KeyMaterial locally in a file named key.pem
def keyPairToFIle() :
    # create a file to store the key locally
    outfile = open('key.pem','w')

    #Create a key pair
    key_pair = client.delete_key_pair(KeyName='key')
    key_pair = client.create_key_pair(KeyName = 'key')

    # capture the key and store it in a file
    outfile.write((key_pair["KeyMaterial"]))
    outfile.close

# This fonction creates an EC2 instance in AWS
def createInstances():
    # create a new EC2 instance
    resource.create_instances(
        ImageId='ami-0885b1f6bd170450c',
        MinCount=1,
        MaxCount=2,
        InstanceType='t3.small',
        KeyName= 'key',
        SecurityGroups = ['groupe']
    )


# This fonction creates a security group in AWS with
# Ingress IpPermissions of HTTP and SSH
def createSecurityGroup():
    response = client.create_security_group(
        GroupName = "groupe",
        Description = "groupe description",
        VpcId = 'vpc-16f0376b'
    )
    gid = response['GroupId']
    client.authorize_security_group_ingress(
        GroupId = gid,
        IpPermissions = [
            {
                'IpProtocol' : 'tcp',
                'FromPort' : 80,
                'ToPort' : 80,
                'IpRanges' : [{'CidrIp' : '0.0.0.0/0'}]
            },
            {
                'IpProtocol' : 'tcp',
                'FromPort' : 22,
                'ToPort' : 22,
                'IpRanges' : [{'CidrIp' : '0.0.0.0/0'}]
            },
            {
                'IpProtocol' : 'tcp',
                'FromPort' : 6443,
                'ToPort' : 6443,
                'IpRanges' : [{'CidrIp' : '0.0.0.0/0'}]
            },
            {
                'IpProtocol' : 'tcp',
                'FromPort' : 5483,
                'ToPort' : 5483,
                'IpRanges' : [{'CidrIp' : '0.0.0.0/0'}]
            },
            {
                'IpProtocol' : '-1',
                'IpRanges' : [{'CidrIp' : '0.0.0.0/0'}]
            }
        ]
    )

def execute_command_with_ssh(user_name, publicIp, cmd):
    bash_script = open(cmd).read()
    key = paramiko.RSAKey.from_private_key_file('/code/key.pem')
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(publicIp, port = 22, username = user_name, pkey = key)
    stdin, stdout, stderr = ssh.exec_command(bash_script)
    output = stdout.readlines()
    ssh.close()
    print(output[-1])
    return output[-1]

def getPublicIpOfRunningInstances():
    filters = [
        {
            'Name' : 'instance-state-name',
            'Values' : ['running']
        }
    ]
    instances = resource.instances.filter(Filters = filters)
    publicIpOfRunningInstances = []
    for instance in instances:
        publicIpOfRunningInstances.append(instance.public_ip_address)
    return publicIpOfRunningInstances    


#Kubernetes
keyPairToFIle()
createSecurityGroup()
createInstances()
time.sleep(90)
publicIpOfRunningInstances = getPublicIpOfRunningInstances()
masterPublicIp = publicIpOfRunningInstances[0]
slavePublicIp = publicIpOfRunningInstances[1]
cmdMaster = "master_conf.sh"
cmdSlave = "slave_conf.sh"
username = "ubuntu" 
os.system("chmod 400 key.pem")
os.system("scp -o StrictHostKeyChecking=no -i key.pem master_conf.sh ubuntu@ec2-" + masterPublicIp.replace('.','-') + ".compute-1.amazonaws.com:/home/ubuntu/")
joinCmd = "sudo " + execute_command_with_ssh(username,masterPublicIp,cmdMaster)
os.system("echo " + joinCmd.rstrip() + " >> slave_conf.sh")
os.system("scp -o StrictHostKeyChecking=no -i key.pem slave_conf.sh ubuntu@ec2-" + slavePublicIp.replace('.','-') + ".compute-1.amazonaws.com:/home/ubuntu/")
final_output = execute_command_with_ssh(username,slavePublicIp,cmdSlave)

#Spark
os.environ['clusterurl'] = masterPublicIp
cmdSparkMaster = "spark_master.sh"
cmdSparkSlave = "spark_slave.sh"
os.system("scp -o StrictHostKeyChecking=no -i key.pem filesample.txt ubuntu@ec2-" + masterPublicIp.replace('.','-') + ".compute-1.amazonaws.com:/home/ubuntu/")
os.system("scp -o StrictHostKeyChecking=no -i key.pem filesample.txt ubuntu@ec2-" + slavePublicIp.replace('.','-') + ".compute-1.amazonaws.com:/home/ubuntu/")
os.system("scp -o StrictHostKeyChecking=no -i key.pem spark_master.sh ubuntu@ec2-" + masterPublicIp.replace('.','-') + ".compute-1.amazonaws.com:/home/ubuntu/")
os.system("scp -o StrictHostKeyChecking=no -i key.pem spark_slave.sh ubuntu@ec2-" + slavePublicIp.replace('.','-') + ".compute-1.amazonaws.com:/home/ubuntu/")
os.system("scp -o StrictHostKeyChecking=no -i key.pem WordCount.java ubuntu@ec2-" + masterPublicIp.replace('.','-') + ".compute-1.amazonaws.com:/home/ubuntu/")
os.system("scp -o StrictHostKeyChecking=no -i key.pem WordCount.java ubuntu@ec2-" + slavePublicIp.replace('.','-') + ".compute-1.amazonaws.com:/home/ubuntu/")

execute_command_with_ssh(username,slavePublicIp,cmdSparkSlave)
execute_command_with_ssh(username,masterPublicIp,cmdSparkMaster)

#Kube-opex
execute_command_with_ssh(username,masterPublicIp,"kube-opex.sh")