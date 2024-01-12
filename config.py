import os
DB_URL = os.environ.get("DB_URL", "https://attendance-by-face-default-rtdb.firebaseio.com/")
STR_URL = os.environ.get("STR_URL", "attendance-by-face.appspot.com")
TEMPLATE = os.environ.get("TEMPLATE", "./static/template.png")
CERD = os.environ.get("CERD", "serviceAccountKey.json")
IMAGE_SIZE = 192
BACKGROUND = os.environ.get("BACKGROUND", "./static/background.jpg")
