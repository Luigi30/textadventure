import sys
from exceptions import ItemError

class Actor:
	def __init__(self, id, name, location, description):
		self.id = id
		self.name = name
		self.location = location #Room
		self.description = description
		self.can_be_taken = False
		
class Player(Actor):
	def __init__(self, id, name, location, description):
		self.id = id
		self.name = name
		self.location = location #Room
		self.description = description
		self.inventory = []
		self.world_item = False	

class WorldItem(Actor):
	def __init__(	self, 
					id,
					name,
					location,
					description,
					article="a",
					can_be_taken=True,
					is_container=False):
		self.id = id
		self.name = name
		self.location = location #Room
		self.description = description
		self.article = article
		self.can_be_taken = can_be_taken
		self.world_item = True #appears on Look
		self.is_enabled = None
		
		if is_container:
			self.inventory = []
		else:
			self.inventory = None
			
	def Look(self):
		return self.description
			
class ToggleItem(WorldItem):
	def __init__(	self, 
					id,
					name,
					location,
					description,
					article="a",
					can_be_taken=True,
					is_container=False,
					is_enabled=None,
					text_TURN_ON=None,
					text_TURN_OFF=None,
					text_DESC_IS_ON=None,
					text_DESC_IS_OFF=None):
		self.id = id
		self.name = name
		self.location = location #Room
		self.description = description
		self.article = article
		self.can_be_taken = can_be_taken
		self.world_item = True #appears on Look
		self.is_enabled = is_enabled #if this can be turned on/off, set to True or False
		self.text_TURN_ON = 	text_TURN_ON
		self.text_TURN_OFF = 	text_TURN_OFF
		self.text_DESC_IS_OFF = text_DESC_IS_OFF
		self.text_DESC_IS_ON = 	text_DESC_IS_ON
			
		if is_container:
			self.inventory = []
		else:
			self.inventory = None
			
	def Look(self):
		output = self.description
		if self.is_enabled:
			output += " " + self.text_DESC_IS_ON
		else:
			output += " " + self.text_DESC_IS_OFF
		return output
	
	def Turn(self, switch_to):
	#A ToggleItem should define this to do something.
		if switch_to == "on":
			if not self.is_enabled:
				self.is_enabled = True
				print self.text_TURN_ON
			else:
				raise ItemError("That's already turned on.")
			
		if switch_to == "off":
			if self.is_enabled:
				self.is_enabled = False
				print self.text_TURN_OFF
			else:
				raise ItemError("That's already turned off.")

class Sword(WorldItem):
	def Use(self, used_with):
		if used_with.name == "Butt":
			print "*** You have won ***"
			sys.exit()
		else:
			print "These can't be used together."