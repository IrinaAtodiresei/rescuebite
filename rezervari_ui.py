import re
from datetime import datetime, timezone

import pandas as pd
import streamlit as st
from bson import ObjectId
from pymongo import ReturnDocument
from pymongo.errors import PyMongoError


def interfata_rezervari(db, client):
    st.subheader("Rezerva un pachet")

    if "cerere_rezervare_id" not in st.session_state:
        st.session_state.cerere_rezervare_id = ObjectId()

    try:
        acum = datetime.now(timezone.utc)
        oferte = list(db.pachete.find({
            "status": "publicat",
            "stocDisponibil": {"$gt": 0},
            "ridicare.sfarsit": {"$gt": acum}
        }).sort("denumire", 1))

        if not oferte:
            st.info("Nu exista oferte disponibile pentru rezervare.")
        else:
            optiuni = {p["_id"]: p for p in oferte}

            ales = st.selectbox(
                "Alege oferta",
                options=list(optiuni),
                format_func=lambda x: optiuni[x]["denumire"],
                key="oferta_rezervare"
            )
            oferta = optiuni[ales]

            st.write(
                f"Pret: {oferta['pretRedusBani'] / 100:.2f} lei / pachet"
                f" | Disponibile: {oferta['stocDisponibil']}"
            )

            with st.form(f"rezervare_{ales}"):
                nume = st.text_input("Nume client")
                email = st.text_input("Email client")
                cantitate = st.number_input(
                    "Cate pachete rezervi?",
                    min_value=1,
                    max_value=int(oferta["stocDisponibil"]),
                    value=1,
                    step=1
                )
                trimite = st.form_submit_button("Confirma rezervarea")

            if trimite:
                nume = nume.strip()
                email = email.strip().lower()

                if len(nume) < 3:
                    st.error("Introdu un nume de minimum 3 caractere.")
                elif not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email):
                    st.error("Introdu o adresa de email valida.")
                else:
                    rezervare_id = st.session_state.cerere_rezervare_id
                    cantitate = int(cantitate)

                    # rezervarea si stocul se modifica impreuna
                    def creeaza(session):
                        existenta = db.rezervari.find_one(
                            {"_id": rezervare_id},
                            session=session
                        )
                        if existenta:
                            return

                        pachet = db.pachete.find_one_and_update(
                            {
                                "_id": ales,
                                "status": "publicat",
                                "stocDisponibil": {"$gte": cantitate},
                                "pretRedusBani": oferta["pretRedusBani"],
                                "ridicare.sfarsit": {
                                    "$gt": datetime.now(timezone.utc)
                                }
                            },
                            {"$inc": {"stocDisponibil": -cantitate}},
                            return_document=ReturnDocument.AFTER,
                            session=session
                        )

                        if not pachet:
                            raise ValueError(
                                "Oferta a expirat sau pretul/stocul s-a "
                                "modificat. Actualizeaza datele."
                            )

                        db.rezervari.insert_one(
                            {
                                "_id": rezervare_id,
                                "pachetId": ales,
                                "client": {"nume": nume, "email": email},
                                "cantitate": cantitate,
                                "pretUnitarBani": pachet["pretRedusBani"],
                                "status": "rezervata",
                                "creatLa": datetime.now(timezone.utc)
                            },
                            session=session
                        )

                    with client.start_session() as session:
                        session.with_transaction(creeaza)

                    st.session_state.cerere_rezervare_id = ObjectId()
                    st.success(
                        "Rezervare salvata. Stocul a fost redus. "
                        "Apasa Actualizeaza datele."
                    )

        st.divider()
        st.subheader("Rezervari in asteptarea ridicarii")

        rezervari = list(db.rezervari.find({
            "status": "rezervata"
        }).sort("creatLa", -1))

        if not rezervari:
            st.info("Nu exista rezervari in asteptare.")
            return

        pachete = {
            p["_id"]: p["denumire"]
            for p in db.pachete.find({}, {"denumire": 1})
        }

        st.dataframe(
            pd.DataFrame([
                {
                    "ID": str(r["_id"]),
                    "Oferta": pachete.get(r["pachetId"], "Necunoscuta"),
                    "Client": r["client"]["nume"],
                    "Cantitate": r["cantitate"],
                    "Total (lei)": (
                        r["cantitate"] * r["pretUnitarBani"] / 100
                    ),
                    "Status": r["status"]
                }
                for r in rezervari
            ]),
            hide_index=True,
            use_container_width=True
        )

        optiuni_rezervari = {r["_id"]: r for r in rezervari}

        anulare_id = st.selectbox(
            "Rezervarea pe care doresti sa o anulezi",
            options=list(optiuni_rezervari),
            format_func=lambda x: (
                f"{optiuni_rezervari[x]['client']['nume']} - "
                f"{pachete.get(optiuni_rezervari[x]['pachetId'], '')}"
                f" - {x}"
            )
        )

        if st.button("Anuleaza rezervarea"):
            def anuleaza(session):
                rezervare = db.rezervari.find_one_and_update(
                    {"_id": anulare_id, "status": "rezervata"},
                    {
                        "$set": {
                            "status": "anulata",
                            "anulataLa": datetime.now(timezone.utc)
                        }
                    },
                    return_document=ReturnDocument.BEFORE,
                    session=session
                )

                if not rezervare:
                    raise ValueError(
                        "Rezervarea nu mai poate fi anulata. "
                        "Actualizeaza datele."
                    )

                rezultat = db.pachete.update_one(
                    {"_id": rezervare["pachetId"]},
                    {"$inc": {
                        "stocDisponibil": rezervare["cantitate"]
                    }},
                    session=session
                )

                if rezultat.matched_count != 1:
                    raise ValueError("Pachetul asociat nu mai exista.")

            with client.start_session() as session:
                session.with_transaction(anuleaza)

            st.success(
                "Rezervare anulata si stoc restituit. "
                "Apasa Actualizeaza datele."
            )

    except ValueError as eroare:
        st.warning(str(eroare))
    except PyMongoError:
        st.error(
            "Operatia nu a putut fi confirmata. Actualizeaza datele "
            "si verifica rezervarile inainte de a reincerca."
        )

