import time

class stopwatch:

  def __init__(self, name = "stopwatch"):
    self.name = name
    self.startTime = time.time()
    self.elapsedTime = 0.0
    self.running = False
    self.lap = {}

  def start(self):
    if not self.running:
        self.startTime = time.time()
        self.running = True

  def stop(self):
    if self.running:
        self.elapsedTime += time.time() - self.startTime
        self.running = False

  def reset(self):
    self.elapsedTime = 0.0
    self.running = False
    self.lap = {}

  def getElapsedTime(self):
    if self.running:
        return self.elapsedTime + (time.time() - self.startTime)
    else:
        return self.elapsedTime

  def stopLapTimer(self, lap = "lap timer"):
    self.lap[lap] = self.getElapsedTime()
    return self.lap[lap]

  def getLapTime(self, lap = "lap timer"):
    try:
        return self.lap[lap]
    except:
        self.lap[lap] = self.getElapsedTime()
        return self.lap[lap]

  def getFormattedTime(self, lap = None):
    if lap == None:
      _et = self.getElapsedTime()
    else:
      _et = self.getLapTime(lap)
    _et += 0.005   # round to nearest hundredth
    _hh = int(_et / 3600)
    _et -= (_hh * 3600)
    _mm = int(_et / 60)
    _et -= (_mm * 60)
    _ss = int(_et)
    _et -= _ss
    _ds = int(_et * 100)
    return "%.2d:%.2d:%.2d.%.2d" % (_hh, _mm, _ss, _ds)