library(glmnet)
setwd(normalizePath(dirname(R.utils::commandArgs(asValues=TRUE)$"f")))
source("../../../scripts/h2o-r-test-setup.R")

# I have added two parameters to GLMModelOutput: lambda_min and lambda_max.  These parameters will take on the following
# meaning when lambda_search is enabled:
# lambda_max is the first lambda value searched;
# lambda_min is the smallest lambda value that may be searched.  If early-stop is enabled, we may not reach the end to 
# build GLM with lambda_min.

test.glm_lambda_min_max <- function() {
    d <-  h2o.importFile(path = locate("smalldata/logreg/prostate.csv"))
    m = h2o.glm(training_frame=d,x=3:9,y=2,family='binomial',lambda_search=TRUE)
    regpath = h2o.getGLMFullRegularizationPath(m)
    expect_true(abs(regpath$lambdas[1]-m@model$lambda_max) < 1e-10) # should equal
    expect_true(regpath$lambdas[length(regpath$lambdas)] >= m@model$lambda_min) # lambda_min should be the minimum lambda
}

doTest("GLM lambda_min and lambda_max in modelOutput.", test.glm_lambda_min_max)