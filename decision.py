#====PROCEDURE ====
# Exigences : 
    #— F doit être close (sans variables libres)
    #— Sinon : fermer avec ∀x0 ...xn. F pour {x0 ...xn}= fv(F)
    #— Les seules symboles relationels permis sont : ordre ≺,  ́egalité = ; pas de fonctions ou constantes.
# Démarche : 
    # 1. Convertir F en forme prénexe
    # 2. Convertir quantif. universels en existentiels : (∀x.φ) ↔¬(∃x. ¬φ) 
        # Attention : ce n’est pas une forme normale négative
    # 3.  ́Eliminer les quantificateurs à partir de l’intérieur

#Il faut peut être creer plusieurs fonctions pour chaque étape ou même fichiers.