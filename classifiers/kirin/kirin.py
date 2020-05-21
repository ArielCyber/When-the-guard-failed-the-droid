

import reports 
import machine
import pandas as pd



def run(data, reports_):

    reports_path = [reports_ + 'kirin.csv']

    reports_items = [[ 'group','attack',' ', 'test_recall', 'test_confusion_matrix', ' ',  'test_manipulated_recall','test_manipulatedconfusion_matrix',' ','num of observations']]

    reports_ = tuple(zip(reports_path, reports_items))

    machine.build_reports(reports_)

    data=pd.read_csv(data)

    data=machine.get_data(data,[
        'perm: SET_DEBUG_APP','perm: READ_PHONE_STATE','perm: RECORD_AUDIO','perm: INTERNET','perm: PROCESS_OUTGOING_CALLS','perm: ACCESS_FINE_LOCATION','perm: RECEIVE_BOOT_COMPLETED',
        'perm: ACCESS_COARSE_LOCATION','perm: RECEIVE_SMS','perm: WRITE_SMS','perm: SEND_SMS','perm: UNINSTALL_SHORTCUT','perm: INSTALL_SHORTCUT','perm: SET_PREFERRED_APPLICATIONS','call__'])
    
    train,test,mani=machine.divide_data(data)
    
    features = []
    f=['perm: SET_DEBUG_APP','perm: READ_PHONE_STATE','perm: RECORD_AUDIO','perm: INTERNET','perm: PROCESS_OUTGOING_CALLS','perm: ACCESS_FINE_LOCATION','perm: RECEIVE_BOOT_COMPLETED',
        'perm: ACCESS_COARSE_LOCATION','perm: RECEIVE_SMS','perm: WRITE_SMS','perm: SEND_SMS','perm: UNINSTALL_SHORTCUT','perm: INSTALL_SHORTCUT','perm: SET_PREFERRED_APPLICATIONS','call__']

       
    for i in range(5):
        features.append(f)

    print('Running kirin...') 
    
    for group in range(5):
        for mani_group in range(6):
            m,t=machine.keep_same_apks(mani[group][mani_group],test[group])
            X_train, X_test, X_mani, y_train, y_test, y_mani, top_features = machine.get_X_y_features(len(f),features, group,t, train, m)
            reports.kirin( str(group),str(mani_group+1), reports_[0][0],  X_test,y_test,X_mani,  y_mani)


if __name__== "__main__":

    #getting paths
    data="data.csv"
    reports_="" #"reports\\"
	
    #running the machine
    run(data,reports_)



