use rescuebite

//1.CREAREA COLECTIILOR

["parteneri", "pachete", "rezervari"].forEach(function(nume) {
    if (!db.getCollectionNames().includes(nume)) {
        db.createCollection(nume);
    }
});


//2.PARTENERI


const parteneriInitiali = [
    {
        _id: 1,
        denumire: "Cuptorul de Cartier",
        tip: "Brutarie",
        adresa: {
            oras: "Bucuresti",
            sector: 3,
            strada: "Strada Lalelelor 12"
        },
        categorii: ["Panificatie", "Patiserie"],
        activ: true
    },
    {
        _id: 2,
        denumire: "Green Lunch",
        tip: "Restaurant",
        adresa: {
            oras: "Bucuresti",
            sector: 1,
            strada: "Strada Castanilor 8"
        },
        categorii: ["Mancare gatita", "Vegetarian"],
        activ: true
    },
    {
        _id: 3,
        denumire: "Dulce de Seara",
        tip: "Cofetarie",
        adresa: {
            oras: "Bucuresti",
            sector: 2,
            strada: "Strada Salcamilor 21"
        },
        categorii: ["Desert"],
        activ: true
    },
    {
        _id: 4,
        denumire: "Fresh Corner",
        tip: "Magazin alimentar",
        adresa: {
            oras: "Bucuresti",
            sector: 3,
            strada: "Strada Ciresilor 5"
        },
        categorii: ["Fructe si legume", "Panificatie"],
        activ: true
    }
];

parteneriInitiali.forEach(function(partener) {
    db.parteneri.updateOne(
        { _id: partener._id },
        { $setOnInsert: partener },
        { upsert: true }
    );
});



//3.PACHETE
//Preturile sunt exprimate in bani: 1500=15 lei, se evita astfel erorile de calcul cu nr zecimale
//stocInitial=nr de pachete publicate
//stocDisponibil=nr ramas pentru rezervare


const pacheteInitiale = [
    {
        _id: 101,
        partenerId: 1,
        denumire: "Micul dejun salvat",
        categorie: "Panificatie",
        continut: [
            { produs: "Paine artizanala", cantitate: 1 },
            { produs: "Croissant", cantitate: 2 }
        ],
        pretInitialBani: 4000,
        pretRedusBani: 1500,
        stocInitial: 8,
        stocDisponibil: 3,
        ridicare: {
            inceput: ISODate("2026-11-16T17:00:00Z"),
            sfarsit: ISODate("2026-11-16T19:00:00Z")
        },
        status: "incheiat",
        etichete: ["vegetarian"],
        creatLa: ISODate("2026-11-16T08:00:00Z")
    },
    {
        _id: 102,
        partenerId: 2,
        denumire: "Pranz verde",
        categorie: "Vegetarian",
        continut: [
            { produs: "Supa de legume", cantitate: 1 },
            { produs: "Orez cu legume", cantitate: 1 }
        ],
        pretInitialBani: 5000,
        pretRedusBani: 2200,
        stocInitial: 6,
        stocDisponibil: 2,
        ridicare: {
            inceput: ISODate("2026-11-16T14:00:00Z"),
            sfarsit: ISODate("2026-11-16T16:00:00Z")
        },
        status: "incheiat",
        etichete: ["vegan"],
        creatLa: ISODate("2026-11-16T09:00:00Z")
    },
    {
        _id: 103,
        partenerId: 3,
        denumire: "Surpriza dulce",
        categorie: "Desert",
        continut: [
            { produs: "Prajitura asortata", cantitate: 3 }
        ],
        pretInitialBani: 6000,
        pretRedusBani: 2500,
        stocInitial: 5,
        stocDisponibil: 0,
        ridicare: {
            inceput: ISODate("2026-11-16T16:00:00Z"),
            sfarsit: ISODate("2026-11-16T18:00:00Z")
        },
        status: "incheiat",
        etichete: ["contine lactate"],
        creatLa: ISODate("2026-11-16T10:00:00Z")
    },
    {
        _id: 104,
        partenerId: 4,
        denumire: "Cosul de vitamine",
        categorie: "Fructe si legume",
        continut: [
            { produs: "Mere", cantitate: 4 },
            { produs: "Banane", cantitate: 4 },
            { produs: "Ardei", cantitate: 3 }
        ],
        pretInitialBani: 4500,
        pretRedusBani: 1800,
        stocInitial: 7,
        stocDisponibil: 5,
        ridicare: {
            inceput: ISODate("2026-11-16T15:00:00Z"),
            sfarsit: ISODate("2026-11-16T18:00:00Z")
        },
        status: "incheiat",
        etichete: ["vegan", "fara gluten"],
        creatLa: ISODate("2026-11-16T08:30:00Z")
    },
    {
        _id: 105,
        partenerId: 1,
        denumire: "Pachet de patiserie",
        categorie: "Patiserie",
        continut: [
            { produs: "Merdenea", cantitate: 2 },
            { produs: "Covrig", cantitate: 3 }
        ],
        pretInitialBani: 3500,
        pretRedusBani: 1400,
        stocInitial: 10,
        stocDisponibil: 10,
        ridicare: {
            inceput: ISODate("2026-11-20T16:00:00Z"),
            sfarsit: ISODate("2026-11-20T19:00:00Z")
        },
        status: "publicat",
        etichete: ["vegetarian"],
        creatLa: ISODate("2026-11-17T10:00:00Z")
    },
    {
        _id: 106,
        partenerId: 2,
        denumire: "Cina pentru doi",
        categorie: "Mancare gatita",
        continut: [
            { produs: "Portie de pui cu orez", cantitate: 2 }
        ],
        pretInitialBani: 9000,
        pretRedusBani: 3900,
        stocInitial: 4,
        stocDisponibil: 4,
        ridicare: {
            inceput: ISODate("2026-11-20T17:00:00Z"),
            sfarsit: ISODate("2026-11-20T19:00:00Z")
        },
        status: "publicat",
        etichete: ["pentru doua persoane"],
        creatLa: ISODate("2026-11-17T10:15:00Z")
    },
    {
        _id: 107,
        partenerId: 3,
        denumire: "Cutia cu mini deserturi",
        categorie: "Desert",
        continut: [
            { produs: "Mini ecler", cantitate: 2 },
            { produs: "Mini tarta", cantitate: 2 }
        ],
        pretInitialBani: 5500,
        pretRedusBani: 2300,
        stocInitial: 6,
        stocDisponibil: 6,
        ridicare: {
            inceput: ISODate("2026-11-21T10:00:00Z"),
            sfarsit: ISODate("2026-11-21T13:00:00Z")
        },
        status: "publicat",
        etichete: ["contine lactate"],
        creatLa: ISODate("2026-11-17T10:30:00Z")
    },
    {
        _id: 108,
        partenerId: 4,
        denumire: "Fructe pentru smoothie",
        categorie: "Fructe si legume",
        continut: [
            { produs: "Banane coapte", cantitate: 6 },
            { produs: "Pere", cantitate: 4 }
        ],
        pretInitialBani: 3000,
        pretRedusBani: 1200,
        stocInitial: 8,
        stocDisponibil: 8,
        ridicare: {
            inceput: ISODate("2026-11-21T09:00:00Z"),
            sfarsit: ISODate("2026-11-21T13:00:00Z")
        },
        status: "publicat",
        etichete: ["vegan", "fara gluten"],
        creatLa: ISODate("2026-11-17T10:45:00Z")
    }
];

