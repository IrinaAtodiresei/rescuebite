use rescuebite

//adaug un pachet nou
db.pachete.insertOne({
    _id: 109,
    partenerId: 1,
    denumire: "Pachet de seara",
    categorie: "Patiserie",
    continut: [
        { produs: "Covrig", cantitate: 2 },
        { produs: "Placinta cu mere", cantitate: 1 }
    ],
    pretInitialBani: 3000,
    pretRedusBani: 1200,
    stocInitial: 5,
    stocDisponibil: 5,
    ridicare: {
        inceput: ISODate("2026-11-21T15:00:00Z"),
        sfarsit: ISODate("2026-11-21T18:00:00Z")
    },
    status: "publicat",
    etichete: ["vegetarian"],
    creatLa: new Date()
})

db.pachete.find({ _id: 109 })


db.pachete.find(
    {
        status: "publicat",
        pretRedusBani: { $lte: 2000 },
        stocDisponibil: { $gt: 0 }
    },
    {
        _id: 1,
        denumire: 1,
        categorie: 1,
        pretRedusBani: 1,
        stocDisponibil: 1
    }
).sort({ pretRedusBani: 1, _id: 1 })



db.pachete.find(
    {
        etichete: "vegan",
        status: "publicat",
        "ridicare.inceput": {
            $gte: ISODate("2026-11-21T00:00:00+02:00"),
            $lt: ISODate("2026-11-22T00:00:00+02:00")
        }
    },
    {
        _id: 1,
        denumire: 1,
        etichete: 1,
        ridicare: 1
    }
)

//modific pretul pachetului
db.pachete.updateOne(
    { _id: 109, status: "publicat" },
    {
        $set: {
            pretRedusBani: 1000
        }
    }
)


db.pachete.find(
    { _id: 109 },
    { denumire: 1, pretRedusBani: 1 }
)


db.pachete.updateOne(
    { _id: 109 },
    {
        $addToSet: {
            etichete: "oferta de seara"
        }
    }
)

db.pachete.find(
    { _id: 109 },
    { denumire: 1, etichete: 1 }
)

//sterg pachetul folosit pt demo
db.pachete.deleteOne({ _id: 109 })

db.pachete.countDocuments({})