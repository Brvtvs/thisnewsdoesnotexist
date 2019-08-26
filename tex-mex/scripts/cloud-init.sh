#!/bin/bash -ex

# log output in easy to find places
exec > >(tee /var/log/user-data.log|logger -t user-data -s 2>/dev/console) 2>&1
service docker status
# start docker
service docker start
# add our user to docker
usermod -a -G docker ec2-user
# run our container with nvidia-docker for gpu support
nvidia-docker run -d -it --name tex-mex --runtime=nvidia -p 8000:8000 --mount type=bind,source=/home/ec2-user/mega,target=/tex-mex/grover/models/mega 244523355081.dkr.ecr.us-east-2.amazonaws.com/tex-mex-grover:latest
# self destruct
echo "sudo shutdown -h" | at now + 55 min
