# -*- coding: utf-8 -*-
from fonctions import *

#------TESTS DES FONCTIONS DE BASES------#
def test_syntax():
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

def test_dual():
    print("\n=== Fonction récursive : dual ===")
    # Test de dual et dualOp
    test = conj(ConstF(True), ConstF(False))
    print("Formule originale :", test)
    print("Dual :", dual(test))
        
    # Exemple de formule avec quantificateurs pour dual2
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
    print("Dual2 sur la formule du sujet :", dual2(f))

def test_nnf():
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
        
def test_dnf():
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

def test_extraireQuantificateurs():
    print("=== Test de la fonction extraireQuantificateurs ===")
    # Exemple de formule avec quantificateurs : ∀x ∀y (x = y)
    f = allq("x", exq("y", eqf("x", "y")))
    print("Formule originale :", f)
    body, quantifiers = extraireQuantificateurs(f)
    print("Corps extrait :", body)
    print("Quantificateurs extraits :",reconstruireAvecQuantificateurs("", quantifiers))

    # Autre exemple avec négation : ¬∀x (x = y)
    g = NotF(allq("x", eqf("x", "y")))
    print("\nFormule avec négation :", g)
    body_g, quantifiers_g = extraireQuantificateurs(g)
    print("Corps extrait :", body_g)
    print("Quantificateurs extraits :",reconstruireAvecQuantificateurs("", quantifiers_g))

def test_reconstruireAvecQuantificateurs():
    print("=== Test de la fonction reconstruireAvecQuantificateurs ===")
    # Utilisons les résultats de extraireQuantificateurs
    f = allq("x", exq("y", eqf("x", "y")))
    body, quantifiers = extraireQuantificateurs(f)
    reconstructed = reconstruireAvecQuantificateurs(body, quantifiers)
    print("Formule originale :", f)
    print("Formule reconstruite :", reconstructed)
    print("Sont-elles égales ?", f == reconstructed)

def test_reconstruireAvecTermes():
    print("=== Test de la fonction reconstruireAvecTermes ===")
    # Exemple de termes : [quantifiers, x< u terms, u< x terms, x= u terms, other terms]
    quantifiers = [QuantifF(All(), "x", None), QuantifF(Ex(), "y", None)]
    terms = [
        quantifiers,
        [ltf("x", "a")],  # x < u
        [ltf("b", "x")],  # u < x
        [eqf("x", "c")],  # x = u
        [ltf("a", "b")]   # other
    ]
    reconstructed = reconstruireAvecTermes(terms)
    print("Termes :")
    affichageFormuleAvecTermes(terms)
    print("Formule reconstruite :", reconstructed)

def test_allVarInFormula():
    print("=== Test de la fonction allVarInFormula ===")
    # Exemple de formule : ∀x ∃y (x = y ∨ x < z)
    f = allq("x", exq("y", disj(eqf("x", "y"), ltf("x", "z"))))
    print("Formule :", f)
    vars_in_formula = allVarInFormula(f)
    print("Toutes les variables dans la formule :", vars_in_formula)

def test_extracts():
    print("=== Test des fonctions extract ===")
    # Exemple de formule : ∃x ( (x < a) ∧ (b < x) ∧ (x = c) ∧ (d < e) )
    f = exq("x", conj(conj(conj(ltf("x", "a"), ltf("b", "x")), eqf("x", "c")), ltf("d", "e")))
    print("Formule :", f)
    affichageListeTermes(extractxltu(f, "x"),"Termes x < u :")
    affichageListeTermes(extractultx(f, "x"),"Termes u < x :")
    affichageListeTermes(extracteqx(f, "x"),"Termes x = w :")
#------FIN TESTS DES FONCTIONS DE BASES------#

#------TESTS DES FONCTIONS DE VERIFICATION DES HYPOTHESES------#
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

def test_freeVar():
    print("=== Test de la fonction freeVar ===")
    # Exemple de formule avec variables libres : ∀x (x = y)
    f = allq("x", eqf("x", "y"))
    print("Formule :", f)
    free_vars = freeVar(f)
    print("Variables libres :", free_vars)

    # Formule close : ∀x ∀y (x = y)
    g = allq("x", allq("y", eqf("x", "y")))
    print("\nFormule close :", g)
    free_vars_g = freeVar(g)
    print("Variables libres :", free_vars_g)

