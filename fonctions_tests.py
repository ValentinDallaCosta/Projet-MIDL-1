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

def test_isClose_toClose():
    print("=== Test des fonctions isClose et toClose ===")
    # Exemple de formule avec variable libre : ∀x (x = y)
    f = allq("x", eqf("x", "y"))
    print("Formule avec variable libre :", f)
    print("Variables libres :", freeVar(f))
    print("isClose(f) =", isClose(f))
    f_closed = toClose(f)
    print("Formule fermée obtenue avec toClose :", f_closed)
    print("Variables libres de la formule fermée :", freeVar(f_closed))
    print("isClose(f_closed) =", isClose(f_closed))

def test_allToExist():
    print("=== Test de la fonction allToExist ===")
    # Exemple de formule en prénexe avec quantificateurs universels : ∀x ∀y (x = y)
    f = allq("x", allq("y", eqf("x", "y")))
    print("Formule en prénexe avec quantificateurs universels :", f)
    f_existential = allToExist(f)
    print("Formule transformée avec allToExist :", f_existential)

def test_isPrenexe():
    print("=== Test de la fonction isPrenexe ===")
    # Exemple de formule en prénexe : ∀x ∃y (x = y)
    f1 = allq("x", exq("y", eqf("x", "y")))
    print("Formule f1 :", f1)
    print("isPrenexe(f1) =", isPrenexe(f1))

    # Exemple de formule non en prénexe : ∃y ∀x (x = y)
    f2 = exq("y", allq("x", eqf("x", "y")))
    print("Formule f2 :", f2)
    print("isPrenexe(f2) =", isPrenexe(f2))

def test_elimNegation():
    print("=== Test de la fonction elimNegation ===")
    # Exemple de formule avec négation devant un quantificateur : ¬(∀x (x = y))
    f = NotF(allq("x", eqf("x", "y")))
    print("Formule avec négation devant un quantificateur :", f)
    f1 = allToExist(f)
    print("Formule après allToExist :", f1)
    f_elim = elimNegation(f1)
    print("Formule après application de elimNegation :", f_elim)

    print("\n")
    # Autre exemple : (∃y ¬(x < y))
    g = exq("y", NotF(ltf("x", "y")))
    print("Autre formule avec négation devant un quantificateur :", g)
    g1 = allToExist(g)
    print("Formule après allToExist :", g1)
    g_elim = elimNegation(g1)
    print("Formule après application de elimNegation :", g_elim)

def test_tirerNegation():
    print("=== Test de la fonction tirerNegation ===")
    # Exemple sur la formule : ¬∃x, ∃y, ¬( (x = y) ∧ (y < z) )
    f = NotF(exq("x", exq("y", NotF(conj(eqf("x", "y"), ltf("y", "z"))))))
    print("Formule avec négation devant une conjonction :", f)
    f_tirer = tirerNegation(f)
    print("Formule après application de tirerNegation :", f_tirer)

    print("\n")
    # Autre exemple : ¬( (x = y) ∨ (y < z) )
    g = NotF(disj(eqf("x", "y"), ltf("y", "z")))
    print("Autre formule avec négation devant une disjonction :", g)
    g_tirer = tirerNegation(g)
    print("Formule après application de tirerNegation :", g_tirer)

def test_toDisjonctive():
    print("=== Test de la fonction toDisjonctive ===")
    # Exemple de formule non en forme disjonctive :∃x, ∃y, ∃z,  (((x < y) ∨ (y < x)) ∧ ((y < z))
    f = exq("x", exq("y", exq("z", conj(disj(ltf("x", "y"), ltf("y", "x")), ltf("y", "z")))))
    print("Formule non en forme disjonctive :", f)
    f_dnf = toDisjonctive(f)
    print("Formule après application de toDisjonctive :", f_dnf)

def test_global():
    print("=== Tests des fonctions sur les formules ===")

    print("Quel test voulez vous exécuter ? :")
    print(" 1 - Test de base")
    print(" 2 - Test des fonctions vérifiant les hypothèses pour la procédure de décision")
    print(" 3 - Test des fonctions de prétraitement des formules")


    choice = input("Entrez 1, 2 ou 3: ")
    while choice not in ["1", "2", "3"]:
        print("Choix invalide. Veuillez entrer 1, 2 ou 3.")
        choice = input("Entrez 1, 2 ou 3 : ")

    if choice == "1":
        print("Début des tests de base\n")
        test_base()
    elif choice == "2":
        print("Début des tests des fonctions vérifiant les hypothèses pour la procédure de décision\n")
        test_isClose_toClose()
        print("\n")
        test_allToExist()
        print("\n")
        test_isPrenexe()
    elif choice == "3":
        print("Début des tests des fonctions de prétraitement des formules\n")
        test_tirerNegation()
        print("\n")
        test_elimNegation()
        print("\n")
        test_toDisjonctive()