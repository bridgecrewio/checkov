class Connector {
    @javax.jws.WebMethod
    void connect(HttpServletRequest req){
          javax.servlet.http.Cookie cook = new Cookie("cookie");
          cook.setSecure(true);
          req.addCookie(cook);
    }
}