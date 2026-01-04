from syntax import *
from typing import Tuple

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
    
def extraireQuantificateurs(f: Formula) -> Tuple[Formula, list]:
    """Extrait les quantificateurs de la formule et retourne le corps sans quantificateurs
    ainsi que la liste des quantificateurs extraits."""
    quantifiers = []
    body = f

    # Extraction des quantificateurs en tête
    # Il faut aussi traiter le cas où on a une négation devant un quantificateur ou deux négations
    while isinstance(body, QuantifF) or (isinstance(body, NotF) and isinstance(body.sub, QuantifF)) or (isinstance(body, NotF) and isinstance(body.sub, NotF)):
        if isinstance(body, NotF) and isinstance(body.sub, NotF):
            # Double négation, on simplifie et on continue
            body = body.sub.sub
            continue
        else:
            if isinstance(body, NotF):
                if isinstance(body.sub, All):
                    quantifiers.append(NotF(QuantifF(All(), body.sub.var, None)))  # On stocke le quantificateur 
                else:
                    quantifiers.append(NotF(QuantifF(Ex(), body.sub.var, None)))  # On stocke le quantificateur
                body = body.sub.body
            else:
                if isinstance(body, All):
                    quantifiers.append(QuantifF(All(), body.var, None))  # On stocke le quantificateur 
                else:
                    quantifiers.append(QuantifF(Ex(), body.var, None))  # On stocke le quantificateur
                body = body.body

    return body, quantifiers

def reconstruireAvecQuantificateurs(body: Formula, quantifiers: list) -> Formula:
    """Reconstruit la formule en réappliquant les quantificateurs extraits.""" 
    for q in reversed(quantifiers):
        if isinstance(q, NotF):
            inner_q = q.sub
            body = NotF(QuantifF(inner_q.q, inner_q.var, body))
        else:
            body = QuantifF(q.q, q.var, body)
    return body

def allVarInFormula(f: Formula) -> list:
    """Retourne toutes les variables présentes dans une formule."""
    if isinstance(f, QuantifF):
        return allVarInFormula(f.body)
    elif isinstance(f, BoolOpF):
        return allVarInFormula(f.left) + allVarInFormula(f.right)
    elif isinstance(f, NotF):
        return allVarInFormula(f.sub)
    elif isinstance(f, ComparF):
        return ([f.left] if isinstance(f.left, str) else []) + ([f.right] if isinstance(f.right, str) else [])
    elif isinstance(f, ConstF):
        return []
    else:
        return []

def affichageListeFormules(formules: list):
    """Affiche une liste de formules."""
    for i, f in enumerate(formules, 1):
        print(f"  Formule {i} :", f)

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
    elif isinstance(f, QuantifF):
        return isJustSymboleRelationnel(f.body)
    else:
        return False
    
def isElimPossible(f: Formula) -> bool:
    """Vérifie si une formule est éligible à l'élimination des quantificateurs."""
    if not(isClose(f)):
        print("La formule n'est pas close.")
        return False
    if not(isJustSymboleRelationnel(f)):
        print("La formule contient des éléments autres que des symboles relationnels.")
        return False
    if not(isPrenexe(f)):
        print("La formule n'est pas en forme prénexe.")
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

def tirerQuantif(f: Formula) -> Formula:
    """Tire les quantificateurs devant les formules extraites d'une formule
    en forme normale disjonctive."""

    # Liste de conjonctions avec leurs quantificateurs
    conjunctions = []

    #On récupère les quantificateurs
    body, quantifiers = extraireQuantificateurs(f)

    # On traite chaque disjonction
    if isinstance(body, BoolOpF) and isinstance(body.op, Disj):
        disjuncts = [body.left, body.right]
    else:
        disjuncts = [body]

    for disj in disjuncts:
        # Pour chaque sous formule d'une disjonction on teste si c'est une conjonction

        # Si c'est une disjonction, on ajoute chaque partie séparément à la liste de disjonctions
        if isinstance(disj, BoolOpF) and isinstance(disj.op, Disj):
            disjuncts.append(disj.left)
            disjuncts.append(disj.right)
        
        # Si ce n'est plus une disjonction, on ajoute la conjonction avec les quantificateurs de la formule
        else:
            conjunctions.append(reconstruireAvecQuantificateurs(disj, quantifiers))

    return conjunctions

#---Fonctions permettant la suppression de variables---#

