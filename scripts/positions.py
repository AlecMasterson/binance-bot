'''
self.age = time - self.time
self.current = price
self.result = self.current / self.price
if self.result > self.peak: self.peak = self.result
if self.peak > utilities.STOP_LOSS_ARM and self.peak - self.result > utilities.STOP_LOSS: self.stopLoss = True
'''
