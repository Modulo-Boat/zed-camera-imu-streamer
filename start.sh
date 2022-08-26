docker run --name=zed-camera-imu --restart=unless-stopped --gpus=all -it -d --privileged -p=30004:5000 -p=30005:9090 zed-camera-imu
