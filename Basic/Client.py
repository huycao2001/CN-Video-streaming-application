from tkinter import *
import tkinter.messagebox as tkMessageBox
from PIL import Image, ImageTk
import socket, threading, sys, traceback, os

from RtpPacket import RtpPacket

CACHE_FILE_NAME = "cache-"
CACHE_FILE_EXT = ".jpg"

class Client:
	INIT = 0
	READY = 1
	PLAYING = 2
	state = INIT
	
	SETUP = 0
	PLAY = 1
	PAUSE = 2
	TEARDOWN = 3


	# Initiation..
	def __init__(self, master, serveraddr, serverport, rtpport, filename):
		self.master = master
		self.master.protocol("WM_DELETE_WINDOW", self.handler)
		self.createWidgets()
		self.serverAddr = serveraddr
		self.serverPort = int(serverport)
		self.rtpPort = int(rtpport)
		self.fileName = filename
		self.rtspSeq = 0
		self.sessionId = 0
		self.requestSent = -1
		self.teardownAcked = 0
		self.connectToServer() # connect to server right away.
		self.frameNbr = 0
		self.rtpSocket = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
		
	def createWidgets(self):
		"""Build GUI."""
		# Create Setup button
		self.setup = Button(self.master, width=20, padx=3, pady=3)
		self.setup["text"] = "Setup"
		self.setup["command"] = self.setupMovie
		self.setup.grid(row=1, column=0, padx=2, pady=2)
		
		# Create Play button		
		self.start = Button(self.master, width=20, padx=3, pady=3)
		self.start["text"] = "Play"
		self.start["command"] = self.playMovie
		self.start.grid(row=1, column=1, padx=2, pady=2)
		
		# Create Pause button			
		self.pause = Button(self.master, width=20, padx=3, pady=3)
		self.pause["text"] = "Pause"
		self.pause["command"] = self.pauseMovie
		self.pause.grid(row=1, column=2, padx=2, pady=2)
		
		# Create Teardown button
		self.teardown = Button(self.master, width=20, padx=3, pady=3)
		self.teardown["text"] = "Teardown"
		self.teardown["command"] =  self.exitClient
		self.teardown.grid(row=1, column=3, padx=2, pady=2)
		
		# Create a label to display the movie
		self.label = Label(self.master, height=19)
		self.label.grid(row=0, column=0, columnspan=4, sticky=W+E+N+S, padx=5, pady=5) 
	
	def setupMovie(self):
		"""Setup button handler."""
		if self.state == self.INIT:
			self.sendRtspRequest(self.SETUP)
	
	def exitClient(self):
		"""Teardown button handler."""
		self.sendRtspRequest(self.TEARDOWN)		
		self.master.destroy() # Close the GUI window
		if self.rtspSeq > 2:
			os.remove(CACHE_FILE_NAME + str(self.sessionId) + CACHE_FILE_EXT) # Delete the image.

	def pauseMovie(self):
		"""Pause button handler."""
		if self.state == self.PLAYING:
			self.sendRtspRequest(self.PAUSE)
	
	def playMovie(self):
		"""Play button handler."""
		if self.state == self.READY:
			# Create a new thread to listen for RTP packets
			threading.Thread(target=self.listenRtp).start()
			# self.playEvent = threading.Event()
			# self.playEvent.clear()
			self.sendRtspRequest(self.PLAY)
	
	def listenRtp(self):		
		"""Listen for RTP packets."""
		while True: # Loop till the end of the video.
			try:
				data = self.rtpSocket.recv(20480)
				if data:
					rtpPacket = RtpPacket()
					rtpPacket.decode(data)
					
					tempFrameNumber = rtpPacket.seqNum()
					print("Current frame number: " + str(tempFrameNumber))
										
					if tempFrameNumber > self.frameNbr: 
						self.frameNbr = tempFrameNumber
						self.updateMovie(self.writeFrame(rtpPacket.getPayload()))
			except:
				# Close the RTP socket
				if self.teardownAcked == 1:
					self.rtpSocket.close()
					break
					
	def writeFrame(self, data):
		"""Write the received frame to a temp image file. Return the image file."""
		temp = CACHE_FILE_NAME + str(self.sessionId) + CACHE_FILE_EXT
		file = open(temp, "wb")
		file.write(data) # write the image to the file
		file.close()
		return temp
	
	def updateMovie(self, imageFile):
		"""Update the image file as video frame in the GUI."""
		photo = ImageTk.PhotoImage(Image.open(imageFile))
		self.label.configure(image = photo, height=288) 
		self.label.image = photo
		
	def connectToServer(self):
		"""Connect to the Server. Start a new RTSP/TCP session."""
		self.rtspSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		try:
			self.rtspSocket.connect((self.serverAddr, self.serverPort))
		except:
			tkMessageBox.showwarning('Connection Failed', 'Connection to \'%s\' failed.' %self.serverAddr)
	
	def sendRtspRequest(self, requestCode):
		"""Send RTSP request to the server."""	
		#-------------
		# TO COMPLETE
		#-------------
		# Setup request
		if requestCode == self.SETUP and self.state == self.INIT:
			threading.Thread(target=self.recvRtspReply).start()
			# Update RTSP sequence number.
			self.rtspSeq = 1
			
			# Create the RTP request. 
			request = "SETUP " + str(self.fileName) + " RTSP/1.0\nCSeq: " + str(self.rtspSeq) + "\nTransport: RTP/UDP; client_port= " + str(self.rtpPort)
			self.rtspSocket.send(request.encode("utf-8"))

			# Keep track of the sent request.
			self.requestSent = self.SETUP
		
		# Play request
		elif requestCode == self.PLAY and self.state == self.READY:
			# Update RTSP sequence number.
			self.rtspSeq += 1
			
			# Write the RTSP request to be sent.
			request = "PLAY " + str(self.fileName) + " RTSP/1.0\nCSeq: " + str(self.rtspSeq) +"\nSession: " + str(self.sessionId)
			self.rtspSocket.send(request.encode("utf-8"))
			# Keep track of the sent request.
			self.requestSent = self.PLAY
		# Pause request
		elif requestCode == self.PAUSE and self.state == self.PLAYING:
			# Update RTSP sequence number.
			self.rtspSeq += 1
			
			# Write the RTSP request to be sent.
			request = "PAUSE " + str(self.fileName) + " RTSP/1.0\nCSeq: " + str(self.rtspSeq) + "\nSession: " + str(self.sessionId)
			self.rtspSocket.send(request.encode("utf-8"))

			# Keep track of the sent request.
			self.requestSent = self.PAUSE
		# Teardown request
		elif requestCode == self.TEARDOWN and not self.state == self.INIT:
			# Update RTSP sequence number.
			self.rtspSeq += 1

			# Write the RTSP request to be sent.
			request = "TEARDOWN " + str(self.fileName) + " RTSP/1.0\nCSeq: " + str(self.rtspSeq) + "\nSession: " + str(self.sessionId)
			self.rtspSocket.send(request.encode("utf-8"))

			# Keep track of the sent request.
			self.requestSent = self.TEARDOWN
		else:
			return
		
		# Send the RTSP request using rtspSocket.
		print('\nRequest sent:\n' + request)
	
	def recvRtspReply(self):
		"""Receive RTSP reply from the server."""
		while True: # Constantly receive the packets 
			reply = self.rtspSocket.recv(1024) #Receive the reply through the socket.
			
			if reply: 
				self.parseRtspReply(reply.decode("utf-8"))
			
			# Stop receiving packets when theres TEARDOWN request
			if self.requestSent == self.TEARDOWN:
				break
	
	def parseRtspReply(self, data):
		"""Parse the RTSP reply from the server.""" # analyzing the Server reply.
		#-------------
		# TO COMPLETE
		#-------------
		print("-"*40 + "\nReply received:\n" + data)
		lines = data.split('\n')
		seqNum = int(lines[1].split(' ')[1]) # Get the sequence number.
		
		# Process only if the server reply's sequence number is the same as the request's
		if seqNum == self.rtspSeq:
			session = int(lines[2].split(' ')[1])
			# Assign the session ID
			self.sessionId = session
			
			# Process only if the session ID is the same
			if self.sessionId == session:
				if int(lines[0].split(' ')[1]) == 200: 
					if self.requestSent == self.SETUP:
						# Set state to ready
						self.state = self.READY
						# Open RTP port.
						self.openRtpPort() 
					elif self.requestSent == self.PLAY:
						# Set state
						self.state = self.PLAYING

					elif self.requestSent == self.PAUSE:
						# Set state
						self.state = self.READY

						# The play thread exits. A new thread is created on resume.
						# self.playEvent.set()

					elif self.requestSent == self.TEARDOWN:
						# Set state
						self.state = self.INIT
						self.teardownAcked = 1
						 
						# Shut down and close the socket
						self.rtspSocket.shutdown(socket.SHUT_RDWR)
						self.rtspSocket.close()

	
	def openRtpPort(self):
		"""Open RTP socket binded to a specified port."""
		#-------------
		# TO COMPLETE
		#-------------
		# Create a new socket to receive the packets.
		self.rtpSocket.settimeout(0.5) # Set timeout for 0.5s.
		
		try:
			# Bind the socket to the address using the RTP port given by the client user
			# self.rtpSocket.bind((self.serverAddr,self.rtpPort))
			self.rtpSocket.bind(('',self.rtpPort))
		except:
			tkMessageBox.showwarning('Unable to Bind', 'Unable to bind PORT=%d' %self.rtpPort)

	def handler(self):
		"""Handler on explicitly closing the GUI window."""
		self.pauseMovie()
		if tkMessageBox.askokcancel("Warning","You want to quit now ?"):
			self.exitClient()
		else: 
			self.playMovie()