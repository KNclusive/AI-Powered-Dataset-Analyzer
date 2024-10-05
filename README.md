# AI-Powered Dataset Analyzer

## Introduction

The AI-Powered Dataset Analyzer is a web application that allows users to upload and analyze survey datasets using an AI-powered Retrieval-Augmented Generation (RAG) pipeline. The application processes datasets in-memory during user sessions, ensuring privacy and efficiency.

## Features

- Upload and preprocess survey datasets containing numerical and demographic data.
- Generate AI-driven insights based on user queries.
- Display insights along with source context.
- Handles multiple users simultaneously without storing datasets persistently.
- User-friendly frontend interface built with React.

## Technologies

- **Backend**: Python, FastAPI
- **Frontend**: React
- **AI Models**: OpenAI GPT-3/GPT-4
- **Data Processing**: Pandas, NumPy
- **In-Memory Data Store**: Redis
- **Deployment**: Docker, Docker Compose

## Project Structure
```bash
AI-Powered-Dataset-Analyzer/
├── backend/
│ ├── app/
│ │ ├── main.py
│ │ ├── routers/
│ │ ├── models/
│ │ └── services/
│ ├── database.py
│ ├── **init**.py
│ ├── requirements.txt
│ └── Dockerfile
├── frontend/
│ ├── lib/
│ ├── main.dart
│ ├── screens/
│ ├── widgets/
│ ├── models/
│ └── pubspec.yaml
├── Dockerfile
├── docs/
├── docker-compose.yml
├── data/
└── README.md
```

## Setup Instructions

- [Backend Setup](#backend-setup)
- [Frontend Setup](#frontend-setup)
- [Deployment](#deployment)

## License

MIT License

## Backend Setup

1. Navigate to the `backend` directory.

   ```bash
   cd backend
   ```

2. Create virtual environment to install all dependencies.

   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. Install requirements.txt file in your virtual environment.

   ```bash
   pip install -r requirements.txt
   ```

## Frontend Setup

1. Navigate to the `frontend` directory.
   ```bash
   cd frontend
   ```
2. Install nmp third-part dependencies and start.
   ```bash
   npm install
   npm start
   ```

## Deployment Setup

Instructions on how to deploy the application using docker are provided in docs/DEPLOYMENT.md
