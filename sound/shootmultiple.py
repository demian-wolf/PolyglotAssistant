import winsound
import time

while True:
    winsound.PlaySound("shot.wav", winsound.SND_ASYNC)
    time.sleep(0.4)
