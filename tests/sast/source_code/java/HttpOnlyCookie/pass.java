class Connector {
    @javax.jws.WebMethod
    void connect(HttpServletRequest req){
        javax.servlet.http.Cookie cook = new Cookie("cookie");
        cook.setHttpOnly(false);
        resp.addCookie(cook);
    }
}
