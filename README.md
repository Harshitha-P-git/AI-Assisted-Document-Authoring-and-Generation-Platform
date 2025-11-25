# AI-Assisted Document Authoring and Generation Platform

A full-stack platform for AI-assisted document creation and generation, supporting Word documents (.docx) and PowerPoint presentations (.pptx). Built with FastAPI backend and React frontend, featuring Google Gemini and OpenAI API integration for intelligent content generation.

## ✨ Features

- **User Authentication**: Secure JWT-based authentication with registration, login, and token management
- **Project Management**: Create, view, update, and delete projects
- **Document Configuration**: 
  - Word: Build document outlines with section titles
  - PowerPoint: Build slide titles for presentations
- **AI Content Generation**: 
  - Context-aware content generation using Google Gemini API or OpenAI API
  - Section-wise generation for Word documents
  - Slide-wise generation for PowerPoint presentations
  - Mock LLM mode for offline development
- **Refinement System**:
  - Per-section/slide refinement with AI assistance
  - Custom prompts for content refinement
  - Like/dislike feedback system
  - Comments and notes
  - Revision history tracking
- **Export Functionality**: 
  - Export Word documents (.docx) with proper formatting
  - Export PowerPoint presentations (.pptx) with formatted slides
- **Storage**: Local file storage with optional AWS S3 integration
- **Rate Limiting**: Configurable rate limiting for LLM API calls
- **Error Handling**: Comprehensive error handling and logging
- **Testing**: Unit tests for backend routes and services
- **Docker Support**: Full Docker and docker-compose setup

## 🛠️ Tech Stack

### Backend
- **FastAPI**: Modern Python web framework
- **SQLAlchemy**: ORM for database operations
- **Alembic**: Database migrations
- **JWT**: Authentication tokens
- **python-docx**: Word document generation
- **python-pptx**: PowerPoint presentation generation
- **Google Gemini API**: AI content generation
- **OpenAI API**: Alternative AI content generation
- **Pytest**: Testing framework

### Frontend
- **React**: UI framework
- **React Router**: Routing
- **Zustand**: State management
- **Axios**: HTTP client
- **CSS3**: Modern SaaS styling

---

## 📦 Installation Steps

### Prerequisites

- **Python 3.11+** (Python 3.12 recommended, Python 3.14 has compatibility issues)
- **Node.js 18+** and npm
- **Git** (for cloning the repository)
- **PostgreSQL** (optional, SQLite used by default)

### Step 1: Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
cd YOUR_REPO_NAME
```

### Step 2: Backend Setup

1. **Navigate to backend directory:**
   ```bash
   cd backend
   ```

2. **Create a virtual environment:**
   ```bash
   # Windows
   python -m venv venv
   venv\Scripts\activate

   # macOS/Linux
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Upgrade pip:**
   ```bash
   python.exe -m pip install --upgrade pip
   ```

4. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

5. **Create `.env` file:**
   ```bash
   # Copy example file (if exists) or create new one
   # See Environment Variables section below
   ```

6. **Initialize database:**
   ```bash
   # Database will be created automatically on first run
   # Or use Alembic for migrations:
   alembic upgrade head
   ```

### Step 3: Frontend Setup

1. **Navigate to frontend directory:**
   ```bash
   cd ../frontend
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Create `.env` file:**
   ```bash
   # Create .env file with:
   REACT_APP_API_URL=http://localhost:8000/api/v1
   ```

---

## 🔐 Environment Variables

### Backend Environment Variables (`.env` in `backend/`)

Create a `.env` file in the `backend/` directory with the following variables:

```env
# Security (REQUIRED)
SECRET_KEY=your-generated-secret-key-here

# Database (REQUIRED)
DATABASE_URL=sqlite:///./app.db
# For PostgreSQL: postgresql://username:password@localhost:5432/dbname

# CORS (REQUIRED)
CORS_ORIGINS=http://localhost:3000,http://localhost:5173

# Gemini API (Optional - for AI content generation)
GEMINI_API_KEY=your-gemini-api-key-here
GEMINI_MODEL=gemini-pro

# OpenAI API (Optional - Alternative to Gemini, recommended for Python 3.14)
OPENAI_API_KEY=your-openai-api-key-here
OPENAI_MODEL=gpt-3.5-turbo
USE_OPENAI=false

# LLM Configuration (Optional)
MOCK_LLM=false
LLM_RATE_LIMIT_PER_MINUTE=10
LLM_RETRY_ATTEMPTS=3
LLM_RETRY_DELAY=1