def test_isJustSymboleRelationnel():
    print("=== Test de la fonction isJustSymboleRelationnel ===")
    # Exemple de formule avec seulement symboles relationnels : (x = y) ∧ (y < z)
    f1 = conj(eqf("x", "y"), ltf("y", "z"))
    print("Formule f1 :", f1)
    print("isJustSymboleRelationnel(f1) =", isJustSymboleRelationnel(f1))

    # Exemple avec constante : (x = y) ∧ True
    f2 = conj(eqf("x", "y"), ConstF(True))
    print("\nFormule f2 :", f2)
    print("isJustSymboleRelationnel(f2) =", isJustSymboleRelationnel(f2))

def test_isElimPossible():
    print("=== Test de la fonction isElimPossible ===")
    # Exemple de formule éligible : ∀x ∃y (x = y)
    f1 = allq("x", exq("y", eqf("x", "y")))
    print("Formule f1 :", f1)
    print("isElimPossible(f1) =", isElimPossible(f1))

    # Exemple non éligible (non close) : ∀x (x = y)
    f2 = allq("x", eqf("x", "y"))
    print("\nFormule f2 :", f2)
    print("isElimPossible(f2) =", isElimPossible(f2))

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
#------FIN TESTS DES FONCTIONS DE VERIFICATION DES HYPOTHESES------#

#------TESTS DES FONCTIONS DE PRETRAITEMENT------#
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

def test_isDisjonctive():
    print("=== Test de la fonction isDisjonctive ===")
    # Exemple de formule en forme disjonctive : ∃x, ∃y,  ((x < y) ∨ (y < x))
    f1 = exq("x", exq("y", disj(ltf("x", "y"), ltf("y", "x"))))
    print("Formule f1 :", f1)
    print("isDisjonctive(f1) =", isDisjonctive(f1))

    # Exemple de formule non en forme disjonctive : ∃x, ∃y,  ((x < y) ∧ (y < x))
    f2 = exq("x", exq("y", conj(ltf("x", "y"), ltf("y", "x"))))
    print("Formule f2 :", f2)
    print("isDisjonctive(f2) =", isDisjonctive(f2))

def test_tirerQuantif():
    print("=== Test de la fonction tirerQuantif ===")
    # Exemple 1 : ∃x ¬∃y ∃z ( (x < y) ∨ (y < z) )
    f1 = exq("x", NotF(exq("y", exq("z", disj(ltf("x", "y"), ltf("y", "z"))))))
    print("Formule f1 :", f1)
    res1 = tirerQuantif(f1)
    print("Liste retournée pour f1 :")
    for i, r in enumerate(res1, 1):
        print(f"  [{i}]", r)

    print("\n")
    # Exemple 2 : ∃x ∃y ∃z ¬∃w ( (x < y ∧ y = z) ∨ (x = z ∧ z < w) )
    f2 = exq("x", exq("y", exq("z", NotF(exq("w", disj(conj(ltf("x", "y"), eqf("y", "z")), conj(eqf("x", "z"), ltf("z", "w"))))))))
    print("Formule f2 :", f2)
    res2 = tirerQuantif(f2)
    print("Liste retournée pour f2 :")
    for i, r in enumerate(res2, 1):
        print(f"  [{i}]", r)
#------FIN TESTS DES FONCTIONS DE PRETRAITEMENT------#

#------TESTS DES FONCTIONS DE SUPPRESIION DE VARIABLES------#
def test_elimQuantifInutile():
    print("=== Test de la fonction elimQuantifInutile ===")
    # Exemple de formule avec quantificateurs inutiles : ∃x ∃y ∃z (x = y)
    f = exq("x", exq("y", exq("z", eqf("x", "y"))))
    print("Formule avec quantificateurs inutiles :", f)
    f_elim = elimQuantifInutile([f])
    print("Formule après application de elimQuantifInutile :", f_elim[0])

    # Autre exemple : ∃x ¬∃w ∃y ∃z ((x < y) ∨ (y < z))
    f2 = exq("x", NotF(exq("w", exq("y", exq("z", disj(ltf("x", "y"), ltf("y", "z")))))))
    print("\nAutre formule avec quantificateurs inutiles :", f2)
    f2_elim = elimQuantifInutile([f2])
    print("Formule après application de elimQuantifInutile :", f2_elim[0])

