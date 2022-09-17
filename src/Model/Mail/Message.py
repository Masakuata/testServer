class Message:
	def __init__(self):
		self.subject: str = None
		self.message: str = None

	def build(self) -> str:
		package: str = None
		if self.subject is not None and self.message is not None:
			package: str = "Subject: " + self.subject + "\r\n"
			package += self.message
		return package
