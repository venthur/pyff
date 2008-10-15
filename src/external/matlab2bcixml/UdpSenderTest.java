public class UdpSenderTest {

	/**
	 * @param args
	 */
	public static void main(String[] args) {
		// TODO Auto-generated method stub
		try {
			UdpSender sender = new UdpSender("localhost", 12345);
			sender.sendString("foo");
			sender.sendString("bar");
			sender.sendString("baz");
			sender.close();
		} catch (Exception e) {
			e.printStackTrace();
			System.exit(1);
		}
		System.out.println("Send successfully.");
		System.exit(0);
	}
}
