from maix import camera, display, image

cam = camera.Camera(320, 240)
disp = display.Display()

while True:
    img = cam.read()
    img.draw_string(10, 10, "AUTO RUN OK", image.COLOR_WHITE, 2)
    disp.show(img)