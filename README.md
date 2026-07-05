🧠 AIoT Smart Learning Environment (Edge-Based)

An advanced, decentralized Educational Technology (EdTech) platform that utilizes Artificial Intelligence of Things (AIoT) to scale pedagogical complexity dynamically. Built for early childhood education (Math, Alphabets, Shapes), this system analyzes real-time physical telemetry (device motion) and cognitive load (touch latency) to adjust learning difficulty without relying on high-latency cloud APIs.

✨ Key Features

Zero-Latency Edge Machine Vision: Validates handwritten alphabets and shapes directly on the client tablet using a custom Topological Peak Detection algorithm, eliminating the need for cloud OCR and preserving student privacy.

Cognitive Telemetry Engine: Utilizes Scikit-Learn's SGDRegressor to dynamically scale difficulty (Level 2 to 20) by factoring in task correctness, physical frustration (via accelerometer), and cognitive hesitation (via touch latency).

Dual-Stack Network Architecture: Bypasses OS-level socket restrictions to serve Adhoc HTTPS over both IPv4 and IPv6 simultaneously, ensuring strict mobile browser hardware sensor permissions are met.

Anti-Scribble Heuristics: Uses Bidirectional Axis Reversal Tracking and Bounding Box Density mathematics to prevent users from generating False Positives by scribbling.

Live Teacher Dashboard: A responsive admin panel featuring live SQLite telemetry logs and dynamic Chart.js progress curves.

🛠️ Technology Stack

Backend: Python 3.12, Flask, Scikit-Learn (SGDRegressor), NumPy, pyOpenSSL

Database: SQLite3 (Local Transactional Storage)

Frontend / Edge Node: HTML5 Canvas, Vanilla JavaScript (ES6), Chart.js

Sensors Utilized: DeviceMotion API (Accelerometer), Touch/Pointer Events

🚀 Installation & Setup

To run this project locally on your network:

Clone the repository:

git clone [https://github.com/yourusername/AIoT-Smart-Learning-Edge.git](https://github.com/yourusername/AIoT-Smart-Learning-Edge.git)
cd AIoT-Smart-Learning-Edge


Install the required Python libraries:
It is recommended to use a virtual environment (venv).

pip install Flask flask-cors scikit-learn numpy pyOpenSSL


Start the Dual-Stack Server:

python server.py


Connect your Edge Device (Tablet/Phone):

Make sure your device is on the same Wi-Fi network as the host machine.

Open Chrome/Safari and connect via HTTPS using your laptop's IP address:

IPv4: https://[Your-IPv4-Address]:5000

IPv6: https://[[Your-IPv6-Address]]:5001

Note: Accept the self-signed SSL certificate warning to allow the browser to access the device's physical hardware sensors.

📂 Project Structure

├── server.py               # Main Flask Server, ML Engine, and Dual-Stack threads
├── school.db               # SQLite database (auto-generated on first run)
└── templates/
    ├── index.html          # Edge Node Client (Canvas, Vector Math, Sensor Polling)
    └── admin.html          # Teacher Dashboard (Live Logs, Chart.js Analytics)


🧠 Core Algorithms

This project implements custom geometric and topological heuristics to bypass the need for external OCR APIs:

M vs N Resolution: Evaluates Y-Axis reversals (peaks) and stroke counts to differentiate structurally similar characters (e.g., forcing exactly 3 peaks for 'M').

Ink Density Guard: Rejects inputs where the fill density of the bounding box exceeds 40%, identifying them as chaotic scribbles.

👨‍🎓 Academic Context

This project was developed in partial fulfillment of the requirements for the award of the degree of Master of Computer Application MCA at Chandigarh University.

📝 License

This project is open-source and available for educational purposes.