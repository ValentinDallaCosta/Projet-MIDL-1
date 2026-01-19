from fonctions_tests import *


if __name__ == "__main__":
    print("=== Programme principal ===")

    print("\n--- Quel programme voulez-vous exécuter ? ---")
    print("1 : Tests des fonctions sur les formules")
    print("2 : Lancement du programme de décision avec une formule donnée")
    print("3 : Lancement du programme de décision avec une formule saisie par l'utilisateur")

    choice = input("Entrez 1, 2 ou 3 : ")
    while choice not in ["1", "2", "3"]:
        print("Choix invalide. Veuillez entrer 1, 2 ou 3.")
        choice = input("Entrez 1, 2 ou 3 : ")

    if choice == "1":
        print("\n")
        test_global()
    elif choice == "2":
        print("=== Test avec une formule prédéfinie ===\n")
        # Formule de test : ∀x ∀y ∃z ∃w ( ¬(x < x ∨ z < y) ∨ (y = z ∧ y < z) )
        f = allq("x", allq("y", exq("z", exq("w", disj(NotF(disj(ltf("w", "y"), ltf("y", "z"))), conj(eqf("y", "z"), ltf("y", "z")))))))
        print("Formule de test :", f)
        print("Lancement du programme de décision avec cette formule...\n")
        decision(f)

        print("\n")
    else:
        formule_utilisateur = input_formula_interactive()
        decision(formule_utilisateur)

        print("\n")
    