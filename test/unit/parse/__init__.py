PATIENT_LIGHT_RESOURCE = """{
          "id": "cjpicvbkxusn60a57glvgvc90",
          "name": "Patient",
          "attributes": [
            {
              "id": "cjpicvbl2usn70a57x5juy08k",
              "comment": "An identifier for this patient",
              "name": "identifier",
              "mergingScript": null,
              "isProfile": null,
              "type": "list::Identifier",
              "inputColumns": [

              ],
              "attributes": [
                {
                  "id": "cjpicvbl5usn90a57dhmj6m07",
                  "comment": null,
                  "name": "Identifier_0",
                  "mergingScript": null,
                  "isProfile": true,
                  "type": "Identifier",
                  "inputColumns": [

                  ],
                  "attributes": [
                    {
                      "id": "cjpicvbm7usnx0a57f0zp7f4b",
                      "comment": "The value that is unique",
                      "name": "value",
                      "mergingScript": null,
                      "isProfile": null,
                      "type": "string",
                      "inputColumns": [
                        {
                          "id": "cjpil1tdao3lz0a61s50cn8ss",
                          "owner": "ICSF",
                          "table": "PATIENT",
                          "column": "NOPAT",
                          "script": null,
                          "staticValue": null,
                          "joins": [

                          ]
                        }
                      ],
                      "attributes": [

                      ]
                    }
                  ]
                }
              ]
            },
            {
              "id": "cjpicvbmmuso70a57cs3gclss",
              "comment": "Whether this patient's record is in active use",
              "name": "active",
              "mergingScript": null,
              "isProfile": null,
              "type": "boolean",
              "inputColumns": [

              ],
              "attributes": [

              ]
            },
            {
              "id": "cjpicvbmouso90a57p8irnpx6",
              "comment": "A name associated with the patient",
              "name": "name",
              "mergingScript": null,
              "isProfile": null,
              "type": "list::HumanName",
              "inputColumns": [

              ],
              "attributes": [
                {
                  "id": "cjpicvbmrusob0a57ru95njt5",
                  "comment": null,
                  "name": "HumanName_0",
                  "mergingScript": null,
                  "isProfile": true,
                  "type": "HumanName",
                  "inputColumns": [

                  ],
                  "attributes": [
                    {
                      "id": "cjpicvbmuusod0a572zcixgqn",
                      "comment": "usual | official | temp | nickname | anonymous | old | maiden",
                      "name": "use",
                      "mergingScript": null,
                      "isProfile": null,
                      "type": "code",
                      "inputColumns": [

                      ],
                      "attributes": [

                      ]
                    },
                    {
                      "id": "cjpicvbmyusoh0a579qvwoi1p",
                      "comment": "Family name (often called 'Surname')",
                      "name": "family",
                      "mergingScript": null,
                      "isProfile": null,
                      "type": "string",
                      "inputColumns": [
                        {
                          "id": "cjpikp174o1ia0a61owy0aumv",
                          "owner": "ICSF",
                          "table": "PATIENT",
                          "column": "NOMPAT",
                          "script": null,
                          "staticValue": null,
                          "joins": [

                          ]
                        }
                      ],
                      "attributes": [

                      ]
                    },
                    {
                      "id": "cjpicvbn1usoj0a57209fc3np",
                      "comment": "Given names (not always 'first'). Includes middle names",
                      "name": "given",
                      "mergingScript": null,
                      "isProfile": null,
                      "type": "list::string",
                      "inputColumns": [
                        {
                          "id": "cjpikpcxeo1k70a61o2qeklnj",
                          "owner": "ICSF",
                          "table": "PATIENT",
                          "column": "PREPAT",
                          "script": null,
                          "staticValue": null,
                          "joins": [

                          ]
                        },
                        {
                          "id": "cjpikpfl6wji10a57cyj19385",
                          "owner": "ICSF",
                          "table": "PATIENT",
                          "column": "PREPATSUITE",
                          "script": null,
                          "staticValue": null,
                          "joins": [

                          ]
                        }
                      ],
                      "attributes": [

                      ]
                    }
                  ]
                }
              ]
            },
            {
              "id": "cjpicvbo9uspd0a57n14ntf5y",
              "comment": "male | female | other | unknown",
              "name": "gender",
              "mergingScript": null,
              "isProfile": null,
              "type": "code",
              "inputColumns": [
                {
                  "id": "cjpikq0t0o1ot0a61lv9q4xgr",
                  "owner": "ICSF",
                  "table": "PATIENT",
                  "column": "SEXE",
                  "script": null,
                  "staticValue": null,
                  "joins": [

                  ]
                }
              ],
              "attributes": [

              ]
            }
          ]
        }
    """

