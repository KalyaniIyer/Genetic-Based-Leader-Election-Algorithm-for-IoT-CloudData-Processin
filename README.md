# Genetic-Based-Leader-Election-Algorithm-for-IoT-CloudData-Processing

This project implements a Genetic Algorithm-based leader election system for optimizing task delegation in IoT-cloud environments. 
The simulator emulates distributed IoT devices and cloud nodes, employing evolutionary strategies—including chromosome initialization, fitness evaluation, crossover, mutation, and selection—to dynamically elect a leader.

An interactive Streamlit dashboard provides real-time visualization of IoT device behavior and leader selection dynamics.

Research Basis:
 This implementation is based on the paper-

"A Genetic Based Leader Election Algorithm for IoT Cloud Data Processing"
by Samira Kanwal, Zeshan Iqbal, Aun Irtaza, Rashid Ali, and Kamran Siddique.

Setup & Execution:
 To run the simulator in VS Code or a local environment-

python -m venv venv

pip install streamlit

python -m streamlit run iot_dashboard.py
