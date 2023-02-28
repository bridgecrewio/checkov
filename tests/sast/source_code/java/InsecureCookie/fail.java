class Connector {
    @javax.jws.WebMethod
    void connect(HttpServletRequest req){
          javax.servlet.http.Cookie cook = new Cookie("cookie");
          req.addCookie(cook);
    }
}
