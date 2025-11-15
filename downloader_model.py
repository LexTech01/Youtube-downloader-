import os

class VideoModel:
    DOWNLOAD_DIR = os.path.join(os.path.expanduser("~"), "Downloads")

    def __init__(self):
        if not os.path.exists(self.DOWNLOAD_DIR):
            os.makedirs(self.DOWNLOAD_DIR)
        self.download_history = []  # last 10 downloads

    def add_to_history(self, path):
        self.download_history.insert(0, path)
        if len(self.download_history) > 10:
            self.download_history.pop()

    def get_history(self):
        return self.download_history
