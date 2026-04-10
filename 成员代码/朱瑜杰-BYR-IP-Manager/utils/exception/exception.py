from django.http import JsonResponse


class CommonException(Exception):
    def __init__(self, exception: Exception = None):
        super().__init__()
        self.status = 500
        self.msg = str(exception if exception else "Server error")

    def __str__(self):
        return self.msg

    def response(self):
        return JsonResponse({"msg": self.msg}, status=self.status)


class UnauthorizedException(CommonException):
    def __init__(self, msg="Not logged in"):
        super().__init__()
        self.status = 401
        self.msg = msg


class InvalidException(UnauthorizedException):
    def __init__(self):
        super().__init__("Invalid token")


class OutdatedException(UnauthorizedException):

    def __init__(self):
        super().__init__("Outdated")
