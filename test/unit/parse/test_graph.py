from fhirpipe.parse.graph import DependencyGraph, Table


def test_graph():
    graph = DependencyGraph()

    assert not graph.has('tutu')

    graph.add('tutu')

    assert graph.has('tutu')

    assert isinstance(graph.get('tutu'), Table)

    graph.add('tata')

    tutu = graph.get('tutu')
    tata = graph.get('tata')

    assert not tutu.connected(tata)
    tutu.connect(tata, 'OneToOne')
    assert tutu.connected(tata)