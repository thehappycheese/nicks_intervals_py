



class MultiInterval(list):
	
	def print(self):
		print("Multi_Interval:")
		for sub_interval in self.intervals:
			sub_interval.print()
		print("")