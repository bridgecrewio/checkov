public class LambdaFunctionHandler implements RequestHandler < Request, String > {
  @javax.ws.rs.Path("some/path")
  String handleRequest(Request request, Context context) {
    String s = " ";
    if (s == "") {
      s = "Sucess " + String.format("Added %s %s %s %s %s.", request.emp_id, request.month, request.year, request.overtime);
    }
    return s;
  }
}