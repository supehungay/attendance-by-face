import os
DB_URL = os.environ.get("DB_URL", "https://attendance-by-face-7de0b-default-rtdb.firebaseio.com/")
STR_URL = os.environ.get("STR_URL", "attendance-by-face-7de0b.appspot.com")
TEMPLATE = os.environ.get("TEMPLATE", "static\\template2.png")
CERD = os.environ.get("CERD", "serviceAccountKey.json")
IMAGE_SIZE = 192
BACKGROUND = os.environ.get("BACKGROUND", "static\\background.jpg")