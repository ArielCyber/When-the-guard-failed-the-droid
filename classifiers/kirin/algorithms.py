import numpy as np
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.ensemble import RandomForestClassifier
from sklearn.tree import DecisionTreeClassifier


def pca_(X,n):
        pca = PCA(n_components=n)
        pca.fit(X)
        return pca.fit_transform(X)


def kmeans_(X,n_clusters=2):
        kmeans = KMeans(n_clusters=n_clusters)
        return kmeans.fit_predict(X)

	#	X_train, y_train, X_test,X_test_manipulated, n,criteria,  max_depth
def random_forest_(X_train, y_train,X_test,X_test_manipulated, num,criterion,min_samples_split):
        clf = RandomForestClassifier(n_estimators=num,criterion=criterion,min_samples_split=min_samples_split)
        clf.fit(X_train, y_train)
        return (clf.predict(X_test),clf.predict(X_test_manipulated),num,criterion,min_samples_split)

def decision_tree_(X_train, y_train,X_test,X_test_manipulated,criterion,min_samples_split):
       clf = DecisionTreeClassifier(criterion=criterion,min_samples_split=min_samples_split)
       clf.fit(X_train, y_train)
       return (clf.predict(X_test),clf.predict(X_test_manipulated),criterion,min_samples_split)

def kirin_(X):
        import pandas as pd
        groups=[['perm: SET_DEBUG_APP'],
        ['perm: READ_PHONE_STATE','perm: RECORD_AUDIO','perm: INTERNET'],
        ['perm: PROCESS_OUTGOING_CALLS','perm: RECORD_AUDIO','perm: INTERNET'],
        ['perm: ACCESS_FINE_LOCATION','perm: INTERNET','perm: RECEIVE_BOOT_COMPLETED'],
        ['perm: ACCESS_COARSE_LOCATION','perm: INTERNET','perm: RECEIVE_BOOT_COMPLETED'],
        ['perm: RECEIVE_SMS','perm: WRITE_SMS'],
        ['perm: SEND_SMS','perm: WRITE_SMS'],
        ['perm: UNINSTALL_SHORTCUT','perm: INSTALL_SHORTCUT'],
        ['perm: SET_PREFERRED_APPLICATIONS','call__']]

        y_pred=[0]*X.shape[0]
        for i in range(X.shape[0]):
	        row = X.iloc[i, :]
	        for group in groups:
		        if all(elem in X.columns.to_list() for elem in group)==True:
		            r=row[group]
		            if sum(r)==len(group):
			            y_pred[i]=1

        y_pred=pd.Series(y_pred)
        return y_pred
        
def dl_(X_train,y_train,X_test,X_test_manipulated,layer_1_nodes,layer_2_nodes,input_nodes):
    import keras
    from keras.models import Sequential
    from keras.layers import Dense

    # Initialising the ANN
    classifier = Sequential()

    # Adding the input layer and the first hidden layer
    classifier.add(Dense(units = layer_1_nodes, kernel_initializer = 'uniform', activation = 'relu', input_dim = input_nodes))

    # Adding the second hidden layer
    classifier.add(Dense(units = layer_2_nodes, kernel_initializer = 'uniform', activation = 'relu'))

    # Adding the output layer
    classifier.add(Dense(units = 1, kernel_initializer = 'uniform', activation = 'sigmoid'))

    # Compiling the ANN
    classifier.compile(optimizer = 'adam', loss = 'binary_crossentropy', metrics = ['accuracy'])

    # Fitting the ANN to the Training set
    classifier.fit(X_train, y_train, batch_size = 40, epochs = 100)

    # Part 3 - Making the predictions and evaluating the model

    # Predicting the Test set results
    y_pred_test = classifier.predict(X_test)
    y_pred_test = (y_pred_test > 0.5)

    y_pred_test_manipulated = classifier.predict(X_test_manipulated)
    y_pred_test_manipulated = (y_pred_test_manipulated > 0.5)
    
    return y_pred_test,y_pred_test_manipulated
 








