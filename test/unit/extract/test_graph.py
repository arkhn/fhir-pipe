from fhirpipe.extract.graph import DependencyGraph, Table


def test_graph():
    graph = DependencyGraph()

    assert not graph.has("tutu")

    graph.add("tutu")

    assert graph.has("tutu")

    assert isinstance(graph.get("tutu"), Table)

    graph.add("titi")

    tutu = graph.get("tutu")
    tata = graph.get("titi")

    assert not tutu.connected(tata)
    tutu.connect(tata)
    assert tutu.connected(tata)
