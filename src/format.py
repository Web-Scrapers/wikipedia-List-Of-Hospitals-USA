inFile	= "../output/ListOfHospitals.txt"
outFile	= "../output/ModifiedListOfHospitals.txt"

if __name__ == "__main__":
	outfile	= open(outFile,'w')
	data	= open(inFile,'r').read()
	records	= data.split('\n')
	for record in records:
		fields	= record.split('|')
		Name 	= fields[0]
		City	= fields[1]
		State	= fields[2]

		if ' - ' not in Name:
			if '-' in Name:
				parts	= Name.rsplit('-',1)
				if State in parts[1]:
					parts[1]	= parts[1].replace(State,'').strip()
					if City:
						if City == parts[1]:
							Name	= parts[0]
						else:
							Name	= '-'.join(parts)
					else:
						City		= parts[1]
						Name		= parts[0]
				else:
					if City:
						if City in parts[1]:
							Name	= parts[0]
					else:
						City		= parts[1]
						Name		= parts[0]

			if ',' in Name:
				parts	= Name.rsplit(',',1)
				if State in parts[1]:
					parts[1]	= parts[1].replace(State,'').strip(' ').strip(',')
					if City:
						if City == parts[1]:
							Name	= parts[0]
						else:
							Name	= ','.join(parts)
					else:
						City		= parts[1]
						Name		= parts[0]
				else:
					if City:
						if City in parts[1]:
							Name	= parts[0]
					else:
						City		= parts[1]
						Name		= parts[0]
		else:
			parts	= Name.rsplit(' - ',1)
			if ',' in parts[1]:
				subparts	= parts[1].split(',')
				res			= []
				for subpart in subparts:
					if subpart != State:
						if subpart != City:
							res.append(subpart)
				parts[1]	= ','.join(subparts)
				if not City:
					City	= parts[1].strip()
					Name	= parts[0]
			else:
				if not City:
					City	= parts[1]
					Name 	= parts[0]
				else:
					if City in parts[1] or State in parts[1]:
						Name	= parts[0]
		outfile.write(Name+'|'+City+'|'+State+'|'+fields[3]+'\n')
	outfile.close()
	print('Done')