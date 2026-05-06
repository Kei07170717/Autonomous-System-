import json_numpy
import numpy as np
from flask import Flask, request, jsonify

# Patch json module to handle numpy arrays seamlessly
json_numpy.patch()

app = Flask(__name__)

# ==========================================
# Action Generation Strategies
# ==========================================

def strategy_zero_delta(current_state, num_steps):
    """
    Safe strategy: Produces strictly zero deltas. 
    The robot will not move.
    """
    # 6 joints + 1 gripper = 8 action dimensions
    return np.zeros((num_steps, 8), dtype=np.float32)


def strategy_random_wiggle(current_state, num_steps):
    """
    Produces tiny random delta movements.
    """
    # Delta for 7 joints: bounded between -0.01 and 0.01 radians
    joint_deltas = np.random.uniform(-0.01, 0.01, size=(num_steps, 7))
    
    # Delta for 1 gripper: bounded between -1 and 1
    gripper_deltas = np.random.uniform(-1.0, 1.0, size=(num_steps, 1))
    
    # Combine joints and gripper into shape (num_steps, 7)
    actions = np.hstack((joint_deltas, gripper_deltas))
    return actions.astype(np.float32)


# Map string names to the function objects so they can be easily swapped
ACTION_STRATEGIES = {
    "zero_delta": strategy_zero_delta,
    "random_wiggle": strategy_random_wiggle
}

# CHANGE THIS VARIABLE TO SWAP STRATEGIES
CURRENT_STRATEGY = "zero_delta" 

# ==========================================
# Server Endpoints
# ==========================================

@app.route('/act', methods=['POST'])
def act():
    try:
        # 1. Parse the incoming JSON payload
        payload = request.get_json()
        if not payload or "encoded" not in payload:
            return jsonify({"error": "Invalid payload format. Missing 'encoded' key."}), 400

        # 2. Decode the client's observation data
        decoded_data = json_numpy.loads(payload["encoded"])
        
        print("\n--- 📥 Received Observation ---")
        print(f"Instruction : {decoded_data.get('instruction')}")
        print(f"Image shape : {decoded_data.get('full_image').shape}")
        
        current_state = decoded_data.get('state')
        print(f"Robot state : {current_state}")

        # 3. Generate Actions using the active strategy
        num_steps = 10
        strategy_func = ACTION_STRATEGIES.get(CURRENT_STRATEGY)
        
        if not strategy_func:
            raise ValueError(f"Strategy '{CURRENT_STRATEGY}' not found.")
            
        actions = strategy_func(current_state, num_steps)

        print("--- 📤 Sending Mock DELTA Actions ---")
        print(f"Active Strategy : {CURRENT_STRATEGY}")
        print(f"Actions shape   : {actions.shape}")
        print(f"First action    : {actions[0]}")

        # 4. Encode the numpy array back to a string 
        encoded_actions = json_numpy.dumps(actions)
        
        # Return as a JSON string
        return jsonify(encoded_actions)

    except Exception as e:
        print(f"❌ Server Error: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    print(f"🚀 Starting Mock Server on http://0.0.0.0:8777...")
    print(f"🔒 Active Action Strategy: {CURRENT_STRATEGY}")
    # Host 0.0.0.0 allows connections if your client is on another machine
    app.run(host='0.0.0.0', port=8777)
