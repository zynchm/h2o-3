import sys
import os
import tempfile
import time

sys.path.insert(1, os.path.join("..", "..", ".."))
import h2o
from tests import pyunit_utils
from h2o.grid.grid_search import H2OGridSearch
from h2o.estimators.gbm import H2OGradientBoostingEstimator


def grid_ft_resume():
    train = h2o.import_file(path=pyunit_utils.locate("smalldata/iris/iris_wheader.csv"))

    ntrees_opts = [100, 200, 300, 400]
    learn_rate_opts = [0.01, 0.02, 0.03, 0.04, 0.05]
    grid_size = len(ntrees_opts) * len(learn_rate_opts)
    print("max models %s" % grid_size)
    hyper_parameters = {
        "learn_rate": learn_rate_opts,
        "ntrees": ntrees_opts
    }
    
    export_dir = tempfile.mkdtemp()
    print("export_checkpoints_dir=%s" % export_dir)
    grid = H2OGridSearch(
        H2OGradientBoostingEstimator,
        grid_id="grid_ft_resume_test",
        hyper_params=hyper_parameters,
        export_checkpoints_dir=export_dir,
        checkpoint_frames=True
    )
    grid.start(x=list(range(4)), y=4, training_frame=train)
    time.sleep(10)  # give it tome to train some models
    grid.cancel()

    grid = h2o.get_grid(grid.grid_id)
    old_grid_model_count = len(grid.model_ids)
    for x in sorted(grid.model_ids):
        print(x)
    print("Baseline grid has %d models" % old_grid_model_count)
    h2o.remove_all()

    loaded = h2o.load_grid("%s/%s" % (export_dir, grid.grid_id), load_frames=True)
    assert loaded is not None
    assert len(grid.model_ids) == old_grid_model_count
    loaded_train = h2o.H2OFrame.get_frame(train.frame_id)
    assert loaded_train is not None, "Train frame was not loaded"
    loaded.hyper_params = hyper_parameters
    loaded.train(x=list(range(4)), y=4, training_frame=loaded_train)
    for x in sorted(loaded.model_ids):
        print(x)
    print("Newly grained grid has %d models" % len(loaded.model_ids))
    assert len(loaded.model_ids) == grid_size, "The full grid was not trained."
    

if __name__ == "__main__":
    pyunit_utils.standalone_test(grid_ft_resume)
else:
    grid_ft_resume()
