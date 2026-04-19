import json_numpy
import numpy as np
from flask import Flask, request, jsonify

# Patch json module to handle numpy arrays seamlessly
json_numpy.patch()

app = Flask(__name__)

@app.route('/act', methods=['POST'])
def act():
    try:
        # 1. Parse the incoming JSON payload
        payload = request.get_json()
        if not payload or "encoded" not in payload:
            return jsonify({"error": "Invalid payload format. Missing 'encoded' key."}), 400

        # 2. Decode the client's observation data (for testing/verification)
        decoded_data = json_numpy.loads(payload["encoded"])
        
        print("\n--- 📥 Received Observation ---")
        print(f"Instruction : {decoded_data.get('instruction')}")
        print(f"Image shape : {decoded_data.get('full_image').shape}")
        print(f"Robot state : {decoded_data.get('state')}")

        # 3. Generate mock actions (e.g., returning a trajectory of 5 steps)
        num_steps = 10
        
        # Generate 6 joint angles (using radians between -pi and pi as an example)
        joint_angles = np.random.uniform(-np.pi, np.pi, size=(num_steps, 6))
        
        # Generate 1 gripper value (between 0 and 100)
        gripper_values = np.random.uniform(0, 100, size=(num_steps, 1))
        
        # Horizontally stack them to create an (N, 7) array
        actions = np.hstack((joint_angles, gripper_values)).astype(np.float32)

        print("--- 📤 Sending Mock Actions ---")
        print(f"Actions shape : {actions.shape}")
        print(f"First action  : {actions[0]}")

        # 4. Encode the numpy array back to a string 
        encoded_actions = json_numpy.dumps(actions)
        
        # Return as a JSON string so resp.json() in your client parses it correctly 
        # into a string that json_numpy.loads() can then process.
        return jsonify(encoded_actions)

    except Exception as e:
        print(f"❌ Server Error: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    print("🚀 Starting Mock OpenVLA Server on http://0.0.0.0:8777...")
    # Host 0.0.0.0 allows connections if your client ('cerulean') is on another machine
    app.run(host='0.0.0.0', port=8777)
