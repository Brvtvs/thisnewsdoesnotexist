#!/bin/bash

# start instance
aws ec2 run-instances --image-id ami-058af1402f6c2e8fa --key-name grover-tex-mex --security-groups tex-mex-ssh tex-mex-http tex-mex-http-for-docker-images --instance-type g3s.xlarge --placement AvailabilityZone=us-east-2a --count 1 --instance-initiated-shutdown-behavior terminate --user-data file://cloud-init.sh >/dev/null && \
sleep 30 && \
ip=$(aws ec2 describe-instances --filter Name=instance-state-name,Values=running --query 'Reservations[*].Instances[*].PublicIpAddress' | sed 's/[][]//g' | tr -d ' "\t\n\r\f') && \
# send ip to stdoutt & write to file
echo "$ip" && \
echo "$ip" >> running_instance_ip.txt
