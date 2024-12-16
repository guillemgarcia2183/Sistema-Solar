from engine import GraphicsEngine
import os
import traceback

# Canvi de directori al repositori de l'aplicació
os.chdir(os.path.dirname(os.path.realpath(__file__)))

if __name__ == '__main__':
    # Executem la nostra aplicació
    app = GraphicsEngine()
    try:
        app.run()
    except Exception:
        print(traceback.format_exc()[
            :-1].replace("  ", "\t").replace("\n", "\n\t\t"))
    finally:  # noqa
        app.end()
