class Connector {
    void connect(HttpServletRequest req){
        javax.servlet.http.Cookie cookie = new Cookie("cookie")
        HttpServletResponse res = new HttpServletResponse();
        res.addCookie(cookie);
    }
}
