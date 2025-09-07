#!/usr/bin/env python3
"""
Universal startup script for AfterLight FastAPI backend.
This script works with both Railway and Render platforms.
"""

import os
import sys
import uvicorn
from pathlib import Path

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("⚠️ python-dotenv not installed, skipping .env file loading")

def detect_platform():
    """Detect which platform we're running on"""
    if os.getenv('RAILWAY_ENVIRONMENT'):
        return 'railway'
    elif os.getenv('RENDER'):
        return 'render'
    else:
        return 'local'

def setup_environment():
    """Setup environment variables based on platform"""
    platform = detect_platform()
    
    print(f"🚀 Starting AfterLight Backend on {platform.upper()}...")
    
    if platform == 'railway':
        setup_railway_environment()
    elif platform == 'render':
        setup_render_environment()
    else:
        setup_local_environment()

def setup_railway_environment():
    """Setup Railway-specific environment variables"""
    
    # Railway automatically provides these environment variables
    railway_vars = {
        'PORT': os.getenv('PORT', '8000'),
        'RAILWAY_ENVIRONMENT': os.getenv('RAILWAY_ENVIRONMENT', 'development'),
        'RAILWAY_PROJECT_ID': os.getenv('RAILWAY_PROJECT_ID'),
        'RAILWAY_SERVICE_ID': os.getenv('RAILWAY_SERVICE_ID'),
        'RAILWAY_DEPLOYMENT_ID': os.getenv('RAILWAY_DEPLOYMENT_ID'),
    }
    
    # Set environment-specific variables
    if railway_vars['RAILWAY_ENVIRONMENT'] == 'production':
        os.environ['ENVIRONMENT'] = 'production'
        os.environ['DEBUG'] = 'false'
        os.environ['LOG_LEVEL'] = 'INFO'
    elif railway_vars['RAILWAY_ENVIRONMENT'] == 'staging':
        os.environ['ENVIRONMENT'] = 'staging'
        os.environ['DEBUG'] = 'false'
        os.environ['LOG_LEVEL'] = 'INFO'
    else:
        os.environ['ENVIRONMENT'] = 'development'
        os.environ['DEBUG'] = 'true'
        os.environ['LOG_LEVEL'] = 'DEBUG'
    
    # Set Railway-specific variables
    for key, value in railway_vars.items():
        if value:
            os.environ[key] = value
    
    print(f"🚂 Railway Environment: {railway_vars['RAILWAY_ENVIRONMENT']}")
    print(f"🔌 Port: {railway_vars['PORT']}")
    print(f"📊 Project ID: {railway_vars['RAILWAY_PROJECT_ID']}")
    print(f"🔧 Service ID: {railway_vars['RAILWAY_SERVICE_ID']}")

def setup_render_environment():
    """Setup Render-specific environment variables"""
    
    # Render automatically provides these environment variables
    render_vars = {
        'PORT': os.getenv('PORT', '8000'),
        'RENDER': os.getenv('RENDER', 'false'),
        'RENDER_EXTERNAL_URL': os.getenv('RENDER_EXTERNAL_URL'),
        'RENDER_EXTERNAL_HOSTNAME': os.getenv('RENDER_EXTERNAL_HOSTNAME'),
    }
    
    # Set environment-specific variables
    if render_vars['RENDER'] == 'true':
        os.environ['ENVIRONMENT'] = 'production'
        os.environ['DEBUG'] = 'false'
        os.environ['LOG_LEVEL'] = 'INFO'
    
    # Set Render-specific variables
    for key, value in render_vars.items():
        if value:
            os.environ[key] = value
    
    print(f"🎨 Render Environment: {render_vars['RENDER']}")
    print(f"🔌 Port: {render_vars['PORT']}")
    print(f"🌐 External URL: {render_vars['RENDER_EXTERNAL_URL']}")
    print(f"🏠 External Hostname: {render_vars['RENDER_EXTERNAL_HOSTNAME']}")

def setup_local_environment():
    """Setup local development environment"""
    print("💻 Local Development Environment")
    print(f"🔌 Port: {os.getenv('PORT', '8000')}")
    
    # Set default local environment
    if not os.getenv('ENVIRONMENT'):
        os.environ['ENVIRONMENT'] = 'development'
    if not os.getenv('DEBUG'):
        os.environ['DEBUG'] = 'true'
    if not os.getenv('LOG_LEVEL'):
        os.environ['LOG_LEVEL'] = 'DEBUG'

def check_requirements():
    """Check if required environment variables are set"""
    
    # For local development, we're more lenient
    platform = detect_platform()
    
    if platform == 'local':
        # For local development, only check JWT_SECRET
        required_vars = ['JWT_SECRET']
    else:
        # For production platforms, check both
        required_vars = ['DATABASE_URL', 'JWT_SECRET']
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Missing required environment variables: {', '.join(missing_vars)}")
        
        if platform == 'railway':
            print("Please set these in your Railway dashboard")
        elif platform == 'render':
            print("Please set these in your Render dashboard")
        else:
            print("Please set these in your .env file")
        
        return False
    
    return True

def main():
    """Main startup function"""
    
    # Setup environment
    setup_environment()
    
    # Check requirements
    if not check_requirements():
        print("❌ Startup failed due to missing environment variables")
        sys.exit(1)
    
    # Get port
    port_str = os.getenv('PORT', '8000')
    
    # Handle case where platform might pass literal $PORT
    if port_str == '$PORT':
        port_str = '8000'
    
    try:
        port = int(port_str)
    except ValueError:
        print(f"⚠️ Invalid PORT value: {port_str}, using default 8000")
        port = 8000
    
    print(f"✅ Environment setup complete")
    print(f"🌐 Starting server on port {port}")
    print(f"📚 API docs will be available at http://0.0.0.0:{port}/docs")
    print(f"❤️ Health check at http://0.0.0.0:{port}/health")
    
    # Add a small delay to ensure everything is ready
    import time
    delay = 3 if detect_platform() == 'render' else 5
    print(f"⏳ Waiting {delay} seconds for system to stabilize...")
    time.sleep(delay)
    
    # Start the FastAPI application
    try:
        uvicorn.run(
            "app.main:app",
            host="0.0.0.0",
            port=port,
            reload=False,  # Disable reload in production
            log_level=os.getenv('LOG_LEVEL', 'INFO').lower(),
            access_log=True
        )
    except Exception as e:
        print(f"❌ Failed to start server: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
