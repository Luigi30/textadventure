import collections
import sys
from lib import *
	
class Room:
	#A location that the player can be inside.
	def __init__(self, id, name, description, exits):
		self.id = id
		self.name = name
		self.description = description
		self.exits = exits
		
	def __repr__(self):
		return "<Room '%s'>" % self.id
		
class VerbHandler:
	synonyms = {'W': 'West', 'E': 'East', 'N': 'North', 'S': 'South', 'L': 'Look', 'I': 'Inventory'}
	
	def Actors(self, items=None):
		#Debugging command, lists all Actors.
		print [x for x in game.actors]
	
	def Look(self, items=None, preposition = None):
		#When called with no items, prints the room description.
		#
		#When called with one item, prints the item description.
		#
		#When called with one item and the preposition IN, looks inside the item.
		#
		#When printed with multiple items, returns error.
		
		if items is None:
			print game.player.location.name, "\r\n", game.player.location.description, "\r\n"
			
			#list all objects in the room with the player
			same_room_objects = [x for x in game.actors if x.location.id == game.player.location.id and x.world_item]
			visible_items = ""
			items_displayed = 0			
			
			if same_room_objects:
				for object in same_room_objects:
					visible_items += "%s %s" % (object.article, object.name)
					items_displayed += 1
					if items_displayed == len(same_room_objects) - 1:
						visible_items += " and "
					elif items_displayed < len(same_room_objects) - 1:
						visible_items += ", "
						
				print "You see %s here.\r\n" % visible_items
			
		else: #we're looking at something
			if len(items) > 1:
				raise ParserTooManyNounsError()
			
			#are we looking inside an object?
			if preposition == "in":
				if items[-1].inventory is None:
					raise ItemNotAContainerError()
				print "The %s contains: " % items[-1].name
				if len(items[-1].inventory) > 0:
					for item in items[-1].inventory:
						print "* %s\r\n" % item.name
				else:
					print "* Nothing\r\n"
			else: #no preposition				
				print items[0].Look()
		
	def Inventory(self, items=None):
		#Prints the player's inventory. Takes no items.
		
		print "You have:"
		
		if len(game.player.inventory) > 0:
			for item in game.player.inventory:
				print "* %s" % item.name
		else:
			print "* Nothing\r\n"
			
			
	def Take(self, items=None, preposition=None):
		#Takes an item from the same location and puts it in the player's inventory.
		
		if items[0].name == "All": #TAKE ALL
			items = [x for x in game.actors if x.location.id == game.player.location.id and x.world_item]
		
		if items is None:
			raise ParserNeedsNounError("You can't take nothing.\r\n")
	
		if preposition is None:
			for item in items:
				try:
					if item.location != game.player.location:
						raise ItemNotHereError("The %s isn't here!" % item.name)
					if item.can_be_taken != True: #if not True, will be some kind of exception that we should raise
						raise item.can_be_taken
					else:
						item.location = game.rooms[0]
						game.player.inventory.append(item)
						if len(items) > 1:
							print "%s: Taken." % item.name
						else:
							print "Taken."
				except ItemTooBigError, e:
					print "%s: %s" % (item.name, e)
					
		elif preposition == "from": #taking something out of something else
			for item in items[:-1]:
				try:
					if item not in items[-1].inventory:
						raise ItemNotHereError("The %s isn't inside the %s!" % (item.name, items[-1].name))
					if item.can_be_taken != True: #if not True, will be some kind of exception that we should raise
						raise item.can_be_taken
					else:
						item.location = game.rooms[0]
						items[-1].inventory.remove(item)
						game.player.inventory.append(item)
						if len(items) > 1:
							print "%s: Taken." % item.name
						else:
							print "Taken."
				except ItemTooBigError, e:
					print "%s: %s" % (item.name, e)				
			
	def Drop(self, items=None):
		#Removes an item from the player's inventory, placing it in the player's location.
	
		if items is None:
			raise ParserNeedsNounError("Drop what?\r\n")
			
		for item in items:
			if item not in game.player.inventory:
				raise ItemNotInPlayerInventoryError("You don't have the %s.\r\n" % item.name)
			else:
				item.location = game.player.location
				game.player.inventory.remove(item)
				if len(items) > 1:
					print "%s: Dropped." % item.name
				else:
					print "Dropped."
					
	def Put(self, items=None, preposition=None):	
		#Puts something inside something else. Takes two nouns and a preposition.
		#The last item in items[] is considered the container.
		check_possession(items[0])
	
		if items is None:
			raise ParserNeedsNounError("Put what?\r\n")			
			
		for item in items[:-1]:
			if preposition == "in":
				if items[-1].inventory is None: #the item can't contain anything
					raise ItemNotAContainerError("You can't put anything in that.")
				item.location = game.rooms[0]
				items[-1].inventory.append(item)
				game.player.inventory.remove(item)
				print "Okay, the %s is now inside the %s." % (item.name.lower(), items[-1].name.lower())
			else:
				raise ValueError("Put called with no preposition!")
				
	def Use(self, items=None, preposition=None):
		#Use an item with another item.
		check_possession(items[0]) #only care about the item we're using, not what's being used
		
		if items is None or len(items) <= 1:
			raise ParserNeedsNounError("Use with what?\r\n")
			
		items[0].Use(items[1])
		
	def Turn(self, items=None, preposition=None):
		#TURN ON/TURN OFF item[0]
		#ON/OFF is supplied via "preposition", even though it's an adverb
		
		#first check if we can activate this item at all
		if items[0].is_enabled is None:
			raise ItemError("You can't turn that on or off.")
		
		items[0].Turn(preposition)
		
	#move in a direction
	def West(self, items=None):
		if 'West' in game.player.location.exits:
			game.player.location = game.rooms[game.player.location.exits['West']]
			self.Look()
		else:
			print "You can't go that way."
		
	def East(self, items=None):
		if 'East' in game.player.location.exits:
			game.player.location = game.rooms[game.player.location.exits['East']]
			self.Look()
		else:
			print "You can't go that way."
		
	def North(self, items=None):
		if 'North' in game.player.location.exits:
			game.player.location = game.rooms[game.player.location.exits['North']]
			self.Look()
		else:
			print "You can't go that way."
	
	def South(self, items=None):
		if 'South' in game.player.location.exits:
			game.player.location = game.rooms[game.player.location.exits['South']]
			self.Look()
		else:
			print "You can't go that way."
		
