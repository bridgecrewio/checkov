class Connector {
    @javax.jws.WebMethod
    void connect(HttpServletRequest req){
        Cookie cook = new Cookie("cookie");
        for (Cookie cookie : req.getCookies()) {
            cookie.getAbsPath();
        }
    }
}