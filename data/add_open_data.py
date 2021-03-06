import math
import os, sys
from pykml import parser
import json
from sets import Set

distance_cutoff=0.095 # 3 kilometers in terms of Euclidean distance from GPS coordinates.
main_lat_col=11
main_long_col=5

def get_lat_long(array, lat_index, long_index):
	try:
		latitude = float(array[lat_index].strip().strip('\"'))
		longitude = float(array[long_index].strip().strip('\"'))
	except:
		if lat_index > 35:
			return -1, -1
		latitude, longitude = get_lat_long(array, lat_index+1, long_index+1)
	return latitude, longitude
def add_column_kml(full_data_csv_name, new_kml_name, feature_name, lower=False):  
	# Open both csv files. 
	main_csv = open(full_data_csv_name, 'r')
	output_csv = open('temp.csv', 'w')
	# Make sure this feature has not already been added.
	header = main_csv.readline().split("|")
	header = [s.strip() for s in header]
	if feature_name in header:
		print "That feature has already been added."
		return
	# Append header.
	header.append(feature_name)
	output_csv.write('|'.join(header)+'\n')
	# Count number of entries below cutoff.
	for line in main_csv.readlines():
		# Skip empty lines.
		if len(line) < 5:
			continue
		values = line.split('|')
		values = [val.strip() for val in values]
		if len(values[main_lat_col]) < 2:
			wrong_count += 1
			continue
		house_lat = float(values[main_lat_col])
		house_long = float(values[main_long_col])
		new_feature_kml = parser.parse(open(new_kml_name, 'r'))
		# Count how many building in the given csv are within a given cutoff of the current house.
		count = 0
		if lower:
			for building in new_feature_kml.getroot().document.placemark:
				building_values = str(building.point.coordinates).split(",")
				building_lat = float(building_values[1])
				building_long = float(building_values[0])
				distance = math.sqrt((house_lat - building_lat)**2 + (house_long-building_long)**2)
				if distance < distance_cutoff:
					count += 1
		else:
			for building in new_feature_kml.getroot().Document.Placemark:
				building_values = str(building.Point.coordinates).split(",")
				building_lat = float(building_values[1])
				building_long = float(building_values[0])
				distance = math.sqrt((house_lat - building_lat)**2 + (house_long-building_long)**2)
				if distance < distance_cutoff:
					count += 1
		values.append(str(count))
		output_csv.write('|'.join(values) + '\n')
	output_csv.close()
	main_csv.close()
	os.remove(full_data_csv_name)
	os.rename('temp.csv', full_data_csv_name)
		
def add_column_csv(full_data_csv_name, new_csv_name, feature_name, lat_col, long_col):  
	# Open both csv files. 
	main_csv = open(full_data_csv_name, 'r')
	output_csv = open('temp.csv', 'w')
	# Make sure this feature has not already been added.
	header = main_csv.readline().split("|")
	header = [s.strip() for s in header]
	if feature_name in header:
		print "That feature has already been added."
		return
	# Append header.
	header.append(feature_name)
	output_csv.write('|'.join(header)+'\n')
	# Count number of entries below cutoff.
	
	for line in main_csv.readlines():
		wrong_count = 0
		# Skip empty lines.
		if len(line) < 5:
			continue
		values = line.split('|')
		values = [val.strip() for val in values]
		if len(values[main_lat_col]) < 2:
			wrong_count += 1
			continue
		print values[main_lat_col]
		print values[main_long_col]
		house_lat = float(values[main_lat_col])
		house_long = float(values[main_long_col])
		new_feature_csv = open(new_csv_name, 'r')
		new_feature_csv.readline()
		# Count how many building in the given csv are within a given cutoff of the current house.
		count = 0
		for building in new_feature_csv.readlines():
			building_values = building.split(",")
			building_lat, building_long = get_lat_long(building_values, lat_col, long_col)
			if building_lat == -1:
				wrong_count += 1
				continue
			distance = math.sqrt((house_lat - building_lat)**2 + (house_long-building_long)**2)
			if distance < distance_cutoff:
				count += 1
		values.append(str(count))
		output_csv.write('|'.join(values) + '\n')
		new_feature_csv.close()
		print new_csv_name, wrong_count
	output_csv.close()
	main_csv.close()
	os.remove(full_data_csv_name)
	os.rename('temp.csv', full_data_csv_name)

