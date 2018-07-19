import boto3
import re
import json, sys # Only used for manual testing

class EC2Instance:
    def __init__(self, InstanceId, DNSName, HostedZone, PrivateIpAddress):
        self.InstanceId = InstanceId
        self.DNSName = DNSName
        self.HostedZone = HostedZone
        self.PrivateIpAddress = PrivateIpAddress

def GetZoneId(hosted_zone):
    client = boto3.client('route53')
    try:
        zoneId = client.list_hosted_zones_by_name(DNSName=hosted_zone,MaxItems='1')
        for zone in zoneId["HostedZones"]:
            zid = zone['Id']
            break
        # Regex remove /hostedzone/ string in the return of zid
        zid = re.sub('(/.*/)', '', zid)
    except Exception as e:
        print(e)
    else:
        return zid
def UpdateZone(r53,zoneId,DNSName,HostedZone,PrivateIpAddress,aws_request_id):
    try:
        response = r53.change_resource_record_sets(
            HostedZoneId=zoneId,
            ChangeBatch={
                'Comment': 'LambdaFunction Request ID: '+aws_request_id ,
                'Changes': [
                    {
                        'Action': 'UPSERT',
                        'ResourceRecordSet': {
                            'Name': DNSName+'.'+HostedZone,
                            'Type': 'A',
                            'SetIdentifier': 'LambdaFunction',
                            'Region': 'ap-southeast-2',
                            "TTL": 300,
                            'ResourceRecords': [
                                {
                                    'Value': PrivateIpAddress
                                }
                            ]
                        }
                    },
                ]
            }
        )
    except Exception as e:
        print("Unexpected error: %s" % e)
    else:
        print("DNS Update Complete")
def CreateInstnaceTag(ec2,InstanceId,PrivateIpAddress):
    try:
        # print(PrivateIpAddress)
        ec2.create_tags(Resources=[InstanceId], Tags=[{'Key':'Private_IP_Address', 'Value':PrivateIpAddress}])
    except Exception as e:
        print("Unexpected error: %s" % e)
    else:
        print("Tag Update Complete")

def lambda_handler(context,event):
    instanceId = context['detail']['instance-id']
    # print(instanceId)
    # Define Filters
    filters=[
        {
            'Name': 'tag:Hosted_Zone',
            'Values': [
                '*'
            ]
        },
        {
            'Name': 'tag:DNS_Name',
            'Values': [
                '*'
            ]
        },
        {
            'Name': 'instance-id',
            'Values': [
                instanceId
            ]
        }
    ]
    # Define EC2 objects
    ec2 = boto3.resource('ec2', region_name='ap-southeast-2')
    # ec2_list = ec2.instances.all()
    ec2_list = ec2.instances.filter(Filters=filters)


    # Define Route53 object
    r53 = boto3.client('route53')

    # Define List from EC2Instance Class
    Ec2_Instance = []

    # Define Variables
    DNS_Name = ''
    Hosted_Zone = ''

    for instance in ec2_list:
        #print(instance.instance_id)
        if instance.tags:
            for tag in instance.tags:
                if tag['Key'] == "Hosted_Zone":
                    Hosted_Zone = (tag['Value'])
                elif  tag['Key'] == "DNS_Name":
                    DNS_Name =  (tag['Value'])
            Ec2_Instance.append(EC2Instance(instance.instance_id,DNS_Name,Hosted_Zone,instance.private_ip_address))
        else:
            print("Instance ID: %s has no tags" % (instance.instance_id))
            continue

    # Update Zone
    for instance in Ec2_Instance:
        if instance.InstanceId and instance.DNSName and instance.HostedZone:
            # Get The ZoneID
            zoneId = GetZoneId(instance.HostedZone)
            print("========= UPDATING ========\nInstane ID: %s \nDNS Name: %s \nHosted Zone: %s \nZone ID: %s \nPrivate IP: %s" % (instance.InstanceId,instance.DNSName,instance.HostedZone,zoneId,instance.PrivateIpAddress))
            # Update The Zone Record
            UpdateZone(r53,zoneId,instance.DNSName,instance.HostedZone,instance.PrivateIpAddress,event.aws_request_id)
            # Create Tag with the PrivateIpAddress
            CreateInstnaceTag(ec2,instance.InstanceId,instance.PrivateIpAddress)

if __name__ == '__main__':
    context = json.load( sys.stdin )
    lambda_handler(context)
