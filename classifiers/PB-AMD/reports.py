import algorithms
import concurrent.futures
import math

# X_train, X_test,X_test_manipulated, y_train, y_test,y_test_manipulated
def random_forest(num_of_features,features,group,group_mani,report,X_train, X_test,X_test_manipulated, y_train, y_test,y_test_manipulated):

    dict1={'num of trees':0,'criterion':0,'min_samples_split':0,'recall':0,'confusion matrix':0}
    dict2={'recall':0,'confusion matrix':0}

    with concurrent.futures.ProcessPoolExecutor() as executor:
        results = [executor.submit(algorithms.random_forest_, X_train, y_train, X_test,X_test_manipulated, n,criteria,  min_samples_split ) for n in range(20,301,20) for criteria in ['entropy','gini']  for min_samples_split in [3,11,21,51,101,201,401,601,801]]
    
    max1,max2=0,0

    for f_ in concurrent.futures.as_completed(results):
        result = f_.result()
        get_perfomances(y_test, result[0], dict1)
        get_perfomances(y_test_manipulated, result[1], dict2)
        dict1['num of trees']=(result[2])
        dict1['criterion']=(result[3])
        dict1['min_samples_split']=(result[4])
        x = [group,group_mani,' ',num_of_features,features, dict1['num of trees'],dict1['criterion'],dict1['min_samples_split'],' ', dict1['recall'], dict1['confusion matrix'],' ',dict2['recall'], dict2['confusion matrix'],' ',X_test_manipulated.shape[0]]
        r1,r2=dict1['recall'],dict2['recall']
        if r1>max1:
           max1=r1
           x1=x
        if r2>max2:
           max2=r2
           x2=x
  
    if max1!=0:
       write_to_csv(report,x1)
    if max2!=0:
       write_to_csv(report,x2)

	
	
def cart(num_of_features,features,group,group_mani,report,X_train, X_test,X_test_manipulated, y_train, y_test,y_test_manipulated):
    dict={'criterion':0,'min_samples_split':0, 'recall':0,'confusion matrix':0}
    dict1={'recall':0,'confusion matrix':0}
	
    with concurrent.futures.ProcessPoolExecutor() as executor:
        results=[executor.submit(algorithms.decision_tree_,X_train, y_train, X_test,X_test_manipulated, criteria,  min_samples_split )  for criteria in ['entropy','gini']  for min_samples_split in [3,11,21,51,101,201,401,601,801]]

    max1,max2=0,0
    for f_ in concurrent.futures.as_completed(results):
        result=f_.result()
        get_perfomances(y_test, result[0], dict)
        get_perfomances(y_test_manipulated, result[1], dict1)
        dict['criterion']=(result[2])
        dict['min_samples_split']=result[3]
        x = [group,group_mani,' ', num_of_features,features, dict['criterion'],dict['min_samples_split'],' ', dict['recall'], dict['confusion matrix'],' ',dict1['recall'], dict1['confusion matrix'],' ',X_test_manipulated.shape[0]]
        r1,r2=dict['recall'],dict1['recall']
        if r1>max1:
           max1=r1
           x1=x
        if r2>max2:
           max2=r2
           x2=x

    if max1!=0:
       write_to_csv(report,x1)
    if max2!=0:
       write_to_csv(report,x2)

	
	
