import json
import threading

import bottle


class MeasurementServer(bottle.Bottle):

    def __init__(self, measurement_dao):
        super(MeasurementServer, self).__init__()
        self.measurement_dao = measurement_dao
        self.route('/measurements', callback=self.measurements)
        self.route('/asOf', callback=self.measurement_dao.get_as_of)
        self.route('/static/<filename>', callback=self.server_static)

    def measurements(self):
        window_size = int(bottle.request.query.window_size if hasattr(bottle.request.query, 'window_size') else 1)
        windows = int(bottle.request.query.windows if hasattr(bottle.request.query, 'windows') else 1000)
        bottle.response.content_type = "application/json"
        return json.dumps(
            map(lambda measurement: measurement.__dict__, self.measurement_dao.get_measurements(window_size, windows))
        )

    @staticmethod
    def server_static(filename):
        return bottle.static_file(filename, root='web/')

    def gogo(self):
        t = threading.Thread(target=lambda: self.run(host='0.0.0.0', port=8080))
        t.start()
