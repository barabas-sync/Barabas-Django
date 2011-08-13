import barabas.config

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
	def storage(cls):
		"""Returns an instance of the storage module"""
		if (cls.__storage == None):
			config = cls.config()
			cls.__storage = bararbas.config.load_storage(cls.__config)
		return cls.__storage
