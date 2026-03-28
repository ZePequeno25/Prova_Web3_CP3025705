import bcrypt

def hash_senha(senha: str) -> str:
    """Gera o hash da senha usando bcrypt"""
    # Converte a senha para bytes e gera o hash
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(senha.encode('utf-8'), salt)
    return hashed.decode('utf-8')


def verificar_senha(senha_simples: str, senha_hashed: str) -> bool:
    """Verifica se a senha digitada corresponde ao hash salvo"""
    return bcrypt.checkpw(
        senha_simples.encode('utf-8'), 
        senha_hashed.encode('utf-8')
    )