from flask import Flask, request, jsonify, send_file, make_response
from flask_cors import CORS, cross_origin
import h5py
from datetime import datetime
import pandas as pd
import sys
import os
import io
import zipfile

app = Flask(__name__)
# cors = CORS(app, resources={r'*':{'origins': '*'}})
# app.config['CORS_HEADERS'] = 'Content-Type'

@app.route('/execute-script', methods=['POST', 'OPTIONS'])
@cross_origin()
def execute_script():
    try:
        fileName = request.files.get('file')
        if fileName:
            f = h5py.File(fileName, 'r')  # name of the file from which data is being extracted
            # use these loops to get the key names
            csv_links = []
            for group in f.keys():
                if group == "Sensors":
                    for dset in f[group]:
                        print("-", type(dset))
                        print("Extracting data................")
                        accel = list(f['Sensors'][dset]['Accelerometer'])
                        gyro = list(f['Sensors'][dset]['Gyroscope'])
                        time = list(f['Sensors'][dset]['Time'])
                        # Time is in string, you will have to convert to timestamps
                        time = [datetime.fromtimestamp(x / 1000000) for x in time]

                        x_accel = []
                        y_accel = []
                        z_accel = []

                        # Extract values from the list of arrays
                        for array in accel:
                            x_accel.append(array[0])
                            y_accel.append(array[1])
                            z_accel.append(array[2])

                        x_gyro = []
                        y_gyro = []
                        z_gyro = []

                        # Extract values from the list of arrays
                        for array in gyro:
                            x_gyro.append(array[0])
                            y_gyro.append(array[1])
                            z_gyro.append(array[2])

                        df = pd.DataFrame({
                            'time': time,
                            'x_accel': x_accel,
                            'y_accel': y_accel,
                            'z_accel': z_accel,
                            'x_gyro': x_gyro,
                            'z_gyro': z_gyro,
                            'y_gyro': y_gyro
                        })
                        csv_filename = f'data_{dset}_new.csv'
                        csv_filepath = os.path.join('.', csv_filename)
                        result = "CSV file(s) saved"
                        df.to_csv(csv_filepath, index=False)
                        print("File converted successfully")
                        csv_links.append(csv_filename)
                        
            return jsonify({"result": "CSV file(s) processed", "csv_data": csv_links})
        else:
            return jsonify({"error": "Missing or invalid filename"})
    except Exception as e:
        return jsonify({"error": str(e)})


@app.route('/get-csv/<filename>', methods=['GET'])
@cross_origin()
def get_csv(filename):
    try:
        csv_filepath = os.path.join(request.args.get('download_path', ''), filename)

        if os.path.exists(csv_filepath):
            with open(csv_filepath, 'r') as csv_file:
                csv_content = csv_file.read()
                return jsonify({"content": csv_content})
        else:
            return jsonify({"error": "File not found"})
    except Exception as e:
        return jsonify({"error": str(e)})       

if __name__ == '__main__':
    app.run(debug=True)
