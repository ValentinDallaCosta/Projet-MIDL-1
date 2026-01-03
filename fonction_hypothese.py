from syntax import *
from typing import Tuple



#---Fonctions permettant de vérifier les hypothèse pour la procédure de décision---#

def freeVar(f: Formula, bound_vars=None) -> list:
    """Retourne la liste (éventuellement vide) des variables libres de la formule f."""
    if bound_vars is None:
        bound_vars = set()

    if isinstance(f, QuantifF):
        return freeVar(f.body, bound_vars | {f.var})
    elif isinstance(f, NotF):
        return freeVar(f.sub, bound_vars)
    elif isinstance(f, BoolOpF):
        left_free = set(freeVar(f.left, bound_vars))
        right_free = set(freeVar(f.right, bound_vars))
        return sorted(list(left_free | right_free))
    elif isinstance(f, ComparF):
        free = set()
        # on suppose que left/right sont des identifiants représentant des variables
        if isinstance(f.left, str) and (f.left not in bound_vars):
            free.add(f.left)
        if isinstance(f.right, str) and (f.right not in bound_vars):
            free.add(f.right)
        return sorted(list(free))
    elif isinstance(f, ConstF):
        return []
    else:
        raise ValueError("isClose: type non connu")
    
def isClose(f: Formula) -> bool:
    """Vérifie si une formule est close (sans variable libre)."""
    free_vars = freeVar(f)
    return len(free_vars) == 0

def toClose(f: Formula) -> Formula:
    """Retourne une formule close en préfixant des quantificateurs universels
    pour chaque variable libre trouvée."""

    free_vars = freeVar(f)
    if not free_vars:
        return f
    # Préfixe les quantificateurs universels dans un ordre déterministe
    for v in free_vars:
        f = QuantifF(All(), v, f)
    return f

def isJustSymboleRelationnel(f: Formula) -> bool:
    """Vérifie si une formule est constituée uniquement de symboles relationnels."""
    if isinstance(f, ComparF):
        return True
    elif isinstance(f, NotF):
        return isJustSymboleRelationnel(f.sub)
    elif isinstance(f, BoolOpF):
        return isJustSymboleRelationnel(f.left) and isJustSymboleRelationnel(f.right)
    else:
        return False
    
def isElimPossible(f: Formula) -> bool:
    """Vérifie si une formule est éligible à l'élimination des quantificateurs."""
    if not(isClose(f)):
        ValueError("La formule n'est pas close.")
        return False
    if not(isJustSymboleRelationnel(f)):
        ValueError("La formule contient des éléments autres que des symboles relationnels.")
        return False
    if not(isPrenexe(f)):
        ValueError("La formule n'est pas en forme prénexe.")
        return False
    return True

def isPrenexe(f: Formula) -> bool:
    """Vérifie si une formule est en forme prénexe."""
    def hasQuantifiers(f: Formula) -> bool:
        """Vérifie si une formule contient des quantificateurs."""
        if isinstance(f, QuantifF):
            return True
        elif isinstance(f, NotF):
            return hasQuantifiers(f.sub)
        elif isinstance(f, BoolOpF):
            return hasQuantifiers(f.left) or hasQuantifiers(f.right)
        else:
            return False
    
    if isinstance(f, QuantifF):
        return isPrenexe(f.body)
    else:
        # Si on atteint une formule qui n'est pas un quantificateur, on vérifie qu'elle ne contient pas de quantificateurs
        return not hasQuantifiers(f)

def allToExist(f: Formula) -> Formula:
    """Transforme f en formule composée uniquement de quantificateurs existentiels en suivant la règle :
    ∀x.P  ==  ¬(∃x.¬P)"""
    if isinstance(f, QuantifF):
        if isinstance(f.q, All):
            return NotF(QuantifF(Ex(), f.var, NotF(allToExist(f.body))))
        else:
            return QuantifF(Ex(), f.var, allToExist(f.body))
    elif isinstance(f, NotF):
        return NotF(allToExist(f.sub))
    elif isinstance(f, BoolOpF):
        return BoolOpF(allToExist(f.left), f.op, allToExist(f.right))
    else:
        return f
