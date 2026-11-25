use rescuebite

// totalul din rezervarile ridicate
db.rezervari.aggregate([
    {
        $match: { status: "ridicata" }
    },
    {
        $group: {
            _id: null,
            numarRezervari: { $sum: 1 },
            pacheteSalvate: { $sum: "$cantitate" },
            venitBani: {
                $sum: {
                    $multiply: ["$cantitate", "$pretUnitarBani"]
                }
            }
        }
    },
    {
        $project: {
            _id: 0,
            numarRezervari: 1,
            pacheteSalvate: 1,
            venitLei: { $divide: ["$venitBani", 100] }
        }
    }
])


//venitul obtinut de fiecare partener
db.rezervari.aggregate([
    {
        $match: { status: "ridicata" }
    },
    {
        $lookup: {
            from: "pachete",
            localField: "pachetId",
            foreignField: "_id",
            as: "pachet"
        }
    },
    {
        $unwind: "$pachet"
    },
    {
        $group: {
            _id: "$pachet.partenerId",
            pacheteSalvate: { $sum: "$cantitate" },
            venitBani: {
                $sum: {
                    $multiply: ["$cantitate", "$pretUnitarBani"]
                }
            }
        }
    },
    {
        $lookup: {
            from: "parteneri",
            localField: "_id",
            foreignField: "_id",
            as: "partener"
        }
    },
    {
        $unwind: "$partener"
    },
    {
        $project: {
            _id: 0,
            partener: "$partener.denumire",
            sector: "$partener.adresa.sector",
            pacheteSalvate: 1,
            venitLei: { $divide: ["$venitBani", 100] }
        }
    },
    {
        $sort: { venitLei: -1, partener: 1 }
    }
])

//oferte incheiate cu rata mica de salvare
db.pachete.aggregate([
    {
        $match: { status: "incheiat" }
    },
    {
        $lookup: {
            from: "rezervari",
            localField: "_id",
            foreignField: "pachetId",
            as: "rezervari"
        }
    },
    {
        $addFields: {
            pacheteSalvate: {
                $reduce: {
                    input: "$rezervari",
                    initialValue: 0,
                    in: {
                        $add: [
                            "$$value",
                            {
                                $cond: [
                                    { $eq: ["$$this.status", "ridicata"] },
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
        $addFields: {
            rataSalvarePct: {
                $cond: [
                    { $gt: ["$stocInitial", 0] },
                    {
                        $multiply: [
                            { $divide: ["$pacheteSalvate", "$stocInitial"] },
                            100
                        ]
                    },
                    0
                ]
            },
            pacheteNesalvate: {
                $subtract: ["$stocInitial", "$pacheteSalvate"]
            }
        }
    },
    {
        $match: { rataSalvarePct: { $lt: 70 } }
    },
    {
        $project: {
            _id: 0,
            denumire: 1,
            stocInitial: 1,
            pacheteSalvate: 1,
            pacheteNesalvate: 1,
            rataSalvarePct: { $round: ["$rataSalvarePct", 2] }
        }
    },
    {
        $sort: { rataSalvarePct: 1, denumire: 1 }
    }
])

//clientii care au revenit
db.rezervari.aggregate([
    {
        $match: { status: "ridicata" }
    },
    {
        $group: {
            _id: "$client.email",
            nume: { $first: "$client.nume" },
            numarRezervari: { $sum: 1 },
            pacheteSalvate: { $sum: "$cantitate" },
            totalBani: {
                $sum: {
                    $multiply: ["$cantitate", "$pretUnitarBani"]
                }
            }
        }
    },
    {
        $match: { numarRezervari: { $gte: 2 } }
    },
    {
        $project: {
            _id: 0,
            email: "$_id",
            nume: 1,
            numarRezervari: 1,
            pacheteSalvate: 1,
            totalLei: { $divide: ["$totalBani", 100] }
        }
    },
    {
        $sort: { totalLei: -1, email: 1 }
    }
])

//cate bucati din fiecare produs sunt disponibile
db.pachete.aggregate([
    {
        $match: {
            status: "publicat",
            stocDisponibil: { $gt: 0 }
        }
    },
    {
        $unwind: "$continut"
    },
    {
        $group: {
            _id: "$continut.produs",
            bucatiDisponibile: {
                $sum: {
                    $multiply: [
                        "$continut.cantitate",
                        "$stocDisponibil"
                    ]
                }
            },
            oferte: { $addToSet: "$denumire" }
        }
    },
    {
        $project: {
            _id: 0,
            produs: "$_id",
            bucatiDisponibile: 1,
            oferte: 1
        }
    },
    {
        $sort: { bucatiDisponibile: -1, produs: 1 }
    }
])