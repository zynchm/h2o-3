from __future__ import division
from __future__ import print_function
from past.utils import old_div
import sys
sys.path.insert(1,"../../../")
import h2o
from tests import pyunit_utils
from h2o.estimators.glm import H2OGeneralizedLinearEstimator
import pandas as pd
import numpy as np

# test missing_value handling for interactions.  Test all cases of skip, meanImputation and plug values
def interactions():
    # test interaction of enum and enum columns
    pd_df_cat_cat_NA = pd.DataFrame(np.array([[1,0,1,0], ["a", "b", "a", "b"], ['Foo', 'UNKNOWN', 'Foo', 'Bar']]).T,
                                    columns=['label', 'categorical_feat', 'categorical_feat2'])
    pd_df_cat_cat = pd.DataFrame(np.array([[1,0,1,0], ["a", "b", "a", "a"], ['Foo', 'Foo', 'Foo', 'Bar']]).T,
                                 columns=['label', 'categorical_feat', 'categorical_feat2'])
    performOneTest(pd_df_cat_cat_NA, pd_df_cat_cat, interactionColumn= ['categorical_feat', 'categorical_feat2'],
                   xcols=['categorical_feat', 'categorical_feat2'])
    
    # test interaction of enum and num columns
    pd_df_cat_num_NA = pd.DataFrame(np.array([[1,0,1,0], [1,2,3,4], ['Foo', 'UNKNOWN', 'Foo', 'Bar']]).T,
                         columns=['label', 'numerical_feat', 'categorical_feat'])
    pd_df_cat_num = pd.DataFrame(np.array([[1,0,1,0], [1,2,3,4], ['Foo', 'Foo', 'Foo', 'Bar']]).T,
                                 columns=['label', 'numerical_feat', 'categorical_feat'])
    performOneTest(pd_df_cat_num_NA, pd_df_cat_num, interactionColumn= ['numerical_feat', 'categorical_feat'], 
                   xcols=['numerical_feat', 'categorical_feat'])

    # test interaction of num and num columns
    pd_df_num_num_NA = pd.DataFrame(np.array([[1,0,1,0], [1,2,3,4], [2, 3, float('NaN'), 1]]).T,
                                 columns=['label', 'numerical_feat', 'numerical_feat2'])
    pd_df_num_num = pd.DataFrame(np.array([[1,0,1,0], [1,2,3,4], [2, 3, 2, 2]]).T,
                                    columns=['label', 'numerical_feat', 'numerical_feat2'])
    performOneTest(pd_df_num_num_NA, pd_df_num_num, interactionColumn= ['numerical_feat', 'numerical_feat2'],
                   xcols=['numerical_feat', 'numerical_feat2'])

def performOneTest(frameWithNA, frameWithoutNA, interactionColumn, xcols):
    # default missing value handling = meanImputation
    h2o_df_NA = h2o.H2OFrame(frameWithNA, na_strings=["UNKNOWN"])
    h2o_df_NA_Valid = h2o.H2OFrame(frameWithNA, na_strings=["UNKNOWN"])
    modelNA = H2OGeneralizedLinearEstimator(family = "Binomial", alpha=0, lambda_search=False,
                                            interactions=interactionColumn, missing_value_handling="skip")
    modelNA.train(x=xcols, y='label', training_frame=h2o_df_NA)
    coef_m_NA = modelNA._model_json['output']['coefficients_table']
    
    h2o_df = h2o.H2OFrame(frameWithoutNA, na_strings=["UNKNOWN"])
    model = H2OGeneralizedLinearEstimator(family = "Binomial", alpha=0, lambda_search=False, 
                                          interactions=interactionColumn)
    model.train(x=xcols, y='label', training_frame=h2o_df)
    coef_m =  model._model_json['output']['coefficients_table']
 
    pyunit_utils.compare_two_arrays(coef_m_NA, coef_m)

    
if __name__ == "__main__":
 # h2o.init(ip="192.168.86.28", port=54321, strict_version_check=False)
  pyunit_utils.standalone_test(interactions)
else:
 # h2o.init(ip="192.168.86.28", port=54321, strict_version_check=False)
  interactions()
