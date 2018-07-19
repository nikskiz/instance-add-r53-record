# README #

### What is this repository for? ###

* Lambda function written in python3 which updates route53 zone based on instance tags.
* The purpose is to target dynamic private instances, where the private IP will be updated in a private Route53 zone.
* The end result will create a FQDN tag for the instance and the record in route53.
* Version 1 

### How do I get set up? ###

#### Summary of set up ####
* Python script will utilize the following modules
      * boto3 - Used for querying the AWS API
      * Json, sys - Only used for manual execution via cli not AWS Lambda
      * re - Regex in python
#### Configuration ####
* Create lambda using Python Version 3.6
* In AWS setup a Lambda function, ensure the following permissions:
    * EC2 - Describe permissions
    * Cloudwatch - create groups and streams. Put logs
    * Route53 Update record
* Create a cloudwatch rule to trigger the event when a instance is in a pending state

* Ensure instances are tagged with `Hosted_Zone: Value` and `DNS_Name: Value`
    * DNS_Name - The name of the dns record i.e docker-cluster-1
    * Hosted_Zone - The Zone Name in route53 - i.e private.company.com
* create a test with the following json. You can replace the SnapId's with your own.
`
{
  "version": "0",
  "id": "f74e985d-c3ff-415d-b5fa-d3614c5e3434",
  "detail-type": "EC2 Instance State-change Notification",
  "source": "aws.ec2",
  "account": "123456789012",
  "time": "2015-11-11T21:36:48Z",
  "region": "us-east-1",
  "resources": [
    "arn:aws:ec2:us-east-1:123456789012:instance/i-0c3d1f4a834d93691"
  ],
  "detail": {
    "instance-id": "i-123456789",
    "state": "pending"
  }
}
`
* Configure lambda timeout 30 Seconds
#### Dependencies ####
* N/A
* How to run tests
  * Tests can be performed via linux CLI. Ensure the modules exampled above are installed. To run a test perform the following. `cat example_event.json| python3 main.py`
* Deployment instructions
  * Ensure tests are performed to the develop branch first, or checkout master in your own branch. Once tested, merge to master. Please ensure to create tags with each release to master.

### Who do I talk to? ###

* Repo owner or admin
* Nikola Sepentulevski