def C45(num_of_features,features,group,group_mani,report,X_train, X_test,X_test_manipulated, y_train, y_test,y_test_manipulated):
    import Chefboost.Chefboost as Chef
    import pandas as pd
    df_train = pd.DataFrame(data=X_train)
    df_train['Decision'] = y_train
    config = {'algorithm': 'C4.5'}
    model = Chef.fit(df_train, config)

    df_test = pd.DataFrame(data=X_test)

    y_pred_1=[]
    for index,instance in df_test.iterrows():
        y_pred_1.append(Chef.predict(model, instance))
    y_pred1=[]
    for i in y_pred_1:
        if i is None:
            y_pred1.append(0)
        else:
            y_pred1.append(int(round(i)))

    df_test1 = pd.DataFrame(data=X_test_manipulated)

    y_pred_2=[]
    for index,instance in df_test1.iterrows():
        y_pred_2.append(Chef.predict(model, instance))
    y_pred2=[]
    for i in y_pred_2:
        if i is None:
            y_pred2.append(0)
        else:
            y_pred2.append(int(round(i)))
			
	
    dict1 = {'recall': 0, 'confusion matrix': 0}
    get_perfomances(y_test, y_pred1, dict1)
    dict2 = {'recall': 0, 'confusion matrix': 0}
    get_perfomances(y_test_manipulated, y_pred2, dict2)

    list_=[group,group_mani,'',num_of_features,features,' ',dict1['recall'],dict1['confusion matrix'],' ',dict2['recall'],dict2['confusion matrix'],' ',X_test_manipulated.shape[0]]
    write_to_csv(report,list_)

def rotation_forest(group,group_mani,report,x_train, x_test,x_test_manipulated, y_train, y_test,y_test_manipulated,lock):
    import RotationForest as rf
    dict={'num of sub trees':0,'features at sub tree':0,'feature_subsets':0, 'recall':0,'confusion matrix':0}
    dict1={'recall':0,'confusion matrix':0}

    models, r_matrices, feature_subsets, d, k=rf.build_rotationtree_model( x_train, y_train, 23, 7)
    result=rf.predict( models, r_matrices, x_test,x_test_manipulated,feature_subsets,d,k)


    get_perfomances(y_test,result[0],dict)
    get_perfomances(y_test_manipulated,result[1],dict1)
    dict['feature_subsets']=(result[2])
    dict['num of sub trees']=(result[3])
    dict['features at sub tree']=(result[4])
    group_mani+=1
    x1 = [ group,str(group_mani),' ',dict['num of sub trees'], dict['features at sub tree'],dict['feature_subsets'],' ', dict['recall'], dict['confusion matrix'],' ', dict1['recall'], dict1['confusion matrix']]

    lock.acquire()
    write_to_csv(report, x1)
    lock.release()



def kirin(group,group_mani,report,X_test,y_test,X_test_manipulated,y_test_manipulated):
    dict1={'recall':0,'confusion matrix':0}
    y_pred1=algorithms.kirin_(X_test)
    get_perfomances(y_test, y_pred1, dict1)
    dict2={'recall':0,'confusion matrix':0}
    y_pred2=algorithms.kirin_(X_test_manipulated)
    get_perfomances(y_test_manipulated, y_pred2, dict2)
    x = [group, group_mani,' ', dict1['recall'], dict1['confusion matrix'], ' ', dict2['recall'], dict2['confusion matrix'],' ',X_test_manipulated.shape[0]]
    write_to_csv(report, x)
    

def dl(group,mani_group,num_of_features,layer1,layer2,report, X_train, X_test, X_mani,y_train, y_test,y_mani):
    dict={'recall':0,'confusion matrix':0}
    dict1={'recall':0,'confusion matrix':0}

    y_pred,y_pred_manipulated=algorithms.dl_(X_train,y_train,X_test,X_mani,layer1,layer2,num_of_features)

    get_perfomances(y_test,y_pred,dict)
    get_perfomances(y_mani,y_pred_manipulated,dict1)
    x = [group,mani_group,' ',num_of_features, layer1, layer2,' ', dict['recall'], dict['confusion matrix'],' ', dict1['recall'], dict1['confusion matrix']]
    write_to_csv(report, x)    

	

def get_perfomances(y, y_pred,dict):

    from sklearn.metrics import accuracy_score, f1_score, confusion_matrix, recall_score,precision_score
    import numpy

    recall=recall_score(y,y_pred,zero_division=1)

    dict['confusion matrix']=(numpy.array_str(confusion_matrix(y, y_pred)))
    dict['recall']=(round(recall_score(y,y_pred,zero_division=1),2))



def write_to_csv(file_name,list_):
    import csv
    with open(file_name, 'a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(list_)



