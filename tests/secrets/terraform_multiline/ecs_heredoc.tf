resource "aws_ecs_task_definition" "service" {
  family = "service"
  # name1 & value1 are not valid fields under environment
  container_definitions = <<TASK_DEFINITION
[
  {
    "cpu": 10,
    "command": ["sleep", "10"],
    "entryPoint": ["/"],
    "environment": [
      {"name": "SOME_NAME", "value": "some_value"},
      {
        "value": "Zo5Zhexnf9TUggdn+zBKGEkmUUvuKzVN+/fKPaMBA4zVyef4irH5H5YfwoC4IqAX0DNoMD12yIF67nIdIMg13atW4WM33eNMfXlE",
        "name": "TEST_PASSWORD_1",
        "name1": "TEST_PASSWORD_2",
        "value1": "1Vab3xejyUlh89P6tUJNXgO4t07DzmomF4tPBwTbwt+sjXHg3G0MPMRpH/I2ho4gS5H3AKJkvJZj87V7/Qnp/rHdbMVYK1F0BX35"
      },
      {
        "name": "TEST_PASSWORD_3",
        "value": "PtpfIZR+zZGPUWUYvLojqylVeEg63CBYN0FpGJ4yuH+9YxZZe8Uq7drEoTSfL64kElPEnVJk+H7SZr+wBoxN5qDWsbDmmUS2H76h"
      },
      {
        "value": "emDJTiv6H/hP6I8Tmr5+kUdpBIQDrXMwFO7AkmbwROf3rM6uNToJlIJW7H5ApfPmSGU0oWBwflV6Cd9pPu5nEvgxt4YMHZ0SQ85z",
        "name": "TEST_PASSWORD_4"
      },
      {
        "name": "TEST_PASSWORD_LONG_1",
        "value": "m9+1ONt6FdpnByhlaKDwZ/jjA5gaPzrKY9q5G8cr6kjn092ogigwEOGGryjDqq/NkX1DnKGGG7iduJUJ48+Rv0tgpdVAxwLQuiszRnssmi2ck/Zf1iDFlNQtiE8rvXE6OTCsb6mrpyItLOVnEwsRSpggyRa3KLSuiguiZsK5KyXQ6BsiAclpLvz6QFBQoQkZNxownQrqgLwVwkK1gW0/EEm0m1ylz20ZeLgYO6tRSvKDW0lrgAI7g60F7/eJGv1UqQlxK58T+7u1UX/K11Q69e9jJE+LkQ932eY37U70oVbBVchHwSFKUoffernEaG9XP1tyEpIptPqVpcS2BMpktoR1p1yyWuxC5GsPc2RlPQzEbs3n5lPPnC/uEVu7/cJENSw5+9DzigiHYPz1Cq/p5HedIl5ysn2U2VFgHWekGBYin6ytfmF2Sx+hYqeRd6RcxyU434CXspWQqc330sp9q7vwPQHNecBrvG2Iy7mqVSvaJDnkZ8AN"
      },
      {
        "name": "TEST_PASSWORD_no_password",
        "value": "RandomP@ssw0rd"
      }
    ],
    "essential": true,
    "image": "jenkins",
    "memory": 128,
    "name": "jenkins",
    "portMappings": [
      {
        "containerPort": 80,
        "hostPort": 8080
      }
    ],
        "resourceRequirements":[
            {
                "type":"InferenceAccelerator",
                "value":"device_1"
            }
        ]
  }
]
TASK_DEFINITION
}