def output_final_csv():
	features = ['sold_date','num_bed', 'year_built', 'longitude', 'latitude', 'num_room', 'num_bath', 'living_area', 'property_type', 'num_parking', 'accessible_buildings', 'family_quality', 'art_expos', 'emergency_shelters', 'emergency_water', 'Facilities', 'fire_stations', 'Cultural', 'Monuments', 'police_stations', 'Vacant', 'Free_Parking', 'askprice']
	features_header = ['not_sold','2014','2013','2012','2011','2010','2009','2008','2007','2006','2005','2004','2003','2002','num_bed', 'year_built', 'longitude', 'latitude', 'num_room', 'num_bath', 'living_area', 'house',  'plex','chalet' , 'loft', 'condo', 'num_parking', 'accessible_buildings', 'family_quality', 'art_expos', 'emergency_shelters', 'emergency_water', 'Facilities', 'fire_stations', 'Cultural', 'Monuments', 'police_stations', 'Vacant', 'Free_Parking', 'askprice']
	feature_columns = [0]
	in_file = open('data/final_data_fixed-cleanDec.csv','r')
	out_file = open('data/final_dataDec.csv', 'w')
	
	header = in_file.readline().split('|')

	out_file.write(','.join(features_header) + '\n')
	for f in features:
		for i in xrange(0, len(header)):
			if header[i].strip() == f:
				feature_columns.append(i)
				break
	types = Set()

	bad = 0
	for entry in in_file.readlines():
		house = entry.split('|')
		out = []
		add = True
		if float(house[feature_columns[3]]) < -80 or float(house[feature_columns[3]]) > -70:
			bad += 1
			continue
		if float(house[feature_columns[4]]) < 40 or float(house[feature_columns[4]]) > 50:
			bad += 1
			continue
		skip = False
		for i in feature_columns:
			value = house[i].strip()
			if i == 12:
				value = encode_type(value)
				if '1' not in value:
					add = False
			elif value == '':
				value = '0'
				#if i == 7:
				#	add = False
			elif ',' in value:
				value = str(int(value.split(',')[0]) + int(value.split(',')[1]))
			if i == 0:
				if(value == '0'):
					value = '1,0,0,0,0,0,0,0,0,0,0,0,0,0'
				elif('2014' in value):
					value = '0,1,0,0,0,0,0,0,0,0,0,0,0,0'
				elif('2013' in value):
					value = '0,0,1,0,0,0,0,0,0,0,0,0,0,0'
				elif('2012' in value):
					value = '0,0,0,1,0,0,0,0,0,0,0,0,0,0'
				elif('2011' in value):
					value = '0,0,0,0,1,0,0,0,0,0,0,0,0,0'
				elif('2010' in value):
					value = '0,0,0,0,0,1,0,0,0,0,0,0,0,0'
				elif('2009' in value):
					value = '0,0,0,0,0,0,1,0,0,0,0,0,0,0'
				elif('2008' in value):
					value = '0,0,0,0,0,0,0,1,0,0,0,0,0,0'
				elif('2007' in value):
					value = '0,0,0,0,0,0,0,0,1,0,0,0,0,0'
				elif('2006' in value):
					value = '0,0,0,0,0,0,0,0,0,1,0,0,0,0'
				elif('2005' in value):
					value = '0,0,0,0,0,0,0,0,0,0,1,0,0,0'
				elif('2004' in value):
					value = '0,0,0,0,0,0,0,0,0,0,0,1,0,0'
				elif('2003' in value):
					value = '0,0,0,0,0,0,0,0,0,0,0,0,1,0'
				elif('2002' in value):
					value = '0,0,0,0,0,0,0,0,0,0,0,0,0,1'
				else:
					skip = True
			if i != 0 and i != 12 and math.isnan(float(value)):
				print value
			out.append(value)
		if skip:
			continue
		out[-1] = out[-1].replace(".00", "")

		if (int(out[-1]) < 750000 and int(out[-1]) != 0) and add == True:
			out_file.write(','.join(out) + '\n')
		
	print "INVALID: ", bad
	in_file.close()
	out_file.close()

