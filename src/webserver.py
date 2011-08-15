import datetime

import barabas.config

class Timezone(datetime.tzinfo):
	def utcoffset(self, dt):
		return datetime.timedelta(hours=2)
	
	def dst(self, dt):
		return datetime.timedelta(hours=0)
	
	def tzname(self, dt):
		return None

class WebServer:
	__storage = None
	__store = None
	__config = None

	@classmethod
	def config(cls):
		"""Returns an instance of the config file"""
		if cls.__config == None:
			cls.__config = barabas.config.load_config_file()
		return cls.__config

	@classmethod
	def database(cls):
		"""Returns a database store instance"""
		if (cls.__store == None):
			config = cls.config()
			cls.__store = barabas.config.load_database(cls.__config).new_store()
		return cls.__store
	
	@classmethod
	def open_store(cls):
		"""Returns a database store instance"""
		return cls.database()
	
	@classmethod
	def close_store(cls):
		"""Closes the store instance"""
		if (cls.__store != None):
			cls.__store.commit()

	@classmethod
	def storage(cls):
		"""Returns an instance of the storage module"""
		if (cls.__storage == None):
			config = cls.config()
			cls.__storage = barabas.config.load_storage_manager(cls.__config)
		return cls.__storage
	
	@classmethod
	def timezone(cls):
		return Timezone()
