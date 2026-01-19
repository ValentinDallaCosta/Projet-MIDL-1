from syntax import *
from typing import Tuple
import sys
import os

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

def reconstruireAvecTermes(terms: list) -> Formula:
    """Reconstruit une formule à partir d'une liste de listes de termes et de quantificateurs."""

    # On construit la formule à partir des termes
    # On concatène toutes les listes de termes
    all_terms = terms[1] + terms[2] + terms[3] + terms[4]
    if not all_terms:
        body = ConstF(True)  # Si pas de termes, on retourne True
    else:
        body = all_terms[0]
        for term in all_terms[1:]:
            body = BoolOpF(body, Conj(), term)  # On construit une conjonction de tous les termes
    return reconstruireAvecQuantificateurs(body, terms[0])

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

def affichageListeFormules(formules: list, prefix="") -> None:
    """Affiche une liste de formules."""
    for i, f in enumerate(formules, 1):
        print(f"{prefix}Formule {i} :", f)

def affichageListeTermes(terms: list, prefix="") -> None:
    """Affiche une liste de termes à la suite espacé d'un tiret"""
    print(f"    {prefix}", end="")
    for term in terms:
        # Affichage à la suite avec un tiret
        print(f" {term} -", end="")
    print()

def affichageFormuleAvecTermes(formule: list) -> None:
    if formule[1] != []:
        affichageListeTermes(formule[1],"     Termes de la forme x < u :")
    if formule[2] != []:
        affichageListeTermes(formule[2],"     Termes de la forme u < x :")
    if formule[3] != []:
        affichageListeTermes(formule[3],"     Termes de la forme x = u :")
    if formule[4] != []:
        affichageListeTermes(formule[4],"     Autres termes :")
    if formule == [formule[0],[],[],[],[]]:
        print("             La formule est vide, donc True")

def input_formula_interactive() -> Formula:
    """Construit une formule via des invites terminales et la retourne.
    Types disponibles : constante, comparaison, négation, opérateur booléen, quantificateur.
    """
    def choose(prompt: str, choices: dict):
        print(prompt)
        for k, v in choices.items():
            print(f" {k} - {v}")
        c = input("Choix: ").strip()
        while c not in choices:
            print("Choix invalide.")
            c = input("Choix: ").strip()
        return c

    def build():
        kind = choose("Type de formule :", {
            "1": "Constante (True/False)",
            "2": "Comparaison (x = y ou x < y)",
            "3": "Négation (¬F)",
            "4": "Opérateur booléen (F ∧ G ou F ∨ G)",
            "5": "Quantificateur (∀x.F ou ∃x.F)"
        })

        if kind == "1":
            val = choose("Valeur de la constante:", {"1": "True", "2": "False"})
            return ConstF(val == "1")
        if kind == "2":
            left = input("Nom de l'identifiant gauche (ex: x): ").strip()
            op = choose("Opérateur de comparaison:", {"1": "=", "2": "<"})
            right = input("Nom de l'identifiant droit (ex: y): ").strip()
            return ComparF(left, Eq() if op == "1" else Lt(), right)
        if kind == "3":
            print("Saisir la sous-formule pour la négation :")
            sub = build()
            return NotF(sub)
        if kind == "4":
            print("Saisir la formule gauche :")
            left = build()
            op = choose("Opérateur booléen:", {"1": "∧", "2": "∨"})
            print("Saisir la formule droite :")
            right = build()
            return BoolOpF(left, Conj() if op == "1" else Disj(), right)
        if kind == "5":
            q = choose("Quantificateur:", {"1": "∀ (All)", "2": "∃ (Exist)"})
            var = input("Nom de la variable liée (ex: x): ").strip()
            print("Saisir le corps du quantificateur :")
            body = build()
            return QuantifF(All() if q == "1" else Ex(), var, body)

    print("--- Construction interactive d'une formule ---")
    f = build()
    print("Formule saisie :", f)
    return f

def extractxltu(f: Formula, x: str) -> list:
    """Extrait les termes de la formule f sans quantificateurs tel que x < u pour tout u."""
    if isinstance(f, BoolOpF):
        terms = extractxltu(f.left, x) + extractxltu(f.right, x)
    elif isinstance(f, NotF):
        terms = extractxltu(f.sub, x)
    elif isinstance(f, QuantifF):
        terms = extractxltu(f.body, x)
    elif isinstance(f, ComparF) and f.op == Lt():
        if f.left == x:
            terms = [f]
        else:
            terms = []
    else:
        terms = []

    return terms

def extractultx(f: Formula, x: str) -> list:
    """Extrait les termes de la formule f sans quantificateurs tel que u < x pour tout u."""
    if isinstance(f, BoolOpF):
        terms = extractultx(f.left, x) + extractultx(f.right, x)
    elif isinstance(f, NotF):
        terms = extractultx(f.sub, x)
    elif isinstance(f, QuantifF):
        terms = extractultx(f.body, x)
    elif isinstance(f, ComparF) and f.op == Lt():
        if f.right == x:
            terms = [f]
        else:
            terms = []
    else:
        terms = []

    return terms