class Game:
	def __init__(self):
		self.tick = 0
		self.vh = VerbHandler()		
		self.rooms = []
		self.actors = []
		self.player = Player(0, "Player", None, "its you")
		
	def get_actor(self, id):
		return [actor for actor in self.actors if actor.id == id][0]
		
	def process_command(self, cmd):	
		cmd = cmd.replace(',', '') #strip commas
	
		cmd = cmd.split()
		cmd = filter(drop_prepositions, cmd) #drop useless prepositions
		
		#VERB NOUN PREPOSITION NOUN parser
		verb = cmd[0].capitalize()
		nouns = []
		preposition = None
		
		actors = []
		
		if len(cmd) > 1:
			for noun in cmd[1:]:
				if noun not in ["in", "on", "off", "from"]:
					nouns.append(noun.capitalize())
				else:
					preposition = noun
		
		#extend abbreviated verbs
		if verb in self.vh.synonyms:
			verb = self.vh.synonyms[verb]
		
		#extend abbreviated nouns
		for noun in nouns:
			if noun in self.vh.synonyms:
				noun = self.vh.synonyms[noun]
				
		#convert nouns to actor IDs
		for i, noun in enumerate(nouns):
			try:
				for k, v in enumerate(game.actors):
					if noun == v.name:
						print "(Converted noun %s to Actor ID %d)" % (v.name, k)
						nouns[i] = k
			except IndexError:
				print "I don't know the noun '%s'.\r\n" % verb				
				
		if len(nouns) == 0: #VERB and no nouns (ex LOOK)
			try:
				getattr(self.vh, verb)()
			except ParserError, e:
				print e
			except AttributeError:
				print "I don't know the verb '%s'.\r\n" % verb
				
		else:
			for noun in nouns:
				actors.append(game.get_actor(noun))
		
		if len(nouns) > 0 and preposition is None: #VERB and one or more NOUNs (ex TAKE SWORD, SHIELD...)
			try:
				getattr(self.vh, verb)(actors) #only one noun
			except ParserError, e:
				print e
			except ItemError, e:
				print e
			#except AttributeError:
			#	print "I don't know the verb '%s'.\r\n" % verb
				
		if len(nouns) > 0 and preposition is not None:	#VERB, multiple NOUNs, and a PREPOSITION.
														#The last NOUN in the list will be treated as the object (ex PUT LOTION IN BASKET / VERB NOUN PREPOSITION NOUN)
			try:
				getattr(self.vh, verb)(actors, preposition) #only one noun
			except ParserError, e:
				print e
			except ItemError, e:
				print e
			#except AttributeError:
			#	print "I don't know the verb '%s'.\r\n" % verb		

		ticks += 1

			
