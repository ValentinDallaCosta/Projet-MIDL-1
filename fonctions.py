from syntax import *

# Fonction récursive simple : inversion des opérateurs
def dualOp(op: BoolOp) -> BoolOp:
    """Transforme les opérateurs ET en OU"""
    if isinstance(op, Conj):
        return Disj() #Si c'est une conjonction, on retourne une disjonction
    else:
        return Conj() #Sinon on retourne une conjonction

def dual(f: Formula) -> Formula:
    """Retourne la formule où ∧ et ∨ sont inversés."""
    if isinstance(f, ConstF): # on ne fait rien si c'est une constante
        return f
    elif isinstance(f, ComparF): # idem pour les comparaisons
        return f
    elif isinstance(f, NotF):
        return NotF(dual(f.sub)) # on applique dual à la sous-formule
    elif isinstance(f, BoolOpF):
        return BoolOpF(dual(f.left), dualOp(f.op), dual(f.right)) # on inverse l'opérateur et on applique dual aux sous-formules
    else:
        raise ValueError("dual applied to quantified formula") # on ne prend pas en charge les quantificateurs

# Pour nous aider à bien assimmiler le fonctionnement de la fonction dual, on la modifie pour qu'elle
# prenne en compte les quantificateurs et inverse les quantificateurs universels et existentiels.
#Même si cela n'a pas de sens logique, ça nous permettra de bien comprendre le fonctionnement de la syntaxe.

def dual2(f: Formula) -> Formula:
    """Retourne la formule où ∧ et ∨ sont inversés."""
    if isinstance(f, ConstF): # on ne fait rien si c'est une constante
        return f
    elif isinstance(f, ComparF): # idem pour les comparaisons
        return f
    elif isinstance(f, NotF):
        return NotF(dual2(f.sub)) # on applique dual2 à la sous-formule
    elif isinstance(f, BoolOpF):
        return BoolOpF(dual2(f.left), dualOp(f.op), dual2(f.right)) # on inverse l'opérateur et on applique dual2 aux sous-formules
    elif isinstance(f, QuantifF): # on gère les quantificateurs
        if isinstance(f.q, All):
            return QuantifF(Ex(), f.var, dual2(f.body)) # on inverse le quantificateur et on applique dual2 à la sous-formule
        else:
            return QuantifF(All(), f.var, dual2(f.body)) # on inverse le quantificateur et on applique dual2 à la sous-formule
    else:
        raise ValueError("dual2: type non connu")


def nnf(f: Formula) -> Formula:
    """Retourne la forme normale négative de la formule f sans quantificateur."""
    if isinstance(f, ConstF) or isinstance(f, ComparF):
        return f
    elif isinstance(f, QuantifF): # on ignore les quantificateurs pour cette fonction
        return nnf(f.body)
    elif isinstance(f, NotF): # on traite la négation
        sub = f.sub
        if isinstance(sub, ConstF): # Négation d'une constante
            return ConstF(not sub.val)
        elif isinstance(sub, ComparF):  # Négation d'une comparaison
            if isinstance(sub.op, Eq): # Egalité devient deux inégalités
                return BoolOpF(ComparF(sub.left, Lt(), sub.right), Disj(), ComparF(sub.right, Lt(), sub.left))
            elif isinstance(sub.op, Lt): # Inégalité devient égalité ou inverse de l'inégalité
                return BoolOpF(ComparF(sub.right, Lt(), sub.left), Disj(), ComparF(sub.left, Eq(), sub.right))
        elif isinstance(sub, NotF): # Double négation, on simplifie
            return nnf(sub.sub)
        elif isinstance(sub, BoolOpF): # Négation d'une opération booléenne
            if isinstance(sub.op, Conj): # OU devient ET
                return disj(nnf(NotF(sub.left)), nnf(NotF(sub.right)))
            elif isinstance(sub.op, Disj): # ET devient OU
                return conj(nnf(NotF(sub.left)), nnf(NotF(sub.right)))
    elif isinstance(f, BoolOpF): # recursivité sur les termes gauche et droite si pas de négation
        return BoolOpF(nnf(f.left), f.op, nnf(f.right))
    else:
        raise ValueError("nnf: type non connu")


def dnf(f: Formula) -> Formula:
    """Retourne la forme normale disjonctive de la formule f sans quantificateur."""
    f_nnf = nnf(f)
    
    if isinstance(f_nnf, ConstF) or isinstance(f_nnf, ComparF): 
        return f_nnf
    elif isinstance(f_nnf, BoolOpF):
        if isinstance(f_nnf.op, Disj): # on distribue la disjonction
            return disj(dnf(f_nnf.left), dnf(f_nnf.right))
        elif isinstance(f_nnf.op, Conj): # on distribue la conjonction
            left_dnf = dnf(f_nnf.left)
            right_dnf = dnf(f_nnf.right)
            if isinstance(left_dnf, BoolOpF) and isinstance(left_dnf.op, Disj):
                return disj(dnf(conj(left_dnf.left, right_dnf)), dnf(conj(left_dnf.right, right_dnf)))
            elif isinstance(right_dnf, BoolOpF) and isinstance(right_dnf.op, Disj):
                return disj(dnf(conj(left_dnf, right_dnf.left)), dnf(conj(left_dnf, right_dnf.right)))
            else:
                return conj(left_dnf, right_dnf)
    else:
        raise ValueError("dnf: type non connu")
     


#Fonctions permettant de vérifier les hypothèse pour la procédure de décision

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
        # on suppose que left/right sont des identifiants (str) représentant des variables
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
        return False
    if not(isJustSymboleRelationnel(f)):
        return False
    return True


