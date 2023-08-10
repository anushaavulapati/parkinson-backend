from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import h5py
from datetime import datetime
import pandas as pd
import sys


app = Flask(__name__)
CORS(app)

@app.route('/execute-script', methods=['POST'])
def execute_script():
    try:
        fileName = request.files.get('file')
        if fileName:
            f = h5py.File(fileName, 'r')  # name of the file from which data is being extracted
            # use these loops to get the key names
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
                        csv_file_path = f'data_{dset}_new.csv'
                        result = "CSV file(s) saved"
                        return jsonify({"result": result, "csv_file_path": csv_file_path})
                        df.to_csv(f'data_{dset}_new.csv', index=False)  # name of the csv file data has to be saved in
                        print("File converted successfully")
        else:
            result = "Missing or invalid filename"

        return jsonify({"result": result})
    except Exception as e:
        return jsonify({"error": str(e)})
    
            
@app.route('/download-csv/<filename>', methods=['GET'])
def download_csv(filename):
    try:
        # Construct the file path based on the filename
        file_path = filename
        # Serve the file using Flask's send_file function
        return send_file(file_path, as_attachment=True)
    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == '__main__':
    app.run(debug=True)
