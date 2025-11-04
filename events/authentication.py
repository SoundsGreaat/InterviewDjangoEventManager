from drf_spectacular.extensions import OpenApiAuthenticationExtension


class TokenAuthenticationScheme(OpenApiAuthenticationExtension):
    target_class = 'rest_framework.authentication.TokenAuthentication'
    name = 'tokenAuth'

    def get_security_definition(self, auto_schema):
        return {
            'type': 'apiKey',
            'in': 'header',
            'name': 'Authorization',
            'description': 'Token-based authentication. Enter only your token value (prefix "Token " will be added automatically)',
        }
