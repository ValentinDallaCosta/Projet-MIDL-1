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

print("\nFormule (exemple du sujet) :", f)

# Autre exemple de formule : ∀x ∃y (x = y ∨ ¬(x < y))

g = allq("x",
        exq("y",
            disj(
                eqf("x", "y"),
                NotF(ltf("x", "y"))
            )
        )
    )

print("\nAutre exemple de formule :", g)
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
    
print("Dual2 sur la formule du sujet :", dual2(f))

print("\n=== Fonction nnf et dnf ===")

def nnf(f: Formula) -> Formula:
    """Retourne la forme normale négative de la formule f sans quantificateur."""
    if isinstance(f, ConstF) or isinstance(f, ComparF):
        return f
    elif isinstance(f, QuantifF): # on ignore les quantificateurs pour cette fonction
        return nnf(f.body)
    elif isinstance(f, NotF):
        sub = f.sub
        if isinstance(sub, ConstF):
            return ConstF(not sub.val)
        elif isinstance(sub, ComparF):
            # Négation d'une comparaison
            if isinstance(sub.op, Eq):
                return BoolOpF(ComparF(sub.left, Lt(), sub.right), Disj(), ComparF(sub.right, Lt(), sub.left))
            elif isinstance(sub.op, Lt):
                return BoolOpF(ComparF(sub.right, Lt(), sub.left), Disj(), ComparF(sub.left, Eq(), sub.right))
        elif isinstance(sub, NotF):
            return nnf(sub.sub)
        elif isinstance(sub, BoolOpF):
            if isinstance(sub.op, Conj):
                return disj(nnf(NotF(sub.left)), nnf(NotF(sub.right)))
            elif isinstance(sub.op, Disj):
                return conj(nnf(NotF(sub.left)), nnf(NotF(sub.right)))
    elif isinstance(f, BoolOpF):
        return BoolOpF(nnf(f.left), f.op, nnf(f.right))
    else:
        raise ValueError("nnf: type non connu")

n1 = NotF(ConstF(True))
n2 = NotF(conj(ComparF("x", Eq(), "y"), ComparF("y", Eq(), "z")))
n3 = NotF(eqf("x", "y"))
n4 = conj(NotF(ConstF(False)), 
          disj(ComparF("x", Eq(), "y"), ConstF(True)))

print("test nnf :",n1,"->",nnf(n1))
print("test nnf :",n2,"->",nnf(n2))
print("test nnf :",n3,"->",nnf(n3))
print("test nnf :",n4,"->",nnf(n4))
print("nnf sur la formule du sujet sans quatificateur:", nnf(f))

def dnf(f: Formula) -> Formula:
    """Retourne la forme normale disjonctive de la formule f sans quantificateur."""
    return nnf(f)  # 
    

d1 = NotF(ConstF(True))
d2 = NotF(conj(ComparF("x", Eq(), "y"), ComparF("y", Eq(), "z")))
d3 = NotF(eqf("x", "y"))
d4 = conj(NotF(ConstF(False)), 
          disj(ComparF("x", Eq(), "y"), ConstF(True)))

print("test dnf :",d1,"->",dnf(d1))
print("test dnf :",d2,"->",dnf(d2))     
print("test dnf :",d3,"->",dnf(d3))
print("test dnf :",d4,"->",dnf(d4))
print("dnf sur la formule du sujet sans quatificateur:", dnf(f))

print("\n=== Fin des tests ===")