def extracteqx(f: Formula, x: str) -> list:
    """Extrait les termes de la formule f sans quantificateurs tel que w = x ou x = w pour tout w."""
    if isinstance(f, BoolOpF):
        terms = extracteqx(f.left, x) + extracteqx(f.right, x)
    elif isinstance(f, NotF):
        terms = extracteqx(f.sub, x)
    elif isinstance(f, QuantifF):
        terms = extracteqx(f.body, x)
    elif isinstance(f, ComparF):
        if f.op == Eq() and (f.left == x or f.right == x):
            terms = [f]
        else:
            terms = []
    else:
        terms = []

    return terms

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
                if isNot:
                    if inner_q.var in vars_in_formula:
                        # Cela fait deux négations donc on les supprime en ajoutant seuleument le quantificateur
                        useful_quantifiers.append(inner_q)
                    # Il n'y a donc plus de négation en attente
                    isNot = False
                else:
                    if inner_q.var in vars_in_formula:
                        # On ajoute le quantificateur avec sa négation
                        useful_quantifiers.append(q)
                    else :
                        # On ajoute pas le quantificateur mais on garde la négation
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

def regrouperTermes(f: Formula, x: str) -> list:
    """regrouper les termes de ψ en : (∧i x ≺ui) ∧ (∧j vj ≺x) ∧ (∧k wk = x) ∧ χ avec x /∈fv(χ)"""
    
    # Pour chaque formule de la liste on crée les listes de termes
    body, quantifiers = extraireQuantificateurs(f)

    less_than_terms = extractxltu(body, x)
    greater_than_terms = extractultx(body, x)
    equal_terms = extracteqx(body, x)

    # On récupère le reste de la formule sans les termes extraits
    def removeExtractedTerms(f: Formula) -> list:
        # Que deux tests car on a déjà extrait les quantificateurs et les négations dans le corps de la formule
        if isinstance(f, BoolOpF):
            left = removeExtractedTerms(f.left)
            right = removeExtractedTerms(f.right)
            return [left, right] if left and right else left or right
        elif isinstance(f, ComparF):
            if (f in less_than_terms) or (f in greater_than_terms) or (f in equal_terms):
                return []  # On supprime ce terme
            else:
                return [f]
        else:
            return [f]
    other_terms = removeExtractedTerms(body)


    return [quantifiers,less_than_terms, greater_than_terms, equal_terms, other_terms]

def xeqw(f: Formula, x: str) -> list:
    """Remplace les occurrences de x par w dans une formule."""
    list_terme = []
    list_terme.append(f[0])  # On garde les quantificateurs
    w = None
    
    # On récupère la valeur à laquelle x est égal
    firsteq = f[3][0]
    while w is None:
        if firsteq.left == x and firsteq.right == x:
            w = None
            # Si x = x on supprime cette égalité et on passe à la suivante
            f[3].remove(firsteq)
            if not f[3]:  # Si la liste des égalités est vide, on arrête
                break
            firsteq = f[3][0]  # On passe à l'égalité suivante
        else:
            w = firsteq.right if firsteq.left == x else firsteq.left
    
    # On remplace x par w dans les autres termes
    new_lessthan_terms = []
    for term in f[1]:
        new_left = w if term.left == x else term.left
        new_right = w if term.right == x else term.right
        new_lessthan_terms.append(ComparF(new_left, Lt(), new_right))
    list_terme.append(new_lessthan_terms)

    new_greaterthan_terms = []
    for term in f[2]:
        new_left = w if term.left == x else term.left
        new_right = w if term.right == x else term.right
        new_greaterthan_terms.append(ComparF(new_left, Lt(), new_right))
    list_terme.append(new_greaterthan_terms)

    for term in f[3]:
        # On supprime le terme à l'avance toute les égalités avec la variable x car elle deviendrons w = w.
        f[3].remove(term) if term.left == x or term.right == x else term.left
    list_terme.append(f[3])

    # Pas besoin de changer le reste de la formule car x n'y apparait pas
    list_terme.append(f[4])

    return list_terme

def simplifierInegalites(less_than_terms: list, greater_than_terms: list) -> list:
    """Simplifie les inégalités de la forme x<u1 et u2<x en u2<u1."""
    new_terms = []
    for lt_term in less_than_terms:
        for gt_term in greater_than_terms:
            new_terms.append(ComparF(gt_term.left, Lt(), lt_term.right))
    return new_terms

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




#---Programme principal : Décision d'une fonction---#

