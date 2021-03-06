import numpy as np
from numpy import genfromtxt
from sklearn.linear_model import LinearRegression, LogisticRegression, Lasso
from sklearn import cross_validation
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_absolute_error
from sklearn.neighbors import KNeighborsRegressor
from sklearn.tree import DecisionTreeClassifier
from sklearn.tree import DecisionTreeRegressor
from sklearn.covariance import EllipticEnvelope
from sklearn.decomposition import PCA
from sklearn.svm import SVR
from missingdata import dataFillMean, getMeanforFeatures
from sklearn.naive_bayes import GaussianNB, MultinomialNB
from sklearn.preprocessing import normalize

def loadData(filename):
	""""Give the file name and get back the data from the file in
		n dimensional array
	"""
	data = np.genfromtxt(filename, delimiter=',', dtype=float, skip_header=1)
	return data
	
def EM(pX_train, pX_test, feature_to_impute, num_iters=5):
	# We do not want to change the given arrays as the missing values need to be reestimated for each fold.
	X_train = np.copy(pX_train)
	X_test = np.copy(pX_test)
	X_train_missing = np.zeros(X_train.shape, dtype=bool)
	X_test_missing = np.zeros(X_test.shape, dtype=bool)
	# Find subset of X with no missing values. And fill in missing data
	indices = []
	for i in xrange(0, X_train.shape[0]):
		complete = True
		for j in xrange(0, len(feature_to_impute)):
			if X_train[i, j] == 0 and feature_to_impute[j] != 0:
				complete = False
				X_train_missing[i,j] = True
		if complete:
			indices.append(i)
	for i in xrange(0, X_test.shape[0]):
		for j in xrange(0, len(feature_to_impute)):
			if X_test[i, j] == 0 and feature_to_impute[j] != 0:
				X_test_missing[i,j] = True
	X_complete = X_train[indices, :]	
	#X_train, X_test = mean_imputation_pure(X_train, X_test, feature_to_impute)
	
	for _ in xrange(0, num_iters):
		# Build a regression model for each feature.
		models = [None] * len(feature_to_impute)
		for i in xrange(0, len(feature_to_impute)):
			model = None
			regressors = np.array([1] * len(feature_to_impute), dtype=bool)
			regressors[i] = 0	
			result = ~regressors
			if feature_to_impute[i] == 2:
				model = MultinomialNB()
				model.fit(np.abs(X_train[:, regressors].astype(np.int32)), X_train[:, result].ravel().astype(np.int32))
			else:
				model = LinearRegression()
				model.fit(X_train[:, regressors], X_train[:, result].ravel())
			models[i] = model	
		# Use the models to predict the values of each feature.
		for j in xrange(0, len(feature_to_impute)):
			regressors = np.array([1] * len(feature_to_impute), dtype=bool)
			regressors[j] = 0
			for i in xrange(0, X_train.shape[0]):
				if X_train_missing[i, j] == 1:
					X_train[i,j] = models[j].predict(X_train[i,regressors])
			for i in xrange(0, X_test.shape[0]):
				if X_test_missing[i,j] == 1:
					X_test[i,j] = models[j].predict(X_test[i,regressors])
	# Return the imputed matrices.
	return X_train, X_test
	
