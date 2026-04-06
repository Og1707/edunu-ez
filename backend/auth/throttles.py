from rest_framework.throttling import SimpleRateThrottle


class InvitacionRateThrottle(SimpleRateThrottle):
    scope = 'invitaciones'
    message = 'Límite de invitaciones alcanzado. Intenta en 1 hora.'

    def get_cache_key(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return None
        return self.cache_format % {
            'scope': self.scope,
            'ident': request.user.pk,
        }
