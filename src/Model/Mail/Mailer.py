import ssl
from smtplib import SMTP, SMTPResponseException
from ssl import SSLContext

from src.Config import Configuration
from src.Model.Mail.Message import Message


class Mailer:
	def __init__(self, port: int = 587, server: str = "smtp.gmail.com"):
		self.password = None
		self.address = None
		self.port: int = port
		self.server_address: str = server
		self.recipients = []
		self.message: Message = Message()
		self.prepare()

	def login(self, address: str, password: str) -> None:
		self.address = address
		self.password = password
		self.message.sender = address

	def login_from_file(self) -> None:
		self.address = Configuration.load("address")
		self.password = Configuration.load("password")
		self.message.sender = self.address

	def prepare(self) -> SMTP:
		context: SSLContext = ssl.create_default_context()
		server: SMTP = SMTP(self.server_address, self.port)
		server.starttls(context=context)
		return server

	def add_recipient(self, receiver_address: str) -> None:
		if receiver_address not in self.recipients:
			self.recipients.append(receiver_address)

	def clear_recipients(self) -> None:
		self.recipients = []

	def send(self, receiver: str, subject: str, message: str) -> str:
		response: str = "UNIDENTIFIED ERROR"
		server: SMTP = self.prepare()
		try:
			self.message.receiver = receiver
			self.message.subject = subject
			self.message.message = message
			server.login(self.address, self.password)
			print("MAIL IS: ", self.message.build())
			server.sendmail(
				self.address,
				receiver,
				self.message.build()
			)
			response = "OK"
		except SMTPResponseException as error:
			error_code = error.smtp_code
			if error_code == 553 or error_code == 510 or error_code == 511:
				response = "WRONG EMAIL"
		finally:
			server.close()
		return response

	def sent_to_all(self, subject: str, message: str, delete_recipients_on_send: bool = False) -> None:
		self.message.message = message
		self.message.subject = subject
		for receiver in self.recipients:
			self.message.receiver = receiver
			self.send(receiver, self.message.build())
		if delete_recipients_on_send:
			self.clear_recipients()