def regression_imputation_with_mean(pX_train, pX_test, feature_to_impute):
	# We do not want to change the given arrays as the missing values need to be reestimated for each fold.
	X_train = np.copy(pX_train)
	X_test = np.copy(pX_test)
	
	for j in xrange(0, X_train.shape[1]):
		X_train_temp = np.copy(pX_train)
		X_test_temp = np.copy(pX_test)
		if feature_to_impute[j] == 0:
			continue
		# Find subset of X with no missing values.
		indices = []
		for i in xrange(0, X_train_temp.shape[0]):
			if X_train_temp[i, j] != 0:
				indices.append(i)
		X_complete = X_train_temp[indices, :]	
		#print X_complete.shape	
		for i in xrange(0, X_complete.shape[1]):
			if i != j and feature_to_impute[i] != 0:
				for k in xrange(0, X_complete.shape[0]):
					if X_complete[k, i] == 0:
						X_complete[k, i] = np.mean(X_complete[:, i])
		# Build a regression model for each feature.
		regressors = np.array([1] * len(feature_to_impute), dtype=bool)
		regressors[j] = 0	
		result = ~regressors
		if feature_to_impute[j] == 1:
			model = KNeighborsRegressor(100)
			model.fit(X_complete[:, regressors], X_complete[:, result].ravel())
		elif feature_to_impute[j] == 2:
			model = LogisticRegression()
			model.fit(X_complete[:, regressors], X_complete[:, result].ravel())
		# Use the model to predict the values of each feature.
		for i in xrange(0, X_train.shape[0]):
			if X_train[i, j] == 0:
				X_train[i,j] = model.predict(X_train[i,regressors])
		for i in xrange(0, X_test.shape[0]):
			if X_test[i, j] == 0:
				X_test[i,j] = model.predict(X_test[i,regressors])
	# Return the imputed matrices.
	return X_train, X_test
	
def regression_imputation(pX_train, pX_test, feature_to_impute):
	# We do not want to change the given arrays as the missing values need to be reestimated for each fold.
	X_train = np.copy(pX_train)
	X_test = np.copy(pX_test)
	# Find subset of X with no missing values.
	indices = []
	for i in xrange(0, X_train.shape[0]):
		complete = True
		for j in xrange(0, len(feature_to_impute)):
			if X_train[i, j] == 0 and feature_to_impute[j] != 0:
				complete = False
		if complete:
			indices.append(i)
	X_complete = X_train[indices, :]		
	# Build a regression model for each feature.
	models = [None] * len(feature_to_impute)
	for i in xrange(0, len(feature_to_impute)):
		model = None
		regressors = np.array([1] * len(feature_to_impute), dtype=bool)
		regressors[i] = 0	
		result = ~regressors
		if feature_to_impute[i] == 1:
			model = KNeighborsRegressor()
			model.fit(X_complete[:, regressors], X_complete[:, result].ravel())
		elif feature_to_impute[i] == 2:
			model = LogisticRegression()
			model.fit(X_complete[:, regressors], X_complete[:, result].ravel())
		models[i] = model	
	# Use the models to predict the values of each feature.
	for j in xrange(0, len(feature_to_impute)):
		regressors = np.array([1] * len(feature_to_impute), dtype=bool)
		regressors[j] = 0
		for i in xrange(0, X_train.shape[0]):
			if X_train[i, j] == 0 and feature_to_impute[j] != 0:
				X_train[i,j] = models[j].predict(X_train[i,regressors])
		for i in xrange(0, X_test.shape[0]):
			if X_test[i, j] == 0 and feature_to_impute[j] != 0:
				X_test[i,j] = models[j].predict(X_test[i,regressors])
	# Return the imputed matrices.
	return X_train, X_test
	
def remove_missing_data(pX_train, pX_test, pY_train, pY_test, feature_to_impute):
	"""
	Remove missing data from the given array.
	parameters
	pX_train: all rows data
	pX_test: test condition to be considered as empty (ex None)
	pY_train: price columns data
	pY_test: test condition to be considered as empty (ex None)
	feature_to_impute: the featrue to impute on the missing data.
	"""
	X_train =  np.copy(pX_train)
	X_test = np.copy(pX_test)
	Y_train =  np.copy(pY_train)
	Y_test = np.copy(pY_test)
	for i in xrange(X_train.shape[0]-1, 0, -1):
		for j in xrange(0, X_train.shape[1], 1):
			if feature_to_impute[j] != 0 and X_train[i, j] == 0:
				X_train = np.delete(X_train, i, 0)
				Y_train = np.delete(Y_train, i, 0)
				break
	if pX_test == None:
		return X_train, Y_train
	for i in xrange(X_test.shape[0]-1, 0, -1):
		for j in xrange(0, X_test.shape[1], 1):
			if feature_to_impute[j] != 0 and X_test[i, j] == 0:
				X_test = np.delete(X_test, i, 0)
				Y_test = np.delete(Y_test, i, 0)
				break
	return X_train, X_test, Y_train, Y_test

