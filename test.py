# -*- coding: utf-8 -*-
from fonctions import *


def test_base():
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


    print("\n=== Fonction récursive : dual ===")

    # Test de dual et dualOp
    test = conj(ConstF(True), ConstF(False))
    print("Formule originale :", test)
    print("Dual :", dual(test))
        
    print("Dual2 sur la formule du sujet :", dual2(f))
    print("\n=== Fonction nnf et dnf ===")

    # Tests de nnf
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
        
    # Tests de dnf
    d1 = NotF(ConstF(True))
    d2 = NotF(disj(ComparF("x", Eq(), "y"), ComparF("y", Eq(), "z")))
    d3 = NotF(eqf("x", "y"))
    d4 = conj(NotF(ConstF(False)), 
            disj(ComparF("x", Eq(), "y"), ConstF(True)))

    print("\ntest dnf :",d1,"->",dnf(d1))
    print("test dnf :",d2,"->",dnf(d2))     
    print("test dnf :",d3,"->",dnf(d3))
    print("test dnf :",d4,"->",dnf(d4))
    print("dnf sur la formule du sujet sans quatificateur:", dnf(f))

    print("\n=== Fin des tests de base ===")

def main():
    print("=== Tests des fonctions sur les formules ===")

    print("Quel test voulez vous exécuter ? :")
    print(" 1 - Test de base")
    print(" 2 - ...")


    choice = input("Entrez 1 ou 2 : ")
    while choice not in ["1", "2"]:
        print("Choix invalide. Veuillez entrer 1 ou 2.")
        choice = input("Entrez 1 ou 2 : ")

    if choice == "1":
        test_base()
    elif choice == "2":
        #test de isClose 
        f = allq("x", eqf("x", "y"))
        print(f)
        print(isClose(f)) # exemple d'appel
        f = toClose(f) # exemple d'appel
        print(f)
        print(isClose(f)) # vérifier que f est maintenant fermé
        print("Tests de isClose et toClose effectués.")




if __name__ == "__main__":
    main()