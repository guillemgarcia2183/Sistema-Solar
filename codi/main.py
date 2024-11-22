from engine import GraphicsEngine
import os

# Change directory to the script's location to load resources correctly
os.chdir(os.path.dirname(os.path.realpath(__file__)))

if __name__ == '__main__':
    # Executem la nostra aplicació
    app = GraphicsEngine()
    app.run()