def mean_imputation_pure(pX_train, pX_test, feature_to_impute):
	X_train =  np.copy(pX_train)
	X_test = np.copy(pX_test)
	for i in xrange(0, len(feature_to_impute)):
		if feature_to_impute[i] == 0:
			continue
		non_zeros = 0
		for j in xrange(0, X_train.shape[0]):
			if X_train[j, i] != 0:
				non_zeros += 1
		mean = np.sum(X_train[:, i])/float(non_zeros)

		for j in xrange(0, X_train.shape[0]):
			if X_train[j, i] == 0:
				X_train[j, i] = mean
		for j in xrange(0, X_test.shape[0]):
			if X_test[j, i] == 0:
				X_test[j, i] = mean
				
	return X_train, X_test
	
def mean_imputation_by_type(pX_train, pX_test, feature_to_impute):
	X_train =  np.copy(pX_train)
	X_test = np.copy(pX_test)
	for i in xrange(0, len(feature_to_impute)):
		if feature_to_impute[i] == 0:
			continue
		means = [0] * 9
		sums = [0] * 9
		non_zeros = [0] * 9
		for j in xrange(0, X_train.shape[0]):
			ix = 0
			for k in xrange(21, 30):
				if pX_train[j, k] == 1:
					ix = k - 21
			if X_train[j, i] != 0:
				non_zeros[ix] += 1
				sums[ix] += X_train[j,i]
		#print non_zeros
		for k in xrange(0, len(means)):
			if non_zeros[k] != 0:
				means[k] = sums[k]/float(non_zeros[k])
		#print means
		for j in xrange(0, X_train.shape[0]):
			ix = 0
			for k in xrange(21, 30):
				if pX_train[j, k] == 1:
					ix = k - 21
			if X_train[j, i] == 0:
				X_train[j, i] = means[ix]
		for j in xrange(0, X_test.shape[0]):
			ix = 0
			for k in xrange(21, 30):
				if pX_train[j, k] == 1:
					ix = k - 21
			if X_test[j, i] == 0:
				X_test[j, i] = means[ix]
				
	return X_train, X_test
	
def remove_years(pData):
	data = np.copy(pData)
	count = 0
	for i in xrange(data.shape[0]-1, 0, -1):
		for j in xrange(6, 14):
			if data[i, j] == 1:
				data = np.delete(data, i, 0)
				count += 1
				break
	print count
	return data
	
def remove_bad_types(pData):
	data = np.copy(pData)
	for i in xrange(data.shape[0]-1, 0, -1):
		if data[i, 22] == 1 or data[i, 25] == 1 or data[i,27] == 1 or data[i,28] == 1:
			data = np.delete(data, i, 0)
	for i in [28, 27, 25, 22]:
		data = np.delete(data, i, 1)
	return data
def fix_sq_feet(pData):
	"""
	Give input as n dimensional array as pdata
	fix the square feet value of the data
	returns th n dimensional array with fixed living_area (normalized)
	"""
	data = np.copy(pData)
	count = 0
	for i in xrange(data.shape[0]-1, 0, -1):
		if data[i, 20] > 500:
			count += 1
			data[i, 20] *= 0.092903
	return data
def remove_too_expensive(pData):
	data = np.copy(pData)
	for i in xrange(data.shape[0]-1, 0, -1):
		if data[i, -1] > 600000:
			data = np.delete(data, i, 0)
	return data
	
def normalize_feature(pX, cols):
	X = np.copy(pX)
	for ix in cols.reverse():
		X[:, ix] = (X[:, ix] - np.mean(X[:, ix]))/np.max(X[:, ix])
	return X

def remove_features(pX, cols):
	X = np.copy(pX)
	for ix in cols:
		X = np.delete(X, ix, 1)
	return X
	
def get_missing_data_stats(X_train, X_test, Y_train, Y_test):
	impute = np.array([0] * X_train.shape[1])
	impute[14] = 2 # num_bed
	impute[15] = 2 # year_built
	impute[18] = 2 # num_room
	impute[19] = 2 # num_bath
	impute[20] = 1 # living_space

	X_train, X_test, Y_train, Y_test = remove_missing_data(X_train, X_test, Y_train, Y_test, impute)
	
	print X_train.shape[0] + X_test.shape[0]

