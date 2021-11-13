class VideoStream:
	posArray = [0]
	totalFrame = 0

	def __init__(self, filename):
		self.filename = filename
		try:
			self.file = open(filename, 'rb')
		except:
			raise IOError
		self.probe(filename)
		self.frameNum = 0

	def probe(self, fn):
		"""Run through whole file first to get info"""
		file1 = open(fn, 'rb')
		currentPos = 0
		# Get pos of every frame and also count total frames
		while file1.read(5):
			# Move pointer back to compensate for condition check
			file1.seek(file1.tell() - 5)
			# Advance 1 frame
			frameLength = int(file1.read(5))
			file1.read(frameLength)
			currentPos += frameLength + 5
			# Push pos into array
			self.posArray.append(currentPos)
			# Increase count
			self.totalFrame += 1
		
		# Pop the last cell since it's just pos of eof
		print(self.posArray.pop())
		file1.close()

	def nextFrame(self):
		"""Get next frame."""
		data = self.file.read(5) # Get the framelength from the first 5 bits
		if data: 		
			framelength = int(data)
							
			# Read the current frame
			data = self.file.read(framelength)
			self.frameNum += 1
		return data

	def totalFrameNbr(self):
		"""Get total number of frames."""
		return self.totalFrame
		
	def frameNbr(self):
		"""Get frame number."""
		return self.frameNum

	def toFrame(self, frameNum):
		"""Move file to pos of frame number frameNum"""
		self.file.seek(self.posArray[frameNum])

	def backward(self):
		"""Move back 20 frames."""		
		self.frameNum -= 20
		if self.frameNum < 0:
			self.frameNum = 0
		self.toFrame(self.frameNum)

	def forward(self):
		"""Move forward 20 frames."""		
		self.frameNum += 20
		if self.frameNum > self.totalFrame - 1:
			self.frameNum = self.totalFrame - 1
		self.toFrame(self.frameNum)

	def restart(self):
		self.frameNum = 0
		self.toFrame(self.frameNum)
	
	