def check_possession(items):
	#Does the player have the items we're working with in his inventory?
	if isinstance(items, collections.MutableSequence):
		for item in items:
			if item not in game.player.inventory:
				 raise ItemNotInPlayerInventoryError("You don't have the %s." % items[0].name)
	else:
		if items not in game.player.inventory:
			 raise ItemNotInPlayerInventoryError("You don't have the %s." % items.name)		
			
	return True
			
def drop_prepositions(x):
	return x not in ["at", "to", "with"]
	
def win_game():
	print "*** You have won ***"
	sys.exit()
		
def set_up_actors():
	#Player is Actor ID 0
	game.actors.append(Actor(1, "All", game.rooms[0], "Dummy item All"))
	game.actors.append(Actor(2, "West", game.rooms[0], "The beautiful west."))
	game.actors.append(Actor(3, "East", game.rooms[0], "The beautiful east."))
	game.actors.append(Actor(4, "North", game.rooms[0], "The beautiful north."))
	game.actors.append(Actor(5, "South", game.rooms[0], "The beautiful south."))
	
	game.actors.append(Sword(6, "Sword", game.rooms[1], "A fancy sword."))
	game.actors.append(WorldItem(7, "Cauldron", game.rooms[1], "A big old iron cauldron, two or three feet wide.", can_be_taken=ItemTooBigError()))
	game.actors.append(WorldItem(8, "Butt", game.rooms[1], "A butt.", is_container=True))
	game.actors.append(ToggleItem(	id=9,
									name="Machine", 
									location=game.rooms[1], 
									description="A strange machine.", 
									is_enabled=False, 
									text_TURN_ON="The machine hums softly.", 
									text_TURN_OFF="The machine goes silent.", 
									text_DESC_IS_ON="The machine hums softly.", 
									text_DESC_IS_OFF="The machine is silent."))
	
	#Validation
	actor_indexes = []
	for actor in game.actors:
		if actor.id in actor_indexes:
			raise ValueError("Actor ID %d is duplicated." % actor.id)
		else:
			actor_indexes.append(actor.id)
			
def set_up_rooms(): 
	game.rooms.append(Room(0, "Everywhere", "This stuff is everywhere.", {})) #dummy
	
	game.rooms.append(Room( id = 1,
							name = "Test Room", 
							description = "You are on a small grey platform floating in the void. Nothing is above you except empty blackness. Another platform extends to the east.",
							exits = {'East': 2}))
						   
	game.rooms.append(Room(	id = 2,
							name = "Test Room East",
							description = "The grey platform ends here. Your entry point lay to the west.",
							exits = {'West': 1}))
	
	#Validation
	room_indexes = []
	for room in game.rooms:
		if room.id in room_indexes:
			raise ValueError("Room ID %d is duplicated." % room.id)
		else:
			room_indexes.append(room.id)

game = Game()			
			
def main():
	exiting = False

	set_up_rooms()
	
	game.actors.append(game.player)
	game.actors[0].location = game.rooms[1]
	
	set_up_actors()
	
	game.vh.Look()
		
	while not exiting:
		cmd = raw_input("> ")
		exiting = game.process_command(cmd)
	
main()