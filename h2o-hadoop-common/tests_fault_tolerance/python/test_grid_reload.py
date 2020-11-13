from __future__ import print_function
import sys
import os
import time
sys.path.insert(1, os.path.join("..", "..", "..", "h2o-py"))
from tests import pyunit_utils
import fault_tolerance_utils as utils
import h2o
from h2o.grid.grid_search import H2OGridSearch
from h2o.estimators.gbm import H2OGradientBoostingEstimator
import unittest


class GridReloadTest(unittest.TestCase):

    def test_frame_reload(self):
        name_node = pyunit_utils.hadoop_namenode()
        work_dir = "hdfs://%s%s" % (name_node, utils.get_workdir())
        dataset = "/datasets/iris_wheader.csv"

        ntrees_opts = [100, 200, 300, 400]
        learn_rate_opts = [0.01, 0.02, 0.03, 0.04, 0.05]
        grid_size = len(ntrees_opts) * len(learn_rate_opts)
        print("max models %s" % grid_size)
        grid_id = "grid_ft_resume"
        hyper_parameters = {
            "learn_rate": learn_rate_opts,
            "ntrees": ntrees_opts
        }
        
        try:
            cluster_1 = utils.start_cluster("grid1")
            h2o.connect(url=cluster_1)
            train = h2o.import_file(path="hdfs://%s%s" % (name_node, dataset))
            grid = H2OGridSearch(
                H2OGradientBoostingEstimator,
                grid_id=grid_id,
                hyper_params=hyper_parameters,
                export_checkpoints_dir=work_dir,
                checkpoint_frames=True
            )
            grid.start(x=list(range(4)), y=4, training_frame=train)
            time.sleep(10)
            h2o.connection().close()
        finally:
            utils.stop_cluster("grid1")
        
        try:
            cluster_2 = utils.start_cluster("grid2")
            h2o.connect(url=cluster_2)
            loaded_train = h2o.H2OFrame.get_frame(train.frame_id)
            loaded = h2o.load_grid("%s/%s" % (work_dir, grid_id), load_frames=True)
            print("models after first run:")
            for x in sorted(loaded.model_ids):
                print(x)
            loaded.hyper_params = hyper_parameters
            loaded.train(x=list(range(4)), y=4, training_frame=loaded_train)
            print("models after second run:")
            for x in sorted(loaded.model_ids):
                print(x)
            print("Newly grained grid has %d models" % len(loaded.model_ids))
            self.assertEqual(len(loaded.model_ids), grid_size, "The full grid was not trained.")
            h2o.connection().close()
        finally:
            utils.stop_cluster("grid2")


if __name__ == '__main__':
    unittest.main()
