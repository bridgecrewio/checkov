resource "ncloud_lb_target_group" "pass" {
    name = "terra-tg"
    vpc_no = data.ncloud_vpc.selected.id
    protocol = "HTTPS"
    target_type = "VSVR"
    port = 443
    description = "cand2_lb_group"
    health_check {
        protocol = "HTTPS"
        http_method = "GET"
        port = 443
        url_path = "/"
        cycle = 30
        up_threshold = 2
        down_threshold = 2
    }
    algorithm_type = "RR"
}


resource "ncloud_lb_listener" "pass" {
    load_balancer_no = ncloud_lb.lb.id
    protocol = "HTTPS"
    port = 443
    target_group_no = ncloud_lb_target_group.tg.id
}


resource "ncloud_lb_target_group" "fail" {
    name = "terra-tg"
    vpc_no = data.ncloud_vpc.selected.id
    protocol = "HTTP"
    target_type = "VSVR"
    port = 80
    description = "cand2_lb_group"
    health_check {
        protocol = "HTTP"
        http_method = "GET"
        port = 80
        url_path = "/"
        cycle = 30
        up_threshold = 2
        down_threshold = 2
    }
    algorithm_type = "RR"
}


resource "ncloud_lb_listener" "fail" {
    load_balancer_no = ncloud_lb.lb.id
    protocol = "HTTP"
    port = 80
    target_group_no = ncloud_lb_target_group.tg.id
}