def supDeVariables(formules: list, affichage: bool) -> list:
    """Applique la fin de la procédure de décision pour supprimer la variable x sur une liste de fonction"""
    if not affichage:
        old_stdout = sys.stdout
        sys.stdout = open(os.devnull, 'w')  # stop affichage

    return_formules = []
    for i, f in enumerate(formules, 1):
        body, quantifiers = extraireQuantificateurs(f)
        if (isinstance(body,NotF) and isinstance(body.sub,ConstF)) or ((not isinstance(body,NotF)) and isinstance(body,ConstF)):
            print(f"Formule {i} : Notre formule est déjà une constante donc on n'a plus rien a supprimer.")
            return_formules.append(f)
            
        else:
            # On traite les différent cas:
            # Cas 1 : La formule contient (x < x) -> on remplace par False

            print(f"Formule {i} :")
            print("    Nous recherchons si la relation x < x est présente :")
            if searchXltX(f):
                print(f"    C'est le cas, la formule devient donc False et la procédure ce termine.")
                terms = [quantifiers] + [ConstF(False)]

            # Sinon cas 2 : On regroupe les termes par relation par rapport à une variable x
            else:
                print("    Ce n'est pas le cas, nous allons donc regrouper les relations identiques de notre formule.")
                x = allVarInFormula(f)[0]  # On prend la première variable de la formule
                print(f"""    Nous prenons la variable "{x}" comme repère.""")
                terms = regrouperTermes(f, x)
                print("    Voici la liste des termes :")
                affichageFormuleAvecTermes(terms)

                # Maintenant : Si on a des égalités, on remplace x par w
                if terms[3]:  # Si la liste des égalités n'est pas vide
                    print(f"    Il y a des égalités présentent alors on remplace par u et on la supprime de la formule (car u = u -> True) :")
                    terms = xeqw(terms, x)

                # Sinon si on a x<u1 et u2<x, on remplace par u1<u2
                elif terms[1] and terms[2]: # Si on a des termes de la forme x<u et u<x
                    print(f"    Il y a pas d'égalité mais {x} < u1 et u2 < {x}, on peut donc simplifier :")
                    new_terms = simplifierInegalites(terms[1], terms[2])
                    terms = [quantifiers,new_terms,[],[],terms[4]]  # On ajoute le reste des termes

                # Sinon si on a que des x<u1 ou u2<x, on peut juste garder les termes où x n'apparaît plus
                else:
                    print(f"    Il y a seulement une ou aucune relation <, on garde donc que les autres termes déjà sans {x} :")
                    terms = [quantifiers,[],[],[],terms[4]]
                print(f"    Voici donc la nouvelle liste de termes sans la variable {x} :")
                affichageFormuleAvecTermes(terms)

            # On reconstruit nos formules à la fin de la suppression de variable :
            if isinstance(terms[1], ConstF):
                return_formules.append(reconstruireAvecQuantificateurs(terms[1], terms[0]))
            else:
                return_formules.append(reconstruireAvecTermes(terms))

    if not affichage:
        # Restauration de stdout
        sys.stdout.close()
        sys.stdout = old_stdout  # reprise affichage

    return return_formules
        
def enchainementSupDeVar(conjunctions: list):
    print("Voulez-vous procéder à la suppression d'une variable ?")
    reponse = input("1 : oui / 2 : non : ")
    while reponse not in ["1", "2"]:
        print("Choix invalide. Veuillez entrer 1 ou 2 :")
        reponse = input("")

    formule_after_sup = conjunctions
    while (reponse == "1"):
        print("\nSuppression d'une variable x dans chaque conjonction :")
        print("Voulez-vous avec détail le déroulé de cette suppression ?")
        choice = input("1 : oui / 2 : non : ")
        while choice not in ["1", "2"]:
            print("Choix invalide. Veuillez entrer 1 ou 2 :")
            choice = input("")

        if choice == "1":
            conjunctions = supDeVariables(conjunctions,True)
        else:
            conjunctions = supDeVariables(conjunctions,False)
        
        print("Formule après suppression d'une variable et sans les quatificateurs inutiles:")
        formule_after_sup = elimQuantifInutile(conjunctions)
        affichageListeFormules(formule_after_sup, "    ")

        print("Voulez-vous procéder à la suppression d'une autre variable ?")
        reponse = input("1 : oui / 2 : non : ")
        while reponse not in ["1", "2"]:
            print("Choix invalide. Veuillez entrer 1 ou 2 :")
            reponse = input("")
    
    return formule_after_sup

def isFormuleValide(formules: list):
    for f in formules:
        if isinstance(f,ConstF) and f.val == True:
            return True
    return False

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

    # Étape 5 : Supprimer la variable x dans chaque conjonction
    formule_after_sup = enchainementSupDeVar(conjunctions)
    
    print(f"La formule de départ {g} A été simplifiée après la procédure de décision en la liste de sous-formule :")
    affichageListeFormules(formule_after_sup, "     ")
    # Étape 5 : Vérification de la validité
    if isFormuleValide(formule_after_sup):
        print(f"Cette liste de sous-formule contient une ou plusieur formule vrai donc notre formule générale est vrai, ")
        print("car c'est une disjonction de ces sous-formules.")
    else:
        print(f"Cette liste de sous-formule contient aucune formule vrai ou n'a pas encore subit assez de suppression")
        print("de variable pour qu'on puisse l'évaluer donc notre formule générale est fausse, car c'est une disjonction de ces sous-formules.")

    print("Voulez vous essayer de supprimer d'autre variables :")
    
    return True
    
