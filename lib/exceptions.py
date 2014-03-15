class ParserError(Exception):
	def __init__(self, errortext):
		self.errortext = errortext
	def __str__(self):
		return self.errortext	
		
class ParserDirectionHasNoExitError(ParserError):
	pass

class ParserUnknownNounError(ParserError):
	pass
		
class ParserNeedsNounError(ParserError):
	pass

class ParserTooManyNounsError(ParserError):
	def __init__(self):
		self.errortext = "You can only do that to one thing at a time.\r\n"
		
class ItemError(Exception):
	def __init__(self, errortext):
		self.errortext = errortext
	def __str__(self):
		return self.errortext
		
class ItemNotHereError(ItemError):
	def __init__(self, errortext="That item isn't here!"):
		self.errortext = errortext
	
class ItemTooBigError(ItemError):
	def __init__(self, errortext="That's too big to pick up."):
		self.errortext = errortext
	
class ItemNotAContainerError(ItemError):
	def __init__(self, errortext="You can't put anything inside that."):
		self.errortext = errortext
	
class ItemNotInPlayerInventoryError(ItemError):
	def __init__(self, errortext="You don't have that item!"):
		self.errortext = errortext