def confirma_ridicare(db):
    st.divider()
    st.subheader("Confirma ridicarea")

    try:
        rezervari = list(db.rezervari.find({
            "status": "rezervata"
        }).sort("creatLa", -1))

        if not rezervari:
            st.info("Nu exista rezervari de confirmat.")
            return

        optiuni = {r["_id"]: r for r in rezervari}

        ales = st.selectbox(
            "Rezervare",
            options=list(optiuni),
            format_func=lambda x: (
                f"{optiuni[x]['client']['nume']} - "
                f"{optiuni[x]['cantitate']} pachete - {x}"
            ),
            key="rezervare_ridicare"
        )

        rezervare = optiuni[ales]
        pachet = db.pachete.find_one({
            "_id": rezervare["pachetId"]
        })

        if not pachet:
            st.error("Oferta asociata nu mai exista.")
            return

        st.write(f"Oferta: {pachet['denumire']}")
        st.write(
            f"Total: "
            f"{rezervare['cantitate'] * rezervare['pretUnitarBani'] / 100:.2f}"
            " lei"
        )

        acum = datetime.now(timezone.utc)
        if acum < pachet["ridicare"]["inceput"]:
            st.warning(
                "Intervalul programat nu a inceput. Confirma numai "
                "daca pachetele au fost predate efectiv. Pentru test, "
                "foloseste exclusiv rezervarea demonstrativa."
            )
        elif acum > pachet["ridicare"]["sfarsit"]:
            st.warning(
                "Intervalul programat s-a incheiat. Confirma numai "
                "daca pachetele au fost predate efectiv."
            )

        with st.form(f"confirmare_ridicare_{ales}"):
            confirmat = st.checkbox(
                "Confirm predarea pachetelor si incasarea sumei"
            )
            trimite = st.form_submit_button("Marcheaza ca ridicata")

        if trimite:
            if not confirmat:
                st.error("Bifeaza confirmarea predarii.")
                return

            # schimb statusul fara sa mai modific stocul
            rezultat = db.rezervari.update_one(
                {"_id": ales, "status": "rezervata"},
                {
                    "$set": {
                        "status": "ridicata",
                        "ridicataLa": datetime.now(timezone.utc)
                    }
                }
            )

            if rezultat.modified_count == 1:
                st.success(
                    "Ridicare confirmata. Pentru actualizarea rapoartelor, "
                    "apasa Actualizeaza datele din bara din stanga."
                )
            else:
                st.warning(
                    "Rezervarea a fost deja modificata. "
                    "Actualizeaza datele."
                )

    except PyMongoError:
        st.error(
            "Confirmarea nu a putut fi verificata. "
            "Actualizeaza datele inainte de a reincerca."
        )