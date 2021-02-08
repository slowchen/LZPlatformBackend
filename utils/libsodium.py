# @author: chengjie142039
# @file: libsodium.py
# @time: 2020/12/24
# @desc: python libsodium 加解密

try:
    from nacl.encoding import HexEncoder, Base64Encoder
    from nacl.public import Box, PrivateKey, PublicKey
except ImportError:
    raise ImportWarning('python环境中未找到nacl，请先执行 pip install pynacl 进行安装')


def encrypt(public_key: str, private_key: str, nonce: str, plain_text: str):
    """
    libsodium 加密
    :param public_key: 公钥
    :param private_key: 私钥
    :param nonce: 随机码
    :param plain_text: 加密文本
    :return:加密后的密文，str 类型
    """
    if len(public_key) != 64:
        raise ValueError('public_key 长度必须为64')
    if len(private_key) != 64:
        raise ValueError('private_key 长度必须为64')
    if len(nonce) != 32:
        raise ValueError('nonce 长度必须为32')

    # 公钥转 bytes，注意encoder指定HexEncoder
    public = PublicKey(
        public_key.encode(),
        encoder=HexEncoder,
    )

    # 私钥转 bytes，注意encoder指定HexEncoder
    private = PrivateKey(
        private_key.encode(),
        encoder=HexEncoder,
    )

    # 生成 box
    box = Box(private, public)

    # 随机码先转成 bytes，再 base64 decode
    nonce_bytes = Base64Encoder.decode(nonce.encode())
    encrypted = box.encrypt(
        plain_text.encode(),
        nonce_bytes
    )
    ciphertext = Base64Encoder.encode(encrypted.ciphertext)
    return str(ciphertext, encoding="utf8")


def decrypt(public_key: str, private_key: str, nonce: str, ciphertext: str):
    """
    libsodium 解密
    :param public_key: 公钥
    :param private_key: 私钥
    :param nonce: 随机码
    :param ciphertext: 密文
    :return: 解密后的文本，str 类型
    """
    if len(public_key) != 64:
        raise ValueError('public_key 长度必须为64')
    if len(private_key) != 64:
        raise ValueError('private_key 长度必须为64')
    if len(nonce) != 32:
        raise ValueError('nonce 长度必须为32')
    public = PublicKey(
        public_key.encode(),
        encoder=HexEncoder,
    )
    private = PrivateKey(
        private_key.encode(),
        encoder=HexEncoder,
    )
    box = Box(private, public)
    nonce_bytes = Base64Encoder.decode(nonce.encode())
    ciphertextByte = Base64Encoder.decode(ciphertext.encode())
    decrypted = box.decrypt(ciphertextByte, nonce_bytes)
    return str(decrypted, encoding='utf-8')


if __name__ == '__main__':
    import json

    public = '5116b4433193568bf77c0a036f7cbe2476bd4701d7c2083bb8f397c56ee83256'
    private = '749ac37351cf4c0232958227018658f1f67490337f4b48dd40c622b65345c092'
    nonce = 'wzqbFRhZxScQGLV9HdoKiky2N3eO6AXI'
    a = json.dumps({})
    text = json.dumps({"password": "a123456", "jigsawVerificationCode": {"offset": "", "token": ""}, "account": "LS5"})
    ciphertext = encrypt(public, private, nonce, a)
    print(ciphertext)