import matplotlib.pyplot as plt
def get_missing_data_plot():
	N = 5
	values = [276, 1492, 1944, 3531, 5276]
	indices = np.arange(N)
	width = 1
	fig, ax = plt.subplots()
	rects1 = ax.bar(indices, values, width, color='r')
	ax.set_ylabel('Number of Samples with Missing Data')
	ax.set_xlabel('Features')
	ax.set_xticks(indices+width/2.0)
	ax.set_xticklabels(('num_bath', 'num_bed', 'year_built', 'living_area', 'num_room'))
	plt.show()
	
	

if __name__=='__main__':
	data = loadData("data/data/final_dataDec.csv")
	data = fix_sq_feet(data)
	#shuffle the records in data
	np.random.shuffle(data)
		
	#Take complete table in Xs
	Xs = data[:, :-1]
	#Take only the price column in Ys
	Ys = data[:, -1]
	
	# Fill in the missing data. 1 == Continuous Feature. 2 == Discrete Feature.
	impute = np.array([0] * Xs.shape[1]) #new array with length equals to the columns of tables with all entries 0
	impute[14] = 2 # num_bed
	impute[15] = 2 # year_built
	impute[18] = 2 # num_room
	impute[19] = 2 # num_bath
	impute[20] = 1 # living_space
	Xs_removed, Ys_removed = remove_missing_data(Xs, None, Ys, None, impute)
	
	#80% considered as training set and 20 % considered as final test records
	#consider complete set
	split = int(Xs.shape[0] * 0.8)
	Xs_train_test = Xs[:split, :]
	Xs_final_test = Xs[split:, :]
	Ys_train_test = Ys[:split]
	Ys_final_test = Ys[split:]
	
	#consider removed set
	split = int(Xs_removed.shape[0] * 0.8)
	Xs_removed_train_test = Xs_removed[:split, :]
	Xs_removed_final_test = Xs_removed[split:, :]
	Ys_removed_train_test = Ys_removed[:split]
	Ys_removed_final_test = Ys_removed[split:]
	
	#get_missing_data_stats(np.copy(Xs[0:5000,:]), np.copy(Xs[5000:,:]), np.copy(Ys[0:5000]), np.copy(Ys[5000:]))
	#get_missing_data_plot()
	
	# First we optimize kNearest Neighbors. 
	kf_full = cross_validation.KFold(Ys_train_test.shape[0], n_folds=5)# two parameters first is size of elements and k val
	for k in [1, 5, 10, 25, 50]:
# 	for k in [1, 5]:
		accs = []
		for train_index, test_index in kf_full:
			X_train, X_test = np.abs(Xs_train_test[train_index]), np.abs(Xs_train_test[test_index])
			Y_train, Y_test = Ys_train_test[train_index], Ys_train_test[test_index]
			
			X_train, X_test = mean_imputation_pure(X_train, X_test, impute)
			#X_train, X_test = EM(X_train, X_test, impute)
		
			clf = KNeighborsRegressor(k)
			clf.fit(X_train, Y_train) 
			acc = clf.predict(X_test)
			
			error = mean_absolute_error(acc, Y_test)
			accs.append(error)
		print "Imputed (kNN):", k, np.mean(accs)
		
	kf_removed = cross_validation.KFold(Ys_removed_train_test.shape[0], n_folds=5)# two parameters first is size of elements and k val
	for k in [1, 5, 10, 25, 50]:
