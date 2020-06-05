from builtins import range
import sys
sys.path.insert(1,"../../../")
import h2o
from tests import pyunit_utils
from h2o.estimators.glm import H2OGeneralizedLinearEstimator

# Verify checkpointing for binomial with IRLSM
def tesGLMtCheckpointing():
    train = h2o.import_file(path=pyunit_utils.locate("smalldata/glm_test/binomial_20_cols_10KRows.csv"))
    for ind in range(10):
        train[ind] = train[ind].asfactor()
    train["C21"] = train["C21"].asfactor()
    Y = "C21"
    X = list(range(0,20))

    solvers = ["irlsm"]
    for solver in solvers:
        print("Checking checkpoint for binomials with solver {0}".format(solver))
        buildModelCheckpointing(train, X, Y, "binomial", solver)
    
    
def buildModelCheckpointing(training_frame, x_indices, y_index, family, solver):
    split_frames = training_frame.split_frame(ratios=[0.9], seed=12345)
    model = H2OGeneralizedLinearEstimator(family=family, max_iterations=3, solver=solver, lambda_search=True)
    model.train(training_frame=split_frames[0], x=x_indices, y=y_index, validation_frame=split_frames[1])
    modelCheckpoint = H2OGeneralizedLinearEstimator(family=family, checkpoint=model.model_id, solver=solver, lambda_search=True)
    modelCheckpoint.train(training_frame=split_frames[0], x=x_indices, y=y_index, validation_frame=split_frames[1])

    modelLong = H2OGeneralizedLinearEstimator(family=family, solver=solver, lambda_search=True) # allow to run to completion
    modelLong.train(training_frame=split_frames[0], x=x_indices, y=y_index, validation_frame=split_frames[1])

    pyunit_utils.assertEqualCoeffDicts(modelCheckpoint.coef(), modelLong.coef(), tol=1e-3)

if __name__ == "__main__":
    pyunit_utils.standalone_test(tesGLMtCheckpointing)
else:
    tesGLMtCheckpointing()