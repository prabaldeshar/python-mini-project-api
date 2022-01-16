from jwcrypto import jwk
import jwt
from jwt import PyJWKClient
import json
def generate_key():
    key = jwk.JWK.generate(kty='RSA', size=2048, alg='RSA', use='enc', kid='12345')
    public_key = key.export_public()
    private_key = key.export_private()
    return private_key, public_key
# pk = json.loads(private_key)

def generate_token(payload):
    private_key, public_key = generate_key()
    pk = jwt.algorithms.RSAAlgorithm.from_jwk(json.loads(private_key)) 
    token = jwt.encode(payload, pk, algorithm='RS256')
    jwks_dict = {}

    jwks_dict["keys"] = json.loads(public_key)
    with open('jwks.json', 'w') as f:
        json.dump(jwks_dict, f)
    return token

def decode_token(token):
    public_keys = {}
    with open('jwks.json', 'r') as f:
        public_k = json.load(f)
        
    key = jwt.algorithms.RSAAlgorithm.from_jwk(public_k["keys"])
    payload = jwt.decode(token, key, algorithms=['RS256'])
    return payload