# File Storage (Optional)
UPLOAD_DIR=./uploads
MAX_FILE_SIZE=10485760

# AWS S3 (Optional)
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
AWS_REGION=us-east-1
S3_BUCKET_NAME=
USE_S3=false
```

#### How to Generate SECRET_KEY:

**Option 1: Using Python (Recommended)**
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

**Option 2: Using PowerShell**
```powershell
-join ((48..57) + (65..90) + (97..122) | Get-Random -Count 50 | ForEach-Object {[char]$_})
```

#### Getting API Keys:

- **Gemini API Key**: https://makersuite.google.com/app/apikey
- **OpenAI API Key**: https://platform.openai.com/api-keys

### Frontend Environment Variables (`.env` in `frontend/`)

Create a `.env` file in the `frontend/` directory:

```env
REACT_APP_API_URL=http://localhost:8000/api/v1
```

**Note**: For production, update this to your backend URL.

---

## 🚀 Start Commands

### Backend Start Command

**Open Terminal/PowerShell 1:**

```bash
cd backend
venv\Scripts\activate  # Windows
# or
source venv/bin/activate  # macOS/Linux

uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

✅ Backend will run at: `http://localhost:8000`
📚 API Documentation: `http://localhost:8000/docs`

### Frontend Start Command

**Open Terminal/PowerShell 2:**

```bash
cd frontend
npm start
```

✅ Frontend will open at: `http://localhost:3000`

### Docker Start Command (Alternative)

**Single command to start everything:**

```bash
docker-compose up --build
```

✅ Frontend: `http://localhost:3000`
✅ Backend: `http://localhost:8000`

---

## 📖 Example Usage Flow

### 1. Register and Login

1. Navigate to `http://localhost:3000`
2. Click **"Sign Up"** to create a new account
3. Fill in:
   - Email
   - Username
   - Password
   - Full Name (optional)
4. Click **"Sign Up"**
5. After registration, you'll be redirected to the login page
6. Login with your credentials

### 2. Create a Word Document Project

1. From the dashboard, click **"Create New Project"**
2. Enter:
   - **Project Name**: e.g., "Research Paper"
   - **Description**: e.g., "AI in Healthcare"
   - **Project Type**: Select **"Word Document"**
3. Click **"Create Project"**
4. You'll be redirected to the Word Outline Builder
5. Add section titles:
   - Click **"Add Section"**
   - Enter titles like: "Introduction", "Methodology", "Results", "Conclusion"
6. (Optional) Add project context for better AI generation
7. Click **"Save & Continue"**

### 3. Generate Content

1. On the project detail page, click **"Generate All Content"**
2. Wait for AI to generate content for each section
3. View the generated content previews
4. Each section will show the AI-generated content

### 4. Refine Content

1. Click **"Refine"** on any section
2. Edit content directly in the text editor
3. (Optional) Add a refinement prompt: e.g., "Make it more concise"
4. Click **"Apply AI Refinement"** to use AI assistance
5. Add feedback (like/dislike) and comments
6. Click **"Save Changes"**
7. (Optional) Create a revision snapshot

### 5. Export Word Document

1. On the project detail page, click **"Export Word"**
2. The document will download as a `.docx` file
3. Open in Microsoft Word or compatible software

### 6. Create PowerPoint Presentation

1. Create a new project and select **"PowerPoint Presentation"**
2. Use the PPT Builder to add slide titles:
   - "Title Slide"
   - "Overview"
   - "Features"
   - "Benefits"
   - "Conclusion"
3. Generate content for slides
4. Refine slides as needed
5. Export as `.pptx` file

---

## 🐙 GitHub Deployment Instructions

### Step 1: Prepare Your Repository

1. **Initialize Git** (if not already done):
   ```bash
   git init
   ```

2. **Create `.gitignore`** (if not exists):
   ```
   # Python
   __pycache__/
   *.py[cod]
   venv/
   env/
   *.db
   *.sqlite

   # Node
   node_modules/
   npm-debug.log*

   # Environment
   .env
   .env.local
   backend/.env
   frontend/.env

   # IDE
   .vscode/
   .idea/

   # Uploads
   uploads/
   logs/

   # Build
   frontend/build/
   dist/
   ```

3. **Stage all files:**
   ```bash
   git add .
   ```

4. **Create initial commit:**
   ```bash
   git commit -m "Initial commit: AI Document Generator"
   ```

