def executer(memoire):
    accumulateur, sortie = 0, []
    for adresse in sorted(memoire):
        instruction = memoire[adresse].split()
        if len(instruction) == 2 and instruction[0] == "CHARGER":
            accumulateur = int(instruction[1])
        elif len(instruction) == 2 and instruction[0] == "AJOUTER":
            accumulateur += int(instruction[1])
        elif instruction == ["AFFICHER"]:
            sortie.append(accumulateur)
        else:
            raise ValueError("instruction inconnue ou mal formee")
    return sortie
