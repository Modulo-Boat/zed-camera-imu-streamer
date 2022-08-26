import pyzed.sl as sl
import cv2
import numpy as np
import math
import threading

from metrics import Metrics

## 
# Basic class to handle the timestamp of the different sensors to know if it is a new sensors_data or an old one
class TimestampHandler:
    def __init__(self):
        self.t_imu = sl.Timestamp()
        self.t_baro = sl.Timestamp()
        self.t_mag = sl.Timestamp()

    ##
    # check if the new timestamp is higher than the reference one, and if yes, save the current as reference
    def is_new(self, sensor):
        if (isinstance(sensor, sl.IMUData)):
            new_ = (sensor.timestamp.get_microseconds() > self.t_imu.get_microseconds())
            if new_:
                self.t_imu = sensor.timestamp
            return new_
        elif (isinstance(sensor, sl.MagnetometerData)):
            new_ = (sensor.timestamp.get_microseconds() > self.t_mag.get_microseconds())
            if new_:
                self.t_mag = sensor.timestamp
            return new_
        elif (isinstance(sensor, sl.BarometerData)):
            new_ = (sensor.timestamp.get_microseconds() > self.t_baro.get_microseconds())
            if new_:
                self.t_baro = sensor.timestamp
            return new_


class Camera:
    def __init__(self):
        # Create a Camera object
        self.zed = sl.Camera()

        init_params = sl.InitParameters()
        init_params.depth_mode = sl.DEPTH_MODE.NONE

        # Open the camera
        err = self.zed.open(init_params)
        if err != sl.ERROR_CODE.SUCCESS :
            print(repr(err))
            self.zed.close()
            exit(1)

        # Get camera information sensors_data
        info = self.zed.get_camera_information()

        cam_model = info.camera_model
        if cam_model == sl.MODEL.ZED :
            print("This tutorial only supports ZED-M and ZED2 camera models, ZED does not have additional sensors")
            exit(1)

        # Display camera information (model,S/N, fw version)
        print("Camera Model: " + str(cam_model))
        print("Serial Number: " + str(info.serial_number))
        print("Camera Firmware: " + str(info.camera_configuration.firmware_version))
        print("Sensors Firmware: " + str(info.sensors_configuration.firmware_version))

        # Display sensors parameters (imu,barometer,magnetometer)
        self.printSensorParameters(info.sensors_configuration.accelerometer_parameters) # accelerometer configuration
        self.printSensorParameters(info.sensors_configuration.gyroscope_parameters) # gyroscope configuration
        self.printSensorParameters(info.sensors_configuration.magnetometer_parameters) # magnetometer configuration
        self.printSensorParameters(info.sensors_configuration.barometer_parameters) # barometer configuration
        
        # Used to store the sensors timestamp to know if the sensors_data is a new one or not
        self.ts_handler = TimestampHandler()

        # Get Sensor Data for 5 seconds
        self.sensors_data = sl.SensorsData()

        self.metrics = Metrics()

        self.quaternion_x = None
        self.quaternion_y = None
        self.quaternion_z = None
        self.quaternion_w = None

        self.linear_acceleration_x = None
        self.linear_acceleration_y = None
        self.linear_acceleration_z = None

        self.angular_velocitiy_x = None
        self.angular_velocitiy_y = None
        self.angular_velocitiy_z = None

        self.magnetic_field_x = None
        self.magnetic_field_y = None
        self.magnetic_field_z = None

        self.atmospheric_pressure = None
        fetch_thread = threading.Thread(target=self.fetch_data)
        fetch_thread.start()

    def fetch_data(self):
        
        while True :
            # retrieve the current sensors sensors_data
            # Depending on your Camera model or its firmware, differents sensors are presents.
            # They do not run at the same rate: Therefore, to do not miss samples we iterate as fast as we can and compare timestamp to know when a sensors_data is a new one
            # NOTE: There is no need to acquire images with grab() function. Sensors sensors_data are running in a separated internal capture thread.
            if self.zed.get_sensors_data(self.sensors_data, sl.TIME_REFERENCE.CURRENT) == sl.ERROR_CODE.SUCCESS :
        
                # Check if the data has been updated since the last time
                # IMU is the sensor with the highest rate
                if self.ts_handler.is_new(self.sensors_data.get_imu_data()):
                    
                    # Filtered orientation quaternion
                    quaternion = self.sensors_data.get_imu_data().get_pose().get_orientation().get()
                    self.quaternion_x = quaternion[0]
                    self.quaternion_y = quaternion[1]
                    self.quaternion_z = quaternion[2]
                    self.quaternion_w = quaternion[3]
                    self.metrics.update_quaternion(self.quaternion_x, self.quaternion_y, self.quaternion_z, self.quaternion_w)
                    
                    # linear acceleration
                    linear_acceleration = self.sensors_data.get_imu_data().get_linear_acceleration()
                    self.linear_acceleration_x = linear_acceleration[0]
                    self.linear_acceleration_y = linear_acceleration[1]
                    self.linear_acceleration_z = linear_acceleration[2]
                    self.metrics.update_linear_acceleration(self.linear_acceleration_x, self.linear_acceleration_y, self.linear_acceleration_z)

                    # angular velocities
                    angular_velocity = self.sensors_data.get_imu_data().get_angular_velocity()
                    self.angular_velocity_x = angular_velocity[0]
                    self.angular_velocity_y = angular_velocity[1]
                    self.angular_velocity_z = angular_velocity[2]
                    self.metrics.update_angular_velocity(self.angular_velocity_x, self.angular_velocity_y, self.angular_velocity_z)

                    # Check if Magnetometer data has been updated (not the same frequency than IMU)
                    if self.ts_handler.is_new(self.sensors_data.get_magnetometer_data()):
                        magnetic_field_calibrated = self.sensors_data.get_magnetometer_data().get_magnetic_field_calibrated()
                        self.magnetic_field_x = magnetic_field_calibrated[0]
                        self.magnetic_field_y = magnetic_field_calibrated[1]
                        self.magnetic_field_z = magnetic_field_calibrated[2]
                        self.metrics.update_magnetic_field(self.magnetic_field_x, self.magnetic_field_y, self.magnetic_field_z)
                    
                    # Check if Barometer data has been updated 
                    if self.ts_handler.is_new(self.sensors_data.get_barometer_data()):
                        magnetic_field_calibrated = self.sensors_data.get_barometer_data().pressure
                        self.atmospheric_pressure = magnetic_field_calibrated
                        self.metrics.update_atmospheric_pressure(self.atmospheric_pressure)

            
        self.zed.close()
        return 0

    ##
    #  Function to display sensor parameters
    def printSensorParameters(self, sensor_parameters):
        if sensor_parameters.is_available:
            print("*****************************")
            print("Sensor type: " + str(sensor_parameters.sensor_type))
            print("Max rate: "  + str(sensor_parameters.sampling_rate) + " "  + str(sl.SENSORS_UNIT.HERTZ))
            print("Range: "  + str(sensor_parameters.sensor_range) + " "  + str(sensor_parameters.sensor_unit))
            print("Resolution: " + str(sensor_parameters.resolution) + " "  + str(sensor_parameters.sensor_unit))
            if not math.isnan(sensor_parameters.noise_density):
                print("Noise Density: "  + str(sensor_parameters.noise_density) + " " + str(sensor_parameters.sensor_unit) + "sqrt Hz")
            if not math.isnan(sensor_parameters.random_walk):
                print("Random Walk: "  + str(sensor_parameters.random_walk) + " " + str(sensor_parameters.sensor_unit) + "/ssqrt Hz")


    def stream_data(self):
        runtime = sl.RuntimeParameters()
        mat = sl.Mat()

        while True:
            err = self.zed.grab(runtime)
            if (err == sl.ERROR_CODE.SUCCESS) :
                self.zed.retrieve_image(mat, sl.VIEW.LEFT)
                frame = mat.get_data()
                ret, buffer = cv2.imencode('.jpg', frame)
                frame = buffer.tobytes()
                yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')





def main():
    cam = Camera()
    

if __name__ == "__main__":
    main()
