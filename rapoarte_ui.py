from datetime import datetime, timezone

import pandas as pd
import streamlit as st
from pymongo.errors import PyMongoError


def raport_valorificare(db):
    st.divider()
    st.subheader("Analiza ofertelor incheiate")

    st.caption(
        "Sunt analizate ofertele incheiate sau cu intervalul de "
        "ridicare expirat. Pachetele salvate sunt cele efectiv ridicate."
    )

    prag = st.slider(
        "Afiseaza ofertele cu rata de salvare sub (%)",
        min_value=0,
        max_value=100,
        value=70,
        step=5
    )

    try:
        # calculez rata de salvare pentru fiecare oferta
        rezultate = list(db.pachete.aggregate([
            {
                "$match": {
                    "status": {"$ne": "retras"},
                    "$or": [
                        {"status": "incheiat"},
                        {
                            "ridicare.sfarsit": {
                                "$lte": datetime.now(timezone.utc)
                            }
                        }
                    ]
                }
            },
            {
                "$lookup": {
                    "from": "rezervari",
                    "localField": "_id",
                    "foreignField": "pachetId",
                    "as": "rezervari"
                }
            },
            {
                "$addFields": {
                    "salvate": {
                        "$reduce": {
                            "input": "$rezervari",
                            "initialValue": 0,
                            "in": {
                                "$add": [
                                    "$$value",
                                    {
                                        "$cond": [
                                            {
                                                "$eq": [
                                                    "$$this.status",
                                                    "ridicata"
                                                ]
                                            },
                                            "$$this.cantitate",
                                            0
                                        ]
                                    }
                                ]
                            }
                        }
                    }
                }
            },
            {
                "$addFields": {
                    "rata": {
                        "$cond": [
                            {"$gt": ["$stocInitial", 0]},
                            {
                                "$multiply": [
                                    {
                                        "$divide": [
                                            "$salvate",
                                            "$stocInitial"
                                        ]
                                    },
                                    100
                                ]
                            },
                            0
                        ]
                    }
                }
            },
            {
                "$match": {
                    "rata": {"$lt": prag}
                }
            },
            {
                "$lookup": {
                    "from": "parteneri",
                    "localField": "partenerId",
                    "foreignField": "_id",
                    "as": "partener"
                }
            },
            {
                "$unwind": "$partener"
            },
            {
                "$project": {
                    "_id": 0,
                    "Oferta": "$denumire",
                    "Partener": "$partener.denumire",
                    "Publicate": "$stocInitial",
                    "Salvate": "$salvate",
                    "Nesalvate": {
                        "$subtract": ["$stocInitial", "$salvate"]
                    },
                    "Rata salvare (%)": {
                        "$round": ["$rata", 2]
                    }
                }
            },
            {
                "$sort": {
                    "Rata salvare (%)": 1,
                    "Oferta": 1
                }
            }
        ]))

        if not rezultate:
            st.info("Nu exista oferte sub pragul selectat.")
            return

        tabel = pd.DataFrame(rezultate)

        st.dataframe(
            tabel,
            hide_index=True,
            use_container_width=True
        )

        st.bar_chart(
            tabel.set_index("Oferta")["Rata salvare (%)"]
        )

        st.download_button(
            label="Descarca raportul CSV",
            data=tabel.to_csv(index=False).encode("utf-8-sig"),
            file_name="rescuebite_valorificare.csv",
            mime="text/csv"
        )

        st.caption(
            "Nesalvate inseamna neridicate prin platforma. "
            "Nu presupune automat ca produsele au fost aruncate."
        )

    except PyMongoError:
        st.error("Raportul nu a putut fi calculat. Verifica conexiunea.")