MOCK_FILE = """
{
    "data": {
        "database": {
            "id": "cjpiarhzxmfmu0a611t9zwqgm",
            "name": "Mimic",
            "resources": [
                {
                    "id": "cjtyglzyd00bh0766w42omeb9",
                    "name": "Patient",
                    "attributes": []
                },
                {
                    "id": "cjtyglzyd00bh0766w42omeb9",
                    "name": "Encounter",
                    "attributes": []
                }
            ]
        }
    }
}
"""

RAW_FHIR_RESOURCE = {
    "id": "cjtyglzyd00bh0766w42omeb9",
    "name": "Patient",
    "attributes": [
        {
            "id": "cjtyglzz300bi0766tjms54pu",
            "comment": "An identifier for this patient",
            "name": "identifier",
            "mergingScript": None,
            "isProfile": None,
            "type": "list::Identifier",
            "inputColumns": [],
            "attributes": [
                {
                    "id": "cjtyglzzd00bk076690zuwn0p",
                    "comment": None,
                    "name": "Identifier_0",
                    "mergingScript": None,
                    "isProfile": True,
                    "type": "Identifier",
                    "inputColumns": [],
                    "attributes": [
                        {
                            "id": "cjtyglzzj00bm0766u84bt3j0",
                            "comment": "usual | official | temp | secondary (If known)",
                            "name": "use",
                            "mergingScript": None,
                            "isProfile": None,
                            "type": "code",
                            "inputColumns": [],
                            "attributes": []
                        },
                        {
                            "id": "cjtyglzzo00bo0766e8x01esh",
                            "comment": "Description of identifier",
                            "name": "type",
                            "mergingScript": None,
                            "isProfile": None,
                            "type": "CodeableConcept",
                            "inputColumns": [],
                            "attributes": [
                                {
                                    "id": "cjtyglzzs00bq0766cgui1ghw",
                                    "comment": "Code defined by a terminology system",
                                    "name": "coding",
                                    "mergingScript": None,
                                    "isProfile": None,
                                    "type": "list::Coding",
                                    "inputColumns": [],
                                    "attributes": [
                                        {
                                            "id": "cjtyglzzw00bs0766x6wvp5fh",
                                            "comment": None,
                                            "name": "Coding_0",
                                            "mergingScript": None,
                                            "isProfile": True,
                                            "type": "Coding",
                                            "inputColumns": [],
                                            "attributes": [
                                                {
                                                    "id": "cjtygm00000bu076675pf69b1",
                                                    "comment": "Identity of the terminology system",
                                                    "name": "system",
                                                    "mergingScript": None,
                                                    "isProfile": None,
                                                    "type": "uri",
                                                    "inputColumns": [],
                                                    "attributes": []
                                                },
                                                {
                                                    "id": "cjtygm00400bw0766m17moy7o",
                                                    "comment": "Version of the system - if relevant",
                                                    "name": "version",
                                                    "mergingScript": None,
                                                    "isProfile": None,
                                                    "type": "string",
                                                    "inputColumns": [],
                                                    "attributes": []
                                                },
                                                {
                                                    "id": "cjtygm00800by0766xlbqm690",
                                                    "comment": "Symbol in syntax defined by the system",
                                                    "name": "code",
                                                    "mergingScript": None,
                                                    "isProfile": None,
                                                    "type": "code",
                                                    "inputColumns": [],
                                                    "attributes": []
                                                },
                                                {
                                                    "id": "cjtygm00d00c00766uxtp3bdo",
                                                    "comment": "Representation defined by the system",
                                                    "name": "display",
                                                    "mergingScript": None,
                                                    "isProfile": None,
                                                    "type": "string",
                                                    "inputColumns": [],
                                                    "attributes": []
                                                },
                                                {
                                                    "id": "cjtygm00k00c20766aws5o1dt",
                                                    "comment": "If this coding was chosen directly by the user",
                                                    "name": "userSelected",
                                                    "mergingScript": None,
                                                    "isProfile": None,
                                                    "type": "boolean",
                                                    "inputColumns": [],
                                                    "attributes": []
                                                }
                                            ]
                                        }
                                    ]
                                },
                                {
                                    "id": "cjtygm00p00c407666p6m9q6w",
                                    "comment": "Plain text representation of the concept",
                                    "name": "text",
                                    "mergingScript": None,
                                    "isProfile": None,
                                    "type": "string",
                                    "inputColumns": [],
                                    "attributes": []
                                }
                            ]
                        },
                        {
                            "id": "cjtygm00t00c607661ssq3prs",
                            "comment": "The namespace for the identifier value",
                            "name": "system",
                            "mergingScript": None,
                            "isProfile": None,
                            "type": "uri",
                            "inputColumns": [],
                            "attributes": []
                        },
                        {
                            "id": "cjtygm00x00c807662i1y484t",
                            "comment": "The value that is unique",
                            "name": "value",
                            "mergingScript": None,
                            "isProfile": None,
                            "type": "string",
                            "inputColumns": [
                                {
                                    "id": "cjtyiyk9500q707661w96ml2j",
                                    "owner": None,
                                    "table": "PATIENTS",
                                    "column": "SUBJECT_ID",
                                    "script": None,
                                    "staticValue": None,
                                    "joins": []
                                }
                            ],
                            "attributes": []
                        },
                        {
                            "id": "cjtygm01100ca07664h0qvxwg",
                            "comment": "Time period when id is/was valid for use",
                            "name": "period",
                            "mergingScript": None,
                            "isProfile": None,
                            "type": "Period",
                            "inputColumns": [],
                            "attributes": [
                                {
                                    "id": "cjtygm01600cc0766fdaox6b0",
                                    "comment": "C? Starting time with inclusive boundary",
                                    "name": "start",
                                    "mergingScript": None,
                                    "isProfile": None,
                                    "type": "dateTime",
                                    "inputColumns": [],
                                    "attributes": []
                                },
                                {
                                    "id": "cjtygm01a00ce0766txwknsbl",
                                    "comment": "C? End time with inclusive boundary if not ongoing",
                                    "name": "end",
                                    "mergingScript": None,
                                    "isProfile": None,
                                    "type": "dateTime",
                                    "inputColumns": [],
                                    "attributes": []
                                }
                            ]
                        },
                        {
                            "id": "cjtygm01e00cg0766cs1eoc2x",
                            "comment": "Organization that issued id (may be just text)",
                            "name": "assigner",
                            "mergingScript": None,
                            "isProfile": None,
                            "type": "Reference(Organization)",
                            "inputColumns": [],
                            "attributes": [
                                {
                                    "id": "cjtygm01h00ci0766mlswvdku",
                                    "comment": "C? Literal reference, Relative, internal or absolute URL",
                                    "name": "reference",
                                    "mergingScript": None,
                                    "isProfile": None,
                                    "type": "string",
                                    "inputColumns": [],
                                    "attributes": []
                                },
                                {
                                    "id": "cjtygm01l00ck0766yyt3te2p",
                                    "comment": "Logical reference, when literal reference is not known",
                                    "name": "identifier",
                                    "mergingScript": None,
                                    "isProfile": None,
                                    "type": "Identifier",
                                    "inputColumns": [],
                                    "attributes": [
                                        {
                                            "id": "cjtygm01p00cm0766j5sqoihu",
                                            "comment": "usual | official | temp | secondary (If known)",
                                            "name": "use",
                                            "mergingScript": None,
                                            "isProfile": None,
                                            "type": "code",
                                            "inputColumns": [],
                                            "attributes": []
                                        },
                                        {
                                            "id": "cjtygm01v00co0766gg7hn2ib",
                                            "comment": "Description of identifier",
                                            "name": "type",
                                            "mergingScript": None,
                                            "isProfile": None,
                                            "type": "CodeableConcept",
                                            "inputColumns": [],
                                            "attributes": [
                                                {
                                                    "id": "cjtygm01z00cq0766duul0tve",
                                                    "comment": "Code defined by a terminology system",
                                                    "name": "coding",
                                                    "mergingScript": None,
                                                    "isProfile": None,
                                                    "type": "list::Coding",
                                                    "inputColumns": [],
                                                    "attributes": [
                                                        {
                                                            "id": "cjtygm02300cs0766n9ocx00a",
                                                            "comment": None,
                                                            "name": "Coding_0",
                                                            "mergingScript": None,
                                                            "isProfile": True,
                                                            "type": "Coding",
                                                            "inputColumns": [],
                                                            "attributes": [
                                                                {
                                                                    "id": "cjtygm02600cu0766f3tgg4nw",
                                                                    "comment": "Identity of the terminology system",
                                                                    "name": "system",
                                                                    "mergingScript": None,
                                                                    "isProfile": None,
                                                                    "type": "uri",
                                                                    "inputColumns": [],
                                                                    "attributes": []
                                                                },
                                                                {
                                                                    "id": "cjtygm02a00cw0766rgwuffx9",
                                                                    "comment": "Version of the system - if relevant",
                                                                    "name": "version",
                                                                    "mergingScript": None,
                                                                    "isProfile": None,
                                                                    "type": "string",
                                                                    "inputColumns": [],
                                                                    "attributes": []
                                                                },
                                                                {
                                                                    "id": "cjtygm02e00cy0766vgxbmjoz",
                                                                    "comment": "Symbol in syntax defined by the system",
                                                                    "name": "code",
                                                                    "mergingScript": None,
                                                                    "isProfile": None,
                                                                    "type": "code",
                                                                    "inputColumns": [],
                                                                    "attributes": []
                                                                },
                                                                {
                                                                    "id": "cjtygm02h00d007665ciph17l",
                                                                    "comment": "Representation defined by the system",
                                                                    "name": "display",
                                                                    "mergingScript": None,
                                                                    "isProfile": None,
                                                                    "type": "string",
                                                                    "inputColumns": [],
                                                                    "attributes": []
                                                                },
                                                                {
                                                                    "id": "cjtygm02l00d20766m17un5z4",
                                                                    "comment": "If this coding was chosen directly by the user",
                                                                    "name": "userSelected",
                                                                    "mergingScript": None,
                                                                    "isProfile": None,
                                                                    "type": "boolean",
                                                                    "inputColumns": [],
                                                                    "attributes": []
                                                                }
                                                            ]
                                                        }
                                                    ]
                                                },
                                                {
                                                    "id": "cjtygm02o00d407662yf9joy6",
                                                    "comment": "Plain text representation of the concept",
                                                    "name": "text",
                                                    "mergingScript": None,
                                                    "isProfile": None,
                                                    "type": "string",
                                                    "inputColumns": [],
                                                    "attributes": []
                                                }
                                            ]
                                        },
                                        {
                                            "id": "cjtygm02r00d60766z6lfgqox",
                                            "comment": "The namespace for the identifier value",
                                            "name": "system",
                                            "mergingScript": None,
                                            "isProfile": None,
                                            "type": "uri",
                                            "inputColumns": [],
                                            "attributes": []
                                        },
                                        {
                                            "id": "cjtygm02v00d807661enfqtk4",
                                            "comment": "The value that is unique",
                                            "name": "value",
                                            "mergingScript": None,
                                            "isProfile": None,
                                            "type": "string",
                                            "inputColumns": [],
                                            "attributes": []
                                        },
                                        {
                                            "id": "cjtygm02y00da0766csyh75wy",
                                            "comment": "Time period when id is/was valid for use",
                                            "name": "period",
                                            "mergingScript": None,
                                            "isProfile": None,
                                            "type": "Period",
                                            "inputColumns": [],
                                            "attributes": [
                                                {
                                                    "id": "cjtygm03100dc0766zgzrlxrv",
                                                    "comment": "C? Starting time with inclusive boundary",
                                                    "name": "start",
                                                    "mergingScript": None,
                                                    "isProfile": None,
                                                    "type": "dateTime",
                                                    "inputColumns": [],
                                                    "attributes": []
                                                },
                                                {
                                                    "id": "cjtygm03400de07665x1y1b3j",
                                                    "comment": "C? End time with inclusive boundary if not ongoing",
                                                    "name": "end",
                                                    "mergingScript": None,
                                                    "isProfile": None,
                                                    "type": "dateTime",
                                                    "inputColumns": [],
                                                    "attributes": []
                                                }
                                            ]
                                        },
                                        {
                                            "id": "cjtygm03700dg0766k05wfwfp",
                                            "comment": "Organization that issued id (may be just text)",
                                            "name": "assigner",
                                            "mergingScript": None,
                                            "isProfile": None,
                                            "type": "Reference(Organization)",
                                            "inputColumns": [],
                                            "attributes": [
                                                {
                                                    "id": "cjtygm03b00di07668rkbzwfo",
                                                    "comment": "C? Literal reference, Relative, internal or absolute URL",
                                                    "name": "reference",
                                                    "mergingScript": None,
                                                    "isProfile": None,
                                                    "type": "string",
                                                    "inputColumns": [],
                                                    "attributes": []
                                                },
                                                {
                                                    "id": "cjtygm03e00dk07667oyxbu68",
                                                    "comment": "Logical reference, when literal reference is not known",
                                                    "name": "identifier",
                                                    "mergingScript": None,
                                                    "isProfile": None,
                                                    "type": "Identifier",
                                                    "inputColumns": [],
                                                    "attributes": [
                                                        {
                                                            "id": "cjtygm03i00dm0766vd0gv24n",
                                                            "comment": "usual | official | temp | secondary (If known)",
                                                            "name": "use",
                                                            "mergingScript": None,
                                                            "isProfile": None,
                                                            "type": "code",
                                                            "inputColumns": [],
                                                            "attributes": []
                                                        },
                                                        {
                                                            "id": "cjtygm03l00do0766qo34dy0x",
                                                            "comment": "Description of identifier",
                                                            "name": "type",
                                                            "mergingScript": None,
                                                            "isProfile": None,
                                                            "type": "CodeableConcept",
                                                            "inputColumns": [],
                                                            "attributes": [
                                                                {
                                                                    "id": "cjtygm03o00dq0766vj1mx4mz",
                                                                    "comment": "Code defined by a terminology system",
                                                                    "name": "coding",
                                                                    "mergingScript": None,
                                                                    "isProfile": None,
                                                                    "type": "list::Coding",
                                                                    "inputColumns": [],
                                                                    "attributes": [
                                                                        {
                                                                            "id": "cjtygm03r00ds0766ngzlza2x",
                                                                            "comment": None,
                                                                            "name": "Coding_0",
                                                                            "mergingScript": None,
                                                                            "isProfile": True,
                                                                            "type": "Coding",
                                                                            "inputColumns": [],
                                                                            "attributes": [
                                                                                {
                                                                                    "id": "cjtygm03u00du0766kfnbegym",
                                                                                    "comment": "Identity of the terminology system",
                                                                                    "name": "system",
                                                                                    "mergingScript": None,
                                                                                    "isProfile": None,
                                                                                    "type": "uri",
                                                                                    "inputColumns": [],
                                                                                    "attributes": []
                                                                                },
                                                                                {
                                                                                    "id": "cjtygm03x00dw0766dwljwp6c",
                                                                                    "comment": "Version of the system - if relevant",
                                                                                    "name": "version",
                                                                                    "mergingScript": None,
                                                                                    "isProfile": None,
                                                                                    "type": "string",
                                                                                    "inputColumns": [],
                                                                                    "attributes": []
                                                                                },
                                                                                {
                                                                                    "id": "cjtygm04000dy0766gmvcqu13",
                                                                                    "comment": "Symbol in syntax defined by the system",
                                                                                    "name": "code",
                                                                                    "mergingScript": None,
                                                                                    "isProfile": None,
                                                                                    "type": "code",
                                                                                    "inputColumns": [],
                                                                                    "attributes": []
                                                                                },
                                                                                {
                                                                                    "id": "cjtygm04400e00766da7tu2qk",
                                                                                    "comment": "Representation defined by the system",
                                                                                    "name": "display",
                                                                                    "mergingScript": None,
                                                                                    "isProfile": None,
                                                                                    "type": "string",
                                                                                    "inputColumns": [],
                                                                                    "attributes": []
                                                                                },
                                                                                {
                                                                                    "id": "cjtygm04800e207660nm01y9c",
                                                                                    "comment": "If this coding was chosen directly by the user",
                                                                                    "name": "userSelected",
                                                                                    "mergingScript": None,
                                                                                    "isProfile": None,
                                                                                    "type": "boolean",
                                                                                    "inputColumns": [],
                                                                                    "attributes": []
                                                                                }
                                                                            ]
                                                                        }
                                                                    ]
                                                                },
                                                                {
                                                                    "id": "cjtygm04c00e40766alayfxth",
                                                                    "comment": "Plain text representation of the concept",
                                                                    "name": "text",
                                                                    "mergingScript": None,
                                                                    "isProfile": None,
                                                                    "type": "string",
                                                                    "inputColumns": [],
                                                                    "attributes": []
                                                                }
                                                            ]
                                                        },
                                                        {
                                                            "id": "cjtygm04f00e60766v40re0c0",
                                                            "comment": "The namespace for the identifier value",
                                                            "name": "system",
                                                            "mergingScript": None,
                                                            "isProfile": None,
                                                            "type": "uri",
                                                            "inputColumns": [],
                                                            "attributes": []
                                                        },
                                                        {
                                                            "id": "cjtygm04i00e8076682nr2oe1",
                                                            "comment": "The value that is unique",
                                                            "name": "value",
                                                            "mergingScript": None,
                                                            "isProfile": None,
                                                            "type": "string",
                                                            "inputColumns": [],
                                                            "attributes": []
                                                        },
                                                        {
                                                            "id": "cjtygm04l00ea07668e3xrm9s",
                                                            "comment": "Time period when id is/was valid for use",
                                                            "name": "period",
                                                            "mergingScript": None,
                                                            "isProfile": None,
                                                            "type": "Period",
                                                            "inputColumns": [],
                                                            "attributes": [
                                                                {
                                                                    "id": "cjtygm04o00ec0766crkuvfyf",
                                                                    "comment": "C? Starting time with inclusive boundary",
                                                                    "name": "start",
                                                                    "mergingScript": None,
                                                                    "isProfile": None,
                                                                    "type": "dateTime",
                                                                    "inputColumns": [],
                                                                    "attributes": []
                                                                },
                                                                {
                                                                    "id": "cjtygm04r00ee0766kx35zxv0",
                                                                    "comment": "C? End time with inclusive boundary if not ongoing",
                                                                    "name": "end",
                                                                    "mergingScript": None,
                                                                    "isProfile": None,
                                                                    "type": "dateTime",
                                                                    "inputColumns": [],
                                                                    "attributes": []
                                                                }
                                                            ]
                                                        },
                                                        {
                                                            "id": "cjtygm04u00eg0766jhjanwk0",
                                                            "comment": "Organization that issued id (may be just text)",
                                                            "name": "assigner",
                                                            "mergingScript": None,
                                                            "isProfile": None,
                                                            "type": "Reference(Organization)",
                                                            "inputColumns": [],
                                                            "attributes": []
                                                        }
                                                    ]
                                                },
                                                {
                                                    "id": "cjtygm04x00ei0766m01bqlhj",
                                                    "comment": "Text alternative for the resource",
                                                    "name": "display",
                                                    "mergingScript": None,
                                                    "isProfile": None,
                                                    "type": "string",
                                                    "inputColumns": [],
                                                    "attributes": []
                                                }
                                            ]
                                        }
                                    ]
                                },
                                {
                                    "id": "cjtygm05100ek0766xsyt2z7g",
                                    "comment": "Text alternative for the resource",
                                    "name": "display",
                                    "mergingScript": None,
                                    "isProfile": None,
                                    "type": "string",
                                    "inputColumns": [],
                                    "attributes": []
                                }
                            ]
                        }
                    ]
                }
            ]
        },
        {
            "id": "cjtygm05400em07666afye0gf",
            "comment": "Whether this patient's record is in active use",
            "name": "active",
            "mergingScript": None,
            "isProfile": None,
            "type": "boolean",
            "inputColumns": [],
            "attributes": []
        },
        {
            "id": "cjtygm05800eo0766chphpouw",
            "comment": "A name associated with the patient",
            "name": "name",
            "mergingScript": None,
            "isProfile": None,
            "type": "list::HumanName",
            "inputColumns": [],
            "attributes": [
                {
                    "id": "cjtygm05b00eq0766rv6dptuo",
                    "comment": None,
                    "name": "HumanName_0",
                    "mergingScript": None,
                    "isProfile": True,
                    "type": "HumanName",
                    "inputColumns": [],
                    "attributes": [
                        {
                            "id": "cjtygm05f00es07663znf8ax1",
                            "comment": "usual | official | temp | nickname | anonymous | old | maiden",
                            "name": "use",
                            "mergingScript": None,
                            "isProfile": None,
                            "type": "code",
                            "inputColumns": [],
                            "attributes": []
                        },
                        {
                            "id": "cjtygm05i00eu0766myh0c0zq",
                            "comment": "Text representation of the full name",
                            "name": "text",
                            "mergingScript": None,
                            "isProfile": None,
                            "type": "string",
                            "inputColumns": [],
                            "attributes": []
                        },
                        {
                            "id": "cjtygm05l00ew0766oe6lsues",
                            "comment": "Family name (often called 'Surname')",
                            "name": "family",
                            "mergingScript": None,
                            "isProfile": None,
                            "type": "string",
                            "inputColumns": [],
                            "attributes": []
                        },
                        {
                            "id": "cjtygm05p00ey0766lbgseek0",
                            "comment": "Given names (not always 'first'). Includes middle names",
                            "name": "given",
                            "mergingScript": None,
                            "isProfile": None,
                            "type": "list::string",
                            "inputColumns": [],
                            "attributes": []
                        },
                        {
                            "id": "cjtygm05s00f007665gz396u1",
                            "comment": "Parts that come before the name",
                            "name": "prefix",
                            "mergingScript": None,
                            "isProfile": None,
                            "type": "list::string",
                            "inputColumns": [],
                            "attributes": []
                        },
                        {
                            "id": "cjtygm05v00f2076679v971fn",
                            "comment": "Parts that come after the name",
                            "name": "suffix",
                            "mergingScript": None,
                            "isProfile": None,
                            "type": "list::string",
                            "inputColumns": [],
                            "attributes": []
                        },
                        {
                            "id": "cjtygm05x00f40766g8o2rtru",
                            "comment": "Time period when name was/is in use",
                            "name": "period",
                            "mergingScript": None,
                            "isProfile": None,
                            "type": "Period",
                            "inputColumns": [],
                            "attributes": [
                                {
                                    "id": "cjtygm06000f60766wgbdfedf",
                                    "comment": "C? Starting time with inclusive boundary",
                                    "name": "start",
                                    "mergingScript": None,
                                    "isProfile": None,
                                    "type": "dateTime",
                                    "inputColumns": [],
                                    "attributes": []
                                },
                                {
                                    "id": "cjtygm06300f80766wm1g3gc3",
                                    "comment": "C? End time with inclusive boundary if not ongoing",
                                    "name": "end",
                                    "mergingScript": None,
                                    "isProfile": None,
                                    "type": "dateTime",
                                    "inputColumns": [],
                                    "attributes": []
                                }
                            ]
                        }
                    ]
                }
            ]
        },
        {
            "id": "cjtygm06700fa076637zdepgs",
            "comment": "A contact detail for the individual",
            "name": "telecom",
            "mergingScript": None,
            "isProfile": None,
            "type": "list::ContactPoint",
            "inputColumns": [],
            "attributes": [
                {
                    "id": "cjtygm06b00fc0766em71ijgx",
                    "comment": None,
                    "name": "ContactPoint_0",
                    "mergingScript": None,
                    "isProfile": True,
                    "type": "ContactPoint",
                    "inputColumns": [],
                    "attributes": [
                        {
                            "id": "cjtygm06f00fe0766etzyh8kg",
                            "comment": "C? phone | fax | email | pager | url | sms | other",
                            "name": "system",
                            "mergingScript": None,
                            "isProfile": None,
                            "type": "code=phone|fax|email|pager|url|sms",
                            "inputColumns": [],
                            "attributes": []
                        },
                        {
                            "id": "cjtygm06j00fg0766fqcr508f",
                            "comment": "The actual contact point details",
                            "name": "value",
                            "mergingScript": None,
                            "isProfile": None,
                            "type": "string",
                            "inputColumns": [],
                            "attributes": []
                        },
                        {
                            "id": "cjtygm06l00fi0766pb8yb5of",
                            "comment": "home | work | temp | old | mobile - purpose of this contact point",
                            "name": "use",
                            "mergingScript": None,
                            "isProfile": None,
                            "type": "code",
                            "inputColumns": [],
                            "attributes": []
                        },
                        {
                            "id": "cjtygm06p00fk0766ltsu752d",
                            "comment": "Specify preferred order of use (1 = highest)",
                            "name": "rank",
                            "mergingScript": None,
                            "isProfile": None,
                            "type": "positiveInt",
                            "inputColumns": [],
                            "attributes": []
                        },
                        {
                            "id": "cjtygm06s00fm0766b33qykdb",
                            "comment": "Time period when the contact point was/is in use",
                            "name": "period",
                            "mergingScript": None,
                            "isProfile": None,
                            "type": "Period",
                            "inputColumns": [],
                            "attributes": [
                                {
                                    "id": "cjtygm06v00fo0766i8jodx4s",
                                    "comment": "C? Starting time with inclusive boundary",
                                    "name": "start",
                                    "mergingScript": None,
                                    "isProfile": None,
                                    "type": "dateTime",
                                    "inputColumns": [],
                                    "attributes": []
                                },
                                {
                                    "id": "cjtygm06y00fq0766rdnttdbg",
                                    "comment": "C? End time with inclusive boundary if not ongoing",
                                    "name": "end",
                                    "mergingScript": None,
                                    "isProfile": None,
                                    "type": "dateTime",
                                    "inputColumns": [],
                                    "attributes": []
                                }
                            ]
                        }
                    ]
                }
            ]
        },
        {
            "id": "cjtygm07000fs07660h9zhut2",
            "comment": "male | female | other | unknown",
            "name": "gender",
            "mergingScript": "fake_merging_script",
            "isProfile": None,
            "type": "code",
            "inputColumns": [
                {
                    "id": "cjtykdszt046607664mzbv9z3",
                    "owner": None,
                    "table": "PATIENTS",
                    "column": "GENDER",
                    "script": "map_gender",
                    "staticValue": None,
                    "joins": []
                },
                {
                    "id": "cjtykdszt046607mzbv9z3",
                    "owner": None,
                    "table": "PATIENTS",
                    "column": "EXPIRE_FLAG",
                    "script": None,
                    "staticValue": None,
                    "joins": []
                },
                {
                    "id": "fakeid",
                    "owner": None,
                    "table": None,
                    "column": None,
                    "script": None,
                    "staticValue": "fake static value",
                    "joins": []
                }
            ],
            "attributes": []
        },
        {
            "id": "cjtygm07400fu07661e1ksmzx",
            "comment": "The date of birth for the individual",
            "name": "birthDate",
            "mergingScript": None,
            "isProfile": None,
            "type": "date",
            "inputColumns": [
                {
                    "id": "cjtyj4gmp00qk0766rkq9flu9",
                    "owner": None,
                    "table": "PATIENTS",
                    "column": "DOB",
                    "script": "format_date_from_yyyymmdd",
                    "staticValue": None,
                    "joins": []
                }
            ],
            "attributes": []
        },
        {
            "id": "cjtygm07700fw0766d55buici",
            "comment": "",
            "name": "deceasedBoolean",
            "mergingScript": None,
            "isProfile": None,
            "type": "boolean",
            "inputColumns": [
                {
                    "id": "cjtykew9z046i0766wxyijau5",
                    "owner": None,
                    "table": "PATIENTS",
                    "column": "EXPIRE_FLAG",
                    "script": "to_boolean",
                    "staticValue": None,
                    "joins": []
                }
            ],
            "attributes": []
        },
        {
            "id": "cjtygm07900fy0766v9bkg2lo",
            "comment": "",
            "name": "deceasedDateTime",
            "mergingScript": None,
            "isProfile": None,
            "type": "dateTime",
            "inputColumns": [
                {
                    "id": "cjtykdfd3045u07661y1d58am",
                    "owner": None,
                    "table": "PATIENTS",
                    "column": "DOD",
                    "script": "format_date_from_yyyymmdd",
                    "staticValue": None,
                    "joins": []
                }
            ],
            "attributes": []
        },
        {
            "id": "cjtygm07c00g00766mfz89tts",
            "comment": "Addresses for the individual",
            "name": "address",
            "mergingScript": None,
            "isProfile": None,
            "type": "list::Address",
            "inputColumns": [],
            "attributes": [
                {
                    "id": "cjtygm07f00g20766sumot89c",
                    "comment": None,
                    "name": "Address_0",
                    "mergingScript": None,
                    "isProfile": True,
                    "type": "Address",
                    "inputColumns": [],
                    "attributes": [
                        {
                            "id": "cjtygm07i00g40766czfgnfe7",
                            "comment": "home | work | temp | old - purpose of this address",
                            "name": "use",
                            "mergingScript": None,
                            "isProfile": None,
                            "type": "code",
                            "inputColumns": [],
                            "attributes": []
                        },
                        {
                            "id": "cjtygm07l00g607661d1a75ld",
                            "comment": "postal | physical | both",
                            "name": "type",
                            "mergingScript": None,
                            "isProfile": None,
                            "type": "code",
                            "inputColumns": [],
                            "attributes": []
                        },
                        {
                            "id": "cjtygm07p00g80766o7oz8ywr",
                            "comment": "Text representation of the address",
                            "name": "text",
                            "mergingScript": None,
                            "isProfile": None,
                            "type": "string",
                            "inputColumns": [],
                            "attributes": []
                        },
                        {
                            "id": "cjtygm07r00ga07667rpn81pg",
                            "comment": "Street name, number, direction & P.O. Box etc.",
                            "name": "line",
                            "mergingScript": None,
                            "isProfile": None,
                            "type": "list::string",
                            "inputColumns": [],
                            "attributes": []
                        },
                        {
                            "id": "cjtygm07u00gc0766v4azds19",
                            "comment": "Name of city, town etc.",
                            "name": "city",
                            "mergingScript": None,
                            "isProfile": None,
                            "type": "string",
                            "inputColumns": [],
                            "attributes": []
                        },
                        {
                            "id": "cjtygm07w00ge0766n4zurlmx",
                            "comment": "District name (aka county)",
                            "name": "district",
                            "mergingScript": None,
                            "isProfile": None,
                            "type": "string",
                            "inputColumns": [],
                            "attributes": []
                        },
                        {
                            "id": "cjtygm07z00gg0766enkv4ttl",
                            "comment": "Sub-unit of country (abbreviations ok)",
                            "name": "state",
                            "mergingScript": None,
                            "isProfile": None,
                            "type": "string",
                            "inputColumns": [],
                            "attributes": []
                        },
                        {
                            "id": "cjtygm08100gi0766osvlpocr",
                            "comment": "Postal code for area",
                            "name": "postalCode",
                            "mergingScript": None,
                            "isProfile": None,
                            "type": "string",
                            "inputColumns": [],
                            "attributes": []
                        },
                        {
                            "id": "cjtygm08400gk07660fas58vw",
                            "comment": "Country (e.g. can be ISO 3166 2 or 3 letter code)",
                            "name": "country",
                            "mergingScript": None,
                            "isProfile": None,
                            "type": "string",
                            "inputColumns": [],
                            "attributes": []
                        },
                        {
                            "id": "cjtygm08600gm0766bfhzlxd1",
                            "comment": "Time period when address was/is in use",
                            "name": "period",
                            "mergingScript": None,
                            "isProfile": None,
                            "type": "Period",
                            "inputColumns": [],
                            "attributes": [
                                {
                                    "id": "cjtygm08800go0766x55qqh78",
                                    "comment": "C? Starting time with inclusive boundary",
                                    "name": "start",
                                    "mergingScript": None,
                                    "isProfile": None,
                                    "type": "dateTime",
                                    "inputColumns": [],
                                    "attributes": []
                                },
                                {
                                    "id": "cjtygm08a00gq0766z07lm0ym",
                                    "comment": "C? End time with inclusive boundary if not ongoing",
                                    "name": "end",
                                    "mergingScript": None,
                                    "isProfile": None,
                                    "type": "dateTime",
                                    "inputColumns": [],
                                    "attributes": []
                                }
                            ]
                        }
                    ]
                }
            ]
        },
        {
            "id": "cjtygm08d00gs0766rdknu8lf",
            "comment": "Marital (civil) status of a patient",
            "name": "maritalStatus",
            "mergingScript": None,
            "isProfile": None,
            "type": "CodeableConcept",
            "inputColumns": [],
            "attributes": [
                {
                    "id": "cjtygm08f00gu0766apr0d58u",
                    "comment": "Code defined by a terminology system",
                    "name": "coding",
                    "mergingScript": None,
                    "isProfile": None,
                    "type": "list::Coding",
                    "inputColumns": [],
                    "attributes": [
                        {
                            "id": "cjtygm08h00gw0766k3dmjf0b",
                            "comment": None,
                            "name": "Coding_0",
                            "mergingScript": None,
                            "isProfile": True,
                            "type": "Coding",
                            "inputColumns": [],
                            "attributes": [
                                {
                                    "id": "cjtygm08k00gy0766es4boavm",
                                    "comment": "Identity of the terminology system",
                                    "name": "system",
                                    "mergingScript": None,
                                    "isProfile": None,
                                    "type": "uri",
                                    "inputColumns": [],
                                    "attributes": []
                                },
                                {
                                    "id": "cjtygm08m00h00766rj0i61kh",
                                    "comment": "Version of the system - if relevant",
                                    "name": "version",
                                    "mergingScript": None,
                                    "isProfile": None,
                                    "type": "string",
                                    "inputColumns": [],
                                    "attributes": []
                                },
                                {
                                    "id": "cjtygm08p00h20766p8pi48qh",
                                    "comment": "Symbol in syntax defined by the system",
                                    "name": "code",
                                    "mergingScript": None,
                                    "isProfile": None,
                                    "type": "code",
                                    "inputColumns": [
                                        {
                                            "id": "cjtyku53b04720766xmmeojwa",
                                            "owner": None,
                                            "table": "ADMISSIONS",
                                            "column": "MARITAL_STATUS",
                                            "script": None,
                                            "staticValue": None,
                                            "joins": [
                                                {
                                                    "id": "cjtykucjh047d0766hopqaa5s",
                                                    "sourceOwner": None,
                                                    "sourceTable": "PATIENTS",
                                                    "sourceColumn": "SUBJECT_ID",
                                                    "targetOwner": None,
                                                    "targetTable": "ADMISSIONS",
                                                    "targetColumn": "SUBJECT_ID"
                                                }
                                            ]
                                        }
                                    ],
                                    "attributes": []
                                },
                                {
                                    "id": "cjtygm08r00h40766dvq99hjs",
                                    "comment": "Representation defined by the system",
                                    "name": "display",
                                    "mergingScript": None,
                                    "isProfile": None,
                                    "type": "string",
                                    "inputColumns": [],
                                    "attributes": []
                                },
                                {
                                    "id": "cjtygm08v00h60766dp84yhg6",
                                    "comment": "If this coding was chosen directly by the user",
                                    "name": "userSelected",
                                    "mergingScript": None,
                                    "isProfile": None,
                                    "type": "boolean",
                                    "inputColumns": [],
                                    "attributes": []
                                }
                            ]
                        }
                    ]
                },
                {
                    "id": "cjtygm08x00h80766kde0v0a0",
                    "comment": "Plain text representation of the concept",
                    "name": "text",
                    "mergingScript": None,
                    "isProfile": None,
                    "type": "string",
                    "inputColumns": [],
                    "attributes": []
                }
            ]
        },
        {
            "id": "cjtygm09000ha0766920k05xu",
            "comment": "",
            "name": "multipleBirthBoolean",
            "mergingScript": None,
            "isProfile": None,
            "type": "boolean",
            "inputColumns": [],
            "attributes": []
        },
        {
            "id": "cjtygm09300hc076685fnvt1s",
            "comment": "",
            "name": "multipleBirthInteger",
            "mergingScript": None,
            "isProfile": None,
            "type": "integer",
            "inputColumns": [],
            "attributes": []
        },
        {
            "id": "cjtygm09500he0766f8b3abze",
            "comment": "Image of the patient",
            "name": "photo",
            "mergingScript": None,
            "isProfile": None,
            "type": "list::Attachment",
            "inputColumns": [],
            "attributes": [
                {
                    "id": "cjtygm09600hg0766llk9mq42",
                    "comment": None,
                    "name": "Attachment_0",
                    "mergingScript": None,
                    "isProfile": True,
                    "type": "Attachment",
                    "inputColumns": [],
                    "attributes": [
                        {
                            "id": "cjtygm09800hi0766xwyxobvn",
                            "comment": "Mime type of the content, with charset etc.",
                            "name": "contentType",
                            "mergingScript": None,
                            "isProfile": None,
                            "type": "code",
                            "inputColumns": [],
                            "attributes": []
                        },
                        {
                            "id": "cjtygm09a00hk0766riowmpsj",
                            "comment": "Human language of the content (BCP-47)",
                            "name": "language",
                            "mergingScript": None,
                            "isProfile": None,
                            "type": "code",
                            "inputColumns": [],
                            "attributes": []
                        },
                        {
                            "id": "cjtygm09d00hm0766kcbjtwae",
                            "comment": "Data inline, base64ed",
                            "name": "data",
                            "mergingScript": None,
                            "isProfile": None,
                            "type": "base64Binary",
                            "inputColumns": [],
                            "attributes": []
                        },
                        {
                            "id": "cjtygm09f00ho0766iqroc8sy",
                            "comment": "Uri where the data can be found",
                            "name": "url",
                            "mergingScript": None,
                            "isProfile": None,
                            "type": "uri",
                            "inputColumns": [],
                            "attributes": []
                        },
                        {
                            "id": "cjtygm09i00hq076653km3nao",
                            "comment": "Number of bytes of content (if url provided)",
                            "name": "size",
                            "mergingScript": None,
                            "isProfile": None,
                            "type": "unsignedInt",
                            "inputColumns": [],
                            "attributes": []
                        },
                        {
                            "id": "cjtygm09l00hs07667nzggqtw",
                            "comment": "Hash of the data (sha-1, base64ed)",
                            "name": "hash",
                            "mergingScript": None,
                            "isProfile": None,
                            "type": "base64Binary",
                            "inputColumns": [],
                            "attributes": []
                        },
                        {
                            "id": "cjtygm09o00hu0766c0gp9jrh",
                            "comment": "Label to display in place of the data",
                            "name": "title",
                            "mergingScript": None,
                            "isProfile": None,
                            "type": "string",
                            "inputColumns": [],
                            "attributes": []
                        },
                        {
                            "id": "cjtygm09r00hw0766c7yiwaex",
                            "comment": "Date attachment was first created",
                            "name": "creation",
                            "mergingScript": None,
                            "isProfile": None,
                            "type": "dateTime",
                            "inputColumns": [],
                            "attributes": []
                        }
                    ]
                }
            ]
        },
        {
            "id": "cjtygm09y00hy0766n3mt8217",
            "comment": "A contact party (e.g. guardian partner friend) for the patient",
            "name": "contact",
            "mergingScript": None,
            "isProfile": None,
            "type": "list",
            "inputColumns": [],
            "attributes": [
                {
                    "id": "cjtygm0a200i007661tgdil8s",
                    "comment": "The kind of relationship",
                    "name": "relationship",
                    "mergingScript": None,
                    "isProfile": None,
                    "type": "list::CodeableConcept",
                    "inputColumns": [],
                    "attributes": [
                        {
                            "id": "cjtygm0a600i20766ymbm1j1w",
                            "comment": None,
                            "name": "CodeableConcept_0",
                            "mergingScript": None,
                            "isProfile": True,
                            "type": "CodeableConcept",
                            "inputColumns": [],
                            "attributes": [
                                {
                                    "id": "cjtygm0a900i40766vr73dhvl",
                                    "comment": "Code defined by a terminology system",
                                    "name": "coding",
                                    "mergingScript": None,
                                    "isProfile": None,
                                    "type": "list::Coding",
                                    "inputColumns": [],
                                    "attributes": [
                                        {
                                            "id": "cjtygm0ac00i6076657xsykyx",
                                            "comment": None,
                                            "name": "Coding_0",
                                            "mergingScript": None,
                                            "isProfile": True,
                                            "type": "Coding",
                                            "inputColumns": [],
                                            "attributes": [
                                                {
                                                    "id": "cjtygm0af00i80766bmc103z4",
                                                    "comment": "Identity of the terminology system",
                                                    "name": "system",
                                                    "mergingScript": None,
                                                    "isProfile": None,
                                                    "type": "uri",
                                                    "inputColumns": [],
                                                    "attributes": []
                                                },
                                                {
                                                    "id": "cjtygm0ai00ia0766a82e909r",
                                                    "comment": "Version of the system - if relevant",
                                                    "name": "version",
                                                    "mergingScript": None,
                                                    "isProfile": None,
                                                    "type": "string",
                                                    "inputColumns": [],
                                                    "attributes": []
                                                },
                                                {
                                                    "id": "cjtygm0ak00ic0766274quo42",
                                                    "comment": "Symbol in syntax defined by the system",
                                                    "name": "code",
                                                    "mergingScript": None,
                                                    "isProfile": None,
                                                    "type": "code",
                                                    "inputColumns": [],
                                                    "attributes": []
                                                },
                                                {
                                                    "id": "cjtygm0an00ie0766p1hb1wiu",
                                                    "comment": "Representation defined by the system",
                                                    "name": "display",
                                                    "mergingScript": None,
                                                    "isProfile": None,
                                                    "type": "string",
                                                    "inputColumns": [],
                                                    "attributes": []
                                                },
                                                {
                                                    "id": "cjtygm0ap00ig07660efw4c7s",
                                                    "comment": "If this coding was chosen directly by the user",
                                                    "name": "userSelected",
                                                    "mergingScript": None,
                                                    "isProfile": None,
                                                    "type": "boolean",
                                                    "inputColumns": [],
                                                    "attributes": []
                                                }
                                            ]
                                        }
                                    ]
                                },
                                {
                                    "id": "cjtygm0as00ii0766tqpokns2",
                                    "comment": "Plain text representation of the concept",
                                    "name": "text",
                                    "mergingScript": None,
                                    "isProfile": None,
                                    "type": "string",
                                    "inputColumns": [],
                                    "attributes": []
                                }
                            ]
                        }
                    ]
                },
                {
                    "id": "cjtygm0av00ik0766gqioh1p6",
                    "comment": "A contact detail for the person",
                    "name": "telecom",
                    "mergingScript": None,
                    "isProfile": None,
                    "type": "list::ContactPoint",
                    "inputColumns": [],
                    "attributes": [
                        {
                            "id": "cjtygm0ax00im0766jsr89fpm",
                            "comment": None,
                            "name": "ContactPoint_0",
                            "mergingScript": None,
                            "isProfile": True,
                            "type": "ContactPoint",
                            "inputColumns": [],
                            "attributes": [
                                {
                                    "id": "cjtygm0b000io0766ytqseid0",
                                    "comment": "C? phone | fax | email | pager | url | sms | other",
                                    "name": "system",
                                    "mergingScript": None,
                                    "isProfile": None,
                                    "type": "code=phone|fax|email|pager|url|sms",
                                    "inputColumns": [],
                                    "attributes": []
                                },
                                {
                                    "id": "cjtygm0b300iq0766l0g6urj7",
                                    "comment": "The actual contact point details",
                                    "name": "value",
                                    "mergingScript": None,
                                    "isProfile": None,
                                    "type": "string",
                                    "inputColumns": [],
                                    "attributes": []
                                },
                                {
                                    "id": "cjtygm0b500is0766rhtd8l3r",
                                    "comment": "home | work | temp | old | mobile - purpose of this contact point",
                                    "name": "use",
                                    "mergingScript": None,
                                    "isProfile": None,
                                    "type": "code",
                                    "inputColumns": [],
                                    "attributes": []
                                },
                                {
                                    "id": "cjtygm0b700iu0766zn47exs1",
                                    "comment": "Specify preferred order of use (1 = highest)",
                                    "name": "rank",
                                    "mergingScript": None,
                                    "isProfile": None,
                                    "type": "positiveInt",
                                    "inputColumns": [],
                                    "attributes": []
                                },
                                {
                                    "id": "cjtygm0ba00iw0766wxz623j2",
                                    "comment": "Time period when the contact point was/is in use",
                                    "name": "period",
                                    "mergingScript": None,
                                    "isProfile": None,
                                    "type": "Period",
                                    "inputColumns": [],
                                    "attributes": [
                                        {
                                            "id": "cjtygm0bc00iy0766zr0rqszl",
                                            "comment": "C? Starting time with inclusive boundary",
                                            "name": "start",
                                            "mergingScript": None,
                                            "isProfile": None,
                                            "type": "dateTime",
                                            "inputColumns": [],
                                            "attributes": []
                                        },
                                        {
                                            "id": "cjtygm0bf00j00766fity09hk",
                                            "comment": "C? End time with inclusive boundary if not ongoing",
                                            "name": "end",
                                            "mergingScript": None,
                                            "isProfile": None,
                                            "type": "dateTime",
                                            "inputColumns": [],
                                            "attributes": []
                                        }
                                    ]
                                }
                            ]
                        }
                    ]
                },
                {
                    "id": "cjtygm0bh00j20766ks6usmds",
                    "comment": "Address for the contact person",
                    "name": "address",
                    "mergingScript": None,
                    "isProfile": None,
                    "type": "Address",
                    "inputColumns": [],
                    "attributes": [
                        {
                            "id": "cjtygm0bk00j407660mbrrvmv",
                            "comment": "home | work | temp | old - purpose of this address",
                            "name": "use",
                            "mergingScript": None,
                            "isProfile": None,
                            "type": "code",
                            "inputColumns": [],
                            "attributes": []
                        },
                        {
                            "id": "cjtygm0bm00j60766le6mylkg",
                            "comment": "postal | physical | both",
                            "name": "type",
                            "mergingScript": None,
                            "isProfile": None,
                            "type": "code",
                            "inputColumns": [],
                            "attributes": []
                        },
                        {
                            "id": "cjtygm0bo00j80766a6fz8e22",
                            "comment": "Text representation of the address",
                            "name": "text",
                            "mergingScript": None,
                            "isProfile": None,
                            "type": "string",
                            "inputColumns": [],
                            "attributes": []
                        },
                        {
                            "id": "cjtygm0bq00ja0766cjczdsci",
                            "comment": "Street name, number, direction & P.O. Box etc.",
                            "name": "line",
                            "mergingScript": None,
                            "isProfile": None,
                            "type": "list::string",
                            "inputColumns": [],
                            "attributes": []
                        },
                        {
                            "id": "cjtygm0bt00jc0766id6ii018",
                            "comment": "Name of city, town etc.",
                            "name": "city",
                            "mergingScript": None,
                            "isProfile": None,
                            "type": "string",
                            "inputColumns": [],
                            "attributes": []
                        },
                        {
                            "id": "cjtygm0bw00je0766vu7mmxp3",
                            "comment": "District name (aka county)",
                            "name": "district",
                            "mergingScript": None,
                            "isProfile": None,
                            "type": "string",
                            "inputColumns": [],
                            "attributes": []
                        },
                        {
                            "id": "cjtygm0c100jg0766bwdhwxzr",
                            "comment": "Sub-unit of country (abbreviations ok)",
                            "name": "state",
                            "mergingScript": None,
                            "isProfile": None,
                            "type": "string",
                            "inputColumns": [],
                            "attributes": []
                        },
                        {
                            "id": "cjtygm0c500ji0766g9b9fyz0",
                            "comment": "Postal code for area",
                            "name": "postalCode",
                            "mergingScript": None,
                            "isProfile": None,
                            "type": "string",
                            "inputColumns": [],
                            "attributes": []
                        },
                        {
                            "id": "cjtygm0c900jk0766wjxkp2q6",
                            "comment": "Country (e.g. can be ISO 3166 2 or 3 letter code)",
                            "name": "country",
                            "mergingScript": None,
                            "isProfile": None,
                            "type": "string",
                            "inputColumns": [],
                            "attributes": []
                        },
                        {
                            "id": "cjtygm0cc00jm0766v2h39qe9",
                            "comment": "Time period when address was/is in use",
                            "name": "period",
                            "mergingScript": None,
                            "isProfile": None,
                            "type": "Period",
                            "inputColumns": [],
                            "attributes": [
                                {
                                    "id": "cjtygm0ce00jo0766gd169wxi",
                                    "comment": "C? Starting time with inclusive boundary",
                                    "name": "start",
                                    "mergingScript": None,
                                    "isProfile": None,
                                    "type": "dateTime",
                                    "inputColumns": [],
                                    "attributes": []
                                },
                                {
                                    "id": "cjtygm0cg00jq0766q5mxylwt",
                                    "comment": "C? End time with inclusive boundary if not ongoing",
                                    "name": "end",
                                    "mergingScript": None,
                                    "isProfile": None,
                                    "type": "dateTime",
                                    "inputColumns": [],
                                    "attributes": []
                                }
                            ]
                        }
                    ]
                },
                {
                    "id": "cjtygm0cj00js076690utka4e",
                    "comment": "male | female | other | unknown",
                    "name": "gender",
                    "mergingScript": None,
                    "isProfile": None,
                    "type": "code",
                    "inputColumns": [],
                    "attributes": []
                },
                {
                    "id": "cjtygm0cl00ju0766ro2rrpfq",
                    "comment": "C? Organization that is associated with the contact",
                    "name": "organization",
                    "mergingScript": None,
                    "isProfile": None,
                    "type": "Reference(Organization)",
                    "inputColumns": [],
                    "attributes": [
                        {
                            "id": "cjtygm0cq00jw0766e1ezno0c",
                            "comment": "C? Literal reference, Relative, internal or absolute URL",
                            "name": "reference",
                            "mergingScript": None,
                            "isProfile": None,
                            "type": "string",
                            "inputColumns": [],
                            "attributes": []
                        },
                        {
                            "id": "cjtygm0ct00jy0766q0hwf7ly",
                            "comment": "Logical reference, when literal reference is not known",
                            "name": "identifier",
                            "mergingScript": None,
                            "isProfile": None,
                            "type": "Identifier",
                            "inputColumns": [],
                            "attributes": [
                                {
                                    "id": "cjtygm0cv00k00766z31gqhd9",
                                    "comment": "usual | official | temp | secondary (If known)",
                                    "name": "use",
                                    "mergingScript": None,
                                    "isProfile": None,
                                    "type": "code",
                                    "inputColumns": [],
                                    "attributes": []
                                },
                                {
                                    "id": "cjtygm0cy00k20766i8jt3k28",
                                    "comment": "Description of identifier",
                                    "name": "type",
                                    "mergingScript": None,
                                    "isProfile": None,
                                    "type": "CodeableConcept",
                                    "inputColumns": [],
                                    "attributes": [
                                        {
                                            "id": "cjtygm0d100k40766j52t5bhg",
                                            "comment": "Code defined by a terminology system",
                                            "name": "coding",
                                            "mergingScript": None,
                                            "isProfile": None,
                                            "type": "list::Coding",
                                            "inputColumns": [],
                                            "attributes": [
                                                {
                                                    "id": "cjtygm0d400k60766nsd3g2ay",
                                                    "comment": None,
                                                    "name": "Coding_0",
                                                    "mergingScript": None,
                                                    "isProfile": True,
                                                    "type": "Coding",
                                                    "inputColumns": [],
                                                    "attributes": [
                                                        {
                                                            "id": "cjtygm0d600k80766rwdtyd8q",
                                                            "comment": "Identity of the terminology system",
                                                            "name": "system",
                                                            "mergingScript": None,
                                                            "isProfile": None,
                                                            "type": "uri",
                                                            "inputColumns": [],
                                                            "attributes": []
                                                        },
                                                        {
                                                            "id": "cjtygm0d900ka07669omi0o9n",
                                                            "comment": "Version of the system - if relevant",
                                                            "name": "version",
                                                            "mergingScript": None,
                                                            "isProfile": None,
                                                            "type": "string",
                                                            "inputColumns": [],
                                                            "attributes": []
                                                        },
                                                        {
                                                            "id": "cjtygm0db00kc07661y5gf4w8",
                                                            "comment": "Symbol in syntax defined by the system",
                                                            "name": "code",
                                                            "mergingScript": None,
                                                            "isProfile": None,
                                                            "type": "code",
                                                            "inputColumns": [],
                                                            "attributes": []
                                                        },
                                                        {
                                                            "id": "cjtygm0dd00ke0766u3szrfl1",
                                                            "comment": "Representation defined by the system",
                                                            "name": "display",
                                                            "mergingScript": None,
                                                            "isProfile": None,
                                                            "type": "string",
                                                            "inputColumns": [],
                                                            "attributes": []
                                                        },
                                                        {
                                                            "id": "cjtygm0df00kg076639ni7llt",
                                                            "comment": "If this coding was chosen directly by the user",
                                                            "name": "userSelected",
                                                            "mergingScript": None,
                                                            "isProfile": None,
                                                            "type": "boolean",
                                                            "inputColumns": [],
                                                            "attributes": []
                                                        }
                                                    ]
                                                }
                                            ]
                                        },
                                        {
                                            "id": "cjtygm0dh00ki0766uf1tfcn9",
                                            "comment": "Plain text representation of the concept",
                                            "name": "text",
                                            "mergingScript": None,
                                            "isProfile": None,
                                            "type": "string",
                                            "inputColumns": [],
                                            "attributes": []
                                        }
                                    ]
                                },
                                {
                                    "id": "cjtygm0dm00kk0766ujg0axsv",
                                    "comment": "The namespace for the identifier value",
                                    "name": "system",
                                    "mergingScript": None,
                                    "isProfile": None,
                                    "type": "uri",
                                    "inputColumns": [],
                                    "attributes": []
                                },
                                {
                                    "id": "cjtygm0dp00km0766yncf1ais",
                                    "comment": "The value that is unique",
                                    "name": "value",
                                    "mergingScript": None,
                                    "isProfile": None,
                                    "type": "string",
                                    "inputColumns": [],
                                    "attributes": []
                                },
                                {
                                    "id": "cjtygm0dt00ko0766mslwuzf2",
                                    "comment": "Time period when id is/was valid for use",
                                    "name": "period",
                                    "mergingScript": None,
                                    "isProfile": None,
                                    "type": "Period",
                                    "inputColumns": [],
                                    "attributes": [
                                        {
                                            "id": "cjtygm0dv00kq07664fh7sisk",
                                            "comment": "C? Starting time with inclusive boundary",
                                            "name": "start",
                                            "mergingScript": None,
                                            "isProfile": None,
                                            "type": "dateTime",
                                            "inputColumns": [],
                                            "attributes": []
                                        },
                                        {
                                            "id": "cjtygm0dx00ks0766rwl6kj31",
                                            "comment": "C? End time with inclusive boundary if not ongoing",
                                            "name": "end",
                                            "mergingScript": None,
                                            "isProfile": None,
                                            "type": "dateTime",
                                            "inputColumns": [],
                                            "attributes": []
                                        }
                                    ]
                                },
                                {
                                    "id": "cjtygm0e300ku0766yfdq1kcu",
                                    "comment": "Organization that issued id (may be just text)",
                                    "name": "assigner",
                                    "mergingScript": None,
                                    "isProfile": None,
                                    "type": "Reference(Organization)",
                                    "inputColumns": [],
                                    "attributes": [
                                        {
                                            "id": "cjtygm0e600kw0766hg6k7nbh",
                                            "comment": "C? Literal reference, Relative, internal or absolute URL",
                                            "name": "reference",
                                            "mergingScript": None,
                                            "isProfile": None,
                                            "type": "string",
                                            "inputColumns": [],
                                            "attributes": []
                                        },
                                        {
                                            "id": "cjtygm0e800ky0766a9f270a1",
                                            "comment": "Logical reference, when literal reference is not known",
                                            "name": "identifier",
                                            "mergingScript": None,
                                            "isProfile": None,
                                            "type": "Identifier",
                                            "inputColumns": [],
                                            "attributes": [
                                                {
                                                    "id": "cjtygm0ec00l00766qg96g4st",
                                                    "comment": "usual | official | temp | secondary (If known)",
                                                    "name": "use",
                                                    "mergingScript": None,
                                                    "isProfile": None,
                                                    "type": "code",
                                                    "inputColumns": [],
                                                    "attributes": []
                                                },
                                                {
                                                    "id": "cjtygm0ef00l20766ny5wovqu",
                                                    "comment": "Description of identifier",
                                                    "name": "type",
                                                    "mergingScript": None,
                                                    "isProfile": None,
                                                    "type": "CodeableConcept",
                                                    "inputColumns": [],
                                                    "attributes": [
                                                        {
                                                            "id": "cjtygm0ei00l407669iqb38rj",
                                                            "comment": "Code defined by a terminology system",
                                                            "name": "coding",
                                                            "mergingScript": None,
                                                            "isProfile": None,
                                                            "type": "list::Coding",
                                                            "inputColumns": [],
                                                            "attributes": [
                                                                {
                                                                    "id": "cjtygm0ek00l607666v90ga6e",
                                                                    "comment": None,
                                                                    "name": "Coding_0",
                                                                    "mergingScript": None,
                                                                    "isProfile": True,
                                                                    "type": "Coding",
                                                                    "inputColumns": [],
                                                                    "attributes": [
                                                                        {
                                                                            "id": "cjtygm0en00l807661wfoculu",
                                                                            "comment": "Identity of the terminology system",
                                                                            "name": "system",
                                                                            "mergingScript": None,
                                                                            "isProfile": None,
                                                                            "type": "uri",
                                                                            "inputColumns": [],
                                                                            "attributes": []
                                                                        },
                                                                        {
                                                                            "id": "cjtygm0eq00la076619uadukt",
                                                                            "comment": "Version of the system - if relevant",
                                                                            "name": "version",
                                                                            "mergingScript": None,
                                                                            "isProfile": None,
                                                                            "type": "string",
                                                                            "inputColumns": [],
                                                                            "attributes": []
                                                                        },
                                                                        {
                                                                            "id": "cjtygm0es00lc0766uycav5qg",
                                                                            "comment": "Symbol in syntax defined by the system",
                                                                            "name": "code",
                                                                            "mergingScript": None,
                                                                            "isProfile": None,
                                                                            "type": "code",
                                                                            "inputColumns": [],
                                                                            "attributes": []
                                                                        },
                                                                        {
                                                                            "id": "cjtygm0ev00le0766gdakur5u",
                                                                            "comment": "Representation defined by the system",
                                                                            "name": "display",
                                                                            "mergingScript": None,
                                                                            "isProfile": None,
                                                                            "type": "string",
                                                                            "inputColumns": [],
                                                                            "attributes": []
                                                                        },
                                                                        {
                                                                            "id": "cjtygm0ex00lg0766oks4d4qw",
                                                                            "comment": "If this coding was chosen directly by the user",
                                                                            "name": "userSelected",
                                                                            "mergingScript": None,
                                                                            "isProfile": None,
                                                                            "type": "boolean",
                                                                            "inputColumns": [],
                                                                            "attributes": []
                                                                        }
                                                                    ]
                                                                }
                                                            ]
                                                        },
                                                        {
                                                            "id": "cjtygm0f000li07667yke8ucl",
                                                            "comment": "Plain text representation of the concept",
                                                            "name": "text",
                                                            "mergingScript": None,
                                                            "isProfile": None,
                                                            "type": "string",
                                                            "inputColumns": [],
                                                            "attributes": []
                                                        }
                                                    ]
                                                },
                                                {
                                                    "id": "cjtygm0f200lk07668378gqzx",
                                                    "comment": "The namespace for the identifier value",
                                                    "name": "system",
                                                    "mergingScript": None,
                                                    "isProfile": None,
                                                    "type": "uri",
                                                    "inputColumns": [],
                                                    "attributes": []
                                                },
                                                {
                                                    "id": "cjtygm0f500lm0766poy7zk5u",
                                                    "comment": "The value that is unique",
                                                    "name": "value",
                                                    "mergingScript": None,
                                                    "isProfile": None,
                                                    "type": "string",
                                                    "inputColumns": [],
                                                    "attributes": []
                                                },
                                                {
                                                    "id": "cjtygm0f700lo0766q302v9lj",
                                                    "comment": "Time period when id is/was valid for use",
                                                    "name": "period",
                                                    "mergingScript": None,
                                                    "isProfile": None,
                                                    "type": "Period",
                                                    "inputColumns": [],
                                                    "attributes": [
                                                        {
                                                            "id": "cjtygm0f900lq07664wnwob3p",
                                                            "comment": "C? Starting time with inclusive boundary",
                                                            "name": "start",
                                                            "mergingScript": None,
                                                            "isProfile": None,
                                                            "type": "dateTime",
                                                            "inputColumns": [],
                                                            "attributes": []
                                                        },
                                                        {
                                                            "id": "cjtygm0fb00ls0766qs1bukxu",
                                                            "comment": "C? End time with inclusive boundary if not ongoing",
                                                            "name": "end",
                                                            "mergingScript": None,
                                                            "isProfile": None,
                                                            "type": "dateTime",
                                                            "inputColumns": [],
                                                            "attributes": []
                                                        }
                                                    ]
                                                },
                                                {
                                                    "id": "cjtygm0fe00lu0766l3we5vkv",
                                                    "comment": "Organization that issued id (may be just text)",
                                                    "name": "assigner",
                                                    "mergingScript": None,
                                                    "isProfile": None,
                                                    "type": "Reference(Organization)",
                                                    "inputColumns": [],
                                                    "attributes": []
                                                }
                                            ]
                                        },
                                        {
                                            "id": "cjtygm0fh00lw0766rdc3zvs1",
                                            "comment": "Text alternative for the resource",
                                            "name": "display",
                                            "mergingScript": None,
                                            "isProfile": None,
                                            "type": "string",
                                            "inputColumns": [],
                                            "attributes": []
                                        }
                                    ]
                                }
                            ]
                        },
                        {
                            "id": "cjtygm0fl00ly0766y2uzrkx9",
                            "comment": "Text alternative for the resource",
                            "name": "display",
                            "mergingScript": None,
                            "isProfile": None,
                            "type": "string",
                            "inputColumns": [],
                            "attributes": []
                        }
                    ]
                },
                {
                    "id": "cjtygm0fp00m00766nwltgoyg",
                    "comment": "The period during which this contact person or organization is valid to be contacted relating to this patient",
                    "name": "period",
                    "mergingScript": None,
                    "isProfile": None,
                    "type": "Period",
                    "inputColumns": [],
                    "attributes": [
                        {
                            "id": "cjtygm0fr00m20766tnd5xr2s",
                            "comment": "C? Starting time with inclusive boundary",
                            "name": "start",
                            "mergingScript": None,
                            "isProfile": None,
                            "type": "dateTime",
                            "inputColumns": [],
                            "attributes": []
                        },
                        {
                            "id": "cjtygm0fw00m40766i72r8gtl",
                            "comment": "C? End time with inclusive boundary if not ongoing",
                            "name": "end",
                            "mergingScript": None,
                            "isProfile": None,
                            "type": "dateTime",
                            "inputColumns": [],
                            "attributes": []
                        }
                    ]
                }
            ]
        },
        {
            "id": "cjtygm0fz00m6076604kv280a",
            "comment": None,
            "name": "animal",
            "mergingScript": None,
            "isProfile": None,
            "type": "animal",
            "inputColumns": [],
            "attributes": [
                {
                    "id": "cjtygm0g100m807663a9b5vej",
                    "comment": "R!  E.g. Dog, Cow",
                    "name": "species",
                    "mergingScript": None,
                    "isProfile": None,
                    "type": "CodeableConcept",
                    "inputColumns": [],
                    "attributes": [
                        {
                            "id": "cjtygm0g400ma07665ffo8fwx",
                            "comment": "Code defined by a terminology system",
                            "name": "coding",
                            "mergingScript": None,
                            "isProfile": None,
                            "type": "list::Coding",
                            "inputColumns": [],
                            "attributes": [
                                {
                                    "id": "cjtygm0g700mc07669z5urweu",
                                    "comment": None,
                                    "name": "Coding_0",
                                    "mergingScript": None,
                                    "isProfile": True,
                                    "type": "Coding",
                                    "inputColumns": [],
                                    "attributes": [
                                        {
                                            "id": "cjtygm0ga00me0766pwar5va7",
                                            "comment": "Identity of the terminology system",
                                            "name": "system",
                                            "mergingScript": None,
                                            "isProfile": None,
                                            "type": "uri",
                                            "inputColumns": [],
                                            "attributes": []
                                        },
                                        {
                                            "id": "cjtygm0gd00mg07661yk43y47",
                                            "comment": "Version of the system - if relevant",
                                            "name": "version",
                                            "mergingScript": None,
                                            "isProfile": None,
                                            "type": "string",
                                            "inputColumns": [],
                                            "attributes": []
                                        },
                                        {
                                            "id": "cjtygm0gg00mi0766augck9v0",
                                            "comment": "Symbol in syntax defined by the system",
                                            "name": "code",
                                            "mergingScript": None,
                                            "isProfile": None,
                                            "type": "code",
                                            "inputColumns": [],
                                            "attributes": []
                                        },
                                        {
                                            "id": "cjtygm0gj00mk0766s0tu306h",
                                            "comment": "Representation defined by the system",
                                            "name": "display",
                                            "mergingScript": None,
                                            "isProfile": None,
                                            "type": "string",
                                            "inputColumns": [],
                                            "attributes": []
                                        },
                                        {
                                            "id": "cjtygm0gm00mm0766vtypollp",
                                            "comment": "If this coding was chosen directly by the user",
                                            "name": "userSelected",
                                            "mergingScript": None,
                                            "isProfile": None,
                                            "type": "boolean",
                                            "inputColumns": [],
                                            "attributes": []
                                        }
                                    ]
                                }
                            ]
                        },
                        {
                            "id": "cjtygm0gp00mo07664vyw53hk",
                            "comment": "Plain text representation of the concept",
                            "name": "text",
                            "mergingScript": None,
                            "isProfile": None,
                            "type": "string",
                            "inputColumns": [],
                            "attributes": []
                        }
                    ]
                },
                {
                    "id": "cjtygm0gs00mq0766qogtu0nw",
                    "comment": "E.g. Poodle, Angus",
                    "name": "breed",
                    "mergingScript": None,
                    "isProfile": None,
                    "type": "CodeableConcept",
                    "inputColumns": [],
                    "attributes": [
                        {
                            "id": "cjtygm0gw00ms0766p6bp7429",
                            "comment": "Code defined by a terminology system",
                            "name": "coding",
                            "mergingScript": None,
                            "isProfile": None,
                            "type": "list::Coding",
                            "inputColumns": [],
                            "attributes": [
                                {
                                    "id": "cjtygm0gz00mu0766x9h31thm",
                                    "comment": None,
                                    "name": "Coding_0",
                                    "mergingScript": None,
                                    "isProfile": True,
                                    "type": "Coding",
                                    "inputColumns": [],
                                    "attributes": [
                                        {
                                            "id": "cjtygm0h100mw076660lg463s",
                                            "comment": "Identity of the terminology system",
                                            "name": "system",
                                            "mergingScript": None,
                                            "isProfile": None,
                                            "type": "uri",
                                            "inputColumns": [],
                                            "attributes": []
                                        },
                                        {
                                            "id": "cjtygm0h400my0766l2qi9s2q",
                                            "comment": "Version of the system - if relevant",
                                            "name": "version",
                                            "mergingScript": None,
                                            "isProfile": None,
                                            "type": "string",
                                            "inputColumns": [],
                                            "attributes": []
                                        },
                                        {
                                            "id": "cjtygm0h600n00766mtow8n89",
                                            "comment": "Symbol in syntax defined by the system",
                                            "name": "code",
                                            "mergingScript": None,
                                            "isProfile": None,
                                            "type": "code",
                                            "inputColumns": [],
                                            "attributes": []
                                        },
                                        {
                                            "id": "cjtygm0h800n20766ll84nnga",
                                            "comment": "Representation defined by the system",
                                            "name": "display",
                                            "mergingScript": None,
                                            "isProfile": None,
                                            "type": "string",
                                            "inputColumns": [],
                                            "attributes": []
                                        },
                                        {
                                            "id": "cjtygm0ha00n40766hqzwq0ym",
                                            "comment": "If this coding was chosen directly by the user",
                                            "name": "userSelected",
                                            "mergingScript": None,
                                            "isProfile": None,
                                            "type": "boolean",
                                            "inputColumns": [],
                                            "attributes": []
                                        }
                                    ]
                                }
                            ]
                        },
                        {
                            "id": "cjtygm0hc00n607667fbdxegf",
                            "comment": "Plain text representation of the concept",
                            "name": "text",
                            "mergingScript": None,
                            "isProfile": None,
                            "type": "string",
                            "inputColumns": [],
                            "attributes": []
                        }
                    ]
                },
                {
                    "id": "cjtygm0hf00n80766tblmnpk6",
                    "comment": "E.g. Neutered Intact",
                    "name": "genderStatus",
                    "mergingScript": None,
                    "isProfile": None,
                    "type": "CodeableConcept",
                    "inputColumns": [],
                    "attributes": [
                        {
                            "id": "cjtygm0hh00na0766ncpluuv0",
                            "comment": "Code defined by a terminology system",
                            "name": "coding",
                            "mergingScript": None,
                            "isProfile": None,
                            "type": "list::Coding",
                            "inputColumns": [],
                            "attributes": [
                                {
                                    "id": "cjtygm0hk00nc0766at249w7s",
                                    "comment": None,
                                    "name": "Coding_0",
                                    "mergingScript": None,
                                    "isProfile": True,
                                    "type": "Coding",
                                    "inputColumns": [],
                                    "attributes": [
                                        {
                                            "id": "cjtygm0hn00ne076614onadx5",
                                            "comment": "Identity of the terminology system",
                                            "name": "system",
                                            "mergingScript": None,
                                            "isProfile": None,
                                            "type": "uri",
                                            "inputColumns": [],
                                            "attributes": []
                                        },
                                        {
                                            "id": "cjtygm0hp00ng07665s99opp7",
                                            "comment": "Version of the system - if relevant",
                                            "name": "version",
                                            "mergingScript": None,
                                            "isProfile": None,
                                            "type": "string",
                                            "inputColumns": [],
                                            "attributes": []
                                        },
                                        {
                                            "id": "cjtygm0hs00ni0766v774b9dv",
                                            "comment": "Symbol in syntax defined by the system",
                                            "name": "code",
                                            "mergingScript": None,
                                            "isProfile": None,
                                            "type": "code",
                                            "inputColumns": [],
                                            "attributes": []
                                        },
                                        {
                                            "id": "cjtygm0hv00nk0766igxayqiu",
                                            "comment": "Representation defined by the system",
                                            "name": "display",
                                            "mergingScript": None,
                                            "isProfile": None,
                                            "type": "string",
                                            "inputColumns": [],
                                            "attributes": []
                                        },
                                        {
                                            "id": "cjtygm0hx00nm076619gahc2d",
                                            "comment": "If this coding was chosen directly by the user",
                                            "name": "userSelected",
                                            "mergingScript": None,
                                            "isProfile": None,
                                            "type": "boolean",
                                            "inputColumns": [],
                                            "attributes": []
                                        }
                                    ]
                                }
                            ]
                        },
                        {
                            "id": "cjtygm0i000no07665ad8iznw",
                            "comment": "Plain text representation of the concept",
                            "name": "text",
                            "mergingScript": None,
                            "isProfile": None,
                            "type": "string",
                            "inputColumns": [],
                            "attributes": []
                        }
                    ]
                }
            ]
        },
        {
            "id": "cjtygm0i200nq07664qg86ozr",
            "comment": "A list of Languages which may be used to communicate with the patient about his or her health",
            "name": "communication",
            "mergingScript": None,
            "isProfile": None,
            "type": "list",
            "inputColumns": [],
            "attributes": [
                {
                    "id": "cjtygm0i500ns0766r7zq3mxd",
                    "comment": "R!  The language which can be used to communicate with the patient about his or her health",
                    "name": "language",
                    "mergingScript": None,
                    "isProfile": None,
                    "type": "CodeableConcept",
                    "inputColumns": [],
                    "attributes": [
                        {
                            "id": "cjtygm0i700nu0766f444kw8y",
                            "comment": "Code defined by a terminology system",
                            "name": "coding",
                            "mergingScript": None,
                            "isProfile": None,
                            "type": "list::Coding",
                            "inputColumns": [],
                            "attributes": [
                                {
                                    "id": "cjtygm0i900nw0766zg5xrg0c",
                                    "comment": None,
                                    "name": "Coding_0",
                                    "mergingScript": None,
                                    "isProfile": True,
                                    "type": "Coding",
                                    "inputColumns": [],
                                    "attributes": [
                                        {
                                            "id": "cjtygm0ic00ny0766v9j3ogik",
                                            "comment": "Identity of the terminology system",
                                            "name": "system",
                                            "mergingScript": None,
                                            "isProfile": None,
                                            "type": "uri",
                                            "inputColumns": [],
                                            "attributes": []
                                        },
                                        {
                                            "id": "cjtygm0ie00o00766vrz8t7b6",
                                            "comment": "Version of the system - if relevant",
                                            "name": "version",
                                            "mergingScript": None,
                                            "isProfile": None,
                                            "type": "string",
                                            "inputColumns": [],
                                            "attributes": []
                                        },
                                        {
                                            "id": "cjtygm0ig00o20766zmvui8fg",
                                            "comment": "Symbol in syntax defined by the system",
                                            "name": "code",
                                            "mergingScript": None,
                                            "isProfile": None,
                                            "type": "code",
                                            "inputColumns": [
                                                {
                                                    "id": "cjtyl0xj7048d0766u0j1tqtn",
                                                    "owner": None,
                                                    "table": "ADMISSIONS",
                                                    "column": "LANGUAGE",
                                                    "script": None,
                                                    "staticValue": None,
                                                    "joins": []
                                                }
                                            ],
                                            "attributes": []
                                        },
                                        {
                                            "id": "cjtygm0ii00o40766mehyh7kp",
                                            "comment": "Representation defined by the system",
                                            "name": "display",
                                            "mergingScript": None,
                                            "isProfile": None,
                                            "type": "string",
                                            "inputColumns": [],
                                            "attributes": []
                                        },
                                        {
                                            "id": "cjtygm0ik00o60766gfnafarr",
                                            "comment": "If this coding was chosen directly by the user",
                                            "name": "userSelected",
                                            "mergingScript": None,
                                            "isProfile": None,
                                            "type": "boolean",
                                            "inputColumns": [],
                                            "attributes": []
                                        }
                                    ]
                                }
                            ]
                        },
                        {
                            "id": "cjtygm0in00o80766ki15pzex",
                            "comment": "Plain text representation of the concept",
                            "name": "text",
                            "mergingScript": None,
                            "isProfile": None,
                            "type": "string",
                            "inputColumns": [],
                            "attributes": []
                        }
                    ]
                },
                {
                    "id": "cjtygm0ip00oa0766prko10kx",
                    "comment": "Language preference indicator",
                    "name": "preferred",
                    "mergingScript": None,
                    "isProfile": None,
                    "type": "boolean",
                    "inputColumns": [],
                    "attributes": []
                }
            ]
        },
        {
            "id": "cjtygm0ir00oc076625zpmbrx",
            "comment": "Patient's nominated primary care provider",
            "name": "generalPractitioner",
            "mergingScript": None,
            "isProfile": None,
            "type": "list::Reference(Organization|Practitioner)",
            "inputColumns": [],
            "attributes": [
                {
                    "id": "cjtygm0it00oe07662r2v7w94",
                    "comment": None,
                    "name": "Reference_0",
                    "mergingScript": None,
                    "isProfile": True,
                    "type": "Reference",
                    "inputColumns": [],
                    "attributes": [
                        {
                            "id": "cjtygm0iw00og0766h7x93wf0",
                            "comment": "C? Literal reference, Relative, internal or absolute URL",
                            "name": "reference",
                            "mergingScript": None,
                            "isProfile": None,
                            "type": "string",
                            "inputColumns": [],
                            "attributes": []
                        },
                        {
                            "id": "cjtygm0iy00oi0766znjrcwnq",
                            "comment": "Logical reference, when literal reference is not known",
                            "name": "identifier",
                            "mergingScript": None,
                            "isProfile": None,
                            "type": "Identifier",
                            "inputColumns": [],
                            "attributes": [
                                {
                                    "id": "cjtygm0j100ok0766he902fgj",
                                    "comment": "usual | official | temp | secondary (If known)",
                                    "name": "use",
                                    "mergingScript": None,
                                    "isProfile": None,
                                    "type": "code",
                                    "inputColumns": [],
                                    "attributes": []
                                },
                                {
                                    "id": "cjtygm0j300om0766i05llvdu",
                                    "comment": "Description of identifier",
                                    "name": "type",
                                    "mergingScript": None,
                                    "isProfile": None,
                                    "type": "CodeableConcept",
                                    "inputColumns": [],
                                    "attributes": [
                                        {
                                            "id": "cjtygm0j500oo0766hfaj0p2i",
                                            "comment": "Code defined by a terminology system",
                                            "name": "coding",
                                            "mergingScript": None,
                                            "isProfile": None,
                                            "type": "list::Coding",
                                            "inputColumns": [],
                                            "attributes": [
                                                {
                                                    "id": "cjtygm0j600oq07662rqiul4m",
                                                    "comment": None,
                                                    "name": "Coding_0",
                                                    "mergingScript": None,
                                                    "isProfile": True,
                                                    "type": "Coding",
                                                    "inputColumns": [],
                                                    "attributes": [
                                                        {
                                                            "id": "cjtygm0j800os0766pj58xgc3",
                                                            "comment": "Identity of the terminology system",
                                                            "name": "system",
                                                            "mergingScript": None,
                                                            "isProfile": None,
                                                            "type": "uri",
                                                            "inputColumns": [],
                                                            "attributes": []
                                                        },
                                                        {
                                                            "id": "cjtygm0jb00ou0766bkaotbbp",
                                                            "comment": "Version of the system - if relevant",
                                                            "name": "version",
                                                            "mergingScript": None,
                                                            "isProfile": None,
                                                            "type": "string",
                                                            "inputColumns": [],
                                                            "attributes": []
                                                        },
                                                        {
                                                            "id": "cjtygm0jd00ow0766guyaveep",
                                                            "comment": "Symbol in syntax defined by the system",
                                                            "name": "code",
                                                            "mergingScript": None,
                                                            "isProfile": None,
                                                            "type": "code",
                                                            "inputColumns": [],
                                                            "attributes": []
                                                        },
                                                        {
                                                            "id": "cjtygm0jf00oy07668wpaaa28",
                                                            "comment": "Representation defined by the system",
                                                            "name": "display",
                                                            "mergingScript": None,
                                                            "isProfile": None,
                                                            "type": "string",
                                                            "inputColumns": [],
                                                            "attributes": []
                                                        },
                                                        {
                                                            "id": "cjtygm0ji00p00766gc5hkcyf",
                                                            "comment": "If this coding was chosen directly by the user",
                                                            "name": "userSelected",
                                                            "mergingScript": None,
                                                            "isProfile": None,
                                                            "type": "boolean",
                                                            "inputColumns": [],
                                                            "attributes": []
                                                        }
                                                    ]
                                                }
                                            ]
                                        },
                                        {
                                            "id": "cjtygm0jk00p207664l4fitck",
                                            "comment": "Plain text representation of the concept",
                                            "name": "text",
                                            "mergingScript": None,
                                            "isProfile": None,
                                            "type": "string",
                                            "inputColumns": [],
                                            "attributes": []
                                        }
                                    ]
                                },
                                {
                                    "id": "cjtygm0jn00p407666i9i0t0h",
                                    "comment": "The namespace for the identifier value",
                                    "name": "system",
                                    "mergingScript": None,
                                    "isProfile": None,
                                    "type": "uri",
                                    "inputColumns": [],
                                    "attributes": []
                                },
                                {
                                    "id": "cjtygm0jp00p6076642sd9ssp",
                                    "comment": "The value that is unique",
                                    "name": "value",
                                    "mergingScript": None,
                                    "isProfile": None,
                                    "type": "string",
                                    "inputColumns": [],
                                    "attributes": []
                                },
                                {
                                    "id": "cjtygm0jr00p80766wtr4tv9h",
                                    "comment": "Time period when id is/was valid for use",
                                    "name": "period",
                                    "mergingScript": None,
                                    "isProfile": None,
                                    "type": "Period",
                                    "inputColumns": [],
                                    "attributes": [
                                        {
                                            "id": "cjtygm0ju00pa076643md00s8",
                                            "comment": "C? Starting time with inclusive boundary",
                                            "name": "start",
                                            "mergingScript": None,
                                            "isProfile": None,
                                            "type": "dateTime",
                                            "inputColumns": [],
                                            "attributes": []
                                        },
                                        {
                                            "id": "cjtygm0jw00pc0766nykksyu9",
                                            "comment": "C? End time with inclusive boundary if not ongoing",
                                            "name": "end",
                                            "mergingScript": None,
                                            "isProfile": None,
                                            "type": "dateTime",
                                            "inputColumns": [],
                                            "attributes": []
                                        }
                                    ]
                                },
                                {
                                    "id": "cjtygm0jz00pe0766nab6845i",
                                    "comment": "Organization that issued id (may be just text)",
                                    "name": "assigner",
                                    "mergingScript": None,
                                    "isProfile": None,
                                    "type": "Reference(Organization)",
                                    "inputColumns": [],
                                    "attributes": [
                                        {
                                            "id": "cjtygm0k200pg07665kwg17p4",
                                            "comment": "C? Literal reference, Relative, internal or absolute URL",
                                            "name": "reference",
                                            "mergingScript": None,
                                            "isProfile": None,
                                            "type": "string",
                                            "inputColumns": [],
                                            "attributes": []
                                        },
                                        {
                                            "id": "cjtygm0k500pi0766mzdm2pih",
                                            "comment": "Logical reference, when literal reference is not known",
                                            "name": "identifier",
                                            "mergingScript": None,
                                            "isProfile": None,
                                            "type": "Identifier",
                                            "inputColumns": [],
                                            "attributes": [
                                                {
                                                    "id": "cjtygm0k700pk0766r6p2jpm0",
                                                    "comment": "usual | official | temp | secondary (If known)",
                                                    "name": "use",
                                                    "mergingScript": None,
                                                    "isProfile": None,
                                                    "type": "code",
                                                    "inputColumns": [],
                                                    "attributes": []
                                                },
                                                {
                                                    "id": "cjtygm0ka00pm0766e7tmgf7o",
                                                    "comment": "Description of identifier",
                                                    "name": "type",
                                                    "mergingScript": None,
                                                    "isProfile": None,
                                                    "type": "CodeableConcept",
                                                    "inputColumns": [],
                                                    "attributes": [
                                                        {
                                                            "id": "cjtygm0kd00po0766ugjv4wvk",
                                                            "comment": "Code defined by a terminology system",
                                                            "name": "coding",
                                                            "mergingScript": None,
                                                            "isProfile": None,
                                                            "type": "list::Coding",
                                                            "inputColumns": [],
                                                            "attributes": [
                                                                {
                                                                    "id": "cjtygm0kg00pq07667tvdgd16",
                                                                    "comment": None,
                                                                    "name": "Coding_0",
                                                                    "mergingScript": None,
                                                                    "isProfile": True,
                                                                    "type": "Coding",
                                                                    "inputColumns": [],
                                                                    "attributes": [
                                                                        {
                                                                            "id": "cjtygm0kj00ps07664ohw25rp",
                                                                            "comment": "Identity of the terminology system",
                                                                            "name": "system",
                                                                            "mergingScript": None,
                                                                            "isProfile": None,
                                                                            "type": "uri",
                                                                            "inputColumns": [],
                                                                            "attributes": []
                                                                        },
                                                                        {
                                                                            "id": "cjtygm0kl00pu0766dsfuuqo4",
                                                                            "comment": "Version of the system - if relevant",
                                                                            "name": "version",
                                                                            "mergingScript": None,
                                                                            "isProfile": None,
                                                                            "type": "string",
                                                                            "inputColumns": [],
                                                                            "attributes": []
                                                                        },
                                                                        {
                                                                            "id": "cjtygm0kn00pw0766rp8ynjtn",
                                                                            "comment": "Symbol in syntax defined by the system",
                                                                            "name": "code",
                                                                            "mergingScript": None,
                                                                            "isProfile": None,
                                                                            "type": "code",
                                                                            "inputColumns": [],
                                                                            "attributes": []
                                                                        },
                                                                        {
                                                                            "id": "cjtygm0kp00py0766gptrwa2y",
                                                                            "comment": "Representation defined by the system",
                                                                            "name": "display",
                                                                            "mergingScript": None,
                                                                            "isProfile": None,
                                                                            "type": "string",
                                                                            "inputColumns": [],
                                                                            "attributes": []
                                                                        },
                                                                        {
                                                                            "id": "cjtygm0kr00q00766g0hs39zq",
                                                                            "comment": "If this coding was chosen directly by the user",
                                                                            "name": "userSelected",
                                                                            "mergingScript": None,
                                                                            "isProfile": None,
                                                                            "type": "boolean",
                                                                            "inputColumns": [],
                                                                            "attributes": []
                                                                        }
                                                                    ]
                                                                }
                                                            ]
                                                        },
                                                        {
                                                            "id": "cjtygm0kt00q207667m87o0qd",
                                                            "comment": "Plain text representation of the concept",
                                                            "name": "text",
                                                            "mergingScript": None,
                                                            "isProfile": None,
                                                            "type": "string",
                                                            "inputColumns": [],
                                                            "attributes": []
                                                        }
                                                    ]
                                                },
                                                {
                                                    "id": "cjtygm0kv00q40766oes2skrj",
                                                    "comment": "The namespace for the identifier value",
                                                    "name": "system",
                                                    "mergingScript": None,
                                                    "isProfile": None,
                                                    "type": "uri",
                                                    "inputColumns": [],
                                                    "attributes": []
                                                },
                                                {
                                                    "id": "cjtygm0kx00q60766gumtq6tv",
                                                    "comment": "The value that is unique",
                                                    "name": "value",
                                                    "mergingScript": None,
                                                    "isProfile": None,
                                                    "type": "string",
                                                    "inputColumns": [],
                                                    "attributes": []
                                                },
                                                {
                                                    "id": "cjtygm0kz00q807660rjo9f9v",
                                                    "comment": "Time period when id is/was valid for use",
                                                    "name": "period",
                                                    "mergingScript": None,
                                                    "isProfile": None,
                                                    "type": "Period",
                                                    "inputColumns": [],
                                                    "attributes": [
                                                        {
                                                            "id": "cjtygm0l100qa0766ucnevrlc",
                                                            "comment": "C? Starting time with inclusive boundary",
                                                            "name": "start",
                                                            "mergingScript": None,
                                                            "isProfile": None,
                                                            "type": "dateTime",
                                                            "inputColumns": [],
                                                            "attributes": []
                                                        },
                                                        {
                                                            "id": "cjtygm0l300qc0766yfw3b4hs",
                                                            "comment": "C? End time with inclusive boundary if not ongoing",
                                                            "name": "end",
                                                            "mergingScript": None,
                                                            "isProfile": None,
                                                            "type": "dateTime",
                                                            "inputColumns": [],
                                                            "attributes": []
                                                        }
                                                    ]
                                                },
                                                {
                                                    "id": "cjtygm0l500qe076643tz7dmk",
                                                    "comment": "Organization that issued id (may be just text)",
                                                    "name": "assigner",
                                                    "mergingScript": None,
                                                    "isProfile": None,
                                                    "type": "Reference(Organization)",
                                                    "inputColumns": [],
                                                    "attributes": []
                                                }
                                            ]
                                        },
                                        {
                                            "id": "cjtygm0l700qg0766lultyxk7",
                                            "comment": "Text alternative for the resource",
                                            "name": "display",
                                            "mergingScript": None,
                                            "isProfile": None,
                                            "type": "string",
                                            "inputColumns": [],
                                            "attributes": []
                                        }
                                    ]
                                }
                            ]
                        },
                        {
                            "id": "cjtygm0l900qi0766kx2wp6gl",
                            "comment": "Text alternative for the resource",
                            "name": "display",
                            "mergingScript": None,
                            "isProfile": None,
                            "type": "string",
                            "inputColumns": [],
                            "attributes": []
                        }
                    ]
                }
            ]
        },
        {
            "id": "cjtygm0lb00qk0766lo2ekuaj",
            "comment": "Organization that is the custodian of the patient record",
            "name": "managingOrganization",
            "mergingScript": None,
            "isProfile": None,
            "type": "Reference(Organization)",
            "inputColumns": [],
            "attributes": [
                {
                    "id": "cjtygm0lc00qm0766ugni8cbc",
                    "comment": "C? Literal reference, Relative, internal or absolute URL",
                    "name": "reference",
                    "mergingScript": None,
                    "isProfile": None,
                    "type": "string",
                    "inputColumns": [],
                    "attributes": []
                },
                {
                    "id": "cjtygm0lf00qo0766p8itroyp",
                    "comment": "Logical reference, when literal reference is not known",
                    "name": "identifier",
                    "mergingScript": None,
                    "isProfile": None,
                    "type": "Identifier",
                    "inputColumns": [],
                    "attributes": [
                        {
                            "id": "cjtygm0lh00qq0766qndolt5m",
                            "comment": "usual | official | temp | secondary (If known)",
                            "name": "use",
                            "mergingScript": None,
                            "isProfile": None,
                            "type": "code",
                            "inputColumns": [],
                            "attributes": []
                        },
                        {
                            "id": "cjtygm0lj00qs07660nd4eqeu",
                            "comment": "Description of identifier",
                            "name": "type",
                            "mergingScript": None,
                            "isProfile": None,
                            "type": "CodeableConcept",
                            "inputColumns": [],
                            "attributes": [
                                {
                                    "id": "cjtygm0ll00qu0766dbmbwy3t",
                                    "comment": "Code defined by a terminology system",
                                    "name": "coding",
                                    "mergingScript": None,
                                    "isProfile": None,
                                    "type": "list::Coding",
                                    "inputColumns": [],
                                    "attributes": [
                                        {
                                            "id": "cjtygm0lo00qw0766y1wzprij",
                                            "comment": None,
                                            "name": "Coding_0",
                                            "mergingScript": None,
                                            "isProfile": True,
                                            "type": "Coding",
                                            "inputColumns": [],
                                            "attributes": [
                                                {
                                                    "id": "cjtygm0lq00qy0766iaj5jq9k",
                                                    "comment": "Identity of the terminology system",
                                                    "name": "system",
                                                    "mergingScript": None,
                                                    "isProfile": None,
                                                    "type": "uri",
                                                    "inputColumns": [],
                                                    "attributes": []
                                                },
                                                {
                                                    "id": "cjtygm0ls00r007664obp214h",
                                                    "comment": "Version of the system - if relevant",
                                                    "name": "version",
                                                    "mergingScript": None,
                                                    "isProfile": None,
                                                    "type": "string",
                                                    "inputColumns": [],
                                                    "attributes": []
                                                },
                                                {
                                                    "id": "cjtygm0lu00r20766sq82h40m",
                                                    "comment": "Symbol in syntax defined by the system",
                                                    "name": "code",
                                                    "mergingScript": None,
                                                    "isProfile": None,
                                                    "type": "code",
                                                    "inputColumns": [],
                                                    "attributes": []
                                                },
                                                {
                                                    "id": "cjtygm0lw00r40766333z6zi3",
                                                    "comment": "Representation defined by the system",
                                                    "name": "display",
                                                    "mergingScript": None,
                                                    "isProfile": None,
                                                    "type": "string",
                                                    "inputColumns": [],
                                                    "attributes": []
                                                },
                                                {
                                                    "id": "cjtygm0ly00r60766hxcbp7v3",
                                                    "comment": "If this coding was chosen directly by the user",
                                                    "name": "userSelected",
                                                    "mergingScript": None,
                                                    "isProfile": None,
                                                    "type": "boolean",
                                                    "inputColumns": [],
                                                    "attributes": []
                                                }
                                            ]
                                        }
                                    ]
                                },
                                {
                                    "id": "cjtygm0m000r80766b7xjz2bx",
                                    "comment": "Plain text representation of the concept",
                                    "name": "text",
                                    "mergingScript": None,
                                    "isProfile": None,
                                    "type": "string",
                                    "inputColumns": [],
                                    "attributes": []
                                }
                            ]
                        },
                        {
                            "id": "cjtygm0m200ra0766qgnjzzvh",
                            "comment": "The namespace for the identifier value",
                            "name": "system",
                            "mergingScript": None,
                            "isProfile": None,
                            "type": "uri",
                            "inputColumns": [],
                            "attributes": []
                        },
                        {
                            "id": "cjtygm0m400rc0766zo4rpmcx",
                            "comment": "The value that is unique",
                            "name": "value",
                            "mergingScript": None,
                            "isProfile": None,
                            "type": "string",
                            "inputColumns": [],
                            "attributes": []
                        },
                        {
                            "id": "cjtygm0m600re0766hr7abysj",
                            "comment": "Time period when id is/was valid for use",
                            "name": "period",
                            "mergingScript": None,
                            "isProfile": None,
                            "type": "Period",
                            "inputColumns": [],
                            "attributes": [
                                {
                                    "id": "cjtygm0m800rg0766mrn1s5qi",
                                    "comment": "C? Starting time with inclusive boundary",
                                    "name": "start",
                                    "mergingScript": None,
                                    "isProfile": None,
                                    "type": "dateTime",
                                    "inputColumns": [],
                                    "attributes": []
                                },
                                {
                                    "id": "cjtygm0ma00ri0766t1l1jpvg",
                                    "comment": "C? End time with inclusive boundary if not ongoing",
                                    "name": "end",
                                    "mergingScript": None,
                                    "isProfile": None,
                                    "type": "dateTime",
                                    "inputColumns": [],
                                    "attributes": []
                                }
                            ]
                        },
                        {
                            "id": "cjtygm0mc00rk07668yrk6047",
                            "comment": "Organization that issued id (may be just text)",
                            "name": "assigner",
                            "mergingScript": None,
                            "isProfile": None,
                            "type": "Reference(Organization)",
                            "inputColumns": [],
                            "attributes": [
                                {
                                    "id": "cjtygm0me00rm0766vswv9sia",
                                    "comment": "C? Literal reference, Relative, internal or absolute URL",
                                    "name": "reference",
                                    "mergingScript": None,
                                    "isProfile": None,
                                    "type": "string",
                                    "inputColumns": [],
                                    "attributes": []
                                },
                                {
                                    "id": "cjtygm0mf00ro0766x1gzyjkt",
                                    "comment": "Logical reference, when literal reference is not known",
                                    "name": "identifier",
                                    "mergingScript": None,
                                    "isProfile": None,
                                    "type": "Identifier",
                                    "inputColumns": [],
                                    "attributes": [
                                        {
                                            "id": "cjtygm0mi00rq07664m1c3kpe",
                                            "comment": "usual | official | temp | secondary (If known)",
                                            "name": "use",
                                            "mergingScript": None,
                                            "isProfile": None,
                                            "type": "code",
                                            "inputColumns": [],
                                            "attributes": []
                                        },
                                        {
                                            "id": "cjtygm0mk00rs0766tmof37f8",
                                            "comment": "Description of identifier",
                                            "name": "type",
                                            "mergingScript": None,
                                            "isProfile": None,
                                            "type": "CodeableConcept",
                                            "inputColumns": [],
                                            "attributes": [
                                                {
                                                    "id": "cjtygm0mm00ru0766ahkkgvhf",
                                                    "comment": "Code defined by a terminology system",
                                                    "name": "coding",
                                                    "mergingScript": None,
                                                    "isProfile": None,
                                                    "type": "list::Coding",
                                                    "inputColumns": [],
                                                    "attributes": [
                                                        {
                                                            "id": "cjtygm0mp00rw07664m5sr9xi",
                                                            "comment": None,
                                                            "name": "Coding_0",
                                                            "mergingScript": None,
                                                            "isProfile": True,
                                                            "type": "Coding",
                                                            "inputColumns": [],
                                                            "attributes": [
                                                                {
                                                                    "id": "cjtygm0ms00ry07667parus8u",
                                                                    "comment": "Identity of the terminology system",
                                                                    "name": "system",
                                                                    "mergingScript": None,
                                                                    "isProfile": None,
                                                                    "type": "uri",
                                                                    "inputColumns": [],
                                                                    "attributes": []
                                                                },
                                                                {
                                                                    "id": "cjtygm0mu00s007669vlpcq47",
                                                                    "comment": "Version of the system - if relevant",
                                                                    "name": "version",
                                                                    "mergingScript": None,
                                                                    "isProfile": None,
                                                                    "type": "string",
                                                                    "inputColumns": [],
                                                                    "attributes": []
                                                                },
                                                                {
                                                                    "id": "cjtygm0mw00s20766w3ir5i6m",
                                                                    "comment": "Symbol in syntax defined by the system",
                                                                    "name": "code",
                                                                    "mergingScript": None,
                                                                    "isProfile": None,
                                                                    "type": "code",
                                                                    "inputColumns": [],
                                                                    "attributes": []
                                                                },
                                                                {
                                                                    "id": "cjtygm0my00s40766jxdhu6k8",
                                                                    "comment": "Representation defined by the system",
                                                                    "name": "display",
                                                                    "mergingScript": None,
                                                                    "isProfile": None,
                                                                    "type": "string",
                                                                    "inputColumns": [],
                                                                    "attributes": []
                                                                },
                                                                {
                                                                    "id": "cjtygm0n100s60766twwedqsw",
                                                                    "comment": "If this coding was chosen directly by the user",
                                                                    "name": "userSelected",
                                                                    "mergingScript": None,
                                                                    "isProfile": None,
                                                                    "type": "boolean",
                                                                    "inputColumns": [],
                                                                    "attributes": []
                                                                }
                                                            ]
                                                        }
                                                    ]
                                                },
                                                {
                                                    "id": "cjtygm0n300s807661xl3v6dh",
                                                    "comment": "Plain text representation of the concept",
                                                    "name": "text",
                                                    "mergingScript": None,
                                                    "isProfile": None,
                                                    "type": "string",
                                                    "inputColumns": [],
                                                    "attributes": []
                                                }
                                            ]
                                        },
                                        {
                                            "id": "cjtygm0n500sa0766x5d63cla",
                                            "comment": "The namespace for the identifier value",
                                            "name": "system",
                                            "mergingScript": None,
                                            "isProfile": None,
                                            "type": "uri",
                                            "inputColumns": [],
                                            "attributes": []
                                        },
                                        {
                                            "id": "cjtygm0n600sc0766bnzm4tcr",
                                            "comment": "The value that is unique",
                                            "name": "value",
                                            "mergingScript": None,
                                            "isProfile": None,
                                            "type": "string",
                                            "inputColumns": [],
                                            "attributes": []
                                        },
                                        {
                                            "id": "cjtygm0n800se0766agno3sxl",
                                            "comment": "Time period when id is/was valid for use",
                                            "name": "period",
                                            "mergingScript": None,
                                            "isProfile": None,
                                            "type": "Period",
                                            "inputColumns": [],
                                            "attributes": [
                                                {
                                                    "id": "cjtygm0na00sg0766cvaiq0eq",
                                                    "comment": "C? Starting time with inclusive boundary",
                                                    "name": "start",
                                                    "mergingScript": None,
                                                    "isProfile": None,
                                                    "type": "dateTime",
                                                    "inputColumns": [],
                                                    "attributes": []
                                                },
                                                {
                                                    "id": "cjtygm0nc00si0766vn1hg8ax",
                                                    "comment": "C? End time with inclusive boundary if not ongoing",
                                                    "name": "end",
                                                    "mergingScript": None,
                                                    "isProfile": None,
                                                    "type": "dateTime",
                                                    "inputColumns": [],
                                                    "attributes": []
                                                }
                                            ]
                                        },
                                        {
                                            "id": "cjtygm0ne00sk0766qkfhffal",
                                            "comment": "Organization that issued id (may be just text)",
                                            "name": "assigner",
                                            "mergingScript": None,
                                            "isProfile": None,
                                            "type": "Reference(Organization)",
                                            "inputColumns": [],
                                            "attributes": []
                                        }
                                    ]
                                },
                                {
                                    "id": "cjtygm0ng00sm0766omsbnjte",
                                    "comment": "Text alternative for the resource",
                                    "name": "display",
                                    "mergingScript": None,
                                    "isProfile": None,
                                    "type": "string",
                                    "inputColumns": [],
                                    "attributes": []
                                }
                            ]
                        }
                    ]
                },
                {
                    "id": "cjtygm0ni00so07661udrc8ql",
                    "comment": "Text alternative for the resource",
                    "name": "display",
                    "mergingScript": None,
                    "isProfile": None,
                    "type": "string",
                    "inputColumns": [],
                    "attributes": []
                }
            ]
        },
        {
            "id": "cjtygm0nk00sq0766x6ydqf6v",
            "comment": "Link to another patient resource that concerns the same actual person",
            "name": "link",
            "mergingScript": None,
            "isProfile": None,
            "type": "list",
            "inputColumns": [],
            "attributes": [
                {
                    "id": "cjtygm0nm00ss0766wl2o5y0i",
                    "comment": "R!  The other patient or related person resource that the link refers to",
                    "name": "other",
                    "mergingScript": None,
                    "isProfile": None,
                    "type": "Reference(Patient|RelatedPerson)",
                    "inputColumns": [],
                    "attributes": [
                        {
                            "id": "cjtygm0no00su0766k427jm6w",
                            "comment": "C? Literal reference, Relative, internal or absolute URL",
                            "name": "reference",
                            "mergingScript": None,
                            "isProfile": None,
                            "type": "string",
                            "inputColumns": [],
                            "attributes": []
                        },
                        {
                            "id": "cjtygm0nq00sw07665pxx270h",
                            "comment": "Logical reference, when literal reference is not known",
                            "name": "identifier",
                            "mergingScript": None,
                            "isProfile": None,
                            "type": "Identifier",
                            "inputColumns": [],
                            "attributes": [
                                {
                                    "id": "cjtygm0ns00sy0766y36kcgm1",
                                    "comment": "usual | official | temp | secondary (If known)",
                                    "name": "use",
                                    "mergingScript": None,
                                    "isProfile": None,
                                    "type": "code",
                                    "inputColumns": [],
                                    "attributes": []
                                },
                                {
                                    "id": "cjtygm0nv00t007667gpsyzwk",
                                    "comment": "Description of identifier",
                                    "name": "type",
                                    "mergingScript": None,
                                    "isProfile": None,
                                    "type": "CodeableConcept",
                                    "inputColumns": [],
                                    "attributes": [
                                        {
                                            "id": "cjtygm0nx00t20766j81vpzux",
                                            "comment": "Code defined by a terminology system",
                                            "name": "coding",
                                            "mergingScript": None,
                                            "isProfile": None,
                                            "type": "list::Coding",
                                            "inputColumns": [],
                                            "attributes": [
                                                {
                                                    "id": "cjtygm0nz00t40766f2zeq9eq",
                                                    "comment": None,
                                                    "name": "Coding_0",
                                                    "mergingScript": None,
                                                    "isProfile": True,
                                                    "type": "Coding",
                                                    "inputColumns": [],
                                                    "attributes": [
                                                        {
                                                            "id": "cjtygm0o100t60766v6qf8h78",
                                                            "comment": "Identity of the terminology system",
                                                            "name": "system",
                                                            "mergingScript": None,
                                                            "isProfile": None,
                                                            "type": "uri",
                                                            "inputColumns": [],
                                                            "attributes": []
                                                        },
                                                        {
                                                            "id": "cjtygm0o300t807662p3iewsd",
                                                            "comment": "Version of the system - if relevant",
                                                            "name": "version",
                                                            "mergingScript": None,
                                                            "isProfile": None,
                                                            "type": "string",
                                                            "inputColumns": [],
                                                            "attributes": []
                                                        },
                                                        {
                                                            "id": "cjtygm0o500ta0766d1ewfvqt",
                                                            "comment": "Symbol in syntax defined by the system",
                                                            "name": "code",
                                                            "mergingScript": None,
                                                            "isProfile": None,
                                                            "type": "code",
                                                            "inputColumns": [],
                                                            "attributes": []
                                                        },
                                                        {
                                                            "id": "cjtygm0o700tc0766emzxqokt",
                                                            "comment": "Representation defined by the system",
                                                            "name": "display",
                                                            "mergingScript": None,
                                                            "isProfile": None,
                                                            "type": "string",
                                                            "inputColumns": [],
                                                            "attributes": []
                                                        },
                                                        {
                                                            "id": "cjtygm0o900te0766kqvl517d",
                                                            "comment": "If this coding was chosen directly by the user",
                                                            "name": "userSelected",
                                                            "mergingScript": None,
                                                            "isProfile": None,
                                                            "type": "boolean",
                                                            "inputColumns": [],
                                                            "attributes": []
                                                        }
                                                    ]
                                                }
                                            ]
                                        },
                                        {
                                            "id": "cjtygm0ob00tg0766kvhrgr5h",
                                            "comment": "Plain text representation of the concept",
                                            "name": "text",
                                            "mergingScript": None,
                                            "isProfile": None,
                                            "type": "string",
                                            "inputColumns": [],
                                            "attributes": []
                                        }
                                    ]
                                },
                                {
                                    "id": "cjtygm0oc00ti0766xe8w00is",
                                    "comment": "The namespace for the identifier value",
                                    "name": "system",
                                    "mergingScript": None,
                                    "isProfile": None,
                                    "type": "uri",
                                    "inputColumns": [],
                                    "attributes": []
                                },
                                {
                                    "id": "cjtygm0oe00tk0766q0l02c60",
                                    "comment": "The value that is unique",
                                    "name": "value",
                                    "mergingScript": None,
                                    "isProfile": None,
                                    "type": "string",
                                    "inputColumns": [],
                                    "attributes": []
                                },
                                {
                                    "id": "cjtygm0og00tm076644ivxhea",
                                    "comment": "Time period when id is/was valid for use",
                                    "name": "period",
                                    "mergingScript": None,
                                    "isProfile": None,
                                    "type": "Period",
                                    "inputColumns": [],
                                    "attributes": [
                                        {
                                            "id": "cjtygm0oi00to0766cfda7dy4",
                                            "comment": "C? Starting time with inclusive boundary",
                                            "name": "start",
                                            "mergingScript": None,
                                            "isProfile": None,
                                            "type": "dateTime",
                                            "inputColumns": [],
                                            "attributes": []
                                        },
                                        {
                                            "id": "cjtygm0ok00tq0766osihtjsy",
                                            "comment": "C? End time with inclusive boundary if not ongoing",
                                            "name": "end",
                                            "mergingScript": None,
                                            "isProfile": None,
                                            "type": "dateTime",
                                            "inputColumns": [],
                                            "attributes": []
                                        }
                                    ]
                                },
                                {
                                    "id": "cjtygm0om00ts0766qy4jqjw7",
                                    "comment": "Organization that issued id (may be just text)",
                                    "name": "assigner",
                                    "mergingScript": None,
                                    "isProfile": None,
                                    "type": "Reference(Organization)",
                                    "inputColumns": [],
                                    "attributes": [
                                        {
                                            "id": "cjtygm0oo00tu0766idogjuji",
                                            "comment": "C? Literal reference, Relative, internal or absolute URL",
                                            "name": "reference",
                                            "mergingScript": None,
                                            "isProfile": None,
                                            "type": "string",
                                            "inputColumns": [],
                                            "attributes": []
                                        },
                                        {
                                            "id": "cjtygm0oq00tw07669r3c8iy3",
                                            "comment": "Logical reference, when literal reference is not known",
                                            "name": "identifier",
                                            "mergingScript": None,
                                            "isProfile": None,
                                            "type": "Identifier",
                                            "inputColumns": [],
                                            "attributes": [
                                                {
                                                    "id": "cjtygm0os00ty076626iidfw1",
                                                    "comment": "usual | official | temp | secondary (If known)",
                                                    "name": "use",
                                                    "mergingScript": None,
                                                    "isProfile": None,
                                                    "type": "code",
                                                    "inputColumns": [],
                                                    "attributes": []
                                                },
                                                {
                                                    "id": "cjtygm0ot00u00766gujnbx6z",
                                                    "comment": "Description of identifier",
                                                    "name": "type",
                                                    "mergingScript": None,
                                                    "isProfile": None,
                                                    "type": "CodeableConcept",
                                                    "inputColumns": [],
                                                    "attributes": [
                                                        {
                                                            "id": "cjtygm0ov00u20766tqye27fe",
                                                            "comment": "Code defined by a terminology system",
                                                            "name": "coding",
                                                            "mergingScript": None,
                                                            "isProfile": None,
                                                            "type": "list::Coding",
                                                            "inputColumns": [],
                                                            "attributes": [
                                                                {
                                                                    "id": "cjtygm0ox00u40766kqpqbto3",
                                                                    "comment": None,
                                                                    "name": "Coding_0",
                                                                    "mergingScript": None,
                                                                    "isProfile": True,
                                                                    "type": "Coding",
                                                                    "inputColumns": [],
                                                                    "attributes": [
                                                                        {
                                                                            "id": "cjtygm0oz00u607668nfvgc2x",
                                                                            "comment": "Identity of the terminology system",
                                                                            "name": "system",
                                                                            "mergingScript": None,
                                                                            "isProfile": None,
                                                                            "type": "uri",
                                                                            "inputColumns": [],
                                                                            "attributes": []
                                                                        },
                                                                        {
                                                                            "id": "cjtygm0p100u80766us3vw5ey",
                                                                            "comment": "Version of the system - if relevant",
                                                                            "name": "version",
                                                                            "mergingScript": None,
                                                                            "isProfile": None,
                                                                            "type": "string",
                                                                            "inputColumns": [],
                                                                            "attributes": []
                                                                        },
                                                                        {
                                                                            "id": "cjtygm0p300ua0766w1589lgn",
                                                                            "comment": "Symbol in syntax defined by the system",
                                                                            "name": "code",
                                                                            "mergingScript": None,
                                                                            "isProfile": None,
                                                                            "type": "code",
                                                                            "inputColumns": [],
                                                                            "attributes": []
                                                                        },
                                                                        {
                                                                            "id": "cjtygm0p500uc0766not1ryv0",
                                                                            "comment": "Representation defined by the system",
                                                                            "name": "display",
                                                                            "mergingScript": None,
                                                                            "isProfile": None,
                                                                            "type": "string",
                                                                            "inputColumns": [],
                                                                            "attributes": []
                                                                        },
                                                                        {
                                                                            "id": "cjtygm0p800ue0766yzz1azk1",
                                                                            "comment": "If this coding was chosen directly by the user",
                                                                            "name": "userSelected",
                                                                            "mergingScript": None,
                                                                            "isProfile": None,
                                                                            "type": "boolean",
                                                                            "inputColumns": [],
                                                                            "attributes": []
                                                                        }
                                                                    ]
                                                                }
                                                            ]
                                                        },
                                                        {
                                                            "id": "cjtygm0pb00ug0766btajuwla",
                                                            "comment": "Plain text representation of the concept",
                                                            "name": "text",
                                                            "mergingScript": None,
                                                            "isProfile": None,
                                                            "type": "string",
                                                            "inputColumns": [],
                                                            "attributes": []
                                                        }
                                                    ]
                                                },
                                                {
                                                    "id": "cjtygm0pd00ui07667uuygftu",
                                                    "comment": "The namespace for the identifier value",
                                                    "name": "system",
                                                    "mergingScript": None,
                                                    "isProfile": None,
                                                    "type": "uri",
                                                    "inputColumns": [],
                                                    "attributes": []
                                                },
                                                {
                                                    "id": "cjtygm0pf00uk07669ld7zsjs",
                                                    "comment": "The value that is unique",
                                                    "name": "value",
                                                    "mergingScript": None,
                                                    "isProfile": None,
                                                    "type": "string",
                                                    "inputColumns": [],
                                                    "attributes": []
                                                },
                                                {
                                                    "id": "cjtygm0ph00um0766r6yb36t1",
                                                    "comment": "Time period when id is/was valid for use",
                                                    "name": "period",
                                                    "mergingScript": None,
                                                    "isProfile": None,
                                                    "type": "Period",
                                                    "inputColumns": [],
                                                    "attributes": [
                                                        {
                                                            "id": "cjtygm0pj00uo0766rrqaform",
                                                            "comment": "C? Starting time with inclusive boundary",
                                                            "name": "start",
                                                            "mergingScript": None,
                                                            "isProfile": None,
                                                            "type": "dateTime",
                                                            "inputColumns": [],
                                                            "attributes": []
                                                        },
                                                        {
                                                            "id": "cjtygm0pk00uq0766mu89qh7b",
                                                            "comment": "C? End time with inclusive boundary if not ongoing",
                                                            "name": "end",
                                                            "mergingScript": None,
                                                            "isProfile": None,
                                                            "type": "dateTime",
                                                            "inputColumns": [],
                                                            "attributes": []
                                                        }
                                                    ]
                                                },
                                                {
                                                    "id": "cjtygm0pn00us0766hus5tena",
                                                    "comment": "Organization that issued id (may be just text)",
                                                    "name": "assigner",
                                                    "mergingScript": None,
                                                    "isProfile": None,
                                                    "type": "Reference(Organization)",
                                                    "inputColumns": [],
                                                    "attributes": []
                                                }
                                            ]
                                        },
                                        {
                                            "id": "cjtygm0pp00uu0766zq4377n2",
                                            "comment": "Text alternative for the resource",
                                            "name": "display",
                                            "mergingScript": None,
                                            "isProfile": None,
                                            "type": "string",
                                            "inputColumns": [],
                                            "attributes": []
                                        }
                                    ]
                                }
                            ]
                        },
                        {
                            "id": "cjtygm0pr00uw0766md74ypw3",
                            "comment": "Text alternative for the resource",
                            "name": "display",
                            "mergingScript": None,
                            "isProfile": None,
                            "type": "string",
                            "inputColumns": [],
                            "attributes": []
                        }
                    ]
                },
                {
                    "id": "cjtygm0ps00uy07662mnvg81g",
                    "comment": "R!  replaced-by | replaces | refer | seealso - type of link",
                    "name": "type",
                    "mergingScript": None,
                    "isProfile": None,
                    "type": "code=replaced-by|replaces|refer|seealso",
                    "inputColumns": [],
                    "attributes": []
                }
            ]
        }
    ]
}
PRUNED_FHIR_RESOURCE = {
    "id": "cjtyglzyd00bh0766w42omeb9",
    "name": "Patient",
    "attributes": [
        {
            "id": "cjtyglzz300bi0766tjms54pu",
            "comment": "An identifier for this patient",
            "name": "identifier",
            "mergingScript": None,
            "isProfile": None,
            "type": "list::Identifier",
            "inputColumns": [],
            "attributes": [
                {
                    "id": "cjtyglzzd00bk076690zuwn0p",
                    "comment": None,
                    "name": "Identifier_0",
                    "mergingScript": None,
                    "isProfile": True,
                    "type": "Identifier",
                    "inputColumns": [],
                    "attributes": [
                        {
                            "id": "cjtygm00x00c807662i1y484t",
                            "comment": "The value that is unique",
                            "name": "value",
                            "mergingScript": None,
                            "isProfile": None,
                            "type": "string",
                            "inputColumns": [
                                {
                                    "id": "cjtyiyk9500q707661w96ml2j",
                                    "owner": None,
                                    "table": "PATIENTS",
                                    "column": "SUBJECT_ID",
                                    "script": None,
                                    "staticValue": None,
                                    "joins": []
                                }
                            ],
                            "attributes": []
                        }
                    ]
                }
            ]
        },
        {
            "id": "cjtygm07000fs07660h9zhut2",
            "comment": "male | female | other | unknown",
            "name": "gender",
            "mergingScript": "fake_merging_script",
            "isProfile": None,
            "type": "code",
            "inputColumns": [
                {
                    "id": "cjtykdszt046607664mzbv9z3",
                    "owner": None,
                    "table": "PATIENTS",
                    "column": "GENDER",
                    "script": "map_gender",
                    "staticValue": None,
                    "joins": []
                },
                {
                    "id": "cjtykdszt046607mzbv9z3",
                    "owner": None,
                    "table": "PATIENTS",
                    "column": "EXPIRE_FLAG",
                    "script": None,
                    "staticValue": None,
                    "joins": []
                },
                {
                    "id": "fakeid",
                    "owner": None,
                    "table": None,
                    "column": None,
                    "script": None,
                    "staticValue": "fake static value",
                    "joins": []
                }
            ],
            "attributes": []
        },
        {
            "id": "cjtygm07400fu07661e1ksmzx",
            "comment": "The date of birth for the individual",
            "name": "birthDate",
            "mergingScript": None,
            "isProfile": None,
            "type": "date",
            "inputColumns": [
                {
                    "id": "cjtyj4gmp00qk0766rkq9flu9",
                    "owner": None,
                    "table": "PATIENTS",
                    "column": "DOB",
                    "script": "format_date_from_yyyymmdd",
                    "staticValue": None,
                    "joins": []
                }
            ],
            "attributes": []
        },
        {
            "id": "cjtygm07700fw0766d55buici",
            "comment": "",
            "name": "deceasedBoolean",
            "mergingScript": None,
            "isProfile": None,
            "type": "boolean",
            "inputColumns": [
                {
                    "id": "cjtykew9z046i0766wxyijau5",
                    "owner": None,
                    "table": "PATIENTS",
                    "column": "EXPIRE_FLAG",
                    "script": "to_boolean",
                    "staticValue": None,
                    "joins": []
                }
            ],
            "attributes": []
        },
        {
            "id": "cjtygm07900fy0766v9bkg2lo",
            "comment": "",
            "name": "deceasedDateTime",
            "mergingScript": None,
            "isProfile": None,
            "type": "dateTime",
            "inputColumns": [
                {
                    "id": "cjtykdfd3045u07661y1d58am",
                    "owner": None,
                    "table": "PATIENTS",
                    "column": "DOD",
                    "script": "format_date_from_yyyymmdd",
                    "staticValue": None,
                    "joins": []
                }
            ],
            "attributes": []
        },
        {
            "id": "cjtygm08d00gs0766rdknu8lf",
            "comment": "Marital (civil) status of a patient",
            "name": "maritalStatus",
            "mergingScript": None,
            "isProfile": None,
            "type": "CodeableConcept",
            "inputColumns": [],
            "attributes": [
                {
                    "id": "cjtygm08f00gu0766apr0d58u",
                    "comment": "Code defined by a terminology system",
                    "name": "coding",
                    "mergingScript": None,
                    "isProfile": None,
                    "type": "list::Coding",
                    "inputColumns": [],
                    "attributes": [
                        {
                            "id": "cjtygm08h00gw0766k3dmjf0b",
                            "comment": None,
                            "name": "Coding_0",
                            "mergingScript": None,
                            "isProfile": True,
                            "type": "Coding",
                            "inputColumns": [],
                            "attributes": [
                                {
                                    "id": "cjtygm08p00h20766p8pi48qh",
                                    "comment": "Symbol in syntax defined by the system",
                                    "name": "code",
                                    "mergingScript": None,
                                    "isProfile": None,
                                    "type": "code",
                                    "inputColumns": [
                                        {
                                            "id": "cjtyku53b04720766xmmeojwa",
                                            "owner": None,
                                            "table": "ADMISSIONS",
                                            "column": "MARITAL_STATUS",
                                            "script": None,
                                            "staticValue": None,
                                            "joins": [
                                                {
                                                    "id": "cjtykucjh047d0766hopqaa5s",
                                                    "sourceOwner": None,
                                                    "sourceTable": "PATIENTS",
                                                    "sourceColumn": "SUBJECT_ID",
                                                    "targetOwner": None,
                                                    "targetTable": "ADMISSIONS",
                                                    "targetColumn": "SUBJECT_ID"
                                                }
                                            ]
                                        }
                                    ],
                                    "attributes": []
                                }
                            ]
                        }
                    ]
                }
            ]
        },
        {
            "id": "cjtygm0i200nq07664qg86ozr",
            "comment": "A list of Languages which may be used to communicate with the patient about his or her health",
            "name": "communication",
            "mergingScript": None,
            "isProfile": None,
            "type": "list",
            "inputColumns": [],
            "attributes": [
                {
                    "id": "cjtygm0i500ns0766r7zq3mxd",
                    "comment": "R!  The language which can be used to communicate with the patient about his or her health",
                    "name": "language",
                    "mergingScript": None,
                    "isProfile": None,
                    "type": "CodeableConcept",
                    "inputColumns": [],
                    "attributes": [
                        {
                            "id": "cjtygm0i700nu0766f444kw8y",
                            "comment": "Code defined by a terminology system",
                            "name": "coding",
                            "mergingScript": None,
                            "isProfile": None,
                            "type": "list::Coding",
                            "inputColumns": [],
                            "attributes": [
                                {
                                    "id": "cjtygm0i900nw0766zg5xrg0c",
                                    "comment": None,
                                    "name": "Coding_0",
                                    "mergingScript": None,
                                    "isProfile": True,
                                    "type": "Coding",
                                    "inputColumns": [],
                                    "attributes": [
                                        {
                                            "id": "cjtygm0ig00o20766zmvui8fg",
                                            "comment": "Symbol in syntax defined by the system",
                                            "name": "code",
                                            "mergingScript": None,
                                            "isProfile": None,
                                            "type": "code",
                                            "inputColumns": [
                                                {
                                                    "id": "cjtyl0xj7048d0766u0j1tqtn",
                                                    "owner": None,
                                                    "table": "ADMISSIONS",
                                                    "column": "LANGUAGE",
                                                    "script": None,
                                                    "staticValue": None,
                                                    "joins": []
                                                }
                                            ],
                                            "attributes": []
                                        }
                                    ]
                                }
                            ]
                        }
                    ]
                }
            ]
        }
    ]
}