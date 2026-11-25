from datetime import datetime, time, timedelta, timezone
from zoneinfo import ZoneInfo

import streamlit as st
from pymongo.errors import PyMongoError


def formular_oferta(db):
    st.subheader("Publica o oferta noua")

    parteneri = {
        p["_id"]: p["denumire"]
        for p in db.parteneri.find({"activ": True})
    }

    if not parteneri:
        st.info("Nu exista parteneri activi.")
        return

    zona = ZoneInfo("Europe/Bucharest")
    maine = datetime.now(zona).date() + timedelta(days=1)

    with st.form("oferta_noua", clear_on_submit=True):
        partener_id = st.selectbox(
            "Partener",
            options=list(parteneri),
            format_func=lambda x: parteneri[x]
        )

        denumire = st.text_input("Denumirea ofertei")

        categorie = st.selectbox(
            "Categoria",
            [
                "Panificatie",
                "Patiserie",
                "Mancare gatita",
                "Vegetarian",
                "Desert",
                "Fructe si legume"
            ]
        )

        continut_text = st.text_area(
            "Continut: un produs pe rand, in formatul produs;cantitate",
            placeholder="Covrig;2\nPlacinta cu mere;1"
        )

        c1, c2 = st.columns(2)

        with c1:
            pret_initial = st.number_input(
                "Pret initial (lei)",
                min_value=0.01,
                value=30.0,
                step=1.0,
                format="%.2f"
            )

        with c2:
            pret_redus = st.number_input(
                "Pret redus (lei)",
                min_value=0.01,
                value=12.0,
                step=1.0,
                format="%.2f"
            )

        stoc = st.number_input(
            "Numar de pachete",
            min_value=1,
            value=5,
            step=1
        )

        data_ridicare = st.date_input(
            "Data ridicarii",
            value=maine
        )

        c3, c4 = st.columns(2)

        with c3:
            ora_inceput = st.time_input(
                "Ridicare de la",
                value=time(17, 0)
            )

        with c4:
            ora_sfarsit = st.time_input(
                "Ridicare pana la",
                value=time(19, 0)
            )

        etichete_text = st.text_input(
            "Etichete separate prin virgula",
            placeholder="vegetarian, oferta de seara"
        )

        publicare = st.form_submit_button("Publica oferta")

    if not publicare:
        return

    denumire = denumire.strip()
    if len(denumire) < 3:
        st.error("Denumirea trebuie sa aiba minimum 3 caractere.")
        return

    initial_bani = int(round(pret_initial * 100))
    redus_bani = int(round(pret_redus * 100))

    if redus_bani > initial_bani:
        st.error("Pretul redus nu poate depasi pretul initial.")
        return

    inceput = datetime.combine(
        data_ridicare, ora_inceput, tzinfo=zona
    )
    sfarsit = datetime.combine(
        data_ridicare, ora_sfarsit, tzinfo=zona
    )

    if sfarsit <= inceput:
        st.error("Ora de sfarsit trebuie sa fie dupa ora de inceput.")
        return

    if inceput <= datetime.now(zona):
        st.error("Intervalul de ridicare trebuie sa inceapa in viitor.")
        return

    # citesc produsele introduse in formular
    continut = []
    try:
        for linie in continut_text.splitlines():
            if not linie.strip():
                continue

            produs, cantitate_text = linie.rsplit(";", 1)
            cantitate = int(cantitate_text.strip())
            produs = produs.strip()

            if not produs or cantitate < 1:
                raise ValueError

            continut.append({
                "produs": produs,
                "cantitate": cantitate
            })
    except ValueError:
        st.error(
            "Continut invalid. Exemplu: Covrig;2. "
            "Cantitatea trebuie sa fie un numar intreg pozitiv."
        )
        return

    if not continut:
        st.error("Introdu cel putin un produs.")
        return

    etichete = list(dict.fromkeys(
        text.strip().lower()
        for text in etichete_text.split(",")
        if text.strip()
    ))

    try:
        if not db.parteneri.find_one({
            "_id": partener_id,
            "activ": True
        }):
            st.error("Partenerul nu mai este activ.")
            return

        rezultat = db.pachete.insert_one({
            "partenerId": partener_id,
            "denumire": denumire,
            "categorie": categorie,
            "continut": continut,
            "pretInitialBani": initial_bani,
            "pretRedusBani": redus_bani,
            "stocInitial": int(stoc),
            "stocDisponibil": int(stoc),
            "ridicare": {
                "inceput": inceput.astimezone(timezone.utc),
                "sfarsit": sfarsit.astimezone(timezone.utc)
            },
            "status": "publicat",
            "etichete": etichete,
            "creatLa": datetime.now(timezone.utc)
        })

        st.success("Oferta a fost publicata in MongoDB.")
        st.code(str(rezultat.inserted_id), language=None)
        st.info("Apasa Actualizeaza datele pentru a vedea oferta in catalog.")

    except PyMongoError:
        st.error("Oferta nu a putut fi salvata in MongoDB.")