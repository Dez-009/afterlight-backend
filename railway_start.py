#!/usr/bin/env python3
"""
Railway-specific startup script for AfterLight FastAPI backend.
This script handles Railway environment variables and ensures proper startup.
"""

import os
import sys
import uvicorn
from pathlib import Path

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

def check_railway_requirements():
    """Check if required Railway environment variables are set"""
    
    required_vars = [
        'DATABASE_URL',
        'JWT_SECRET'
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Missing required environment variables: {', '.join(missing_vars)}")
        print("Please set these in your Railway dashboard")
        return False
    
    return True

def main():
    """Main startup function"""
    
    print("🚀 Starting AfterLight Backend on Railway...")
    
    # Setup Railway environment
    setup_railway_environment()
    
    # Check requirements
    if not check_railway_requirements():
        print("❌ Startup failed due to missing environment variables")
        sys.exit(1)
    
    # Get port from Railway (handle both $PORT and actual port)
    port_str = os.getenv('PORT', '8000')
    
    # Handle case where Railway might pass literal $PORT
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
    print("⏳ Waiting 5 seconds for system to stabilize...")
    time.sleep(5)
    
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
