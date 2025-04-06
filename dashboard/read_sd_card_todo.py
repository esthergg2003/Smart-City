import serial
import time
import pandas as pd

ser = serial.Serial('COM8', 9600, timeout=1)  # Open serial connection

# Function to request data from SD card via Arduino
def request_data_from_sd_card():
    ser.write(b'read_sd_card\n')  # Send command to Arduino to read SD card
    time.sleep(2)  # Wait for Arduino to process the command and read file
    data = ser.readlines()  # Read all available lines from Arduino
    return data

# Main function
def main():
    data = request_data_from_sd_card()  # Request data from SD card once
    print("Data from SD card:\n", data)
    
    # Initialize lists to store parsed data
    temperatures = []
    humidities = []
    pressures = []
    luminosities = []
    
    # Parse each line
    for line in data:
        line = line.decode().strip()  # Convert bytes to string and remove whitespace
        if line.startswith('Temperature'):
            temperature = float(line.split(':')[1])
            temperatures.append(temperature)
        elif line.startswith('Humidity'):
            humidity = float(line.split(':')[1])
            humidities.append(humidity)
        elif line.startswith('Pressure'):
            pressure = float(line.split(':')[1])
            pressures.append(pressure)
        elif line.startswith('Luminosity'):
            luminosity = int(line.split(':')[1])
            luminosities.append(luminosity)

    # Create a DataFrame
    df = pd.DataFrame({
        'Temperature [°C]': temperatures,
        'Humidity [%]': humidities,
        'Pressure [hPa]': pressures,
        'Luminosity': luminosities
    })

    return df

def append_to_excel(df, filename):
    try:
        existing_df = pd.read_excel(filename)
        combined_df = pd.concat([existing_df, df], ignore_index=True)
        combined_df.to_excel(filename, index=False)
        print("Data appended to existing Excel file.")
    except FileNotFoundError:
        df.to_excel(filename, index=False)
        print("New Excel file created.")

if __name__ == "__main__":
    df = main()
    df['Location'] = 'MIRAMON - ZORROAGA'  # Will be changing for different locations
    append_to_excel(df, 'sensor_data.xlsx')
