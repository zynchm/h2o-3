package water.api.schemas3;

import water.H2ONode;
import water.Iced;
import water.fvec.Frame;
import water.api.API;
import water.fvec.Vec;

public class FrameChunksV3 extends SchemaV3<Frame, FrameChunksV3> {

    @API(help="ID of a given frame", json=false)
    public KeyV3.FrameKeyV3 frame_id;

    @API(help="Description of particular chunks", direction=API.Direction.OUTPUT)
    public FrameChunkV3[] chunks;
    
    public static class FrameChunkV3 extends SchemaV3<Iced, FrameChunkV3> {

        @API(help="An identifier unique in scope of a given frame", direction=API.Direction.OUTPUT)
        public int chunk_id;

        @API(help="Number of rows represented byt the chunk", direction=API.Direction.OUTPUT)
        public int row_count;
        
        @API(help="Description of H2O node where the chunk is located", direction=API.Direction.OUTPUT)
        public CloudV3.NodeV3 location;
        
        public FrameChunkV3(int id, Vec vector) {
            this.chunk_id = id;
            H2ONode node = vector.chunkKey(id).home_node();
            this.row_count = vector.chunkLen(id);
            this.location = new CloudV3.NodeV3(node, true);
        }
    }

    @Override public FrameChunksV3 fillFromImpl(Frame frame) {
        this.frame_id = new KeyV3.FrameKeyV3(frame._key);
        Vec vector = frame.anyVec();
        this.chunks = new FrameChunkV3[vector.nChunks()];
        for(int i = 0; i < vector.nChunks(); i++) {
            this.chunks[i] = new FrameChunkV3(i, vector);
        }
        return this;
    }
}
