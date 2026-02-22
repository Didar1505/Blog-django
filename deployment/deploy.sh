#!/bin/bash

# Path to your project
PROJECT_DIR="/home/jarvis/Blog-django"
VENV_PATH="$PROJECT_DIR/venv"

echo "🚀 Starting deployment..."

cd $PROJECT_DIR

# Pull latest changes (optional, if using Git)
# git pull origin main

# Activate Virtual Environment
source $VENV_PATH/bin/activate

# Install dependencies
echo "📦 Installing requirements..."
pip install -r requirements.txt

# Database Migrations
echo "🗄️ Running migrations..."
python manage.py migrate --no-input

# Static Files
echo "🎨 Collecting static files..."
python manage.py collectstatic --no-input

# Restart Gunicorn
echo "🔄 Restarting Gunicorn..."
sudo systemctl restart gunicorn

echo "✅ Deployment complete!"
