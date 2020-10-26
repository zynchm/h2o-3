package water.api.schemas3;

import water.Iced;
import water.api.API;

import java.util.Map;

/**
 * Model's training data domains.
 */
public class DomainsV3 extends RequestSchemaV3<Iced, DomainsV3> {

  /** Model to get domains from. */
  @API(help="Name of Model of interest", json=false)
  public KeyV3.ModelKeyV3 model_id;

  @API(help="Column names of the model's training data.", direction = API.Direction.OUTPUT)
  public String[] names = null;

  @API(help="Domains of the model's training data.", direction = API.Direction.OUTPUT)
  public String[][] domains = null;
}
