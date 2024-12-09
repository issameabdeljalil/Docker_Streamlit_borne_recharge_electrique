# App_API_Paris

This repository contains the code for deploying and using **App_API_Paris**, which integrates an API-based data collection and a streamlit app.

### Step 1: Set Up Python Virtual Environment and Install Dependencies
To set up the Python environment and install the required packages, run the following command:

```bash
bash install.sh
```

This script will:

1. Set up a Python virtual environment (`.venv`).
2. Install the required Python packages specified in `requirements.txt`.

### Step 2: Launch Data Collection Service and the Application
After setting up the environment, you can launch the data collection service along with the streamlit application by running:

```bash
bash bin/run.sh
```

This command will start all necessary services, including the data collection pipeline and the application server.

## Requirements
- **Python**: Version 3.10+