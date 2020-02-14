""" Dataset Features analysis :

 - audit dataset  : get informations on the data (NA, features type, low variance features, ...)
 - is_date : detect if an object/num feature is a date
 - get_all_dates : identify all dates features in a DataFrame and store their names in a list
 - low variance features : identify all features with a low variance (<threshold) and sotre their name in a list
"""
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from MLBG59.Utils.Display import *
from MLBG59.Utils.Utils import get_type_features


def audit_dataset(df, verbose=1):
    """Achieve a short audit of the dataset

    Identify features of each type (num, cat, date), features containing NA and features whose variance is null
        
    Parameters
    ----------
    df : DataFrame
        input dataset
    target : string (Default : None)
        target name
    verbose : int (0/1) (Default : 1)
        get more operations information
            
    Returns
    -------
    list of the x features names
        - x = num : numerical features
        - x = cat : categorical features
        - x = date : date features
        - x = NA : features which contains NA values
        - x = low_var : list of the features with low variance
    """

    # dataset dimensions
    if verbose > 0:
        color_print("Dimensions : ")
        print("  > row number : ", df.shape[0], "\n  > col number : ", df.shape[1])

    #################
    # features type #
    #################
    # numerical
    num_columns = df._get_numeric_data().columns.tolist()
    # date
    date_columns = get_all_dates(df)
    # categorical
    cat_columns = [x for x in df.columns if (x not in num_columns) and (x not in date_columns)]

    if verbose > 0:
        color_print("Features type identification : ")
        print("  > cat : " + str(len(cat_columns)) + ' (' + str(round(len(cat_columns) / df.shape[1] * 100)) + '%)',
              '\n  > num : ' + str(len(num_columns)) + ' (' + str(round(len(num_columns) / df.shape[1] * 100)) + '%)',
              '\n  > dates: ' + str(len(date_columns)) + ' (' + str(
                  round(len(date_columns) / df.shape[1] * 100)) + ' %)')

    ######################
    # NA values analysis
    ######################
    df_col = pd.DataFrame(df.columns.values, columns=['variables'])
    df_col['Nbr NA'] = df.isna().sum().tolist()
    df_col['Taux NA'] = df_col['Nbr NA'] / df.shape[0]
    # features containing NA values
    NA_columns = df_col.loc[df_col['Nbr NA'] > 0].sort_values('Nbr NA', ascending=False).variables.tolist()
    col_des = df_col['Taux NA'].describe()

    if verbose > 0:
        color_print(str(len(NA_columns)) + " features containing NA")
        print('  > Taux NA moyen : ' + str(round(col_des['mean'] * 100, 2)) + '%',
              '\n  >           min : ' + str(round(col_des['min'] * 100, 2)) + '%',
              '\n  >           max : ' + str(round(col_des['max'] * 100, 2)) + '%')

    #########################
    # Low variance features
    #########################
    if verbose > 0:
        color_print('Low variance features')
    low_var_columns = \
        low_variance_features(df, var_list=num_columns, threshold=0, rescale=True, verbose=verbose).index.tolist()

    return num_columns, date_columns, cat_columns, NA_columns, low_var_columns


"""
-------------------------------------------------------------------------------------------------------------------------
"""


def is_date(df, col):
    """Test if a DataFrame feature is recognized as a date (using to_datetime)

    Parameters
    ----------
     df : DataFrame
        input dataset
     col : string
        feature name

    Returns
    -------
    res : boolean
        True if the col is recognized as a date
    """
    # if col is datetime type, res = True
    if df[col].dtype == 'datetime64[ns]':
        return True

    # if col is object type, try apply to_datetime
    elif df[col].dtype == 'object':
        try:
            df_smpl = df.sample(100).copy()
            pd.to_datetime(df_smpl[col])
            return True
        except ValueError:
            return False
        except OverflowError:
            return False


"""
-------------------------------------------------------------------------------------------------------------------------
"""


def get_all_dates(df):
    """Identify all date features of a DataFrame
    
    Parameters
    ----------
     df : DataFrame
        input DataFrame

    Returns
    -------
     list
        list of features recognized as date
    """
    date_list = list()

    for col in df.columns:
        # if col is recognized as date
        if is_date(df, col): date_list.append(col)

    return date_list


"""
-------------------------------------------------------------------------------------------------------------------------
"""


def low_variance_features(df, var_list=None, threshold=0, rescale=True, verbose=1):
    """identify  features with low variance (<= threshold)

    Parameters
    ----------
     df : DataFrame
        input DataFrame
     var_list : list (default : None)
        features to check variance
     threshold : float (default : 0
        variance threshold
     rescale : bool (default : true)
        if yes : use MinMaxScaler on data before computing variance

    Returns
    -------
    list
        list of the variable with low variance
    """
    # if var_list = None, get all numerical features
    # else, exclude features from var_list whose type is not numerical
    var_list = get_type_features(df, 'num', var_list)

    df_bis = df.copy()

    if rescale:
        scler = MinMaxScaler()
        df_bis[var_list] = scler.fit_transform(df_bis[var_list].astype('float64'))

    selected_var = df_bis[var_list].var().loc[df_bis.var() <= threshold]

    if verbose > 0:
        # print('features : ',list(var_list))
        if rescale: print('  **MinMaxScaler [0,1]')
        print('  ', str(len(selected_var)) + ' feature(s) with  variance <= threshold (' + str(threshold) + ')')

    return selected_var.sort_values(ascending=True)
