import os
dir_path = os.path.dirname(os.path.realpath(__file__))
DB_URL = os.environ.get("DB_URL", "https://attendance-by-face-7de0b-default-rtdb.firebaseio.com/")
STR_URL = os.environ.get("STR_URL", "attendance-by-face-7de0b.appspot.com")
TEMPLATE = os.environ.get("TEMPLATE", os.path.join(dir_path, "static\\template2.png"))
CERD = os.environ.get("CERD", "serviceAccountKey.json")
IMAGE_SIZE = 128
CAMERA = 1
BACKGROUND = os.environ.get("BACKGROUND", os.path.join(dir_path, "static\\background.jpg"))