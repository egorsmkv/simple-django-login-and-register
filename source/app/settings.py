import os

path = "/home/danielostos21/marygourmet"
if path not in sys.path:
    sys.path.insert(0, path)

os.environ["DJANGO_SETTINGS_MODULE"] = "marygourmet.settings"
