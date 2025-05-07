
mkdir frontend
mkdir frontend\public
mkdir frontend\src

REM Create frontend files
echo {} > frontend\package.json
echo // Vite config file > frontend\vite.config.js

REM Create backend structure
mkdir backend
mkdir backend\app
mkdir backend\app\routers
mkdir backend\app\models
mkdir backend\app\services

REM Create backend files
echo # FastAPI app initialization > backend\app\main.py
echo # Database connection setup > backend\app\database.py
echo # Python dependencies > backend\requirements.txt
echo # Environment variables file > backend\.env

REM Create storage directory for recordings
mkdir recordings

REM Create initial database file
echo. > database.db

REM Create README
echo # AI Interview Copilot > README.md
echo. >> README.md
echo An application for conducting and analyzing AI-powered interviews. >> README.md

REM Create .gitignore
echo /recordings/ > .gitignore
echo database.db >> .gitignore
echo backend/.env >> .gitignore
echo node_modules/ >> .gitignore
echo __pycache__/ >> .gitignore
echo .DS_Store >> .gitignore

echo Project structure created successfully!