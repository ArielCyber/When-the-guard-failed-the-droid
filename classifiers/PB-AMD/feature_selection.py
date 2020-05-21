
from math import log2,log10
import pandas as pd

def by_info_gain(data):
     #the function a dataframe with the features and the labels, and the number of features to select
     #returns a list of features which are ordered by information gain score
     data.drop(columns=['name'],inplace=True)
     #caculating the entropy before the split
     number_of_samples=len(data.loc[:,'type'])
     percentage_type_0=len(data[data['type']==0])/number_of_samples
     percentage_type_1=len(data[data['type']==1])/number_of_samples
     entropy_before_split=-(percentage_type_0*log2(percentage_type_0)+percentage_type_1*log2(percentage_type_1))

     df = pd.DataFrame(columns=['feature', 'info_gain'])

     # caculating the entropy after the split, for every sample
     for i in data.columns:
       if (i!='type'):
           
         data_=data.loc[:,[i,'type']]
         
         #getting the percentage of every type in the left node and in the right node
         left=data_.loc[data_.loc[:,i]==0]
         len_left=len(left)
         left_percentage=len_left/number_of_samples

         right=data_.loc[data_.loc[:,i]==1]
         len_right=len(right)
         right_percentage=len_right/number_of_samples

         if (len_left==0):
             len_left=1
         if (len_right==0):
             len_right=1      
    
         #getting the percentage of every type in the children of the left node and the right node
         left_0_percentage=len(left[left.loc[:,'type']==0])/len_left
         left_1_percentage=len(left[left.loc[:,'type']==1])/len_left
         right_0_percentage=len(right[right.loc[:,'type']==0])/len_right
         right_1_percentage=len(right[right.loc[:,'type']==1])/len_right
         
         #calculating entropy at each side
         entropy_left=0
         if ((left_0_percentage==0) or (left_1_percentage==0)): 
             entropy_left=0
         else:
             entropy_left=-(left_0_percentage*log2(left_0_percentage)+left_1_percentage*log2(left_1_percentage))
         entropy_right=0
         if ((right_0_percentage==0) or (right_1_percentage==0)):
             entropy_right=0
         else:
             entropy_right=-(right_0_percentage*log2(right_0_percentage)+right_1_percentage*log2(right_1_percentage))
         
         #calculating the entropy after split
         entropy_after_split=(left_percentage*entropy_left+right_percentage*entropy_right)
         
         #getting the information gain
         info_gain= entropy_before_split-entropy_after_split
         df2 = pd.DataFrame([[i, info_gain]], columns=['feature', 'info_gain'])
         df=pd.concat([df,df2]) 
     df.sort_values(by='info_gain', ascending=False,inplace=True)
     top_features=df['feature'].to_list()
     return top_features


def by_tf_idf(data):
    # gets a dataframe with the features and the number of features to select
    # returns a list of features which are ordered by tf_idf scores

    data1=data.drop(columns=['perm_rate','type'])
    
    #samples counter
    num_of_samples=data1.shape[0]
    
    #the number of samples where each feature appears
    num_of_appearances=data1.sum(axis=0)
    columns_to_delete=num_of_appearances[num_of_appearances==0]
    columns_to_delete=columns_to_delete.index.to_list()
    data1.drop(columns=columns_to_delete,inplace=True)
    num_of_appearances=data1.sum(axis=0)
    
    div=num_of_samples/num_of_appearances
    div=div.fillna(0)
    
    D=[]
    for d in div:
           D.append(log10(d))

           
    #getting the tf part
           
    # 1  / the number of features at each sample -> weight of each feature in the sample
    percentage=pd.Series(1/data1.sum(axis=1))
    percentage=percentage.fillna(0)
    percentage=percentage.to_list()

    #calculating tf-idf -> sum(log*percentage) for every feature
    columns=data1.columns.to_list()

    sum_=[(data1[c].multiply(percentage)).sum(axis=0)*D[columns.index(c)] for c in columns ]


    #getting the top features
    dict_=zip(columns,sum_)
    df_=pd.DataFrame(data=dict_)
    df_.sort_values(by=[1],ascending=False,inplace=True)
    top_features=df_.iloc[:,0].to_list()
    return top_features


def by_boruta(data):

    import numpy as np
    from sklearn.ensemble import RandomForestClassifier
    from boruta import BorutaPy
    y=data.loc[:,'type'].values
    y=y.astype(int)
    X=data.drop(columns=['type'])
    features=X.columns.to_list()
    X=X.values
    X=X.astype(int)
    rf = RandomForestClassifier(n_jobs=-1, class_weight='balanced')
    feat_selector = BorutaPy(rf, n_estimators='auto', verbose=2)
    feat_selector.fit(X, y)
    df=pd.DataFrame(data={'features':features,'ranking':feat_selector.ranking_})
    #df.columns = [col.strip() for col in list(df.columns)]
    #print(df.columns.to_list());
    df.sort_values(["ranking"],axis="rows",ascending=[False],inplace=True)
    #print(df.ranking)
    #print(feat_selector.ranking_)
    #print(df)
    top_features=df.features.to_list()
    return top_features
       
        
if __name__ == "__main__":
     """    
     df=pd.DataFrame(columns=['type','perm_rate','a','b','c','d','e'])
     df.loc[0]=[0,0.6,1,1,1,1,0]
     df.loc[1]=[0,0.2,1,1,1,1,1]
     df.loc[2]=[0,0.3,0,1,1,1,0]
     df.loc[3]=[0,0.5,0,1,0,1,0]
     df.loc[4]=[0,0.2,0,1,0,1,0]
     df.loc[5]=[1,0.3,0,0,1,0,0]
     df.loc[6]=[1,0.1,0,0,0,1,1]
     df.loc[7]=[1,0.5,0,0,0,0,0]
     df.loc[8]=[1,0.1,0,0,1,0,1]
     df.loc[9]=[1,0.2,0,0,0,0,0]
     print(by_tf_idf(df))
     """	 
     df=pd.DataFrame(columns=['name','type','a','b','c','d','e'])
     df.loc[0]=['a',0,1,1,1,1,0]
     df.loc[1]=['b',0,1,1,1,1,1]
     df.loc[2]=['c',0,0,1,1,1,0]
     df.loc[3]=['d',0,0,1,0,1,0]
     df.loc[4]=['e',0,0,1,0,1,0]
     df.loc[5]=['f',1,0,0,1,0,0]
     df.loc[6]=['g',1,0,0,0,1,1]
     df.loc[7]=['h',1,0,0,0,0,0]
     df.loc[8]=['i',1,0,0,1,0,1]
     df.loc[9]=['j',1,0,0,0,0,0]
     print(by_info_gain(df))



