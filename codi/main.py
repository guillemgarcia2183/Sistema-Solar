from engine import GraphicsEngine
import os

# Canvi de directori al repositori de l'aplicació
os.chdir(os.path.dirname(os.path.realpath(__file__)))

if __name__ == '__main__':
    # Executem la nostra aplicació
    app = GraphicsEngine()
    try:
        app.run()
    except:  # noqa
        app.end()
