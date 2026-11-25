use rescuebite

//reguli pt datele din pachete
db.runCommand({
    collMod: "pachete",
    validator: {
        $and: [
            {
                $jsonSchema: {
                    bsonType: "object",
                    required: [
                        "partenerId", "denumire", "categorie",
                        "continut", "pretInitialBani", "pretRedusBani",
                        "stocInitial", "stocDisponibil",
                        "ridicare", "status", "etichete", "creatLa"
                    ],
                    properties: {
                        partenerId: {
                            bsonType: ["int", "long", "double", "decimal"]
                        },
                        denumire: {
                            bsonType: "string",
                            minLength: 3
                        },
                        categorie: {
                            bsonType: "string",
                            minLength: 1
                        },
                        continut: {
                            bsonType: "array",
                            minItems: 1,
                            items: {
                                bsonType: "object",
                                required: ["produs", "cantitate"],
                                properties: {
                                    produs: {
                                        bsonType: "string",
                                        minLength: 1
                                    },
                                    cantitate: {
                                        bsonType: ["int", "long", "double", "decimal"],
                                        minimum: 1,
                                        multipleOf: 1
                                    }
                                }
                            }
                        },
                        pretInitialBani: {
                            bsonType: ["int", "long", "double", "decimal"],
                            minimum: 1,
                            multipleOf: 1
                        },
                        pretRedusBani: {
                            bsonType: ["int", "long", "double", "decimal"],
                            minimum: 1,
                            multipleOf: 1
                        },
                        stocInitial: {
                            bsonType: ["int", "long", "double", "decimal"],
                            minimum: 1,
                            multipleOf: 1
                        },
                        stocDisponibil: {
                            bsonType: ["int", "long", "double", "decimal"],
                            minimum: 0,
                            multipleOf: 1
                        },
                        ridicare: {
                            bsonType: "object",
                            required: ["inceput", "sfarsit"],
                            properties: {
                                inceput: { bsonType: "date" },
                                sfarsit: { bsonType: "date" }
                            }
                        },
                        status: {
                            enum: ["publicat", "incheiat", "retras"]
                        },
                        etichete: {
                            bsonType: "array",
                            items: { bsonType: "string" }
                        },
                        creatLa: {
                            bsonType: "date"
                        }
                    }
                }
            },
            {
                $expr: {
                    $and: [
                        { $lte: ["$pretRedusBani", "$pretInitialBani"] },
                        { $lte: ["$stocDisponibil", "$stocInitial"] },
                        { $lt: ["$ridicare.inceput", "$ridicare.sfarsit"] }
                    ]
                }
            }
        ]
    },
    validationLevel: "strict",
    validationAction: "error"
})

//indici pt cautari si rapoarte
db.pachete.createIndex(
    { status: 1, pretRedusBani: 1, _id: 1 },
    { name: "status_pret" }
)

db.pachete.createIndex(
    { partenerId: 1 },
    { name: "pachete_partener" }
)

db.rezervari.createIndex(
    { pachetId: 1, status: 1 },
    { name: "rezervari_pachet_status" }
)

db.rezervari.createIndex(
    { status: 1, "client.email": 1 },
    { name: "rezervari_status_client" }
)

db.pachete.getIndexes()


//verific daca este respins un stoc negativ
db.pachete.updateOne(
    { _id: 105 },
    { $set: { stocDisponibil: -1 } }
)

db.pachete.find(
    { _id: 105 },
    { denumire: 1, stocDisponibil: 1 }
)