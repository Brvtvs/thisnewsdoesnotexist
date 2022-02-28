#!/bin/bash

# start instance
aws ec2 run-instances --image-id ami-097b5b85aa90c2802 --key-name grover-tex-mex --security-groups tex-mex-ssh tex-mex-http tex-mex-http-for-docker-images --instance-type g3s.xlarge --count 1 --instance-initiated-shutdown-behavior terminate --user-data file://cloud-init.sh >/dev/null && \
sleep 30 && \
ip=$(aws ec2 describe-instances --filter Name=instance-state-name,Values=running --query 'Reservations[*].Instances[*].PublicIpAddress' | sed 's/[][]//g' | tr -d ' "\t\n\r\f') && \
# send ip to stdoutt & write to file
echo "$ip" && \
echo "$ip" > running_instance_ip.txt
