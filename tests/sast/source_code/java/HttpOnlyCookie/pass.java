class Connector {
    @javax.jws.WebMethod
    void connect(HttpServletRequest req){
        javax.servlet.http.Cookie cookie = new Cookie("cookie")
        HttpServletResponse res = new HttpServletResponse();
        cookie.setHttpOnly(true);
        res.addCookie(cookie);
    }
}
