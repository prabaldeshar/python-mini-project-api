import json
from jwcrypto import jwk, jwt


# private_key = jwk.JWK.generate(kty='RSA', size=2048)


# #import a P-256 Public key
# exp_key = private_key.export(private_key=False)

# x = json.loads(str(private_key))
# print()
# y = json.loads(exp_key)
# public_key = jwk.JWK(**y)
# from jwcrypto import jwk, jwt

with open("keypair.pem", "rb") as pemfile:
    key = jwk.JWK.from_pem(pemfile.read())

# public_key = key.export(private_key=False)

# jwks = {}
# jwks["keys"] = [json.loads(public_key)]

# with open("jwks.json", "w") as h:
#     h.write(json.dumps(jwks))

Token = jwt.JWT(header={"alg": "RS256", "typ": "JWT","kid": key.key_id},
                    claims={"username": "Prabal Deshar"})
Token.make_signed_token(key)
token = Token.serialize()
print(token)

with open("jwks.json") as f:
    k = json.loads(f.read())

print(type(k["keys"][0]))
key = jwk.JWK(**k["keys"][0])

print(key)
ET = jwt.JWT(key=key, jwt=token)
ST = jwt.JWT(key=key, jwt=ET.claims)

# print(ST.claims)