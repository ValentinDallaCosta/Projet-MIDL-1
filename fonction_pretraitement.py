from syntax import *
from fonction_bases import *

#---Fonctions permettant de prétraitement des formules---#

def tirerNegation(f: Formula) -> Formula:
    """Tire les négations devant les quantificateurs en utilisant la fonction
    nnf que l'on a déjà définie."""
    # nnf ne pard en parametre que des formules sans quantificateurs, on doit donc
    # séparer les quantificateurs de la formule, on
    # reconstruira la formule complète après traitement pour tout renvoyer.

    body, quantifiers = extraireQuantificateurs(f)

    # Appliquer nnf sur le corps sans quantificateurs
    body_nnf = nnf(body)

    return reconstruireAvecQuantificateurs(body_nnf, quantifiers)

def elimNegation(f: Formula) -> Formula:
    """elimine le plus possible les négations devant les relations de la formule en utilisant les lois suivantes.
    (a) ¬(z ≺ z') ↔ (z = z' v z' ≺ z)
    (b) ¬(z = z') ↔ (z ≺ z' v z' ≺ z)
    """
    # Si c'est une negation :
    if isinstance(f, NotF):
        sub = f.sub
        if isinstance(sub, ComparF):
            if isinstance(sub.op, Lt):
                # cas (a) ->
                return BoolOpF(ComparF(sub.left, Eq(), sub.right), Disj(), ComparF(sub.right, Lt(), sub.left))
            elif isinstance(sub.op, Eq):
                # cas (b) ->
                return BoolOpF(ComparF(sub.left, Lt(), sub.right), Disj(), ComparF(sub.right, Lt(), sub.left))
        else:
            if isinstance(sub, NotF):
                # Double négation, on simplifie
                return elimNegation(sub.sub)
            return NotF(elimNegation(sub))
    elif isinstance(f, BoolOpF):
        return BoolOpF(elimNegation(f.left), f.op, elimNegation(f.right))
    elif isinstance(f, QuantifF):
        return QuantifF(f.q, f.var, elimNegation(f.body))
    else:
        return f
    
def toDisjonctive(f: Formula) -> Formula:
    """Met la formule en forme disjonctive sans quantificateur."""

    # On sépare les quantificateurs de la formule
    body, quantifiers = extraireQuantificateurs(f)

    # On applique dnf sur le corps sans quantificateurs
    f1 = dnf(body)

    if not isDisjonctive(f1):
        raise ValueError("La formule n'a pas pu être mise en forme disjonctive.")
    
    return reconstruireAvecQuantificateurs(f1, quantifiers)

def isDisjonctive(f: Formula) -> bool:
    """Vérifie si une formule est en forme disjonctive (disjonction de conjonctions)."""
    def isConjunctionOfLiterals(f: Formula) -> bool:
        """Vérifie si une formule est une conjonction de littéraux (pas de disjonction à l'intérieur)."""
        if isinstance(f, BoolOpF):
            if isinstance(f.op, Conj):
                # Pour une conjonction, les deux côtés doivent être des conjonctions de littéraux
                return isConjunctionOfLiterals(f.left) and isConjunctionOfLiterals(f.right)
            elif isinstance(f.op, Disj):
                # Une disjonction ne doit pas apparaître dans une conjonction
                return False
        elif isinstance(f, NotF):
            # Une négation est un littéral si elle porte sur une comparaison
            return isinstance(f.sub, ComparF)
        elif isinstance(f, ComparF):
            # Une comparaison est un littéral
            return True
        elif isinstance(f, ConstF):
            return True
        elif isinstance(f, QuantifF):
            return isConjunctionOfLiterals(f.body)
        else:
            return False

    if isinstance(f, BoolOpF):
        if isinstance(f.op, Disj):
            # Au niveau d'une disjonction, les deux côtés doivent être en forme disjonctive
            return isDisjonctive(f.left) and isDisjonctive(f.right)
        elif isinstance(f.op, Conj):
            # Au niveau d'une conjonction, tous les éléments doivent être des littéraux (pas de disjonction à l'intérieur)
            return isConjunctionOfLiterals(f)
    elif isinstance(f, NotF):
        # Une négation est un littéral
        return isinstance(f.sub, ComparF)
    elif isinstance(f, QuantifF):
        return isDisjonctive(f.body)
    elif isinstance(f, ComparF):
        # Une comparaison est un littéral
        return True
    elif isinstance(f, ConstF):
        return True
    else:
        return False
    