def test_searchXltX():
    print("=== Test de la fonction searchXltX ===")
    # Exemple de formule contenant (x < x) : ∃x ( (x < x) ∨ (y < z) )
    f1 = exq("x", disj(ltf("x", "x"), ltf("y", "z")))
    print("Formule f1 :", f1)
    print("searchXltX(f1) =", searchXltX(f1))

    # Exemple de formule ne contenant pas (x < x) : ∃x ( (x < y) ∨ (y < z) )
    f2 = exq("x", disj(ltf("x", "y"), ltf("y", "z")))
    print("Formule f2 :", f2)
    print("searchXltX(f2) =", searchXltX(f2))

def test_regrouperTermes():
    print("=== Test de la fonction regrouperTermes ===")
    # Exemple de formule : ∃x ∃y ∃z ( (x < y) ∧ (y < x) ∧ (y = x) ∧ (u < v) ) et ∃a ∃b ( (x < a) ∧ (b < x) ∧ (x = b) )
    f = exq("x", exq("y", exq("z", conj(conj(conj(ltf("x", "y"), ltf("y", "x")), eqf("y", "x")), ltf("u", "v")))))
    f2 = exq("a", exq("b", conj(conj(ltf("x", "a"), ltf("b", "x")), eqf("x", "b"))))
    print("Formule 1 :", f, "\nFormule 2 :", f2)
    grouped_terms1 = regrouperTermes(f, "x")
    grouped_terms2 = regrouperTermes(f2, "x")
    grouped_terms = [grouped_terms1, grouped_terms2]

    print("Résultat de regrouperTermes avec x comme variable de référence :")

    for i, formule in enumerate(grouped_terms, 1):
        print(f"  Formule {i} :")
        print(f"    Quantificateurs :")
        print("      - ", reconstruireAvecQuantificateurs("", formule[0]))

        affichageFormuleAvecTermes(formule)
        print()

def test_simplifierInegalites():
    print("=== Test de la fonction simplifierInegalites ===")
    # Exemple de termes
    less_than_terms = [ltf("x", "a"), ltf("x", "b")]
    greater_than_terms = [ltf("c", "x"), ltf("d", "x")]
    affichageListeTermes(less_than_terms,"Termes x < v :")
    affichageListeTermes(greater_than_terms,"Termes u < x :")
    simplified = simplifierInegalites(less_than_terms, greater_than_terms)
    affichageListeTermes(simplified,"Termes simplifiés (u < v) :")

def test_xeqw():
    print("=== Test de la fonction xeqw ===")
    # Exemple avec les formules de test_regroupertermes
    # Exemple de formule : ∃x ∃y ∃z ( (x < y) ∧ (y < x) ∧ (y = x) ∧ (u < v) ) et ∃a ∃b ( (x < a) ∧ (b < x) ∧ (x = b) )
    f = exq("x", exq("y", exq("z", conj(conj(conj(ltf("x", "y"), ltf("y", "x")), eqf("y", "x")), ltf("u", "v")))))
    f2 = exq("a", exq("b", conj(conj(ltf("x", "a"), ltf("b", "x")), eqf("x", "b"))))
    print("Formule 1 :", f, "\nFormule 2 :", f2)
    xeqw_result1 = xeqw(regrouperTermes(f, "x"), "x")
    xeqw_result2 = xeqw(regrouperTermes(f2, "x"), "x")
    xeqw_result = [xeqw_result1, xeqw_result2]

    print("Résultat de xeqw avec x comme variable de référence sur les formules de test_regrouperTermes() :")
    for i, formule in enumerate(xeqw_result, 1):
        print(f"    Quantificateurs :")
        
        print("      - ", reconstruireAvecQuantificateurs("", formule[0]))
        affichageFormuleAvecTermes(formule)
        print()
#------FIN TESTS DES FONCTIONS DE SUPPRESIION DE VARIABLES------#

