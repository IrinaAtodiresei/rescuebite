import os
from oferte_ui import formular_oferta
from pathlib import Path
from rezervari_ui import interfata_rezervari, confirma_ridicare
from rapoarte_ui import raport_valorificare

import pandas as pd
import streamlit as st
from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.errors import PyMongoError

load_dotenv(Path(__file__).with_name(".env"))

st.set_page_config(
    page_title="RescueBite",
    page_icon="🌿",
    layout="wide"
)


@st.cache_resource
def conectare():
    uri = os.getenv("MONGODB_URI")
    if not uri:
        raise ValueError("Lipseste MONGODB_URI din fisierul .env.")

    client = MongoClient(
        uri,
        serverSelectionTimeoutMS=10000,
        tz_aware=True
    )
    client.admin.command("ping")
    return client


try:
    client = conectare()
    db = client[os.getenv("MONGODB_DB", "rescuebite")]
    if not {"parteneri", "pachete", "rezervari"}.issubset(
        set(db.list_collection_names())
    ):
        st.error("Baza selectata nu contine toate colectiile proiectului.")
        st.stop()
except (PyMongoError, ValueError):
    st.error(
        "Conectarea a esuat. Verifica URI-ul, parola si accesul "
        "la clusterul Atlas."
    )
    st.stop()

st.title("🌿 RescueBite")
st.caption("Surplus alimentar transformat in oportunitate.")

st.sidebar.success("Conectat la MongoDB")
st.sidebar.write("Baza de date: rescuebite")
if st.sidebar.button("Actualizeaza datele"):
    st.rerun()

oferte_tab, editare_tab, rezervari_tab, rapoarte_tab = st.tabs(
    ["Oferte", "Administrare", "Rezervari", "Rapoarte"]
)

try:
    parteneri = {
        p["_id"]: p["denumire"]
        for p in db.parteneri.find()
    }

    with oferte_tab:
        st.subheader("Catalogul ofertelor")
        categorii = ["Toate"] + sorted(db.pachete.distinct("categorie"))
        categorie = st.selectbox("Categorie", categorii)
        doar_publicate = st.checkbox("Doar oferte publicate", value=True)

        filtru = {}
        if categorie != "Toate":
            filtru["categorie"] = categorie
        if doar_publicate:
            filtru["status"] = "publicat"

        pachete = list(db.pachete.find(filtru).sort("_id", 1))

        randuri = [
            {
                "ID": p["_id"],
                "Oferta": p["denumire"],
                "Partener": parteneri.get(p["partenerId"], "Necunoscut"),
                "Categorie": p["categorie"],
                "Pret initial (lei)": p["pretInitialBani"] / 100,
                "Pret redus (lei)": p["pretRedusBani"] / 100,
                "Stoc": p["stocDisponibil"],
                "Status": p["status"]
            }
            for p in pachete
        ]

        if randuri:
            st.dataframe(
                pd.DataFrame(randuri),
                hide_index=True,
                use_container_width=True
            )
        else:
            st.info("Nu exista oferte pentru filtrele selectate.")

    with editare_tab:
        st.subheader("Modifica pretul unei oferte")
        editabile = list(
            db.pachete.find({"status": "publicat"}).sort("_id", 1)
        )

        if not editabile:
            st.info("Nu exista oferte publicate.")
        else:
            optiuni = {p["_id"]: p for p in editabile}
            ales = st.selectbox(
                "Oferta",
                options=list(optiuni),
                format_func=lambda x: f"{x} - {optiuni[x]['denumire']}"
            )
            pachet = optiuni[ales]

            with st.form(f"pret_{ales}"):
                st.write(
                    f"Pret initial: {pachet['pretInitialBani'] / 100:.2f} lei"
                )
                pret = st.number_input(
                    "Pret redus nou (lei)",
                    min_value=0.01,
                    max_value=float(pachet["pretInitialBani"] / 100),
                    value=float(pachet["pretRedusBani"] / 100),
                    step=0.50,
                    format="%.2f"
                )
                salveaza = st.form_submit_button("Salveaza pretul")

            if salveaza:
                pret_bani = int(round(pret * 100))
                rezultat = db.pachete.update_one(
                    {
                        "_id": ales,
                        "status": "publicat",
                        "pretRedusBani": pachet["pretRedusBani"],
                        "pretInitialBani": {"$gte": pret_bani}
                    },
                    {"$set": {"pretRedusBani": pret_bani}}
                )
                if rezultat.matched_count:
                    st.success(
                        "Pret salvat in MongoDB. Apasa Actualizeaza "
                        "datele pentru reincarcarea catalogului."
                    )
                else:
                    st.warning(
                        "Oferta a fost modificata intre timp. "
                        "Actualizeaza datele si incearca din nou."
                    )

    with rapoarte_tab:
        st.subheader("Impact si vanzari")

        # indicatorii sunt calculati in MongoDB
        totaluri = list(db.rezervari.aggregate([
            {"$match": {"status": "ridicata"}},
            {"$group": {
                "_id": None,
                "rezervari": {"$sum": 1},
                "salvate": {"$sum": "$cantitate"},
                "venitBani": {"$sum": {
                    "$multiply": ["$cantitate", "$pretUnitarBani"]
                }}
            }}
        ]))

        total = totaluri[0] if totaluri else {
            "rezervari": 0, "salvate": 0, "venitBani": 0
        }

        c1, c2, c3 = st.columns(3)
        c1.metric("Pachete salvate", total["salvate"])
        c2.metric("Rezervari ridicate", total["rezervari"])
        c3.metric("Vanzari realizate", f"{total['venitBani'] / 100:.2f} lei")

        clasament = list(db.rezervari.aggregate([
            {"$match": {"status": "ridicata"}},
            {"$lookup": {
                "from": "pachete",
                "localField": "pachetId",
                "foreignField": "_id",
                "as": "pachet"
            }},
            {"$unwind": "$pachet"},
            {"$group": {
                "_id": "$pachet.partenerId",
                "salvate": {"$sum": "$cantitate"},
                "venitBani": {"$sum": {
                    "$multiply": ["$cantitate", "$pretUnitarBani"]
                }}
            }},
            {"$lookup": {
                "from": "parteneri",
                "localField": "_id",
                "foreignField": "_id",
                "as": "partener"
            }},
            {"$unwind": "$partener"},
            {"$project": {
                "_id": 0,
                "Partener": "$partener.denumire",
                "Pachete salvate": "$salvate",
                "Venit (lei)": {"$divide": ["$venitBani", 100]}
            }},
            {"$sort": {"Venit (lei)": -1, "Partener": 1}}
        ]))

        if clasament:
            tabel = pd.DataFrame(clasament)
            st.subheader("Vanzari pe partener")
            st.bar_chart(tabel.set_index("Partener")["Venit (lei)"])
            st.dataframe(tabel, hide_index=True, use_container_width=True)

        st.caption(
            "Pachete salvate = pachete din rezervari ridicate. "
            "Vanzarile reprezinta incasarile localurilor, nu profitul platformei."
        )

except PyMongoError:
    st.error(
        "Operatia MongoDB nu a putut fi finalizata. "
        "Verifica conexiunea si regulile de validare."
    )

with editare_tab:
    st.divider()
    formular_oferta(db)

with rezervari_tab:
    interfata_rezervari(db, client)
    confirma_ridicare(db)

with rapoarte_tab:
    raport_valorificare(db)