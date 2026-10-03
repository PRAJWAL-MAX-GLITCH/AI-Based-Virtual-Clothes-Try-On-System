# 👔 AI-Based Virtual Clothes Try-On System

[![React](https://img.shields.io/badge/React-18-61DAFB?style=flat-square&logo=react)](https://reactjs.org/)
[![Vite](https://img.shields.io/badge/Vite-8-646CFF?style=flat-square&logo=vite)](https://vitejs.dev/)
[![Flask](https://img.shields.io/badge/Flask-3.x-000000?style=flat-square&logo=flask)](https://flask.palletsprojects.com/)
[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat-square&logo=python)](https://python.org)
[![MongoDB](https://img.shields.io/badge/MongoDB-Atlas%20%2F%20Local-47A248?style=flat-square&logo=mongodb)](https://mongodb.com/)
[![OpenCV](https://img.shields.io/badge/OpenCV-Computer%20Vision-5C3EE8?style=flat-square&logo=opencv)](https://opencv.org/)
[![MediaPipe](https://img.shields.io/badge/MediaPipe-Pose%20Estimation-FF6F00?style=flat-square&logo=google)](https://mediapipe.dev/)
[![JWT](https://img.shields.io/badge/JWT-Authentication-000000?style=flat-square&logo=json-web-tokens)](https://jwt.io/)

A full-stack, AI-powered 2D Virtual Try-On application that allows users to upload their photos, choose or upload clothing items, and visualize realistic 2D virtual try-ons using Computer Vision and Pose Estimation technology.

---

## 🌟 Highlights & Key Features

- **🤖 AI Pose Estimation & Garment Warping**: Uses Google MediaPipe Pose and OpenCV to detect human body keypoints (shoulders, chest, hips), warp garments dynamically to match body shape, and blend seamlessly with skin tones.
- **🎨 Modern Dark Glassmorphism UI**: Built with React 18, Vite 8, Lucide Icons, and custom design tokens for a responsive, interactive user experience.
- **👕 Dual Garment Sources**: Choose garments from a curated catalog or upload custom user clothing items for personal try-ons.
- **📜 Try-On History**: Save, view, preview, and manage generated try-on results with full paginated history tracking.
- **🔒 Enterprise Security Model**:
  - JWT Stateless Bearer Token Authentication
  - PBKDF2/SHA-256 Password Hashing (Werkzeug)
  - Role-Based Access Control (User vs Admin)
  - IDOR & Database Ownership Checks on all queries
  - File Upload validation (mime-type, image corruption, dimension checks, UUID sanitization)
  - Anti-Path Traversal guards on static assets

---

## 🏗 System Architecture

```
                                +-----------------------------------+
                                |    React + Vite Frontend (UI)    |
                                |     http://localhost:3000       |
                                +-----------------+-----------------+
                                                  |
                                             REST API (Axios)
                                                  |
                                                  v
                                +-----------------+-----------------+
                                |    Flask Backend REST Services    |
                                |     http://localhost:5000       |
                                +--------+----------------+---------+
                                         |                |
                       +-----------------+                +-----------------+
                       |                                                    |
                       v                                                    v
     +-----------------+-----------------+                +-----------------+-----------------+
     |       MongoDB Database            |                |      AI Engine Pipeline (CV)      |
     | (Users, Clothing, History Data)   |                | - MediaPipe Pose Keypoints      |
     +-----------------------------------+                | - Garment Segmentation & Warping|
                                                          | - Seamless OpenCV Image Blending|
                                                          +-----------------------------------+
```

---

## 🧠 AI Virtual Try-On Engine Pipeline

```
[ User Image ] -----> ( Pose Detection ) ------+
                             |                 |
                             v                 v
[ Garment Image ] -> ( Garment Processing ) -> ( Landmark Alignment & Warping ) -> ( Image Blending ) -> [ Final Output ]
```

1. **Body Pose Analysis**: MediaPipe extracts key landmark coordinates (shoulders, elbows, waist, torso bounds).
2. **Garment Processing**: Removes background clutter, identifies garment bounding box, and normalizes aspect ratio.
3. **Alignment & Deformation**: Applies affine/perspective transformation and Thin-Plate Spline deformation to align shoulder lines, chest, and torso width.
4. **Compositing & Blending**: Adjusts lighting/skin tones and seamlessly overlays the garment onto the target body region.

---

## 🛠 Tech Stack

### Frontend
- **Framework**: React 18
- **Build Tool**: Vite 8
- **Routing**: React Router DOM v6
- **HTTP Client**: Axios (Centralized API client with interceptors)
- **Icons**: Lucide React

### Backend
- **Framework**: Python Flask (Application Factory Pattern)
- **Database**: MongoDB (via PyMongo)
- **Auth**: PyJWT (JSON Web Tokens)
- **Computer Vision & AI**: OpenCV (`opencv-python`), MediaPipe, Pillow (PIL), NumPy
- **Testing**: Pytest automated test suite

---

## 📁 Repository Directory Structure

```
AI-Based-Virtual-Clothes-Try-On-System/
├── backend/
│   ├── app/
│   │   ├── ai/                      # AI Try-On Engine (Pose, Alignment, Compositing)
│   │   │   ├── body_analysis.py
│   │   │   ├── garment_alignment.py
│   │   │   ├── garment_processing.py
│   │   │   ├── pose_detection.py
│   │   │   └── virtual_tryon.py
│   │   ├── database/                # MongoDB connections and helpers
│   │   ├── models/                  # Data models and schemas
│   │   ├── routes/                  # API endpoints (Auth, Users, Clothing, TryOn, History)
│   │   ├── services/                # Business logic services
│   │   ├── utils/                   # Security, image handling, error handlers
│   │   ├── config.py                # Environment & App Configuration
│   │   └── extensions.py            # Extensions (Flask-CORS, PyMongo)
│   ├── tests/                       # Pytest unit and integration test suite
│   ├── uploads/                     # Storage for uploads and generated results
│   ├── seed_clothing.py             # Script to seed default clothing catalog
│   ├── run.py                       # App entry point
│   ├── requirements.txt             # Python dependencies
│   ├── .env.example                 # Backend environment variable template
│   └── README.md
├── frontend/
│   ├── src/
│   │   ├── assets/                  # Static images and icons
│   │   ├── components/layout/       # Navbar, Sidebar, and UI Layout components
│   │   ├── context/                 # AuthContext (Global User State)
│   │   ├── layouts/                 # Auth & Main Dashboard App Layouts
│   │   ├── pages/                   # Landing, Login, Register, Dashboard, TryOn, Clothing, History, Profile
│   │   ├── services/                # API service wrappers (Axios client)
│   │   ├── utils/                   # Helpers, formatters, and form validators
│   │   ├── App.jsx                  # Root App & Route configurations
│   │   ├── main.jsx                 # Entry point
│   │   └── index.css                # Global Design Tokens & Glassmorphic CSS
│   ├── public/                      # Static assets
│   ├── index.html                   # HTML entry point
│   ├── package.json                 # Frontend dependencies & scripts
│   ├── vite.config.js               # Vite configuration
│   ├── .env.example                 # Frontend environment variable template
│   └── README.md
├── .gitignore                       # Root Git ignore rules
└── README.md                        # Master Project Documentation
```

---

## ⚡ Quick Start Guide

### Prerequisites

- **Node.js**: v18.0 or higher
- **Python**: v3.10 or higher
- **MongoDB**: Running instance locally (`mongodb://localhost:27017`) or MongoDB Atlas URI.

---

### 1. Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create a virtual environment
python -m venv venv

# Activate the virtual environment
# Windows (PowerShell):
.\venv\Scripts\Activate.ps1
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Copy environment variables
cp .env.example .env

# Seed initial clothing catalog
python seed_clothing.py

# Run the Flask backend server
python run.py
```

> Backend will run at: `http://127.0.0.1:5000`

---

### 2. Frontend Setup

```bash
# Navigate to frontend directory (from project root)
cd frontend

# Install node dependencies
npm install

# Copy environment variables
cp .env.example .env

# Start development server
npm run dev
```

> Frontend will run at: `http://localhost:3000`

---

## 📡 API Reference Summary

### 🔐 Auth & User Management
| Method | Endpoint | Description | Access |
|---|---|---|---|
| `POST` | `/api/v1/auth/register` | Register new user account | Public |
| `POST` | `/api/v1/auth/login` | Authenticate & return JWT token | Public |
| `GET` | `/api/v1/auth/me` | Get current user details | Private |
| `GET` | `/api/v1/users/me` | Get profile details | Private |
| `PUT` | `/api/v1/users/me` | Update name / email | Private |
| `PATCH` | `/api/v1/users/me/password` | Update account password | Private |
| `DELETE` | `/api/v1/users/me` | Deactivate user account | Private |

### 👕 Clothing Catalog & Custom Garments
| Method | Endpoint | Description | Access |
|---|---|---|---|
| `GET` | `/api/v1/clothing` | List clothing catalog with filters & pagination | Private |
| `GET` | `/api/v1/clothing/<id>/preview` | Preview catalog clothing item image | Private |
| `POST` | `/api/v1/clothing` | Add clothing item to catalog | Admin |
| `PUT` | `/api/v1/clothing/<id>` | Update catalog item | Admin |
| `DELETE` | `/api/v1/clothing/<id>` | Deactivate catalog item | Admin |
| `POST` | `/api/v1/user-clothing` | Upload custom clothing item | Private |
| `GET` | `/api/v1/user-clothing` | List custom garments uploaded by user | Private |

### 💃 Virtual Try-On & History
| Method | Endpoint | Description | Access |
|---|---|---|---|
| `POST` | `/api/v1/tryon` | Process 2D Virtual Try-On (person photo + clothing) | Private |
| `GET` | `/api/v1/history` | Get paginated try-on history | Private |
| `GET` | `/api/v1/history/<id>` | Get specific try-on record details | Private |
| `GET` | `/api/v1/history/<id>/result` | Fetch generated try-on output image | Private |
| `DELETE` | `/api/v1/history/<id>` | Delete try-on record and output image | Private |

---

## 🧪 Running Automated Tests

Run backend tests using `pytest`:

```bash
cd backend
pytest
```

---

## 🔒 Security Hardening

- **JWT Token Validation**: Tokens are signed with custom `JWT_SECRET_KEY` and validated on protected endpoints.
- **Ownership Verification (IDOR Protection)**: Database queries enforce `user_id == current_user.id`.
- **Upload File Validation**: Only image formats (`JPG`, `PNG`, `WEBP`) with valid pixel structures are accepted; filenames are sanitized to randomly generated UUIDs.
- **Path Traversal Guards**: Static asset resolution verifies normalized paths remain inside the target directory bounds.

---

## 🤝 Contributing

Contributions are welcome! Please open an issue or submit a Pull Request.

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.
