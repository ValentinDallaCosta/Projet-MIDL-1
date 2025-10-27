# -*- coding: utf-8 -*-
from syntax import *

print("\n=== Création d'une structure ===")
#Les constantes
f1 = ConstF(True)
f2 = ConstF(False)
print("Constantes :", f1, ",", f2)

# Comparaisons
f3 = eqf("x", "y")   # x = y
f4 = ltf("y", "z")   # y < z
print("Comparaisons :", f3, ",", f4)


#Opérateurs booleens
# Conjonction
f5 = conj(f3, f4)    # (x = y) ∧ (y < z)
print("Conjonction :", f5)

# Disjonction
f6 = disj(f3, f4)    # (x = y) ∨ (y < z)
print("Disjonction :", f6)

# Implication (x = y) ⇒ (y < z) devient ¬(x = y) ∨ (y < z)
f7 = impl(f3, f4)
print("Implication :", f7)

# Négation
f8 = NotF(f4)        # ¬(y < z)
print("Négation :", f8)



# Quantificateur : Exemple : ∀x.(x < y)
f9 = allq("x", ltf("x", "y"))
print("Quantificateur universel :", f9)

# Exemple : ∃y.(x = y)
f10 = exq("y", eqf("x", "y"))
print("Quantificateur existentiel :", f10)


print("\nFormule (exemple du sujet) :")

# Sans abrévation ∀x ∀y ∀z ∃u ((x < y ∧ x < z) ⇒ (y < u ∧ z < u))
f = QuantifF(All(), "x" , 
         QuantifF(All(), "y" , 
                  QuantifF(All(), "z" , 
                           QuantifF(Ex(), "u" , 
                                    BoolOpF(NotF(BoolOpF(ComparF( "x" , Lt(), "y" ), Conj(), ComparF( "x" , Lt(), "z" ))), 
                                            Disj(), 
                                            BoolOpF(ComparF( "y" , Lt(), "u" ), Conj(), ComparF( "z" , Lt(), "u" )))))))

# En utilisant les abréviations, plus lisible :
f = allq("x",
        allq("y",
            allq("z",
                exq("u",
                    impl(
                        conj(ltf("x", "y"), ltf("x", "z")),
                        conj(ltf("y", "u"), ltf("z", "u"))
                    )
                )
            )
        )
    )

print("Formule :", f)

# Accès aux sous-formules

print("\n=== Exploration de la structure ===")
print("Quantificateur le plus externe :", f.q)
print("Variable liée :", f.var)
print("Corps de la formule :", f.body)

# Accéder plus profondément :
print("Deuxième quantificateur :", f.body.q)
print("Troisième variable liée :", f.body.body.var)
print("Sous-formule finale (partie droite de l'implication) :")
print(f.body.body.body.body.right)

# Fonction récursive simple : inversion des opérateurs
print("\n=== Fonction récursive : dual ===")

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

# Test de dual et dualOp
test = conj(ConstF(True), ConstF(False))
print("Formule originale :", test)
print("Dual :", dual(test))

#Pou nous aider à bien assimmiler le fonctionnement de la fonction dual, je la modifie pour qu'elle
# prenne en compte les quantificateurs aussi en inversant les quantificateurs universels et existentiels.
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
    
print("Dual2 sur la formule du cours :", dual2(f))

print("\n=== Fin des tests ===")