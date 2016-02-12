import org.opennebula.client.Client;
import org.opennebula.client.vnet.VirtualNetwork;
import org.opennebula.client.OneResponse;
import org.opennebula.client.host.HostPool;

/**
 *
 * <at> author oneadmin
 */
public class NetworkInfo {

    public static void main(String[] args) throws Exception {
        //password and URL standard
        Client client = new Client( args[0],args[1] );
        //network ID
        int net_id = Integer.parseInt(args[2]);
        OneResponse or = VirtualNetwork.info(client,net_id);
        if (or.isError()) {
            System.out.println(or.getErrorMessage());
        }
        else{
            System.out.println(or.getMessage());
        }     
    }
}
