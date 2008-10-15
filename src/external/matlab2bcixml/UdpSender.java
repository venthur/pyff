/**
 * 
 */

import java.io.*;
import java.net.DatagramSocket;
import java.net.InetAddress;
import java.net.DatagramPacket;

/**
 * @author Bastian Venthur <venthur@cs.tu-berlin.de>
 *
 */
public class UdpSender {

	DatagramSocket socket;
	DatagramPacket dgram;
	
	public UdpSender(String host, int port) throws IOException {
		// TODO: check if ip and port are correct
		InetAddress address = InetAddress.getByName(host);
		this.dgram = new DatagramPacket("".getBytes(), 0, address, port);
	}
	
	protected void finalize() throws Throwable {
		this.socket.close();
		super.finalize();
	}
	
	
	/**
	 * @param txt
	 */
	public void sendString(String txt) throws IOException {
		this.dgram.setData(txt.getBytes());
		this.socket = new DatagramSocket();
		this.socket.send(this.dgram);
		this.socket.close();
	}
}
