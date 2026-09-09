def nombre_voyelles(mot):
    """Ecrit par Sara le 12 mars"""
    return sum(1 for caractere in mot if caractere in "aeiouy")
