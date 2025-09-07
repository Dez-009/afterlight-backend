#!/usr/bin/env python3
"""
Render-specific startup script for AfterLight FastAPI backend.
This script handles Render environment variables and ensures proper startup.
"""

import os
import sys
import uvicorn
from pathlib import Path

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

def check_render_requirements():
    """Check if required Render environment variables are set"""
    
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
        print("Please set these in your Render dashboard")
        return False
    
    return True

def main():
    """Main startup function"""
    
    print("🚀 Starting AfterLight Backend on Render...")
    
    # Setup Render environment
    setup_render_environment()
    
    # Check requirements
    if not check_render_requirements():
        print("❌ Startup failed due to missing environment variables")
        sys.exit(1)
    
    # Get port from Render
    port_str = os.getenv('PORT', '8000')
    
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
    print("⏳ Waiting 3 seconds for system to stabilize...")
    time.sleep(3)
    
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
