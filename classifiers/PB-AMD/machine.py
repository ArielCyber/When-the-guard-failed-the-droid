

def build_reports(reports):
    #the function builds a new report with titles
    import csv
    for r in reports:
        with open(r[0], 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(r[1])
					
def get_data(data,list_):
    #the function returns a dataframe with the needed features for the machine
    all_columns=data.columns.to_list()
    data_columns=['name','type','group_num','group_mani','category']
    for l in list_:
        data_columns+=[c for c in all_columns if l in c]
    print(len(data_columns))
    return data.loc[:,data_columns]
	
	   
def divide_data(data):

    #the dunction divides the data to 5 groups
    import pandas as pd
    import feature_selection
    train_data,test_data,test_manipulated_data = data[data.category==0],data[data.category==1],data[data.category==2]   
    train_data.drop(columns=['category'],inplace=True)
    test_data.drop(columns=['category'],inplace=True)
    test_manipulated_data.drop(columns=['category'],inplace=True)
    
    train, test, mani = [], [], []

    for i in range(5):
            train_ = train_data[(train_data.type == 0) | (train_data.group_num == i)]
            train_.reset_index(drop=True, inplace=True)
            train_.drop(columns=[ 'group_num','group_mani'], inplace=True)
            test_ = test_data[ (test_data.group_num == i)]
            test_.drop(columns=[ 'group_num','group_mani'], inplace=True)
            test_.reset_index(drop=True, inplace=True)
            mani_ = test_manipulated_data[ (test_manipulated_data.group_num == i)]
            mani_.drop(columns=[ 'group_num'], inplace=True)
            m=[]
            t=0
            for j in range(1,7,1):
                m.append(mani_[mani_.group_mani==j])   
                m[t].reset_index(drop=True, inplace=True)   
                m[t].drop(columns=['group_mani'], inplace=True)
                t+=1                
            train.append(train_)
            test.append(test_)
            mani.append(m)
            #print(train[i].shape,test[i].shape,mani[i][0].shape,mani[i][1].shape,mani[i][2].shape,mani[i][3].shape,mani[i][4].shape,mani[i][5].shape)

    return train,test,mani

def div_data(data,i):

    #the dunction divides the data to 5 groups
    import pandas as pd
    import feature_selection
    train_data,test_data,test_manipulated_data = data[data.category==0],data[data.category==1],data[data.category==2]   
    train_data.drop(columns=['category'],inplace=True)
    test_data.drop(columns=['category'],inplace=True)
    test_manipulated_data.drop(columns=['category'],inplace=True)
    
    train_data=train_data[(train_data.type==0) | (train_data.group_num==i)]
    train_data.reset_index(drop=True, inplace=True)
    train_data.drop(columns=[ 'group_num','group_mani'], inplace=True)
    test_data=test_data[test_data.group_num==i]
    test_data.drop(columns=[ 'group_num','group_mani'], inplace=True)
    test_data.reset_index(drop=True, inplace=True)
    test_manipulated_data.drop(columns=[ 'group_num'], inplace=True)
    m=[]
    t=0
    for j in range(1,7,1):
                m.append(test_manipulated_data[test_manipulated_data.group_mani==j])   
                m[t].reset_index(drop=True, inplace=True)   
                m[t].drop(columns=['group_mani'], inplace=True)
                t+=1                
            #print(train[i].shape,test[i].shape,mani[i][0].shape,mani[i][1].shape,mani[i][2].shape,mani[i][3].shape,mani[i][4].shape,mani[i][5].shape)

    return train_data,test_data,m
	
def get_X_y_features(num_of_features,features,group,test,train,mani):
        import pandas as pd
        j=group
        top_features = features[j][0:num_of_features]

        train_ = train[j].loc[:, top_features + ['type']]
        """
        for c in train_.columns:
            if c not in test.columns:
                test[c] = pd.Series([0] * test.shape[0])
            if c not in mani.columns:
                print(1)
                print(c)
                mani[c] = pd.Series([0] * mani.shape[0])
        #print(mani[j].shape[0])
        """
        test_ = test.loc[:, top_features + ['type']]
        mani_ = mani.loc[:, top_features + ['type']]

        X_train = train_.loc[:, ~train_.columns.isin(['type'])]
        X_test = test_.loc[:, ~test_.columns.isin(['type'])]
        X_mani = mani_.loc[:, ~mani_.columns.isin(['type'])]

        y_train = train_.type
        y_test = test_.type
        y_mani = mani_.type
        
        return X_train,X_test,X_mani,y_train,y_test,y_mani,top_features
        
def keep_same_apks(test,mani):
    
    test['cat']=1
    mani['cat']=2
    
    
    x=test.append(mani)
    sum=x.groupby('name').type.sum()
    sum=sum[sum==2]
    sum=sum.index.to_list()
    x=x[x.name.isin(sum)]
    
    
    test=x[x.cat==1]
    mani=x[x.cat==2]
    
    test.drop(columns=['cat'],inplace=True)
    mani.drop(columns=['cat'],inplace=True)
    
    return test,mani
    

        
