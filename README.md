# Smart City Safety Assessment using MIOTY Sensors

This project was developed as part of a university course in collaboration with the [City Science MIT Lab](https://www.media.mit.edu/groups/city-science/overview/). The aim was to explore how technology can contribute to the transformation of San Sebastian into a smart city by analyzing environmental conditions and their potential relationship with public safety across different neighborhoods.

---

##  Objective

The project began with understanding the functionality of the MIOTY board, a device equipped with environmental sensors. Our group investigated how these sensors could be used to address the question: **How safe is San Sebastian really?**

Our final proposal involved collecting nighttime illumination, temperature, and humidity data across the city, and analyzing this information in correlation with crime rates and demographic factors to identify potential safety hazards.

---

##  Hardware Setup

We used the MIOTY board, which includes built-in sensors for: Light (illumination), Temperature and Humidity. To enable efficient data logging, we integrated an SD card reader. Data was collected and stored using:
- Arduino IDE for programming.
- A portable power bank for mobility during data collection.
- A switch to toggle between "data recording mode" and "data transfer mode".

---

##  Data Collection

Data was gathered by walking through 49.33 km of San Sebastian's neighborhoods, primarily between 10 PM and 12 AM, to ensure consistency in environmental conditions. We saved our walking routes using apps like Strava and Just Draw It. After each session, we transferred the sensor data from the SD card to a computer via the Arduino IDE, and then processed it using Spyder (Python) for later integration into a dashboard.

---

##  Dashboard Overview

We built an interactive dashboard using Plotly Dash, divided into three main tabs:

### 1. Data Visualization
- Pie charts and bar graphs with range sliders.
- Neighborhood-specific filtering via dropdown menus.

### 2. Analysis
- Cross-referenced sensor data with: Crime rates, Income levels, Population density and Education levels.
- Analyzed correlations between illumination and temperature.

### 3. Interactive Map
- City map divided by neighborhood. explicar breve el color coding
- Displays average environmental values (illumination, humidity, temperature).

##  Repository Contents

- `/arduino`: Arduino scripts for MIOTY board configuration.
- `/data`: Sample datasets and demographic information.
- `/dashboard`: Python scripts for the interactive dashboard.

---
