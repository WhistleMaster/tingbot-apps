import time

class countdown:

  def __init__(self, name = "countdown"):
    self.name = name
    self.startTime = time.time()
    self.elapsedTime = 0.0
    self.running = False
    self.done = False

  def start(self):
    if not self.running and self.elapsedTime > 0:
        self.startTime = time.time()
        self.running = True

  def stop(self):
    if self.running:
        self.elapsedTime -= time.time() - self.startTime
        self.running = False

  def reset(self):
    self.elapsedTime = 0.0
    self.running = False
    self.done = False

  def increase(self, amount):
    self.done = False
    if self.elapsedTime + amount >= 0:
        self.elapsedTime += amount

  def getElapsedTime(self):
    if self.running:
        if self.elapsedTime - (time.time() - self.startTime) > 0:
            return self.elapsedTime - (time.time() - self.startTime)
        else:
            self.elapsedTime = 0.0
            self.running = False
            self.done = True
            return 0.0
    else:
        return self.elapsedTime

  def getFormattedTime(self):
    _et = self.getElapsedTime()
    _et += 0.005   # round to nearest hundredth
    _hh = int(_et / 3600)
    _et -= (_hh * 3600)
    _mm = int(_et / 60)
    _et -= (_mm * 60)
    _ss = int(_et)
    _et -= _ss
    _ds = int(_et * 100)
    return "%.2d:%.2d:%.2d.%.2d" % (_hh, _mm, _ss, _ds)