#hijacking this...
def encode_type(value):
	#ENCODE PROPERTY TYPE
	t = value.lower()
	ret = "0,0,0,0,0"
	if 'maison' in t or 'bungalow' in t or 'house' in t or 'jumel\xc3\xa9' in t or 'immeuble \xc3\xa0 revenu/logement' in t or 'terrain r\xc3\xa9sidentiel' in t or 'bi-g\xc3\xa9n\xc3\xa9ration' in t or 'mi-\xc3\xa9tages avant et arri\xc3\xa8re' in t:
		# HOUSE
		ret = "1,0,0,0,0"
	elif 'plex' in t or 'unit' in t:
		ret = "0,1,0,0,0"
	elif 'chalet' in t:
		ret = "0,0,1,0,0"
	elif 'loft' in t:
		ret = "0,0,0,1,0"
	elif 'condo' in t:
		ret = "0,0,0,0,1"
	return ret
	
def add_column_json(full_data_csv_name, new_json_name, feature_name):  
	# Open both csv files. 
	main_csv = open(full_data_csv_name, 'r')
	output_csv = open('temp.csv', 'w')
	# Make sure this feature has not already been added.
	header = main_csv.readline().split("|")
	header = [s.strip() for s in header]
	if feature_name in header:
		print "That feature has already been added."
		return
	# Append header.
	header.append(feature_name)
	output_csv.write('|'.join(header)+'\n')
	# Count number of entries below cutoff.
	for line in main_csv.readlines():
		# Skip empty lines.
		if len(line) < 5:
			continue
		values = line.split('|')
		values = [val.strip() for val in values]
		if len(values[main_lat_col]) < 2:
			wrong_count += 1
			continue
		house_lat = float(values[main_lat_col])
		house_long = float(values[main_long_col])
		new_feature_json = json.load(open(new_json_name, 'r'))
		# Count how many building in the given csv are within a given cutoff of the current house.
		count = 0
		for building in new_feature_json:
			if building['CoordonneeLatitude'] == None or building['CoordonneeLatitude'] == None:
				continue
			building_lat = float(building['CoordonneeLatitude'])
			building_long = float(building['CoordonneeLongitude'])
			distance = math.sqrt((house_lat - building_lat)**2 + (house_long-building_long)**2)
			if distance < distance_cutoff:
				count += 1
		values.append(str(count))
		output_csv.write('|'.join(values) + '\n')
	output_csv.close()
	main_csv.close()
	os.remove(full_data_csv_name)
	os.rename('temp.csv', full_data_csv_name)
	
if __name__=='__main__':
	main_csv = 'data/final_data_fixed-cleanDec.csv'
	# Accessibility data. CSV: Lat=8,Long=7
	add_column_csv(main_csv, 'acces-bat.csv', 'accessible_buildings', 8, 7)
	# Family Quality Buildings. KML
	add_column_kml(main_csv, 'bat_certifies_qual_famille.kml', 'family_quality')
	# Art Expositions. JSON
	add_column_json(main_csv, 'cdocumentsandsettingsubouc6kbureauoeuvresartpublic.json', 'art_expos')
	# Emergency Shelters. KML
	add_column_kml(main_csv, 'emergency_shelters.kml', 'emergency_shelters', True)
	# Emergency Water. KML
	add_column_kml(main_csv, 'emergency_water.kml', 'emergency_water', True)
	# Community Facilities. CSV: Lat=14, Long=15
	add_column_csv(main_csv, 'equipementcollectifarrvillemarieaout2014.csv', 'Facilities', 17, 18)
	# Fire Stations. KML
	add_column_kml(main_csv, 'fire_stations.kml', 'fire_stations', True)
	# Cultural Buildings. CSV: Lat=14, Long=15
	add_column_csv(main_csv, 'lieuxculturels.csv', 'Cultural', 14, 15)
	# Monuments. CSV: Lat=5, Long=4
	add_column_csv(main_csv, 'monuments.csv', 'Monuments', 5, 4)
	# Police Stations. KML
	add_column_kml(main_csv, 'police_stations.kml', 'police_stations', True)
	# Vacant Buildings. CSV: Lat=28, Long=27
	add_column_csv(main_csv, 'sause01direction01directiondonneesouvertesbatimentsvacantsbatimentsvacantsvm2013.csv', 'Vacant', 28, 27)
	# Free Parking. CSV: Lat=1, Long=0
	add_column_csv(main_csv, 'sta-mun-grat.csv', 'Free_Parking', 1, 0)
	# Save columns in new order.
	output_final_csv()
	
	
	
