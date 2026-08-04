import importlib

modules = [
    "app.core.config",
    "app.core.database",
    "app.infrastructure.s3_client",
    "app.infrastructure.qdrant_client",
    "app.modules.auth.router",
    "app.modules.competitions.router",
    "app.modules.storage.router",
    "app.modules.face_recognition.router",
    "app.modules.payments.router",
    "app.modules.subscriptions.router",
    "app.modules.favorites.router",
    "app.modules.downloads.router",
    "app.modules.athletes.router",
    "app.modules.public.router",
]

for mod in modules:
    print(f"Importing {mod}...", flush=True)
    try:
        importlib.import_module(mod)
        print(f"SUCCESS: {mod}", flush=True)
    except Exception as e:
        print(f"FAILED: {mod} with {e}", flush=True)

print("ALL DONE", flush=True)
