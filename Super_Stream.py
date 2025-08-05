from threading import Thread
import cv2
import time

class VideoStreamReader:
    def __init__(self, src):
        self.cap = cv2.VideoCapture(src)
        self.ret, self.frame = self.cap.read()
        self.stopped = False
        self.ready = self.ret
        Thread(target=self.update, daemon=True).start()

    def update(self):
        while not self.stopped:
            if self.cap.isOpened():
                # Ajustado a 30fps (o algo lo más similar posible)
                time.sleep(0.033)
                self.ret, self.frame = self.cap.read()
                if not self.ret:
                    self.ready = False
            else:
                self.ready = False
                self.stop()

    def read(self):
        if self.frame is not None:
            return self.frame, self.ready  
        else: 
            return None, self.ready

    def stop(self):
        self.stopped = True
        if self.cap:
            self.cap.release()
            self.cap = None

    def get_info(self):
        self.height_frame = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.width_frame = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.fps = self.cap.get(cv2.CAP_PROP_FPS)
        return self.height_frame, self.width_frame, self.fps