# 	for k in [1, 5]:
		accs = []
		for train_index, test_index in kf_removed:
			X_train, X_test = Xs_removed_train_test[train_index], Xs_removed_train_test[test_index]
			Y_train, Y_test = Ys_removed_train_test[train_index], Ys_removed_train_test[test_index]
		
			clf = KNeighborsRegressor(k)
			clf.fit(X_train, Y_train) 
			acc = clf.predict(X_test)
			
			error = mean_absolute_error(acc, Y_test)
			accs.append(error)
		print "Removed (kNN):", k, np.mean(accs)
	
	# Then we optimize Lasso Regression.
	kf_full = cross_validation.KFold(Ys_train_test.shape[0], n_folds=5)
	for l in [0.1, 0.3, 1, 3, 10, 33, 100, 333]:
		accs = []
		for train_index, test_index in kf_full:
			X_train, X_test = np.abs(Xs_train_test[train_index]), np.abs(Xs_train_test[test_index])
			Y_train, Y_test = Ys_train_test[train_index], Ys_train_test[test_index]
			
			X_train, X_test = mean_imputation_pure(X_train, X_test, impute)
			#X_train, X_test = EM(X_train, X_test, impute)

			clf = Lasso(l)
			clf.fit(X_train, Y_train) 
			acc = clf.predict(X_test)

			error = mean_absolute_error(acc, Y_test)
			accs.append(error)
		print "Imptued (Lasso):", l, np.mean(accs)
	# Try optimiznig using the data set with missing data removed.
	kf_removed = cross_validation.KFold(Ys_removed_train_test.shape[0], n_folds=5)
	for l in [0.1, 0.3, 1, 3, 10, 33, 100, 333]:
		accs = []
		for train_index, test_index in kf_removed:
			X_train, X_test = Xs_removed_train_test[train_index], Xs_removed_train_test[test_index]
			Y_train, Y_test = Ys_removed_train_test[train_index], Ys_removed_train_test[test_index]
		
			clf = Lasso(l)
			clf.fit(X_train, Y_train) 
			acc = clf.predict(X_test)
			
			error = mean_absolute_error(acc, Y_test)
			accs.append(error)
		print "Removed (Lasso):", l, np.mean(accs)

	# Finally we try linear regression with each missing data method.	
	kf_full = cross_validation.KFold(Ys_train_test.shape[0], n_folds=5)
	accs = []
	for train_index, test_index in kf_full:
		X_train, X_test = np.abs(Xs_train_test[train_index]), np.abs(Xs_train_test[test_index])
		Y_train, Y_test = Ys_train_test[train_index], Ys_train_test[test_index]
		
		X_train, X_test = mean_imputation_pure(X_train, X_test, impute)
		#X_train, X_test = EM(X_train, X_test, impute)
	
		clf = LinearRegression(normalize=True)
		clf.fit(X_train, Y_train) 
		acc = clf.predict(X_test)
		
		error = mean_absolute_error(acc, Y_test)
		accs.append(error)
	print "Imputed (Linear):", np.mean(accs)

	accs = []
	kf_removed = cross_validation.KFold(Ys_removed_train_test.shape[0], n_folds=5)
	for train_index, test_index in kf_removed:
		X_train, X_test = Xs_removed_train_test[train_index], Xs_removed_train_test[test_index]
		Y_train, Y_test = Ys_removed_train_test[train_index], Ys_removed_train_test[test_index]
	
		clf = LinearRegression(normalize=True)
		clf.fit(X_train, Y_train) 
		acc = clf.predict(X_test)
		
		error = mean_absolute_error(acc, Y_test)
		accs.append(error)
	print "Removed (Linear):", np.mean(accs)
	
	# Now we train on the full test data and test using the optimized parameters.
	lr = LinearRegression()
	lasso = Lasso(100)
	lr.fit(Xs_removed_train_test, Ys_removed_train_test)
	lasso.fit(Xs_removed_train_test, Ys_removed_train_test)
	knn = KNeighborsRegressor(5)
	knn.fit(Xs_removed_train_test, Ys_removed_train_test)
	# View the coefficients for analysis of parameters.
	print "Linear/Lasso coefficients."
	print lr.coef_
	print lasso.coef_
	
	print "Linear/Lasso/kNN on held out test set"
	print mean_absolute_error(Ys_removed_final_test, lr.predict(Xs_removed_final_test))
	print mean_absolute_error(Ys_removed_final_test, lasso.predict(Xs_removed_final_test))
	print mean_absolute_error(Ys_removed_final_test, knn.predict(Xs_removed_final_test))
