#!/bin/bash

# start instance
aws ec2 run-instances --image-id ami-095dfab8d6fbf28d9 --key-name grover-tex-mex --security-groups tex-mex-ssh tex-mex-http tex-mex-http-for-docker-images --instance-type g3s.xlarge --placement AvailabilityZone=us-east-2a --block-device-mappings DeviceName=/dev/sdh,Ebs={VolumeSize=100} --count 1 --instance-initiated-shutdown-behavior terminate --user-data file://cloud-init.sh

echo "waiting 30 seconds for instance to start..."
sleep 30

ip=$(aws ec2 describe-instances --filter Name=instance-state-name,Values=running --query 'Reservations[*].Instances[*].PublicIpAddress' | sed 's/[][]//g' | tr -d ' "\t\n\r\f')

echo "got ip $ip, writing to running_instance_ip.txt"
echo "$ip" > running_instance_ip.txt
