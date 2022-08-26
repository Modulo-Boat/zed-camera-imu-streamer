import flask

from camera import Camera

app = flask.Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True
camera = Camera()

@app.route('/')
def index():
    return flask.render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return flask.Response(camera.stream_data(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/orientation', methods=['GET'])
def orientation():
    msg = {
        'x': camera.quaternion_x,
        'y': camera.quaternion_y,
        'z': camera.quaternion_z,
        'w': camera.quaternion_w
    }
    return flask.jsonify(msg)

@app.route('/accelaration', methods=['GET'])
def accelaration():
    msg = {
        'x': camera.linear_acceleration_x,
        'y': camera.linear_acceleration_y,
        'z': camera.linear_acceleration_z
    }
    return flask.jsonify(msg)

@app.route('/angular_velocity', methods=['GET'])
def angular_velocity():
    msg = {
        'x': camera.angular_velocitiy_x,
        'y': camera.angular_velocitiy_y,
        'z': camera.angular_velocitiy_z,
    }
    return flask.jsonify(msg)

@app.route('/magnetic_field', methods=['GET'])
def magnetic_field():
    msg = {
        'x': camera.magnetic_field_x,
        'y': camera.magnetic_field_y,
        'z': camera.magnetic_field_z
    }
    return flask.jsonify(msg)


@app.route('/atmospheric_pressure', methods=['GET'])
def atmospheric_pressure():
    msg = {
        'value': camera.atmospheric_pressure
    }
    return flask.jsonify(msg)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)