#------TESTS DES FONCTIONS GENERALE DE DECISION------#
def test_isFormuleValide():
    print("=== Test de la fonction isFormuleValide ===")
    # Liste de formules contenant True
    formules1 = [ConstF(False), ConstF(True), eqf("x", "y")]
    print("Liste de formules 1 :")
    affichageListeFormules(formules1,"      ")
    print("isFormuleValide(formules1) =", isFormuleValide(formules1))

    # Liste sans True
    formules2 = [ConstF(False), eqf("x", "y")]
    print("Liste de formules 2 :")
    affichageListeFormules(formules2,"      ")

    print("isFormuleValide(formules2) =", isFormuleValide(formules2))

def test_supDeVariables():
    print("=== Test de la fonction supDeVariables ===")
    # Exemple de liste de formules (conjonctions)
    # Supposons une liste simple pour test
    formules = [exq("x", conj(eqf("x", "a"), ltf("b", "x")))]
    print("Liste de formules avant suppression :")
    affichageListeFormules(formules,"       ")
    result = supDeVariables(formules, False)
    print("Liste de formules après suppression de la variable x :")
    affichageListeFormules(result,"     ")
    # Aussi teste enchainementSupDeVar logiquement, mais comme c'est interactif, on ne peut pas le tester automatiquement
#------FIN TESTS DES FONCTIONS GENERALE DE DECISION------#

#------TESTS GLOBAUX------#
def test_bases():
    print("Début des tests de base\n")
    test_syntax()
    test_nnf()
    test_dual()
    test_dnf()
    print("\n")
    test_extraireQuantificateurs()
    print("\n")
    test_reconstruireAvecQuantificateurs()
    print("\n")
    test_reconstruireAvecTermes()
    print("\n")
    test_allVarInFormula()
    print("\n")
    test_extracts()
    print("\n=== Fin des tests de base ===")

def test_hypothese():
    print("Début des tests des fonctions vérifiant les hypothèses pour la procédure de décision\n")
    test_isClose_toClose()
    print("\n")
    test_freeVar()
    print("\n")
    test_isJustSymboleRelationnel()
    print("\n")
    test_isElimPossible()
    print("\n")
    test_allToExist()
    print("\n")
    test_isPrenexe()

def test_pretraitement():
    print("Début des tests des fonctions de prétraitement des formules\n")
    test_tirerNegation()
    print("\n")
    test_elimNegation()
    print("\n")
    test_toDisjonctive()
    print("\n")
    test_isDisjonctive()
    print("\n")
    test_tirerQuantif()

def test_supression():
    print("Début des tests des fonctions de suppression de variable\n")
    test_elimQuantifInutile()
    print("\n")
    test_searchXltX()
    print("\n")
    test_regrouperTermes()
    print("\n")
    test_simplifierInegalites()
    print("\n")
    test_xeqw()

def test_decision():
    print("Début des tests des fonctions générales de décision\n")
    test_isFormuleValide()
    print("\n")
    test_supDeVariables()

def test_global():
    print("=== Tests des fonctions sur les formules ===")

    print("Quel test voulez vous exécuter ? :")
    print(" 1 - Test de base")
    print(" 2 - Test des fonctions vérifiant les hypothèses pour la procédure de décision")
    print(" 3 - Test des fonctions de prétraitement des formules")
    print(" 4 - Test des fonctions de suppression de variable")
    print(" 5 - Test des fonctions générales de décision")
    print(" 6 - Tout les tests")

    choice = input("Entrez 1, 2, 3, 4, 5 ou 6: ")
    while choice not in ["1", "2", "3", "4", "5", "6"]:
        print("Choix invalide. Veuillez entrer 1, 2, 3, 4, 5 ou 6.")
        choice = input("Entrez 1, 2, 3, 4, 5 ou 6 : ")

    if choice == "6":
        test_bases()
        test_hypothese()
        test_pretraitement()
        test_supression()
        test_decision()
    if choice == "1":
        test_bases()
    elif choice == "2":
        test_hypothese()
    elif choice == "3":
        test_pretraitement()
    elif choice == "4":
        test_supression()
    elif choice == "5":
        test_decision()