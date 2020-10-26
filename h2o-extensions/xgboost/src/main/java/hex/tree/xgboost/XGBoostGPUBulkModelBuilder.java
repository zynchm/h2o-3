package hex.tree.xgboost;

import hex.BulkModelBuilder;
import hex.ModelBuilder;
import org.apache.log4j.Logger;
import water.Job;

import java.util.Deque;
import java.util.LinkedList;
import java.util.Set;

public class XGBoostGPUBulkModelBuilder extends BulkModelBuilder {

    private static final Logger LOG = Logger.getLogger(XGBoostGPUBulkModelBuilder.class);

    private final Deque<Integer> availableGpus;

    public XGBoostGPUBulkModelBuilder(
        String modelType,
        Job job,
        ModelBuilder<?, ?, ?>[] modelBuilders,
        int parallelization,
        int updateInc,
        Set<Integer> gpuIds
    ) {
        super(modelType, job, modelBuilders, parallelization, updateInc);
        availableGpus = new LinkedList<>(gpuIds);
        LOG.info("Using parallel GPU building on " + availableGpus.size() + " GPUs.");
        
    }

    @Override
    protected void prepare(ModelBuilder m) {
        XGBoost xgb = (XGBoost) m;
        xgb._parms._gpu_id = availableGpus.pop();
        LOG.info("Building " + xgb.dest() + " on GPU " + xgb._parms._gpu_id);
    }

    @Override
    protected void finished(ModelBuilder m) {
        XGBoost xgb = (XGBoost) m;
        availableGpus.push(xgb._parms._gpu_id);
    }

}
