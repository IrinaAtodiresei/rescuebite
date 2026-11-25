use rescuebite

//verific stocul fata de rezervarile active si ridicate
db.pachete.aggregate([
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
            cantitateOcupata: {
                $reduce: {
                    input: "$rezervari",
                    initialValue: 0,
                    in: {
                        $add: [
                            "$$value",
                            {
                                $cond: [
                                    {
                                        $in: [
                                            "$$this.status",
                                            ["rezervata", "ridicata"]
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
        $addFields: {
            stocCalculat: {
                $subtract: ["$stocInitial", "$cantitateOcupata"]
            }
        }
    },
    {
        $project: {
            _id: 1,
            denumire: 1,
            stocInitial: 1,
            cantitateOcupata: 1,
            stocDisponibil: 1,
            stocCalculat: 1,
            corect: {
                $eq: ["$stocDisponibil", "$stocCalculat"]
            }
        }
    },
    {
        $sort: { denumire: 1 }
    }
])


//caut rezervari fara oferta asociata
db.rezervari.aggregate([
    {
        $lookup: {
            from: "pachete",
            localField: "pachetId",
            foreignField: "_id",
            as: "pachet"
        }
    },
    {
        $match: {
            pachet: { $size: 0 }
        }
    },
    {
        $project: {
            _id: 1,
            pachetId: 1,
            status: 1
        }
    }
])

db.pachete.aggregate([
    {
        $lookup: {
            from: "parteneri",
            localField: "partenerId",
            foreignField: "_id",
            as: "partener"
        }
    },
    {
        $match: {
            partener: { $size: 0 }
        }
    },
    {
        $project: {
            _id: 1,
            denumire: 1,
            partenerId: 1
        }
    }
])