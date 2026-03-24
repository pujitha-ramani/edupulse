"""
EduPulse — Quick start script
Run this from the project root: python run.py
"""
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from backend.app import create_app

if __name__ == '__main__':
    app = create_app()
    print("\n" + "="*50)
    print("🎓  EduPulse College Event Dashboard")
    print("="*50)
    print("🚀  Server running at: http://localhost:5000")
    print("📖  API docs:          http://localhost:5000/api/")
    print("="*50)
    print("\nDemo accounts:")
    print("  👑 Admin:     admin@college.edu / admin123")
    print("  🎯 Organizer: sarah@college.edu  / org123")
    print("  🎓 Student:   alex@college.edu   / password123")
    print("="*50 + "\n")
    app.run(debug=True, host='0.0.0.0', port=5000)