PATIENT_MEDIUM_RESOURCE = """{
          "id": "cjpicvbkxusn60a57glvgvc90",
          "name": "Patient",
          "attributes": [
            {
              "id": "cjpicvbl2usn70a57x5juy08k",
              "comment": "An identifier for this patient",
              "name": "identifier",
              "mergingScript": null,
              "isProfile": null,
              "type": "list::Identifier",
              "inputColumns": [

              ],
              "attributes": [
                {
                  "id": "cjpicvbl5usn90a57dhmj6m07",
                  "comment": null,
                  "name": "Identifier_0",
                  "mergingScript": null,
                  "isProfile": true,
                  "type": "Identifier",
                  "inputColumns": [

                  ],
                  "attributes": [
                    {
                      "id": "cjpicvbm7usnx0a57f0zp7f4b",
                      "comment": "The value that is unique",
                      "name": "value",
                      "mergingScript": null,
                      "isProfile": null,
                      "type": "string",
                      "inputColumns": [
                        {
                          "id": "cjpil1tdao3lz0a61s50cn8ss",
                          "owner": "ICSF",
                          "table": "PATIENT",
                          "column": "NOPAT",
                          "script": null,
                          "staticValue": null,
                          "joins": [

                          ]
                        }
                      ],
                      "attributes": [

                      ]
                    }
                  ]
                }
              ]
            },
            {
              "id": "cjpicvbmmuso70a57cs3gclss",
              "comment": "Whether this patient's record is in active use",
              "name": "active",
              "mergingScript": null,
              "isProfile": null,
              "type": "boolean",
              "inputColumns": [

              ],
              "attributes": [

              ]
            },
            {
              "id": "cjpicvbmouso90a57p8irnpx6",
              "comment": "A name associated with the patient",
              "name": "name",
              "mergingScript": null,
              "isProfile": null,
              "type": "list::HumanName",
              "inputColumns": [

              ],
              "attributes": [
                {
                  "id": "cjpicvbmrusob0a57ru95njt5",
                  "comment": null,
                  "name": "HumanName_0",
                  "mergingScript": null,
                  "isProfile": true,
                  "type": "HumanName",
                  "inputColumns": [

                  ],
                  "attributes": [
                    {
                      "id": "cjpicvbmuusod0a572zcixgqn",
                      "comment": "usual | official | temp | nickname | anonymous | old | maiden",
                      "name": "use",
                      "mergingScript": null,
                      "isProfile": null,
                      "type": "code",
                      "inputColumns": [

                      ],
                      "attributes": [

                      ]
                    },
                    {
                      "id": "cjpicvbmyusoh0a579qvwoi1p",
                      "comment": "Family name (often called 'Surname')",
                      "name": "family",
                      "mergingScript": null,
                      "isProfile": null,
                      "type": "string",
                      "inputColumns": [
                        {
                          "id": "cjpikp174o1ia0a61owy0aumv",
                          "owner": "ICSF",
                          "table": "PATIENT",
                          "column": "NOMPAT",
                          "script": null,
                          "staticValue": null,
                          "joins": [

                          ]
                        }
                      ],
                      "attributes": [

                      ]
                    },
                    {
                      "id": "cjpicvbn1usoj0a57209fc3np",
                      "comment": "Given names (not always 'first'). Includes middle names",
                      "name": "given",
                      "mergingScript": null,
                      "isProfile": null,
                      "type": "list::string",
                      "inputColumns": [
                        {
                          "id": "cjpikpcxeo1k70a61o2qeklnj",
                          "owner": "ICSF",
                          "table": "PATIENT",
                          "column": "PREPAT",
                          "script": null,
                          "staticValue": null,
                          "joins": [

                          ]
                        },
                        {
                          "id": "cjpikpfl6wji10a57cyj19385",
                          "owner": "ICSF",
                          "table": "PATIENT",
                          "column": "PREPATSUITE",
                          "script": null,
                          "staticValue": null,
                          "joins": [

                          ]
                        }
                      ],
                      "attributes": [

                      ]
                    }
                  ]
                }
              ]
            },
            {
              "id": "cjpicvbo9uspd0a57n14ntf5y",
              "comment": "male | female | other | unknown",
              "name": "gender",
              "mergingScript": null,
              "isProfile": null,
              "type": "code",
              "inputColumns": [
                {
                  "id": "cjpikq0t0o1ot0a61lv9q4xgr",
                  "owner": "ICSF",
                  "table": "PATIENT",
                  "column": "SEXE",
                  "script": null,
                  "staticValue": null,
                  "joins": [

                  ]
                }
              ],
              "attributes": [

              ]
            },
            {
              "id": "cjpicvbokuspl0a57aikmv6fz",
              "comment": "Addresses for the individual",
              "name": "address",
              "mergingScript": null,
              "isProfile": null,
              "type": "list::Address",
              "inputColumns": [

              ],
              "attributes": [
                {
                  "id": "cjpicvbonuspn0a57kuqd1kck",
                  "comment": null,
                  "name": "Address_0",
                  "mergingScript": null,
                  "isProfile": true,
                  "type": "Address",
                  "inputColumns": [

                  ],
                  "attributes": [
                    {
                      "id": "cjpicvboquspp0a576a5mx1eo",
                      "comment": "home | work | temp | old - purpose of this address",
                      "name": "use",
                      "mergingScript": null,
                      "isProfile": null,
                      "type": "code",
                      "inputColumns": [

                      ],
                      "attributes": [

                      ]
                    },
                    {
                      "id": "cjpicvbouuspr0a5794vlsskt",
                      "comment": "postal | physical | both",
                      "name": "type",
                      "mergingScript": null,
                      "isProfile": null,
                      "type": "code",
                      "inputColumns": [

                      ],
                      "attributes": [

                      ]
                    },
                    {
                      "id": "cjpicvbowuspt0a570rorisiw",
                      "comment": "Text representation of the address",
                      "name": "text",
                      "mergingScript": null,
                      "isProfile": null,
                      "type": "string",
                      "inputColumns": [

                      ],
                      "attributes": [

                      ]
                    },
                    {
                      "id": "cjpicvbozuspv0a57c846ssu5",
                      "comment": "Street name, number, direction & P.O. Box etc.",
                      "name": "line",
                      "mergingScript": null,
                      "isProfile": null,
                      "type": "list::string",
                      "inputColumns": [
                        {
                          "id": "cjpikvlqbo2y40a61n2paf9eh",
                          "owner": "ICSF",
                          "table": "PATADR",
                          "column": "ADR1",
                          "script": null,
                          "staticValue": null,
                          "joins": [
                            {
                              "id": "cjpikvsedwlap0a57gxlzmvsg",
                              "sourceOwner": "ICSF",
                              "sourceTable": "PATIENT",
                              "sourceColumn": "NOPAT",
                              "targetOwner": "ICSF",
                              "targetTable": "PATADR",
                              "targetColumn": "NOPAT"
                            }
                          ]
                        }
                      ],
                      "attributes": [

                      ]
                    },
                    {
                      "id": "cjpicvbpeusq50a57ok8qwez4",
                      "comment": "Country (e.g. can be ISO 3166 2 or 3 letter code)",
                      "name": "country",
                      "mergingScript": null,
                      "isProfile": null,
                      "type": "string",
                      "inputColumns": [
                        {
                          "id": "cjpiktq20wku60a57uvvol326",
                          "owner": "ICSF",
                          "table": "PAYS",
                          "column": "LIBELLE",
                          "script": null,
                          "staticValue": null,
                          "joins": [
                            {
                              "id": "cjpiktr9to2n40a616g7eyqun",
                              "sourceOwner": "ICSF",
                              "sourceTable": "PATIENT",
                              "sourceColumn": "NOPAT",
                              "targetOwner": "ICSF",
                              "targetTable": "PATADR",
                              "targetColumn": "NOPAT"
                            },
                            {
                              "id": "cjpikuj95wl1a0a573cy7eh7o",
                              "sourceOwner": "ICSF",
                              "sourceTable": "PATADR",
                              "sourceColumn": "NOPAYS",
                              "targetOwner": "ICSF",
                              "targetTable": "PAYS",
                              "targetColumn": "NOPAYS"
                            }
                          ]
                        }
                      ],
                      "attributes": [

                      ]
                    }
                  ]
                }
              ]
            }
          ]
        }
        """