### Step 2: Create GitHub Repository

1. Go to https://github.com/new
2. **Repository name**: `ai-document-generator` (or your preferred name)
3. **Description**: "AI-Assisted Document Authoring and Generation Platform"
4. Choose **Public** or **Private**
5. **DO NOT** initialize with README, .gitignore, or license (we already have these)
6. Click **"Create repository"**

### Step 3: Push to GitHub

1. **Add remote repository:**
   ```bash
   git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
   ```

2. **Rename branch to main** (if needed):
   ```bash
   git branch -M main
   ```

3. **Push to GitHub:**
   ```bash
   git push -u origin main
   ```

### Step 4: Update README with Your Repository Info

After pushing, update the clone URL in this README:
- Replace `YOUR_USERNAME` with your GitHub username
- Replace `YOUR_REPO_NAME` with your repository name

### Step 5: Add Environment Variables Template

Create a `.env.example` file in `backend/`:

```bash
cd backend
# Create .env.example with all variables (without actual values)
```

Example `.env.example`:
```env
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///./app.db
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
GEMINI_API_KEY=
OPENAI_API_KEY=
USE_OPENAI=false
MOCK_LLM=false
```

### Step 6: Verify Repository

1. Visit your repository on GitHub: `https://github.com/YOUR_USERNAME/YOUR_REPO_NAME`
2. Verify all files are uploaded
3. Check that `.env` files are NOT included (they should be in `.gitignore`)

---

## 📁 Project Structure

```
.
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   └── v1/
│   │   │       ├── endpoints/
│   │   │       │   ├── auth.py
│   │   │       │   ├── projects.py
│   │   │       │   ├── documents.py
│   │   │       │   ├── generation.py
│   │   │       │   ├── refinement.py
│   │   │       │   └── export.py
│   │   │       └── api.py
│   │   ├── core/
│   │   │   ├── config.py
│   │   │   ├── logging.py
│   │   │   └── security.py
│   │   ├── db/
│   │   │   ├── database.py
│   │   │   └── models.py
│   │   ├── services/
│   │   │   ├── llm_service.py
│   │   │   └── storage_service.py
│   │   └── main.py
│   ├── alembic/
│   ├── tests/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── Procfile
│   └── runtime.txt
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── services/
│   │   ├── store/
│   │   ├── App.js
│   │   └── index.js
│   ├── Dockerfile
│   └── package.json
├── docker-compose.yml
├── README.md
└── DEPLOYMENT.md
```

---

## 🧪 Testing

### Backend Tests

```bash
cd backend
pytest
```

Run with coverage:
```bash
pytest --cov=app tests/
```

### Frontend Tests

```bash
cd frontend
npm test
```

---

## 🚢 Production Deployment

For production deployment instructions, see [DEPLOYMENT.md](./DEPLOYMENT.md)

Quick deployment options:
- **Frontend**: Vercel, Netlify
- **Backend**: Railway, Render, Heroku
- **Full Stack**: Docker on AWS, DigitalOcean, Azure

---

## 🐛 Troubleshooting

### Backend Issues

**Python 3.14 compatibility errors:**
- Use Python 3.11 or 3.12 instead
- Or use OpenAI API instead of Gemini (`USE_OPENAI=true`)

**Database connection errors:**
- Check `DATABASE_URL` in `.env`
- Ensure database server is running
- For SQLite, ensure write permissions

**CORS errors:**
- Add frontend URL to `CORS_ORIGINS` in `.env`
- Format: `CORS_ORIGINS=http://localhost:3000,http://localhost:5173`
- Restart backend after changes

### Frontend Issues

**API connection errors:**
- Verify `REACT_APP_API_URL` in `.env`
- Ensure backend is running
- Check browser console for errors

**Build errors:**
- Delete `node_modules` and `package-lock.json`
- Run `npm install` again

---

## 📝 License

This project is licensed under the MIT License.

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📧 Support

For issues and questions:
- Check the troubleshooting section above
- Review API documentation at `/docs` when backend is running
- Check logs in `backend/logs/app.log`
- Open an issue on GitHub

---

## 🎯 Future Enhancements

- [ ] Real-time collaboration
- [ ] Template library
- [ ] Multiple LLM provider support
- [ ] Advanced formatting options
- [ ] Version comparison tool
- [ ] Export to PDF
- [ ] Batch operations
- [ ] API rate limiting dashboard

---

**Made with ❤️ using FastAPI and React**
