import org.opennebula.client.Client;
import org.opennebula.client.vm.VirtualMachine;
import org.opennebula.client.OneResponse;
import org.opennebula.client.host.HostPool;

/**
 *
 * <at> author oneadmin
 */
public class SnapshotRestore {

    public static void main(String[] args) throws Exception {
        Client client = new Client( args[0],args[1] );
        int vm_id = Integer.parseInt(args[2]);
        int snapshot_id = Integer.parseInt(args[3]);
        OneResponse or = VirtualMachine.snapshotRevert(client,vm_id,snapshot_id);
        if (or.isError()) {
            System.out.println(or.getErrorMessage());
        }
        else{
            System.out.println(or.getMessage());
        }     
    }
}
