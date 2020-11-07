import sys
sys.path.insert(1,"../../../")
import h2o
from tests import pyunit_utils
from h2o.estimators.gam import H2OGeneralizedAdditiveEstimator as gam

# This test will generate synthetic GAM dataset.  If given to a GAM model, it should be able to perform well with 
# this dataset since the assumptions associated with GAM are used to generate the dataset.
def test_define_dataset():
    family = 'binomial' # can be any valid GLM families
    nrow = 100000
    ncol = 10
    realFrac = 0.4
    intFrac = 0.3
    enumFrac = 0.3
    missing_fraction = 0
    factorRange= 50
    numericRange = 10
    targetFactor = 1
    numGamCols = 1
    
    assert numGamCols <= ncol*realFrac, "Number of real columns {0} should exceed the number of gam columns " \
                                       "{1}".format(ncol*realFrac, numGamCols) # gam can be only real columns
    gamDataSet = generate_dataset(family, nrow, ncol, realFrac, intFrac, enumFrac, missing_fraction, factorRange, 
                                  numericRange, targetFactor, numGamCols)
    #h2o.download_csv(gamDataSet, "/Users/.../dataset.csv") # save dataset
    assert gamDataSet.nrow == nrow, "Dataset number of row: {0}, expected number of row: {1}".format(gamDataSet.nrow, 
                                                                                                     nrow)
    assert gamDataSet.ncol == (1+ncol), "Dataset number of row: {0}, expected number of row: " \
                                                          "{1}".format(gamDataSet.ncol, (1+ncol))
  
def generate_dataset(family, nrow, ncol, realFrac, intFrac, enumFrac, missingFrac, factorRange, numericRange, 
                     targetFactor, numGamCols):
    if family=="binomial":
        responseFactor = 2
    elif family == 'gaussian':
        responseFactor = 1;
    else :
        responseFactor = targetFactor
        
    trainData = random_dataset(nrow, ncol, realFrac=realFrac, intFrac=intFrac, enumFrac=enumFrac, factorR=factorRange, 
                               integerR=numericRange, responseFactor=responseFactor, misFrac=missingFrac)
   
    myX = trainData.names
    myY = 'response'
    myX.remove(myY)
    
    colNames = trainData.names
    colNames.remove("response")
    m = gam(family=family, max_iterations=10, gam_columns = colNames[0:numGamCols])
    m.train(training_frame=trainData,x=myX,y= myY)
    f2 = m.predict(trainData)
    # to see coefficient, do m.coef()
    finalDataset = trainData[myX]
    finalDataset = finalDataset.cbind(f2[0])
    finalDataset.set_name(col=finalDataset.ncols-1, name='response')

    h2o.remove(trainData)
    return finalDataset

def random_dataset(nrow, ncol, realFrac = 0.4, intFrac = 0.3, enumFrac = 0.3, factorR = 10, integerR=100, 
                   responseFactor = 1, misFrac=0.01, randSeed=None):
    fractions = dict()
    if (ncol==1) and (realFrac >= 1.0):
        fractions["real_fraction"] = 1  # Right now we are dropping string columns, so no point in having them.
        fractions["categorical_fraction"] = 0
        fractions["integer_fraction"] = 0
        fractions["time_fraction"] = 0
        fractions["string_fraction"] = 0  # Right now we are dropping string columns, so no point in having them.
        fractions["binary_fraction"] = 0
        
        return h2o.create_frame(rows=nrow, cols=ncol, missing_fraction=misFrac, has_response=True,
                                response_factors = responseFactor, integer_range=integerR,
                                seed=randSeed, **fractions)
    
    real_part = pyunit_utils.random_dataset_real_only(nrow, (int)(realFrac*ncol), misFrac=misFrac, randSeed=randSeed)
    enumFrac = enumFrac + (1-realFrac)/2
    intFrac = 1-enumFrac
    fractions["real_fraction"] = 0  # Right now we are dropping string columns, so no point in having them.
    fractions["categorical_fraction"] = enumFrac
    fractions["integer_fraction"] = intFrac
    fractions["time_fraction"] = 0
    fractions["string_fraction"] = 0  # Right now we are dropping string columns, so no point in having them.
    fractions["binary_fraction"] = 0

    df = h2o.create_frame(rows=nrow, cols=(ncol-real_part.ncol), missing_fraction=misFrac, has_response=True, 
                          response_factors = responseFactor, integer_range=integerR,
                          seed=randSeed, **fractions)
    return real_part.cbind(df)


if __name__ == "__main__":
    pyunit_utils.standalone_test(test_define_dataset)
else:
    test_define_dataset()