def elimQuantifInutile(conjonctions: list) -> list:
    """Elimine les quantificateurs inutiles de la formule f."""
    # Si x n'appartient pas au variable de ψ : (∃x. ψ) ↔ ψ
    returned_conjonctions = []
    isNot = False

    for conj in conjonctions:
        vars_in_formula = allVarInFormula(conj)
        # On extrait les quantificateurs
        body, quantifiers = extraireQuantificateurs(conj)
        useful_quantifiers = []

        # On filtre les quantificateurs inutiles
        for q in quantifiers:
            if isinstance(q, NotF):
                # On gère le cas des quantificateurs négatifs
                inner_q = q.sub
                if inner_q.var in vars_in_formula:
                    if isNot:
                        useful_quantifiers.append(inner_q)
                        isNot = False
                    else:
                        useful_quantifiers.append(q)
                else :
                    isNot = True
            elif q.var in vars_in_formula:
                if isNot:
                    useful_quantifiers.append(NotF(q))
                    isNot = False
                else:
                    useful_quantifiers.append(q)

        # On reconstruit la formule sans les quantificateurs inutiles
        if isNot:
            # Si le dernier quantificateur était inutile et précédé d'une négation, on ajoute la négation
            body = NotF(body)
            isNot = False
        conj = reconstruireAvecQuantificateurs(body, useful_quantifiers)
        returned_conjonctions.append(conj)
    return returned_conjonctions

def supXltX(conjonctions: list) -> list:
    """Transforme une formule contenant des comparaisons de la forme (x < x) en juste False."""

    def searchXltX(formula):
        """Renvoie True si la formule contient une comparaison de la forme (x < x)."""
        if isinstance(formula, BoolOpF):
            return searchXltX(formula.left) or searchXltX(formula.right)
        elif isinstance(formula, NotF):
            return searchXltX(formula.sub)
        elif isinstance(formula, QuantifF):
            return searchXltX(formula.body)
        elif isinstance(formula, ComparF) and formula.op == Lt() and formula.left == formula.right:
            return True
        else:
            return False

    returned_conjonctions = []
    for f in conjonctions:
        # On cherche si la formule contient une comparaison de la forme (x < x)
        if searchXltX(f):
            # Si oui, on remplace la formule par False
            returned_conjonctions.append(ConstF(False))
        else:
            # Sinon, on garde la formule telle quelle
            returned_conjonctions.append(f)

    return returned_conjonctions













#---Programme principal : Décision d'une fonction---#

def decision(g: Formula) -> bool:
    """Procédure de décision d'une formule"""

    # ÉTAPE 0 : hypothèses vérifiées
    f = toClose(g)  # S'assurer que la formule est close
    print("Formule automatiquement transformée en formule close avec ajout de quantificateurs universels si nécessaire.")

    if not isElimPossible(f):
        # Close, symboles relationnels seulement, et prénexe supposé
        raise ValueError("Formule non éligible à l'élimination des quantificateurs.")

    f0 = allToExist(f) # Convertir forall en exists
    print("Après conversion de tous les quantificateurs universels en existentiels :", f0)

    # ==========PRÉTRAITEMENT DE LA FORMULE========== #
    # Étape 1 : On elimine et tire les négations vers l'interieur

    f1 = tirerNegation(f0)
    f1 = elimNegation(f1)
    print("\nAprès éliminations des négations à l'intérieur :", f1)

    # Étape 2 : Mettre en forme normale disjonctive
    f2 = toDisjonctive(f1)
    print("\nAprès mise en forme normale disjonctive :", f2)

    # Étape 3 : Tirer les quantificateurs devant les disjonctions
    conjunctions = tirerQuantif(f2)

    print("\nAprès tirage des quantificateurs devant les disjonctions :")
    affichageListeFormules(conjunctions)

    # Étape 4 : Éliminer les quantificateurs inutiles
    conjunctions = elimQuantifInutile(conjunctions)
    print("\nAprès élimination des quantificateurs inutiles :")
    affichageListeFormules(conjunctions)

    # Étape 5 : Supprimer les comparaisons de la forme (x < x)
    conjunctions = supXltX(conjunctions)
    print("\nAprès suppression des comparaisons de la forme (x < x) :")
    affichageListeFormules(conjunctions)


    return True






    # Étape 5 : Vérification de la validité
    if isinstance(f, ConstF):
        return f.val
    else:
        raise ValueError("La formule finale n'est pas une constante.")