pacheteInitiale.forEach(function(pachet) {
    db.pachete.updateOne(
        { _id: pachet._id },
        { $setOnInsert: pachet },
        { upsert: true }
    );
});



//4.REZERVARI ISTORICE
//Doar rezervarile "ridicata" vor intra in venitul realizat
//O rezervare poate cuprinde mai multe pachete identice

const rezervariInitiale = [
    {
        _id: 1001,
        pachetId: 101,
        client: {
            nume: "Ana Pop",
            email: "ana@example.com"
        },
        cantitate: 2,
        pretUnitarBani: 1500,
        status: "ridicata",
        creatLa: ISODate("2026-11-16T10:00:00Z")
    },
    {
        _id: 1002,
        pachetId: 101,
        client: {
            nume: "Mihai Stan",
            email: "mihai@example.com"
        },
        cantitate: 3,
        pretUnitarBani: 1500,
        status: "ridicata",
        creatLa: ISODate("2026-11-16T11:00:00Z")
    },
    {
        _id: 1003,
        pachetId: 102,
        client: {
            nume: "Ioana Marin",
            email: "ioana@example.com"
        },
        cantitate: 2,
        pretUnitarBani: 2200,
        status: "ridicata",
        creatLa: ISODate("2026-11-16T11:15:00Z")
    },
    {
        _id: 1004,
        pachetId: 102,
        client: {
            nume: "Andrei Dima",
            email: "andrei@example.com"
        },
        cantitate: 2,
        pretUnitarBani: 2200,
        status: "ridicata",
        creatLa: ISODate("2026-11-16T12:00:00Z")
    },
    {
        _id: 1005,
        pachetId: 103,
        client: {
            nume: "Ana Pop",
            email: "ana@example.com"
        },
        cantitate: 3,
        pretUnitarBani: 2500,
        status: "ridicata",
        creatLa: ISODate("2026-11-16T12:15:00Z")
    },
    {
        _id: 1006,
        pachetId: 103,
        client: {
            nume: "Radu Ene",
            email: "radu@example.com"
        },
        cantitate: 2,
        pretUnitarBani: 2500,
        status: "ridicata",
        creatLa: ISODate("2026-11-16T13:00:00Z")
    },
    {
        _id: 1007,
        pachetId: 104,
        client: {
            nume: "Ioana Marin",
            email: "ioana@example.com"
        },
        cantitate: 2,
        pretUnitarBani: 1800,
        status: "ridicata",
        creatLa: ISODate("2026-11-16T13:15:00Z")
    },
    {
        _id: 1008,
        pachetId: 104,
        client: {
            nume: "Mihai Stan",
            email: "mihai@example.com"
        },
        cantitate: 1,
        pretUnitarBani: 1800,
        status: "anulata",
        creatLa: ISODate("2026-11-16T14:00:00Z")
    }
];

rezervariInitiale.forEach(function(rezervare) {
    db.rezervari.updateOne(
        { _id: rezervare._id },
        { $setOnInsert: rezervare },
        { upsert: true }
    );
});



//5.VERIFICAREA DATELOR

print("Baza de date: " + db.getName());
print("Parteneri: " + db.parteneri.countDocuments({}));
print("Pachete: " + db.pachete.countDocuments({}));
print("Rezervari: " + db.rezervari.countDocuments({}));

db.pachete.find(
    {},
    {
        _id: 1,
        denumire: 1,
        partenerId: 1,
        pretRedusBani: 1,
        stocDisponibil: 1,
        status: 1
    }
).sort({ _id: 1 });