import prometheus_client

class Metrics:
    def __init__(self, interval_seconds=0):
        self.interval_seconds = interval_seconds

        self.quaternion_x = prometheus_client.Gauge("quaternion_x", "quaternion_x")
        self.quaternion_y = prometheus_client.Gauge("quaternion_y", "quaternion_y")
        self.quaternion_z = prometheus_client.Gauge("quaternion_z", "quaternion_z")
        self.quaternion_w = prometheus_client.Gauge("quaternion_w", "quaternion_w")

        self.linear_acceleration_x = prometheus_client.Gauge("linear_acceleration_x", "linear_acceleration_x")
        self.linear_acceleration_y = prometheus_client.Gauge("linear_acceleration_y", "linear_acceleration_y")
        self.linear_acceleration_z = prometheus_client.Gauge("linear_acceleration_z", "linear_acceleration_z")

        self.angular_velocity_x = prometheus_client.Gauge("angular_velocity_x", "angular_velocity_x")
        self.angular_velocity_y = prometheus_client.Gauge("angular_velocity_y", "angular_velocity_y")
        self.angular_velocity_z = prometheus_client.Gauge("angular_velocity_z", "angular_velocity_z")

        self.magnetic_field_x = prometheus_client.Gauge("magnetic_field_x", "magnetic_field_x")
        self.magnetic_field_y = prometheus_client.Gauge("magnetic_field_y", "magnetic_field_y")
        self.magnetic_field_z = prometheus_client.Gauge("magnetic_field_z", "magnetic_field_z")

        self.atmospheric_pressure = prometheus_client.Gauge("atmospheric_pressure", "atmospheric_pressure")

        prometheus_client.start_http_server(9090)

    def update_quaternion(self, x, y, z, w):
        self.quaternion_x.set(x)
        self.quaternion_y.set(y)
        self.quaternion_z.set(z)
        self.quaternion_w.set(w)
        

    def update_linear_acceleration(self, x, y, z):
        self.linear_acceleration_x.set(x)
        self.linear_acceleration_y.set(y)
        self.linear_acceleration_z.set(z)

    def update_angular_velocity(self, x, y, z):
        self.angular_velocity_x.set(x)
        self.angular_velocity_y.set(y)
        self.angular_velocity_z.set(z)

    def update_magnetic_field(self, x, y, z):
        self.magnetic_field_x.set(x)
        self.magnetic_field_y.set(y)
        self.magnetic_field_z.set(z)

    def update_atmospheric_pressure(self, number):
        self.atmospheric_pressure.set(number)

